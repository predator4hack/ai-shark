"""Configuration settings for the VC Document Analyzer."""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # API Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "VC Document Analyzer")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    SUPPORTED_FORMATS: List[str] = os.getenv("SUPPORTED_FORMATS", "pdf,pptx,png,jpg,jpeg").split(",")
    
    # Directory Configuration
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "outputs"))
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "temp"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = Path(os.getenv("LOG_FILE", "logs/app.log"))
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "google")  # "google" or "groq"

    # Gemini API Configuration
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))  # Increased for comprehensive analysis
    GEMINI_RETRY_ATTEMPTS: int = int(os.getenv("GEMINI_RETRY_ATTEMPTS", "3"))
    GEMINI_RETRY_DELAY: float = float(os.getenv("GEMINI_RETRY_DELAY", "1.0"))

    # Groq API Configuration
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.1"))
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "8192"))  # Increased for comprehensive analysis
    GROQ_RETRY_ATTEMPTS: int = int(os.getenv("GROQ_RETRY_ATTEMPTS", "3"))
    GROQ_RETRY_DELAY: float = float(os.getenv("GROQ_RETRY_DELAY", "1.0"))
    
    def __post_init__(self):
        """Create necessary directories."""
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.TEMP_DIR.mkdir(exist_ok=True)
        self.LOG_FILE.parent.mkdir(exist_ok=True)
    
    def validate_configuration(self) -> bool:
        """Validate configuration settings.

        Returns:
            True if configuration is valid, False otherwise
        """
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