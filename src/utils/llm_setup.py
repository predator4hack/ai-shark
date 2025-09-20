"""
LLM Setup and Configuration for Multi-Agent Startup Analysis System
Task 4: Google AI LLM Integration and Base Agent

This module handles LLM initialization, rate limiting, and error handling.
"""

import logging
import time
from typing import Optional, Dict, Any, List
import asyncio
from functools import wraps

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.language_models import BaseLanguageModel
# from langchain_google_genai.chat_models import HarmCategory, HarmBlockThreshold
import google.generativeai as genai

from config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Custom exception for rate limiting issues"""
    pass


class LLMConnectionError(Exception):
    """Custom exception for LLM connection issues"""
    pass


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed LLM calls"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            raise last_exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class LLMSetup:
    """
    Handles LLM initialization and configuration for multiple providers (Google AI, Groq)
    """

    def __init__(self):
        self.llm: Optional[BaseLanguageModel] = None
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        self.provider = settings.LLM_PROVIDER.lower()
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the configured LLM provider"""
        if self.provider == "google":
            self._initialize_genai()
        elif self.provider == "groq":
            self._initialize_groq()
        else:
            raise LLMConnectionError(f"Unsupported LLM provider: {self.provider}")

    def _initialize_genai(self):
        """Initialize Google Generative AI client"""
        if not settings.GOOGLE_API_KEY:
            raise LLMConnectionError("Google API key not found in environment variables")

        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            logger.info("Google Generative AI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google AI client: {e}")
            raise LLMConnectionError(f"Failed to initialize Google AI: {e}")

    def _initialize_groq(self):
        """Initialize Groq API client"""
        if not settings.GROQ_API_KEY:
            raise LLMConnectionError("Groq API key not found in environment variables")

        try:
            # Groq doesn't require explicit initialization like Google AI
            logger.info("Groq API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise LLMConnectionError(f"Failed to initialize Groq: {e}")

    def create_llm(self,
                   model_name: str = None,
                   temperature: float = None,
                   max_tokens: int = None,
                   provider: str = None,
                   **kwargs) -> BaseLanguageModel:
        """
        Create and configure LLM instance for the specified provider

        Args:
            model_name: Model name (defaults based on provider)
            temperature: Sampling temperature (defaults based on provider)
            max_tokens: Maximum tokens (defaults based on provider)
            provider: LLM provider ("google" or "groq", defaults to configured provider)
            **kwargs: Additional parameters for the model

        Returns:
            Configured LLM instance
        """
        provider = provider or self.provider

        if provider == "google":
            return self._create_google_llm(model_name, temperature, max_tokens, **kwargs)
        elif provider == "groq":
            return self._create_groq_llm(model_name, temperature, max_tokens, **kwargs)
        else:
            raise LLMConnectionError(f"Unsupported provider: {provider}")

    def _create_google_llm(self,
                          model_name: str = None,
                          temperature: float = None,
                          max_tokens: int = None,
                          **kwargs) -> ChatGoogleGenerativeAI:
        """Create Google AI LLM instance"""
        model_name = model_name or settings.GEMINI_MODEL
        temperature = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
        max_tokens = max_tokens or settings.GEMINI_MAX_TOKENS

        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                convert_system_message_to_human=True,
                **kwargs
            )
            logger.info(f"Created Google AI LLM instance with model: {model_name}")
            return llm
        except Exception as e:
            logger.error(f"Failed to create Google AI LLM instance: {e}")
            raise LLMConnectionError(f"Failed to create Google AI LLM: {e}")

    def _create_groq_llm(self,
                        model_name: str = None,
                        temperature: float = None,
                        max_tokens: int = None,
                        **kwargs) -> ChatGroq:
        """Create Groq LLM instance"""
        model_name = model_name or settings.GROQ_MODEL
        temperature = temperature if temperature is not None else settings.GROQ_TEMPERATURE
        max_tokens = max_tokens or settings.GROQ_MAX_TOKENS

        try:
            llm = ChatGroq(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                groq_api_key=settings.GROQ_API_KEY,
                **kwargs
            )
            logger.info(f"Created Groq LLM instance with model: {model_name}")
            return llm
        except Exception as e:
            logger.error(f"Failed to create Groq LLM instance: {e}")
            raise LLMConnectionError(f"Failed to create Groq LLM: {e}")

    def get_default_llm(self) -> BaseLanguageModel:
        """Get or create default LLM instance"""
        if self.llm is None:
            self.llm = self.create_llm()
        return self.llm

    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    @retry_on_failure(max_retries=3, delay=1.0)
    def invoke_with_retry(self, llm: BaseLanguageModel, prompt: str, **kwargs) -> str:
        """
        Invoke LLM with retry logic and rate limiting

        Args:
            llm: Language model instance
            prompt: Input prompt
            **kwargs: Additional parameters for the model

        Returns:
            Model response as string
        """
        self._enforce_rate_limit()

        try:
            response = llm.invoke(prompt, **kwargs)
            logger.debug(f"LLM invocation successful. Response length: {len(response.content)}")
            return response.content
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            raise

    async def ainvoke_with_retry(self, llm: BaseLanguageModel, prompt: str, **kwargs) -> str:
        """
        Async invoke LLM with retry logic and rate limiting

        Args:
            llm: Language model instance
            prompt: Input prompt
            **kwargs: Additional parameters for the model

        Returns:
            Model response as string
        """
        # Async rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()

        try:
            response = await llm.ainvoke(prompt, **kwargs)
            logger.debug(f"Async LLM invocation successful. Response length: {len(response.content)}")
            return response.content
        except Exception as e:
            logger.error(f"Async LLM invocation failed: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test LLM connection with a simple prompt

        Returns:
            True if connection successful, False otherwise
        """
        try:
            llm = self.get_default_llm()
            test_prompt = "Hello, respond with 'OK' if you can receive this message."
            response = self.invoke_with_retry(llm, test_prompt)

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
        if self.provider == "google":
            return {
                "provider": "google",
                "model_name": settings.GEMINI_MODEL,
                "temperature": settings.GEMINI_TEMPERATURE,
                "max_tokens": settings.GEMINI_MAX_TOKENS,
                "retry_attempts": settings.GEMINI_RETRY_ATTEMPTS,
                "retry_delay": settings.GEMINI_RETRY_DELAY,
                "rate_limit_interval": self.min_request_interval
            }
        elif self.provider == "groq":
            return {
                "provider": "groq",
                "model_name": settings.GROQ_MODEL,
                "temperature": settings.GROQ_TEMPERATURE,
                "max_tokens": settings.GROQ_MAX_TOKENS,
                "retry_attempts": settings.GROQ_RETRY_ATTEMPTS,
                "retry_delay": settings.GROQ_RETRY_DELAY,
                "rate_limit_interval": self.min_request_interval
            }
        else:
            return {"provider": "unknown"}


# Global LLM setup instance
llm_setup = LLMSetup()


def get_llm() -> BaseLanguageModel:
    """Convenience function to get default LLM instance"""
    return llm_setup.get_default_llm()


def create_custom_llm(**kwargs) -> BaseLanguageModel:
    """Convenience function to create custom LLM instance"""
    return llm_setup.create_llm(**kwargs)


def create_groq_llm(**kwargs) -> BaseLanguageModel:
    """Convenience function to create Groq LLM instance"""
    return llm_setup.create_llm(provider="groq", **kwargs)


def create_google_llm(**kwargs) -> BaseLanguageModel:
    """Convenience function to create Google AI LLM instance"""
    return llm_setup.create_llm(provider="google", **kwargs)


# Testing utilities
class MockLLM:
    """Mock LLM for testing purposes"""

    def __init__(self, responses: List[str] = None):
        self.responses = responses or ["Mock response"]
        self.call_count = 0

    def invoke(self, prompt: str, **kwargs) -> object:
        """Mock invoke method"""
        response_text = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1

        # Create a mock response object
        class MockResponse:
            def __init__(self, content):
                self.content = content

        return MockResponse(response_text)

    async def ainvoke(self, prompt: str, **kwargs) -> object:
        """Mock async invoke method"""
        return self.invoke(prompt, **kwargs)


def create_mock_llm(responses: List[str] = None) -> MockLLM:
    """Create mock LLM for testing"""
    return MockLLM(responses)


if __name__ == "__main__":
    # Basic connection test
    try:
        setup = LLMSetup()
        if setup.test_connection():
            print("✓ LLM setup and connection successful")
            print(f"Model info: {setup.get_model_info()}")
        else:
            print("✗ LLM connection test failed")
    except Exception as e:
        print(f"✗ LLM setup failed: {e}")