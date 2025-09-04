"""
Tests for the core data models and utilities.
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from src.models import (
    SlideImage, SlideAnalysis, ProcessingResult,
    validate_file_format, validate_file_size, validate_uploaded_file,
    get_supported_extensions, sanitize_filename, generate_output_filename,
    ensure_directory_exists, get_file_info
)


class TestDataModels:
    """Test the core data model classes."""
    
    def test_slide_image_creation(self):
        """Test SlideImage dataclass creation."""
        slide = SlideImage(
            slide_number=1,
            image_data=b'fake_image_data',
            image_format='PNG',
            original_size=(1920, 1080)
        )
        
        assert slide.slide_number == 1
        assert slide.image_data == b'fake_image_data'
        assert slide.image_format == 'PNG'
        assert slide.original_size == (1920, 1080)
    
    def test_slide_analysis_creation(self):
        """Test SlideAnalysis dataclass creation."""
        analysis = SlideAnalysis(
            slide_number=1,
            heading="Company Overview",
            image_descriptions=["Logo image", "Team photo"],
            chart_table_data=["Revenue chart showing 50% growth"],
            interpretation="This slide introduces the company"
        )
        
        assert analysis.slide_number == 1
        assert analysis.heading == "Company Overview"
        assert len(analysis.image_descriptions) == 2
        assert len(analysis.chart_table_data) == 1
        assert analysis.errors == []  # Should initialize empty list
    
    def test_processing_result_creation(self):
        """Test ProcessingResult dataclass creation."""
        result = ProcessingResult(
            document_name="test.pdf",
            total_slides=5,
            successful_slides=4,
            failed_slides=[3],
            processing_time=45.2,
            output_file_path="/path/to/output.md",
            slide_analyses=[]
        )
        
        assert result.document_name == "test.pdf"
        assert result.total_slides == 5
        assert result.successful_slides == 4
        assert result.success_rate == 80.0
        assert result.has_failures is True


class TestUtilityFunctions:
    """Test utility functions for file handling."""
    
    def test_get_supported_extensions(self):
        """Test getting supported file extensions."""
        extensions = get_supported_extensions()
        
        assert '.pdf' in extensions
        assert '.pptx' in extensions
        assert '.png' in extensions
        assert '.jpg' in extensions
        assert '.jpeg' in extensions
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test invalid characters
        assert sanitize_filename('file<>name.pdf') == 'file__name.pdf'
        assert sanitize_filename('file:name|test.pdf') == 'file_name_test.pdf'
        
        # Test empty filename
        assert sanitize_filename('') == 'unnamed_file'
        assert sanitize_filename('   ') == 'unnamed_file'
        
        # Test normal filename
        assert sanitize_filename('normal_file.pdf') == 'normal_file.pdf'
    
    def test_generate_output_filename(self):
        """Test output filename generation."""
        timestamp = datetime(2024, 1, 15, 14, 30, 0)
        filename = generate_output_filename('test_document.pdf', timestamp)
        
        assert filename == 'test_document_2024-01-15_14-30.md'
        
        # Test with special characters
        filename = generate_output_filename('test<>file.pptx', timestamp)
        assert filename == 'test__file_2024-01-15_14-30.md'
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, 'test_subdir')
            
            # Directory should not exist initially
            assert not os.path.exists(test_dir)
            
            # Create directory
            result = ensure_directory_exists(test_dir)
            assert result is True
            assert os.path.exists(test_dir)
            
            # Should work if directory already exists
            result = ensure_directory_exists(test_dir)
            assert result is True
    
    def test_file_validation_with_temp_files(self):
        """Test file validation with temporary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = os.path.join(temp_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test content')
            
            # Test file info
            info = get_file_info(test_file)
            assert 'error' not in info
            assert info['name'] == 'test.txt'
            assert info['size'] > 0
            
            # Test non-existent file
            info = get_file_info(os.path.join(temp_dir, 'nonexistent.txt'))
            assert 'error' in info


if __name__ == '__main__':
    pytest.main([__file__])