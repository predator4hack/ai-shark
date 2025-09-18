"""
Unified LLM Manager for AI Shark
Handles both direct Gemini API calls and LangChain integration
"""

import os
import io
import json
import time
import functools
import logging
from typing import List, Dict, Any, Optional, Union
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv

# LangChain imports (for multi-agent system compatibility)
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.language_models import BaseLanguageModel
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseLanguageModel = None

from src.utils.prompt_manager import PromptManager

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMConnectionError(Exception):
    """Custom exception for LLM connection issues"""
    pass

class LLMManager:
    """
    Unified LLM Manager that supports both direct Gemini API and LangChain integration
    """
    
    def __init__(self):
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.gemini_embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
        self.prompt_manager = PromptManager()
        self._configure_gemini()
        
        # For LangChain compatibility
        self.llm_instance: Optional[BaseLanguageModel] = None
        self.last_request_time = 0
        self.min_request_interval = 1.0
    
    def _configure_gemini(self):
        """Configure the Gemini API with the key from environment variables"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please set it in a .env file.")
        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")
    
    @staticmethod
    def retry_with_backoff(retries=5, backoff_in_seconds=5):
        """Decorator for retrying a function with exponential backoff"""
        def rwb(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                x = 0
                while True:
                    try:
                        return f(*args, **kwargs)
                    except Exception as e:
                        if x == retries:
                            raise e
                        else:
                            sleep = backoff_in_seconds * 2 ** x
                            logger.warning(f"Error in {f.__name__}: {e}. Retrying in {sleep} seconds.")
                            time.sleep(sleep)
                            x += 1
            return wrapper
        return rwb
    
    # Direct Gemini API Methods (for document processing)
    
    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Convert each page of a PDF into a list of PIL Images"""
        try:
            doc = fitz.open(pdf_path)
            images = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=150)
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                images.append(image)
            doc.close()
            logger.info(f"Successfully converted PDF to {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []
    
    @retry_with_backoff()
    def extract_metadata(self, page_images: List[Image.Image]) -> Optional[Dict[str, Any]]:
        """Extract startup metadata including name, sector, sub-sector, website, and table of contents"""
        try:
            logger.info("Extracting metadata from pitch deck...")
            model = genai.GenerativeModel(self.gemini_model)
            
            # Get the metadata extraction prompt
            prompt = self.prompt_manager.format_prompt("metadata_extraction")
            
            # Prepare content list [prompt, image1, image2, ...]
            content = [prompt] + page_images
            
            response = model.generate_content(content)
            
            # Clean up the response to extract only the JSON part
            cleaned_response = response.text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                # Handle case where it's just ```
                parts = cleaned_response.split("```")
                if len(parts) >= 3:
                    cleaned_response = parts[1].strip()
            
            metadata = json.loads(cleaned_response)
            logger.info("Successfully extracted metadata")
            logger.debug(f"Metadata: {json.dumps(metadata, indent=2)}")
            
            return metadata
            
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error extracting metadata: {e}")
            if 'response' in locals():
                logger.debug(f"Model response was: {response.text}")
            return None
    
    @retry_with_backoff()
    def extract_topic_data(self, topic: str, page_images: List[Image.Image]) -> str:
        """Extract detailed information for a specific topic from its relevant pages"""
        try:
            model = genai.GenerativeModel(self.gemini_model)
            
            # Get the topic analysis prompt
            prompt = self.prompt_manager.format_prompt(
                "topic_analysis",
                topic=topic,
                version="v2"
            )
            
            content = [prompt] + page_images
            response = model.generate_content(content)
            return response.text
            
        except Exception as e:
            logger.error(f"Error extracting topic data for '{topic}': {e}")
            return f"Error extracting data for topic '{topic}': {e}"
    
    @retry_with_backoff()
    def structure_document_content(self, text: str, filename: str) -> str:
        """Use LLM to structure and clean up document content"""
        try:
            model = genai.GenerativeModel(self.gemini_model)
            
            # Get the document structuring prompt
            prompt = self.prompt_manager.format_prompt(
                "document_structuring",
                filename=filename,
                content=text[:8000]  # Limit to avoid token limits
            )
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error structuring document content: {e}")
            return text  # Return original text if LLM processing fails
    
    @retry_with_backoff()
    def generate_embeddings(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """Generate embeddings for the given text"""
        try:
            embedding = genai.embed_content(
                model=self.gemini_embedding_model, 
                content=text, 
                task_type=task_type
            )
            return embedding['embedding']
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    # LangChain Integration Methods (for multi-agent system)
    
    def create_langchain_llm(self,
                           model_name: str = None,
                           temperature: float = 0.7,
                           max_tokens: int = 4000,
                           **kwargs) -> Optional[BaseLanguageModel]:
        """
        Create LangChain LLM instance for multi-agent system
        
        Args:
            model_name: Model name (defaults to configured model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            LangChain LLM instance or None if LangChain not available
        """
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available. Cannot create LangChain LLM instance.")
            return None
        
        model_name = model_name or self.gemini_model
        
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                convert_system_message_to_human=True,
                **kwargs
            )
            logger.info(f"Created LangChain LLM instance with model: {model_name}")
            return llm
        except Exception as e:
            logger.error(f"Failed to create LangChain LLM instance: {e}")
            raise LLMConnectionError(f"Failed to create LangChain LLM: {e}")
    
    def get_default_langchain_llm(self) -> Optional[BaseLanguageModel]:
        """Get or create default LangChain LLM instance"""
        if self.llm_instance is None and LANGCHAIN_AVAILABLE:
            self.llm_instance = self.create_langchain_llm()
        return self.llm_instance
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()
    
    def invoke_with_retry(self, prompt: str, use_langchain: bool = False, **kwargs) -> str:
        """
        Invoke LLM with retry logic and rate limiting
        
        Args:
            prompt: Input prompt
            use_langchain: Whether to use LangChain or direct API
            **kwargs: Additional parameters
            
        Returns:
            Model response as string
        """
        self._enforce_rate_limit()
        
        if use_langchain and LANGCHAIN_AVAILABLE:
            llm = self.get_default_langchain_llm()
            if llm:
                try:
                    response = llm.invoke(prompt, **kwargs)
                    return response.content
                except Exception as e:
                    logger.error(f"LangChain LLM invocation failed: {e}")
                    raise
        
        # Fallback to direct API
        try:
            model = genai.GenerativeModel(self.gemini_model)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Direct Gemini API invocation failed: {e}")
            raise
    
    # Utility Methods
    
    def json_to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert a dictionary to a Markdown string"""
        markdown_string = ""
        for key, value in data.items():
            # Skip certain metadata fields in the main content
            if key in ['startup_name', 'sector', 'sub_sector', 'website']:
                continue
            
            markdown_string += f"## {key.replace('_', ' ').title()}\n\n"
            
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    markdown_string += f"### {subkey.replace('_', ' ').title()}\n\n"
                    markdown_string += f"{subvalue}\n\n"
            else:
                markdown_string += f"{value}\n\n"
        
        return markdown_string
    
    def test_connection(self) -> bool:
        """Test LLM connection with a simple prompt"""
        try:
            test_prompt = "Hello, respond with 'OK' if you can receive this message."
            response = self.invoke_with_retry(test_prompt)
            
            if "OK" in response.upper():
                logger.info("LLM connection test passed")
                return True
            else:
                logger.warning(f"LLM connection test unclear response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current LLM configuration"""
        return {
            "gemini_model": self.gemini_model,
            "embedding_model": self.gemini_embedding_model,
            "langchain_available": LANGCHAIN_AVAILABLE,
            "rate_limit_interval": self.min_request_interval,
            "api_configured": bool(os.getenv("GOOGLE_API_KEY"))
        }

# Global instance for backward compatibility
llm_manager = LLMManager()

# Convenience functions for document processing (direct API)
def extract_metadata(page_images: List[Image.Image]) -> Optional[Dict[str, Any]]:
    """Extract metadata from pitch deck images"""
    return llm_manager.extract_metadata(page_images)

def extract_topic_data(topic: str, page_images: List[Image.Image]) -> str:
    """Extract topic data from images"""
    return llm_manager.extract_topic_data(topic, page_images)

def structure_document_content(text: str, filename: str) -> str:
    """Structure document content using LLM"""
    return llm_manager.structure_document_content(text, filename)

def pdf_to_images(pdf_path: str) -> List[Image.Image]:
    """Convert PDF to images"""
    return llm_manager.pdf_to_images(pdf_path)

# Convenience functions for multi-agent system (LangChain)
def get_langchain_llm(**kwargs) -> Optional[BaseLanguageModel]:
    """Get LangChain LLM instance"""
    return llm_manager.create_langchain_llm(**kwargs)

def get_default_llm() -> Optional[BaseLanguageModel]:
    """Get default LangChain LLM instance"""
    return llm_manager.get_default_langchain_llm()