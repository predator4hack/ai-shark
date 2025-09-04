"""
Models package for the VC Document Analyzer.

This package contains the core data models and utility functions
used throughout the application.
"""

from .data_models import SlideImage, SlideAnalysis, ProcessingResult
from .utils import (
    validate_file_format,
    validate_file_size,
    validate_uploaded_file,
    get_supported_extensions,
    sanitize_filename,
    generate_output_filename,
    ensure_directory_exists,
    get_file_info,
    SUPPORTED_FORMATS,
    MAX_FILE_SIZE,
    MIN_FILE_SIZE
)

__all__ = [
    # Data models
    'SlideImage',
    'SlideAnalysis', 
    'ProcessingResult',
    # Utility functions
    'validate_file_format',
    'validate_file_size',
    'validate_uploaded_file',
    'get_supported_extensions',
    'sanitize_filename',
    'generate_output_filename',
    'ensure_directory_exists',
    'get_file_info',
    # Constants
    'SUPPORTED_FORMATS',
    'MAX_FILE_SIZE',
    'MIN_FILE_SIZE'
]