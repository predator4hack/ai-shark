"""
Products and Services Extractor

This module extracts information about a company's products and services
using Gemini with URL context tools to analyze the company website.
"""

import logging
from typing import Dict, Any

import google.generativeai as genai
from google.ai import generativelanguage as glm

from ..base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class ProductsServicesExtractor(BaseExtractor):
    """
    Extracts products and services information using Gemini with URL context
    
    This extractor analyzes the company website to understand their offerings,
    target market, pricing, and business model.
    """
    
    def __init__(self):
        """Initialize the extractor with Gemini model configuration"""
        self.model_name = "gemini-2.5-flash"
        
        # Verify Gemini is configured
        try:
            # Test that genai is properly configured
            from src.utils.llm_manager import llm_manager
            if not llm_manager.test_connection():
                logger.warning("Gemini API connection test failed")
        except Exception as e:
            logger.warning(f"Could not verify Gemini configuration: {e}")
    
    def get_extractor_name(self) -> str:
        """Return the unique name of this extractor"""
        return "products_services"
    
    def get_section_title(self) -> str:
        """Return the markdown section title for this extractor"""
        return "Products and Services Analysis"
    
    def should_extract(self, metadata: Dict[str, Any]) -> bool:
        """Only extract if website is available in metadata"""
        website = metadata.get('website', '').strip()
        return bool(website)
    
    def extract(self, company_name: str, website: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract products and services using Gemini with URL context tools
        
        Args:
            company_name: Name of the company
            website: Company website URL (already normalized)
            metadata: Company metadata from pitch deck processing
            
        Returns:
            Dictionary containing extraction results
        """
        if not website:
            return {
                'status': 'skipped',
                'reason': 'No website provided in metadata',
                'content': '*Website not available for analysis*'
            }
        
        try:
            logger.info(f"Analyzing website {website} for {company_name}")
            
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(company_name, website)
            
            # Use Gemini with URL context as specified in requirements
            contents = [
                glm.Content(
                    role="user",
                    parts=[
                        glm.Part(text=prompt),
                    ],
                ),
            ]
            
            tools = [
                glm.Tool(url_context=glm.UrlContext()),
            ]
            
            generate_content_config = glm.GenerateContentConfig(
                thinking_config=glm.ThinkingConfig(thinking_budget=-1),
                tools=tools,
            )
            
            # Generate the analysis
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                contents=contents,
                config=generate_content_config
            )
            
            # Extract the response text
            if response and response.text:
                content = response.text.strip()
                
                logger.info(f"Successfully analyzed {website} for {company_name}")
                
                return {
                    'status': 'success',
                    'content': content,
                    'website_analyzed': website,
                    'model_used': self.model_name
                }
            else:
                logger.warning(f"Empty response from Gemini for {website}")
                return {
                    'status': 'error',
                    'error': 'Empty response from Gemini API',
                    'content': f'*Unable to analyze website {website} - empty response from AI model*'
                }
            
        except Exception as e:
            logger.error(f"Error extracting products/services for {company_name} from {website}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'content': f'*Error analyzing website {website}: {str(e)}*',
                'website_analyzed': website
            }
    
    def _create_analysis_prompt(self, company_name: str, website: str) -> str:
        """
        Create the analysis prompt for Gemini
        
        Args:
            company_name: Name of the company
            website: Company website URL
            
        Returns:
            Formatted prompt string
        """
        return f"""
Analyze the website for {company_name} ({website}) and provide a comprehensive analysis of their products and services.

Please extract and organize the following information in clear markdown format:

### Core Products/Services
- What are the main products or services offered by {company_name}?
- Describe each product/service in detail

### Key Features & Capabilities
- What are the most important features or capabilities of their offerings?
- What technical capabilities do they highlight?

### Target Market & Customers
- Who is the primary target audience?
- What market segments do they serve?
- What types of customers do they focus on?

### Value Proposition
- What makes their offering unique or valuable?
- What problems do they solve for customers?
- What benefits do they emphasize?

### Pricing Information
- Any pricing details, plans, or pricing models mentioned
- Is it subscription-based, one-time purchase, freemium, etc.?

### Technology & Platform
- What technologies, platforms, or technical infrastructure do they mention?
- Any integrations or technical specifications highlighted?

### Business Model
- How do they appear to generate revenue?
- What is their go-to-market approach?

**Instructions:**
- Be specific and factual, only including information that can be found on their website
- Use clear, professional language suitable for business analysis
- Structure your response with proper markdown headers and bullet points
- If certain information is not available on the website, mention that explicitly
- Focus on concrete details rather than marketing language
- Aim for comprehensive coverage while being concise and organized

Please analyze the website thoroughly and provide detailed insights about {company_name}'s products and services.
"""