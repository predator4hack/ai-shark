"""
Gemini API integration for slide analysis.

This module provides the GeminiAnalyzer class that interfaces with Google's
Gemini Pro Vision API to analyze pitch deck slides and extract structured information.
"""

import base64
import time
import logging
from typing import Optional, Dict, Any
from io import BytesIO

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image

from src.models.data_models import SlideImage, SlideAnalysis
from config.settings import settings


logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Handles slide analysis using Google's Gemini Pro Vision API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini analyzer with API authentication.
        
        Args:
            api_key: Google API key. If None, uses settings.GOOGLE_API_KEY
            
        Raises:
            ValueError: If no API key is provided or found in settings
        """
        self.api_key = api_key or settings.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Safety settings to allow business content analysis
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        
        # Generation configuration
        self.generation_config = {
            "temperature": settings.GEMINI_TEMPERATURE,
            "max_output_tokens": settings.GEMINI_MAX_TOKENS,
        }
        
        # Rate limiting state
        self._rate_limited_until = 0
        self._consecutive_rate_limits = 0
        self._last_successful_call = 0
    
    def analyze_slide(self, slide_image: SlideImage) -> SlideAnalysis:
        """Analyze a single slide image using Gemini multimodal model.
        
        Args:
            slide_image: SlideImage object containing the image data
            
        Returns:
            SlideAnalysis object with extracted information
            
        Raises:
            Exception: For API errors, network issues, or parsing failures
        """
        start_time = time.time()
        errors = []
        
        # Check if we're currently rate limited
        if self._is_rate_limited():
            logger.warning(f"Skipping API call for slide {slide_image.slide_number} due to rate limiting")
            errors.append("Skipped due to rate limiting")
            fallback_analysis = self._generate_fallback_analysis(slide_image)
            return SlideAnalysis(
                slide_number=slide_image.slide_number,
                heading=fallback_analysis.get("heading", f"Slide {slide_image.slide_number}"),
                image_descriptions=fallback_analysis.get("image_descriptions", []),
                chart_table_data=fallback_analysis.get("chart_table_data", []),
                interpretation=fallback_analysis.get("interpretation", "Analysis skipped due to rate limiting."),
                confidence_score=0.1,
                processing_time=time.time() - start_time,
                errors=errors
            )
        
        # Retry logic for API calls
        for attempt in range(settings.GEMINI_RETRY_ATTEMPTS):
            try:
                # Convert image data to PIL Image
                pil_image = self._bytes_to_pil_image(slide_image.image_data)
                
                # Create the structured prompt
                prompt = self._create_analysis_prompt()
                
                # Generate content using Gemini
                response = self.model.generate_content(
                    [prompt, pil_image],
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings
                )
                
                # Check if response was blocked or empty
                if not response.candidates:
                    raise Exception("No response candidates returned")
                
                candidate = response.candidates[0]
                if candidate.finish_reason.name in ['SAFETY', 'RECITATION']:
                    raise Exception(f"Response blocked due to {candidate.finish_reason.name}")
                
                if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                    raise Exception("Response contains no content parts")
                
                # Get the text content safely
                response_text = ""
                for part in candidate.content.parts:
                    if hasattr(part, 'text'):
                        response_text += part.text
                
                if not response_text.strip():
                    raise Exception("Response text is empty")
                
                # Parse the response
                analysis_data = self._parse_response(response_text)
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Mark successful API call
                self._last_successful_call = time.time()
                self._consecutive_rate_limits = 0  # Reset on success
                
                # Create SlideAnalysis object
                return SlideAnalysis(
                    slide_number=slide_image.slide_number,
                    heading=analysis_data.get("heading", ""),
                    image_descriptions=analysis_data.get("image_descriptions", []),
                    chart_table_data=analysis_data.get("chart_table_data", []),
                    interpretation=analysis_data.get("interpretation", ""),
                    confidence_score=analysis_data.get("confidence_score", 0.8),
                    processing_time=processing_time,
                    errors=errors
                )
                
            except Exception as e:
                error_msg, should_retry = self._handle_api_error(e)
                errors.append(f"Attempt {attempt + 1}: {error_msg}")
                
                logger.warning(f"Attempt {attempt + 1} failed for slide {slide_image.slide_number}: {error_msg}")
                
                # Handle rate limiting
                if "rate limit" in error_msg.lower():
                    self._handle_rate_limit(str(e))
                    break  # Don't retry rate limited requests
                
                # If shouldn't retry, break early
                if not should_retry:
                    logger.error(f"Non-retryable error for slide {slide_image.slide_number}: {error_msg}")
                    break
                
                # If this is not the last attempt, wait before retrying
                if attempt < settings.GEMINI_RETRY_ATTEMPTS - 1:
                    time.sleep(settings.GEMINI_RETRY_DELAY * (attempt + 1))  # Exponential backoff
        
        # All attempts failed - provide fallback analysis
        processing_time = time.time() - start_time
        logger.error(f"All attempts failed for slide {slide_image.slide_number}")
        
        # Generate fallback analysis based on image properties
        fallback_analysis = self._generate_fallback_analysis(slide_image)
        
        return SlideAnalysis(
            slide_number=slide_image.slide_number,
            heading=fallback_analysis.get("heading", f"Slide {slide_image.slide_number}"),
            image_descriptions=fallback_analysis.get("image_descriptions", []),
            chart_table_data=fallback_analysis.get("chart_table_data", []),
            interpretation=fallback_analysis.get("interpretation", "Analysis unavailable due to API limitations."),
            confidence_score=0.1,  # Low confidence for fallback
            processing_time=processing_time,
            errors=errors
        )
    
    def _create_analysis_prompt(self) -> str:
        """Create a structured prompt for slide analysis.
        
        Returns:
            Formatted prompt string for Gemini API
        """
        return """
