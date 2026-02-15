"""
Unified LLM Manager for AI Shark
Handles both direct Gemini API calls and LangChain integration
Supports multi-LLM routing: Gemini for vision, Groq Llama 4 for text
"""

import os
import io
import json
import time
import base64
import functools
import logging
from typing import List, Dict, Any, Optional, Union
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv
import httpx

from config.secrets import get_google_api_key, get_groq_api_key
from config.settings import settings

# LangChain imports (for multi-agent system compatibility)
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    from langchain_core.language_models import BaseLanguageModel
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseLanguageModel = None

from src.utils.prompt_manager import PromptManager

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class LLMConnectionError(Exception):
    """Custom exception for LLM connection issues"""
    pass

class LLMManager:
    """
    Unified LLM Manager that supports both direct Gemini API and LangChain integration.
    Supports multi-LLM routing:
    - Vision tasks: Configurable between Gemini and Groq Llama 4 Maverick
    - Text tasks: Groq Llama 4 Scout (cost-efficient)
    - Fallback: Groq Llama 4 Maverick
    """

    def __init__(self):
        # Vision provider configuration (for A/B testing)
        self.vision_provider = settings.VISION_PROVIDER.lower()
        self.vision_model_google = settings.VISION_MODEL_GOOGLE
        self.vision_model_groq = settings.VISION_MODEL_GROQ

        # Text model configuration
        self.text_model = settings.TEXT_MODEL
        self.fallback_model = settings.FALLBACK_MODEL
        self.enable_fallback = settings.ENABLE_LLM_FALLBACK

        # Legacy Gemini config
        self.gemini_model = settings.GEMINI_MODEL
        self.gemini_embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
        self.prompt_manager = PromptManager()

        # Mock mode detection with explicit logging
        env_value = os.getenv("USE_MOCK_LLM", "false")
        self.use_mock = env_value.lower() == "true"

        logger.info(f"🔧 LLMManager initialization:")
        logger.info(f"   USE_MOCK_LLM={env_value}, use_mock={self.use_mock}")
        logger.info(f"   Vision provider: {self.vision_provider}")
        logger.info(f"   Text model: {self.text_model}")
        logger.info(f"   Fallback enabled: {self.enable_fallback}")

        # For LangChain compatibility
        self.llm_instance: Optional[BaseLanguageModel] = None
        self.last_request_time = 0
        self.min_request_interval = 1.0

        # Groq API client for vision and text tasks
        self.groq_api_key = get_groq_api_key()
        self.groq_base_url = "https://api.groq.com/openai/v1"

        if not self.use_mock:
            # Configure APIs based on providers
            if self.vision_provider == "google":
                logger.info("⚠️  Real LLM mode - configuring Gemini API for vision")
                self._configure_gemini()

            # Always configure Groq for text tasks
            self._configure_groq()
        else:
            logger.info("✅ Mock LLM mode enabled - skipping API configuration")
    
    def _configure_gemini(self):
        """Configure the Gemini API with the key from environment variables or mounted secret"""
        api_key = get_google_api_key()
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please set it in a .env file or mount as secret.")

        # Validate API key format
        if not api_key.startswith("AIza"):
            logger.warning(f"⚠️ Google API key format looks unusual. First 4 chars: {api_key[:4]}")

        genai.configure(api_key=api_key)
        logger.info(f"✅ Gemini API configured successfully (key: ...{api_key[-4:]})")

    def _configure_groq(self):
        """Configure Groq API for text tasks and optionally vision"""
        if not self.groq_api_key:
            logger.warning("⚠️ GROQ_API_KEY not found. Text tasks will fail without it.")
        else:
            # Validate API key format
            if not self.groq_api_key.startswith("gsk_"):
                logger.warning(f"⚠️ Groq API key format looks unusual. First 4 chars: {self.groq_api_key[:4]}")
            logger.info(f"✅ Groq API configured successfully (key: ...{self.groq_api_key[-4:]})")
    
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
    
    def pdf_to_images(self, pdf_path: str, max_dimension: int = 1024) -> List[Image.Image]:
        """
        Convert each page of a PDF into a list of PIL Images

        Args:
            pdf_path: Path to PDF file
            max_dimension: Maximum width or height for resized images (default: 1024)

        Returns:
            List of PIL Image objects
        """
        # Mock mode: skip PDF conversion
        if self.use_mock:
            logger.info("Mock mode: Skipping PDF to images conversion")
            return []

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            logger.info(f"Converting PDF with {total_pages} pages to images...")

            images = []
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                # Use lower DPI for faster processing and smaller payload
                pix = page.get_pixmap(dpi=120)
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))

                # Resize image if too large to reduce API payload size
                width, height = image.size
                if width > max_dimension or height > max_dimension:
                    ratio = max_dimension / max(width, height)
                    new_size = (int(width * ratio), int(height * ratio))
                    image = image.resize(new_size, Image.Resampling.LANCZOS)

                images.append(image)

                # Log progress for large documents
                if (page_num + 1) % 5 == 0 or (page_num + 1) == total_pages:
                    logger.info(f"Converted {page_num + 1}/{total_pages} pages")

            doc.close()
            logger.info(f"✅ Successfully converted PDF to {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"❌ Error converting PDF to images: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    @retry_with_backoff()
    def extract_metadata(self, page_images: List[Image.Image]) -> Optional[Dict[str, Any]]:
        """Extract startup metadata including name, sector, sub-sector, website, and table of contents"""
        # Mock mode: return fixed metadata without processing images
        if self.use_mock:
            from src.utils.mock_responses import MOCK_METADATA
            logger.info("Mock mode: Returning mock metadata")
            return MOCK_METADATA

        try:
            logger.info(f"Extracting metadata from pitch deck using {self.vision_provider} provider...")

            # Get the metadata extraction prompt
            prompt = self.prompt_manager.format_prompt("metadata_extraction")

            response_text = self._extract_vision_with_fallback(prompt, page_images)

            # Clean up the response to extract only the JSON part
            cleaned_response = response_text.strip()

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
            return None

    def _extract_vision_with_fallback(self, prompt: str, page_images: List[Image.Image]) -> str:
        """
        Extract content using vision LLM with automatic fallback.
        Falls back to Groq Llama 4 Maverick if primary provider fails.
        """
        try:
            if self.vision_provider == "google":
                return self._extract_with_gemini_vision(prompt, page_images)
            else:  # groq
                return self._extract_with_groq_vision(prompt, page_images)
        except Exception as e:
            if self.enable_fallback:
                logger.warning(f"Primary vision LLM ({self.vision_provider}) failed: {e}. Falling back to Groq Llama 4 Maverick...")
                return self._extract_with_groq_vision(prompt, page_images)
            raise

    def _extract_with_gemini_vision(self, prompt: str, page_images: List[Image.Image]) -> str:
        """Extract content using Gemini vision API"""
        try:
            logger.info(f"Calling Gemini vision API with {len(page_images)} images...")
            model = genai.GenerativeModel(self.vision_model_google)
            content = [prompt] + page_images
            response = model.generate_content(content)
            logger.info(f"✅ Gemini vision response received")
            return response.text
        except Exception as e:
            logger.error(f"❌ Gemini vision API error: {e}")
            raise

    def _extract_with_groq_vision(self, prompt: str, page_images: List[Image.Image]) -> str:
        """Extract content using Groq vision API (Llama 4 Maverick)"""
        try:
            logger.info(f"Calling Groq vision API with {len(page_images)} images...")
            # Convert PIL images to base64
            image_contents = []
            for i, img in enumerate(page_images):
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                image_contents.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_base64}"
                    }
                })
                if (i + 1) % 5 == 0:
                    logger.info(f"Encoded {i + 1}/{len(page_images)} images")

            # Build message with text and images
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *image_contents
                    ]
                }
            ]

            logger.info(f"Sending request to Groq API...")
            # Call Groq API with increased timeout for large documents
            with httpx.Client(timeout=240.0) as client:
                response = client.post(
                    f"{self.groq_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.vision_model_groq,
                        "messages": messages,
                        "max_tokens": 8000,
                        "temperature": 0.1
                    }
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"✅ Groq vision response received")
                return result["choices"][0]["message"]["content"]
        except httpx.TimeoutException as e:
            logger.error(f"❌ Groq vision API timeout: {e}")
            raise Exception(f"Vision API request timed out after 240s. Document may be too large.")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Groq vision API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Vision API returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ Groq vision API error: {e}")
            raise
    
    @retry_with_backoff()
    def extract_topic_data(self, topic: str, page_images: List[Image.Image]) -> str:
        """Extract detailed information for a specific topic from its relevant pages"""
        # Mock mode: return fixed content without processing
        if self.use_mock:
            from src.utils.mock_responses import MOCK_TOPIC_CONTENT
            logger.info(f"Mock mode: Returning mock content for topic '{topic}'")
            return MOCK_TOPIC_CONTENT.get(topic, f"# {topic}\n\nMock content for {topic}")

        try:
            logger.info(f"Extracting topic '{topic}' using {self.vision_provider} provider...")

            # Get the topic analysis prompt
            prompt = self.prompt_manager.format_prompt(
                "topic_analysis",
                topic=topic,
                version="v2"
            )

            return self._extract_vision_with_fallback(prompt, page_images)

        except Exception as e:
            logger.error(f"Error extracting topic data for '{topic}': {e}")
            return f"Error extracting data for topic '{topic}': {e}"
    
    @retry_with_backoff()
    def structure_document_content(self, text: str, filename: str) -> str:
        """Use LLM to structure and clean up document content.
        Uses text LLM (Llama 4 Scout) with fallback to Maverick.
        """
        try:
            # Get the document structuring prompt
            prompt = self.prompt_manager.format_prompt(
                "document_structuring",
                filename=filename,
                content=text[:8000]  # Limit to avoid token limits
            )

            return self._invoke_text_llm(prompt)

        except Exception as e:
            logger.error(f"Error structuring document content: {e}")
            return text  # Return original text if LLM processing fails

    def _invoke_text_llm(self, prompt: str, use_fallback: bool = True) -> str:
        """Invoke text LLM (Llama 4 Scout) with optional fallback to Maverick"""
        self._enforce_rate_limit()

        try:
            # Use Groq API for text tasks
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.groq_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.text_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 8000,
                        "temperature": 0.1
                    }
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Text LLM ({self.text_model}) response received")
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            if use_fallback and self.enable_fallback:
                logger.warning(f"Primary text LLM failed: {e}. Falling back to {self.fallback_model}...")
                return self._invoke_fallback_llm(prompt)
            raise

    def _invoke_fallback_llm(self, prompt: str) -> str:
        """Invoke fallback LLM (Llama 4 Maverick)"""
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.groq_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.fallback_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 8000,
                    "temperature": 0.1
                }
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Fallback LLM ({self.fallback_model}) response received")
            return result["choices"][0]["message"]["content"]
    
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
            "vision_provider": self.vision_provider,
            "vision_model": self.vision_model_google if self.vision_provider == "google" else self.vision_model_groq,
            "text_model": self.text_model,
            "fallback_model": self.fallback_model,
            "fallback_enabled": self.enable_fallback,
            "embedding_model": self.gemini_embedding_model,
            "langchain_available": LANGCHAIN_AVAILABLE,
            "rate_limit_interval": self.min_request_interval,
            "google_api_configured": bool(get_google_api_key()),
            "groq_api_configured": bool(self.groq_api_key)
        }

    def _get_mock_founder_responses(self) -> str:
        """
        Return mock founder responses for testing without hitting API rate limits
        """
        return """**Sarah Chen (CEO)**

*Q1: What problem are you solving?*
We're solving the data analytics gap for SMBs. 70% of small businesses have valuable data but lack the tools or expertise to analyze it. Traditional BI tools like Tableau cost $70/user/month and require data scientists. We make analytics accessible through natural language - any employee can ask questions in plain English and get instant insights.

*Q2: Why is your team uniquely positioned to solve this?*
I spent 10 years at Google leading Product Management for Google Analytics, working directly with SMB customers. Our CTO Alex built AI infrastructure at OpenAI for 5 years. Our Head of Data came from Segment where she processed analytics for 10,000+ SMB customers. We've seen this problem from every angle - product, technology, and scale.

*Q3: What's your go-to-market strategy?*
We're going PLG (Product-Led Growth) with a freemium model. Free tier gets 100 queries/month, enough to show value. Premium is $49/user/month - 30% cheaper than Tableau. We target accounting firms, marketing agencies, and e-commerce stores first since they're data-rich but resource-constrained. Our first 500 users came through Product Hunt and G2 reviews with zero paid marketing.

**Alex Rodriguez (CTO)**

*Q1: What's your technical moat?*
We've built a proprietary SQL generation engine that converts natural language to database queries with 95% accuracy - better than competitors at 75-80%. We use fine-tuned LLMs on 2M+ real business queries we collected. Plus, our semantic caching layer reduces API costs by 60% while maintaining sub-second response times. This gives us 40% better margins than competitors.

*Q2: How do you handle data security and privacy?*
Security is foundational. We're SOC 2 Type II compliant, all data encrypted at rest (AES-256) and in transit (TLS 1.3). We never train our models on customer data - it's in our terms of service. For enterprises, we offer on-premise deployment. Our architecture keeps customer data in their own database - we only read, never write or store PII.

*Q3: What are your biggest technical challenges?*
Scale and accuracy. We need to handle 100+ data source integrations (SQL, Snowflake, BigQuery, MongoDB, etc.) with different query syntaxes. Each new connector takes 2-3 weeks. We're also constantly improving our NLP model - edge cases where users ask ambiguous questions. We've built a feedback loop where users can correct wrong queries, which trains our model in real-time.

**Jennifer Wu (Head of Data/Growth)**

*Q1: What does your customer acquisition look like?*
We're spending $50K/month across Google Ads and content marketing. CAC is $800 with an average LTV of $4,200 (7 year lifetime), giving us 5.25x LTV:CAC. 40% of signups convert to paid within 30 days. Our viral coefficient is 1.3 - each user invites 1.3 colleagues on average. Retention is strong: 92% monthly, 75% annually.

*Q2: Who are your competitors and how do you differentiate?*
Direct competitors are Mode Analytics, Thoughtspot, and Sisense. We're 50% cheaper and 10x easier to use. Tableau/Power BI are indirect competitors - powerful but need data science teams. Our biggest differentiator is speed to value: customers get insights in 5 minutes vs 5 weeks with traditional BI tools. We win on ease of use, not features.

*Q3: What metrics matter most right now?*
MRR growth (currently $120K, growing 40% month-over-month), Net Revenue Retention (115% - customers expand usage over time), and activation rate (% of signups that run 10+ queries in first week - currently 62%). We also track query accuracy since that drives retention. Bad answers = churn.

---

**Key Themes Across Responses:**
- Strong technical foundation with proprietary IP (SQL generation engine)
- Experienced team with direct domain expertise (Google, OpenAI, Segment)
- Clear product-market fit with paying customers and strong unit economics
- Focus on underserved SMB market with PLG motion
- Security and compliance built in from day one
- Data-driven approach to growth with healthy metrics"""

    @retry_with_backoff()
    def generate_founder_responses(self, prompt: str) -> str:
        """
        Generate founder responses for questionnaire simulation.
        Uses text LLM (Llama 4 Scout) with fallback to Maverick.

        Args:
            prompt: Formatted prompt for founder response simulation

        Returns:
            Generated response string
        """
        # Mock mode: return simulated founder responses
        if self.use_mock:
            logger.info("🔧 Mock mode: Returning simulated founder responses")
            return self._get_mock_founder_responses()

        try:
            logger.info(f"Generating founder responses using {self.text_model}...")
            response = self._invoke_text_llm(prompt)

            if not response:
                raise LLMConnectionError("Empty response from LLM")

            logger.info("Successfully generated founder responses")
            return response.strip()

        except Exception as e:
            logger.error(f"Error generating founder responses: {e}")
            raise LLMConnectionError(f"Failed to generate founder responses: {e}")

