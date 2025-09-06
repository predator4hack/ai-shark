"""Startup validation for the VC Document Analyzer."""

import logging
import sys
from pathlib import Path

from config.settings import settings
from config.logging_config import setup_logging


logger = logging.getLogger(__name__)


def validate_dependencies():
    """Validate that all required dependencies are available."""
    try:
        import streamlit
        import google.generativeai
        import fitz  # PyMuPDF
        import pptx
        from PIL import Image
        logger.info("All required dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        return False


def validate_api_connection():
    """Validate that the Gemini API connection works."""
    try:
        from src.analyzers.gemini_analyzer import GeminiAnalyzer
        
        analyzer = GeminiAnalyzer()
        if analyzer.test_connection():
            logger.info("Gemini API connection successful")
            return True
        else:
            logger.error("Gemini API connection failed")
            return False
    except Exception as e:
        logger.error(f"Failed to test API connection: {e}")
        return False


def validate_directories():
    """Validate that all required directories exist and are writable."""
    directories = [
        settings.OUTPUT_DIR,
        settings.TEMP_DIR,
        settings.LOG_FILE.parent
    ]
    
    for directory in directories:
        try:
            directory.mkdir(exist_ok=True)
            # Test write permissions
            test_file = directory / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            logger.info(f"Directory {directory} is accessible and writable")
        except Exception as e:
            logger.error(f"Directory {directory} is not accessible or writable: {e}")
            return False
    
    return True


def run_startup_validation():
    """Run all startup validations.
    
    Returns:
        True if all validations pass, False otherwise
    """
    # Setup logging first
    setup_logging()
    
    logger.info("Starting application validation...")
    
    validations = [
        ("Configuration", settings.validate_configuration),
        ("Dependencies", validate_dependencies),
        ("Directories", validate_directories),
        ("API Connection", validate_api_connection),
    ]
    
    all_passed = True
    
    for name, validation_func in validations:
        try:
            if validation_func():
                logger.info(f"✓ {name} validation passed")
            else:
                logger.error(f"✗ {name} validation failed")
                all_passed = False
        except Exception as e:
            logger.error(f"✗ {name} validation error: {e}")
            all_passed = False
    
    if all_passed:
        logger.info("All startup validations passed successfully")
    else:
        logger.error("Some startup validations failed")
    
    return all_passed


if __name__ == "__main__":
    if not run_startup_validation():
        sys.exit(1)
    print("All validations passed!")