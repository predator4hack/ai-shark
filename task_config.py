"""
Configuration management for Multi-Agent Startup Analysis System
Task 1: Environment Setup and Dependencies
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class for the application"""

    # Google AI Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-flash-2.5")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "8192"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))

    # Project Paths
    PROJECT_ROOT: Path = Path(__file__).parent
    SRC_DIR: Path = PROJECT_ROOT / "src"
    AGENTS_DIR: Path = SRC_DIR / "agents"
    MODELS_DIR: Path = SRC_DIR / "models"
    UTILS_DIR: Path = SRC_DIR / "utils"
    TESTS_DIR: Path = PROJECT_ROOT / "tests"
    RESULTS_DIR: Path = PROJECT_ROOT / "results"
    OUTPUT_DIR: Path = PROJECT_ROOT / "outputs"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")

    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        # Ensure directories exist
        for directory in [cls.SRC_DIR, cls.AGENTS_DIR, cls.MODELS_DIR,
                         cls.UTILS_DIR, cls.TESTS_DIR, cls.RESULTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

        return True

    @classmethod
    def setup_logging(cls) -> None:
        """Setup logging configuration"""
        logging_config = {
            'level': getattr(logging, cls.LOG_LEVEL.upper()),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }

        if cls.LOG_FILE:
            # Ensure log directory exists
            log_path = Path(cls.LOG_FILE)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            logging_config['filename'] = cls.LOG_FILE

        logging.basicConfig(**logging_config)

# Create output directory if it doesn't exist
Config.OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize configuration
config = Config()