# Global instance for backward compatibility - using lazy initialization
_llm_manager_instance = None

def get_llm_manager() -> 'LLMManager':
    """
    Get or create LLMManager singleton instance.
    Uses lazy initialization to ensure environment variables are loaded.
    """
    global _llm_manager_instance
    if _llm_manager_instance is None:
        _llm_manager_instance = LLMManager()
    return _llm_manager_instance

# Convenience functions for document processing (direct API)
def extract_metadata(page_images: List[Image.Image]) -> Optional[Dict[str, Any]]:
    """Extract metadata from pitch deck images"""
    return get_llm_manager().extract_metadata(page_images)

def extract_topic_data(topic: str, page_images: List[Image.Image]) -> str:
    """Extract topic data from images"""
    return get_llm_manager().extract_topic_data(topic, page_images)

def structure_document_content(text: str, filename: str) -> str:
    """Structure document content using LLM"""
    return get_llm_manager().structure_document_content(text, filename)

def pdf_to_images(pdf_path: str) -> List[Image.Image]:
    """Convert PDF to images"""
    return get_llm_manager().pdf_to_images(pdf_path)

# Convenience functions for multi-agent system (LangChain)
def get_langchain_llm(**kwargs) -> Optional[BaseLanguageModel]:
    """Get LangChain LLM instance"""
    return get_llm_manager().create_langchain_llm(**kwargs)

def get_default_llm() -> Optional[BaseLanguageModel]:
    """Get default LangChain LLM instance"""
    return get_llm_manager().get_default_langchain_llm()