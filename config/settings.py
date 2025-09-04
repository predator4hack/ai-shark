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
    
    # Gemini API Configuration
    GEMINI_MODEL: str = "gemini-pro-vision"
    GEMINI_TEMPERATURE: float = 0.1
    GEMINI_MAX_TOKENS: int = 2048
    
    def __post_init__(self):
        """Create necessary directories."""
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.TEMP_DIR.mkdir(exist_ok=True)
        self.LOG_FILE.parent.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()