Analyze this pitch deck slide and provide structured information in the following format:

HEADING: [Extract the main title, heading, or key topic of this slide]

IMAGE_DESCRIPTIONS: [Describe any images, logos, charts, graphs, or visual elements you see. If there are multiple visual elements, list each one separately]

CHART_TABLE_DATA: [If there are any charts, graphs, tables, or data visualizations, extract and explain the key data points, trends, or insights in plain text format]

INTERPRETATION: [Explain what this slide is trying to convey, its purpose in the pitch deck, and why it's important for understanding the business or investment opportunity]

Please be thorough and specific in your analysis. If any section doesn't apply to this slide, write "None" for that section.
"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the Gemini API response into structured data.
        
        Args:
            response_text: Raw response text from Gemini API
            
        Returns:
            Dictionary with parsed analysis data
        """
        analysis_data = {
            "heading": "",
            "image_descriptions": [],
            "chart_table_data": [],
            "interpretation": "",
            "confidence_score": 0.8
        }
        
        try:
            current_section = None
            lines = response_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify section headers
                if line.startswith('HEADING:'):
                    analysis_data["heading"] = line.replace('HEADING:', '').strip()
                    current_section = None
                elif line.startswith('IMAGE_DESCRIPTIONS:'):
                    desc = line.replace('IMAGE_DESCRIPTIONS:', '').strip()
                    if desc and desc.lower() != 'none':
                        # Split by periods to handle multiple descriptions
                        descriptions = [d.strip() for d in desc.split('.') if d.strip()]
                        analysis_data["image_descriptions"].extend(descriptions)
                    current_section = "image_descriptions"
                elif line.startswith('CHART_TABLE_DATA:'):
                    data = line.replace('CHART_TABLE_DATA:', '').strip()
                    if data and data.lower() != 'none':
                        # Split by periods to handle multiple data points
                        data_points = [d.strip() for d in data.split('.') if d.strip()]
                        analysis_data["chart_table_data"].extend(data_points)
                    current_section = "chart_table_data"
                elif line.startswith('INTERPRETATION:'):
                    analysis_data["interpretation"] = line.replace('INTERPRETATION:', '').strip()
                    current_section = "interpretation"
                elif current_section and line and not line.startswith(('HEADING:', 'IMAGE_DESCRIPTIONS:', 'CHART_TABLE_DATA:', 'INTERPRETATION:')):
                    # Continue previous section
                    if current_section == "image_descriptions":
                        if line.lower() != 'none':
                            descriptions = [d.strip() for d in line.split('.') if d.strip()]
                            analysis_data["image_descriptions"].extend(descriptions)
                    elif current_section == "chart_table_data":
                        if line.lower() != 'none':
                            data_points = [d.strip() for d in line.split('.') if d.strip()]
                            analysis_data["chart_table_data"].extend(data_points)
                    elif current_section == "interpretation":
                        analysis_data["interpretation"] += " " + line
            
            # Clean up interpretation
            analysis_data["interpretation"] = analysis_data["interpretation"].strip()
            
            # If no structured content was found, use entire response as interpretation
            if (not analysis_data["heading"] and 
                not analysis_data["image_descriptions"] and 
                not analysis_data["chart_table_data"] and 
                not analysis_data["interpretation"]):
                analysis_data["interpretation"] = response_text.strip()
            
        except Exception as e:
            logger.warning(f"Failed to parse response structure: {e}")
            # Fallback: use entire response as interpretation
            analysis_data["interpretation"] = response_text.strip()
        
        return analysis_data
    
    def _bytes_to_pil_image(self, image_data: bytes) -> Image.Image:
        """Convert bytes data to PIL Image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            PIL Image object
            
        Raises:
            Exception: If image conversion fails
        """
        try:
            return Image.open(BytesIO(image_data))
        except Exception as e:
            raise Exception(f"Failed to convert image data: {str(e)}")
    
    def _handle_api_error(self, error: Exception) -> tuple[str, bool]:
        """Handle and categorize API errors.
        
        Args:
            error: Exception from API call
            
        Returns:
            Tuple of (error_message, should_retry)
        """
        error_str = str(error).lower()
        
        if "quota" in error_str or "rate limit" in error_str:
            # Extract retry delay if available
            retry_delay = self._extract_retry_delay(str(error))
            return f"API rate limit exceeded. Retry after {retry_delay} seconds.", False
        elif "authentication" in error_str or "api key" in error_str:
            return "API authentication failed. Please check your API key.", False
        elif "network" in error_str or "connection" in error_str:
            return "Network error. Please check your internet connection.", True
        elif "safety" in error_str or "blocked" in error_str:
            return "Content was blocked by safety filters.", False
        elif "recitation" in error_str:
            return "Response blocked due to potential recitation of copyrighted content.", False
        elif "finish_reason" in error_str:
            return "Response was blocked or incomplete. Try adjusting the prompt or safety settings.", False
        elif "no content parts" in error_str:
            return "API returned empty response. The model may have blocked the content.", False
        else:
            return f"API error: {str(error)}", True
    
    def _extract_retry_delay(self, error_str: str) -> int:
        """Extract retry delay from error message.
        
        Args:
            error_str: Error message string
            
        Returns:
            Retry delay in seconds, defaults to 60
        """
        import re
        match = re.search(r'retry_delay.*?seconds: (\d+)', error_str)
        if match:
            return int(match.group(1))
        return 60  # Default to 60 seconds
    
    def _generate_fallback_analysis(self, slide_image: SlideImage) -> Dict[str, Any]:
        """Generate a basic fallback analysis when API is unavailable.
        
        Args:
            slide_image: SlideImage object
            
        Returns:
            Dictionary with basic analysis data
        """
        try:
            # Get basic image properties
            pil_image = self._bytes_to_pil_image(slide_image.image_data)
            width, height = pil_image.size
            
            # Basic analysis based on image properties
            analysis = {
                "heading": f"Slide {slide_image.slide_number}",
                "image_descriptions": [
                    f"Image with dimensions {width}x{height} pixels",
                    f"Format: {slide_image.image_format}"
                ],
                "chart_table_data": [],
                "interpretation": (
                    f"This is slide {slide_image.slide_number} from the presentation. "
                    f"Detailed analysis is currently unavailable due to API rate limits. "
                    f"The slide contains visual content that would benefit from manual review."
                )
            }
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Failed to generate fallback analysis: {e}")
            return {
                "heading": f"Slide {slide_image.slide_number}",
                "image_descriptions": ["Image analysis unavailable"],
                "chart_table_data": [],
                "interpretation": "Analysis unavailable due to technical limitations."
            }
    
    def _is_rate_limited(self) -> bool:
        """Check if we're currently in a rate-limited state.
        
        Returns:
            True if rate limited, False otherwise
        """
        return time.time() < self._rate_limited_until
    
    def _handle_rate_limit(self, error_str: str):
        """Handle rate limiting by setting a cooldown period.
        
        Args:
            error_str: Error message from API
        """
        retry_delay = self._extract_retry_delay(error_str)
        self._rate_limited_until = time.time() + retry_delay
        self._consecutive_rate_limits += 1
        
        logger.warning(f"Rate limited for {retry_delay} seconds. Consecutive limits: {self._consecutive_rate_limits}")
    
    def test_connection(self) -> bool:
        """Test the API connection and authentication.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # If we're currently rate limited, don't test
            if self._is_rate_limited():
                logger.warning("Skipping connection test due to rate limiting")
                return False
            
            # If we had a recent successful call, assume connection is good
            if (self._last_successful_call > 0 and 
                time.time() - self._last_successful_call < 600):  # 10 minutes cache
                logger.debug("Using cached connection status")
                return True
            
            # Simple API key validation without making actual API calls
            # This avoids consuming quota during startup
            if not self.api_key or len(self.api_key) < 20:
                logger.error("Invalid API key format")
                return False
            
            # Just validate the API key format and configuration
            try:
                genai.configure(api_key=self.api_key)
                # Mark as successful without making actual API call
                self._last_successful_call = time.time()
                logger.debug("API key configuration successful")
                return True
            except Exception as config_error:
                logger.error(f"API configuration failed: {config_error}")
                return False
            
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "quota" in error_str:
                self._handle_rate_limit(str(e))
            logger.error(f"API connection test failed: {e}")
            return False