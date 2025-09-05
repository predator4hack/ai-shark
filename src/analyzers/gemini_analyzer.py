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
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Generation configuration
        self.generation_config = {
            "temperature": settings.GEMINI_TEMPERATURE,
            "max_output_tokens": settings.GEMINI_MAX_TOKENS,
        }
    
    def analyze_slide(self, slide_image: SlideImage) -> SlideAnalysis:
        """Analyze a single slide image using Gemini Pro Vision.
        
        Args:
            slide_image: SlideImage object containing the image data
            
        Returns:
            SlideAnalysis object with extracted information
            
        Raises:
            Exception: For API errors, network issues, or parsing failures
        """
        start_time = time.time()
        errors = []
        
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
            
            # Parse the response
            analysis_data = self._parse_response(response.text)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
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
            processing_time = time.time() - start_time
            error_msg = self._handle_api_error(e)
            errors.append(error_msg)
            
            logger.error(f"Failed to analyze slide {slide_image.slide_number}: {error_msg}")
            
            # Return partial analysis with error information
            return SlideAnalysis(
                slide_number=slide_image.slide_number,
                heading="",
                image_descriptions=[],
                chart_table_data=[],
                interpretation="",
                confidence_score=0.0,
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
    
    def _handle_api_error(self, error: Exception) -> str:
        """Handle and categorize API errors.
        
        Args:
            error: Exception from API call
            
        Returns:
            User-friendly error message
        """
        error_str = str(error).lower()
        
        if "quota" in error_str or "rate limit" in error_str:
            return "API rate limit exceeded. Please wait before retrying."
        elif "authentication" in error_str or "api key" in error_str:
            return "API authentication failed. Please check your API key."
        elif "network" in error_str or "connection" in error_str:
            return "Network error. Please check your internet connection."
        elif "safety" in error_str or "blocked" in error_str:
            return "Content was blocked by safety filters."
        else:
            return f"API error: {str(error)}"
    
    def test_connection(self) -> bool:
        """Test the API connection and authentication.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Create a simple test image (1x1 white pixel)
            test_image = Image.new('RGB', (1, 1), color='white')
            
            response = self.model.generate_content(
                ["What do you see in this image?", test_image],
                generation_config={"temperature": 0.1, "max_output_tokens": 50}
            )
            
            return bool(response.text)
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False