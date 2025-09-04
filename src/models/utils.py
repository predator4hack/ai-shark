"""
Utility functions for file validation and path handling.

This module provides helper functions for validating uploaded files,
handling file paths, and managing file operations safely.
"""

import os
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime


# Supported file formats and their MIME types
SUPPORTED_FORMATS = {
    'pdf': ['application/pdf'],
    'pptx': [
        'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    ],
    'images': [
        'image/png',
        'image/jpeg',
        'image/jpg'
    ]
}

# File size limits (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB as per requirements
MIN_FILE_SIZE = 1024  # 1KB minimum


def validate_file_format(file_path: str) -> Tuple[bool, Optional[str]]:
    """Validate if the file format is supported.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if file format is supported
        - error_message: None if valid, error description if invalid
    """
    try:
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return False, f"File does not exist: {file_path}"
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        
        if mime_type is None:
            return False, f"Could not determine file type for: {path.name}"
        
        # Check against supported formats
        all_supported_types = []
        for format_types in SUPPORTED_FORMATS.values():
            all_supported_types.extend(format_types)
        
        if mime_type not in all_supported_types:
            supported_extensions = get_supported_extensions()
            return False, f"Unsupported file format. Supported formats: {', '.join(supported_extensions)}"
        
        return True, None
        
    except Exception as e:
        return False, f"Error validating file format: {str(e)}"


def validate_file_size(file_path: str) -> Tuple[bool, Optional[str]]:
    """Validate if the file size is within acceptable limits.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if file size is acceptable
        - error_message: None if valid, error description if invalid
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return False, f"File does not exist: {file_path}"
        
        file_size = path.stat().st_size
        
        if file_size < MIN_FILE_SIZE:
            return False, f"File too small. Minimum size: {MIN_FILE_SIZE} bytes"
        
        if file_size > MAX_FILE_SIZE:
            size_mb = MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {size_mb:.1f}MB"
        
        return True, None
        
    except Exception as e:
        return False, f"Error checking file size: {str(e)}"


def validate_uploaded_file(file_path: str) -> Tuple[bool, List[str]]:
    """Comprehensive validation of an uploaded file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
        - is_valid: True if all validations pass
        - error_messages: List of error messages (empty if valid)
    """
    errors = []
    
    # Validate file format
    format_valid, format_error = validate_file_format(file_path)
    if not format_valid:
        errors.append(format_error)
    
    # Validate file size
    size_valid, size_error = validate_file_size(file_path)
    if not size_valid:
        errors.append(size_error)
    
    return len(errors) == 0, errors


def get_supported_extensions() -> List[str]:
    """Get list of supported file extensions.
    
    Returns:
        List of supported file extensions (e.g., ['.pdf', '.pptx', '.png'])
    """
    extensions = []
    
    # Add PDF extension
    extensions.append('.pdf')
    
    # Add PowerPoint extension
    extensions.append('.pptx')
    
    # Add image extensions
    extensions.extend(['.png', '.jpg', '.jpeg'])
    
    return extensions


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename to sanitize
        
    Returns:
        Sanitized filename safe for file system operations
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    
    # Limit length to reasonable size
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:200-len(ext)] + ext
    
    return sanitized


def generate_output_filename(original_filename: str, timestamp: Optional[datetime] = None) -> str:
    """Generate a timestamped output filename.
    
    Args:
        original_filename: Original document filename
        timestamp: Optional timestamp (uses current time if None)
        
    Returns:
        Generated filename with timestamp (e.g., 'document_2024-01-15_14-30.md')
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Extract base name without extension
    base_name = Path(original_filename).stem
    
    # Sanitize the base name
    base_name = sanitize_filename(base_name)
    
    # Format timestamp
    timestamp_str = timestamp.strftime('%Y-%m-%d_%H-%M')
    
    # Generate final filename
    output_filename = f"{base_name}_{timestamp_str}.md"
    
    return output_filename


def ensure_directory_exists(directory_path: str) -> bool:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_info(file_path: str) -> dict:
    """Get comprehensive information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {'error': 'File does not exist'}
        
        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(str(path))
        
        return {
            'name': path.name,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'mime_type': mime_type,
            'extension': path.suffix.lower(),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'is_supported': validate_file_format(file_path)[0]
        }
        
    except Exception as e:
        return {'error': f'Error getting file info: {str(e)}'}