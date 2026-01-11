"""Configuration settings for the VC Document Analyzer."""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from config.secrets import get_google_api_key, get_groq_api_key

# Load environment variables
load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # API Configuration
    GOOGLE_API_KEY: str = get_google_api_key()
    GROQ_API_KEY: str = get_groq_api_key()
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "VC Document Analyzer")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    SUPPORTED_FORMATS: List[str] = os.getenv("SUPPORTED_FORMATS", "pdf,pptx,png,jpg,jpeg").split(",")
    
    # Directory Configuration
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "outputs"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = Path(os.getenv("LOG_FILE", "logs/app.log"))
    
    # LLM Provider Configuration (Legacy - kept for backward compatibility)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "google")  # "google" or "groq"

    # Vision LLM Configuration (Phase 1 - Pitch Deck Processing)
    # Configurable for A/B testing between Gemini and Groq Llama 4
    VISION_PROVIDER: str = os.getenv("VISION_PROVIDER", "google")  # "google" or "groq"
    VISION_MODEL_GOOGLE: str = os.getenv("VISION_MODEL_GOOGLE", "gemini-2.5-flash")
    VISION_MODEL_GROQ: str = os.getenv("VISION_MODEL_GROQ", "meta-llama/llama-4-maverick-17b-128e-instruct")

    # Text LLM Configuration (Phases 2-5 - Analysis, Q&A, Memo)
    # Uses Llama 4 Scout for cost efficiency
    TEXT_MODEL: str = os.getenv("TEXT_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

    # Fallback Configuration
    # Uses Llama 4 Maverick as fallback (multimodal, affordable)
    ENABLE_LLM_FALLBACK: bool = os.getenv("ENABLE_LLM_FALLBACK", "true").lower() == "true"
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct")

    # Gemini API Configuration (for vision when VISION_PROVIDER=google)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "100000"))
    GEMINI_RETRY_ATTEMPTS: int = int(os.getenv("GEMINI_RETRY_ATTEMPTS", "3"))
    GEMINI_RETRY_DELAY: float = float(os.getenv("GEMINI_RETRY_DELAY", "1.0"))

    # Groq API Configuration
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.1"))
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "100000"))
    GROQ_RETRY_ATTEMPTS: int = int(os.getenv("GROQ_RETRY_ATTEMPTS", "3"))
    GROQ_RETRY_DELAY: float = float(os.getenv("GROQ_RETRY_DELAY", "1.0"))
    
    # Public Data Extraction Configuration
    PUBLIC_DATA_ENABLED: bool = bool(os.getenv("PUBLIC_DATA_ENABLED", "true").lower() == "true")
    PUBLIC_DATA_EXTRACTORS: List[str] = os.getenv("PUBLIC_DATA_EXTRACTORS", "products_services").split(",")
    PUBLIC_DATA_TIMEOUT: int = int(os.getenv("PUBLIC_DATA_TIMEOUT", "60"))
    PUBLIC_DATA_RETRY_ATTEMPTS: int = int(os.getenv("PUBLIC_DATA_RETRY_ATTEMPTS", "2"))

    # Mock Mode Configuration (for testing without API calls)
    USE_MOCK_LLM: bool = bool(os.getenv("USE_MOCK_LLM", "false").lower() == "true")
    
    def __post_init__(self):
        """Create necessary directories."""
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.LOG_FILE.parent.mkdir(exist_ok=True)

        # Warn if mock mode is active
        if self.USE_MOCK_LLM:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("⚠️ MOCK MODE ENABLED - Not suitable for production use!")
    
    def validate_configuration(self) -> bool:
        """Validate configuration settings.

        Returns:
            True if configuration is valid, False otherwise
        """
        # Skip API key validation in mock mode
        if not self.USE_MOCK_LLM:
            # Validate API keys based on provider
            if self.LLM_PROVIDER.lower() == "google":
                if not self.GOOGLE_API_KEY:
                    return False
            elif self.LLM_PROVIDER.lower() == "groq":
                if not self.GROQ_API_KEY:
                    return False
            else:
                # Invalid provider
                return False

        if self.MAX_FILE_SIZE_MB <= 0:
            return False

        if not self.SUPPORTED_FORMATS:
            return False

        return True


# Global settings instance
settings = Settings()