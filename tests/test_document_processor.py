"""
Unit tests for the DocumentProcessor class.

Tests cover PDF processing, PPTX processing, image processing,
file validation, and error handling scenarios.
"""

import io
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from src.processors.document_processor import (
    DocumentProcessor,
    DocumentProcessorError,
    UnsupportedFormatError,
    FileValidationError
)
from src.models.data_models import SlideImage


class TestDocumentProcessor:
    """Test cases for DocumentProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = DocumentProcessor()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.processor.cleanup_temp_files()
    
    def test_init(self):
        """Test DocumentProcessor initialization."""
        processor = DocumentProcessor()
        assert processor.temp_files == []
        assert processor.MAX_FILE_SIZE == 10 * 1024 * 1024
        assert 'PDF' in processor.SUPPORTED_FORMATS.values()
        assert 'PPTX' in processor.SUPPORTED_FORMATS.values()
    
    def test_get_supported_formats(self):
        """Test getting supported file formats."""
        formats = self.processor.get_supported_formats()
        expected_formats = ['.pdf', '.pptx', '.png', '.jpg', '.jpeg']
        
        for fmt in expected_formats:
            assert fmt in formats
    
    def test_detect_format(self):
        """Test file format detection."""
        assert self.processor._detect_format('test.pdf') == 'PDF'
        assert self.processor._detect_format('test.pptx') == 'PPTX'
        assert self.processor._detect_format('test.png') == 'PNG'
        assert self.processor._detect_format('test.jpg') == 'JPEG'
        assert self.processor._detect_format('test.jpeg') == 'JPEG'
        assert self.processor._detect_format('test.txt') == 'UNKNOWN'
    
    def test_validate_file_nonexistent(self):
        """Test validation with non-existent file."""
        with pytest.raises(FileValidationError, match="File does not exist"):
            self.processor._validate_file('nonexistent.pdf')
    
    def test_validate_file_directory(self):
        """Test validation with directory instead of file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(FileValidationError, match="Path is not a file"):
                self.processor._validate_file(temp_dir)
    
    def test_validate_file_too_large(self):
        """Test validation with file too large."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Create a file larger than MAX_FILE_SIZE
            large_data = b'x' * (self.processor.MAX_FILE_SIZE + 1)
            temp_file.write(large_data)
            temp_file.flush()
            
            try:
                with pytest.raises(FileValidationError, match="File too large"):
                    self.processor._validate_file(temp_file.name)
            finally:
                Path(temp_file.name).unlink()
    
    def test_validate_file_empty(self):
        """Test validation with empty file."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.flush()  # Create empty file
            
            try:
                with pytest.raises(FileValidationError, match="File is empty"):
                    self.processor._validate_file(temp_file.name)
            finally:
                Path(temp_file.name).unlink()
    
    def test_validate_file_unsupported_format(self):
        """Test validation with unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'some content')
            temp_file.flush()
            
            try:
                with pytest.raises(FileValidationError, match="Unsupported file format"):
                    self.processor._validate_file(temp_file.name)
            finally:
                Path(temp_file.name).unlink()
    
    def test_validate_file_format_success(self):
        """Test successful file format validation."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'some pdf content')
            temp_file.flush()
            
            try:
                assert self.processor.validate_file_format(temp_file.name) is True
            finally:
                Path(temp_file.name).unlink()
    
    def test_validate_file_format_failure(self):
        """Test failed file format validation."""
        assert self.processor.validate_file_format('nonexistent.pdf') is False
    
    @patch('src.processors.document_processor.fitz')
    def test_extract_pdf_slides_success(self, mock_fitz):
        """Test successful PDF slide extraction."""
        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc.page_count = 2
        mock_fitz.open.return_value = mock_doc
        
        # Mock pages
        mock_page1 = MagicMock()
        mock_page2 = MagicMock()
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        
        # Mock pixmap
        mock_pixmap = MagicMock()
        mock_pixmap.tobytes.return_value = self._create_test_image_bytes()
        mock_page1.get_pixmap.return_value = mock_pixmap
        mock_page2.get_pixmap.return_value = mock_pixmap
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'fake pdf content')
            temp_file.flush()
            
            try:
                slides = self.processor._extract_pdf_slides(temp_file.name)
                
                assert len(slides) == 2
                assert slides[0].slide_number == 1
                assert slides[1].slide_number == 2
                assert slides[0].image_format == 'PNG'
                assert isinstance(slides[0].image_data, bytes)
                
                mock_fitz.open.assert_called_once_with(temp_file.name)
                mock_doc.close.assert_called_once()
                
            finally:
                Path(temp_file.name).unlink()
    
    @patch('src.processors.document_processor.fitz')
    def test_extract_pdf_slides_empty_document(self, mock_fitz):
        """Test PDF extraction with empty document."""
        mock_doc = MagicMock()
        mock_doc.page_count = 0
        mock_fitz.open.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'fake pdf content')
            temp_file.flush()
            
            try:
                with pytest.raises(DocumentProcessorError, match="PDF contains no pages"):
                    self.processor._extract_pdf_slides(temp_file.name)
            finally:
                Path(temp_file.name).unlink()
    
    @patch('src.processors.document_processor.fitz')
    def test_extract_pdf_slides_corrupted_file(self, mock_fitz):
        """Test PDF extraction with corrupted file."""
        mock_fitz.open.side_effect = Exception("FileDataError: Invalid PDF")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'fake pdf content')
            temp_file.flush()
            
            try:
                with pytest.raises(DocumentProcessorError, match="Invalid or corrupted PDF file"):
                    self.processor._extract_pdf_slides(temp_file.name)
            finally:
                Path(temp_file.name).unlink()
    
    @patch('src.processors.document_processor.Presentation')
    def test_extract_pptx_slides_success(self, mock_presentation_class):
        """Test successful PPTX slide extraction."""
        # Mock presentation
        mock_prs = MagicMock()
        mock_slide1 = MagicMock()
        mock_slide2 = MagicMock()
        mock_prs.slides = [mock_slide1, mock_slide2]
        mock_presentation_class.return_value = mock_prs
        
        with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as temp_file:
            temp_file.write(b'fake pptx content')
            temp_file.flush()
            
            try:
                slides = self.processor._extract_pptx_slides(temp_file.name)
                
                assert len(slides) == 2
                assert slides[0].slide_number == 1
                assert slides[1].slide_number == 2
                assert slides[0].image_format == 'PNG'
                
                mock_presentation_class.assert_called_once_with(temp_file.name)
                
            finally:
                Path(temp_file.name).unlink()
    
    @patch('src.processors.document_processor.Presentation')
    def test_extract_pptx_slides_empty_presentation(self, mock_presentation_class):
        """Test PPTX extraction with empty presentation."""
        mock_prs = MagicMock()
        mock_prs.slides = []
        mock_presentation_class.return_value = mock_prs
        
        with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as temp_file:
            temp_file.write(b'fake pptx content')
            temp_file.flush()
            
            try:
                with pytest.raises(DocumentProcessorError, match="PPTX contains no slides"):
                    self.processor._extract_pptx_slides(temp_file.name)
            finally:
                Path(temp_file.name).unlink()
    
    def test_process_image_file_png(self):
        """Test processing PNG image file."""
        # Create a test PNG image
        test_image = Image.new('RGB', (800, 600), color='red')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            test_image.save(temp_file.name, 'PNG')
            
            try:
                slides = self.processor._process_image_file(temp_file.name, 'PNG')
                
                assert len(slides) == 1
                assert slides[0].slide_number == 1
                assert slides[0].image_format == 'PNG'
                assert isinstance(slides[0].image_data, bytes)
                assert slides[0].original_size == (800, 600)
                
            finally:
                Path(temp_file.name).unlink()
    
    def test_process_image_file_jpeg(self):
        """Test processing JPEG image file."""
        # Create a test JPEG image
        test_image = Image.new('RGB', (1200, 800), color='blue')
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            test_image.save(temp_file.name, 'JPEG')
            
            try:
                slides = self.processor._process_image_file(temp_file.name, 'JPEG')
                
                assert len(slides) == 1
                assert slides[0].slide_number == 1
                assert slides[0].image_format == 'JPEG'
                assert isinstance(slides[0].image_data, bytes)
                
            finally:
                Path(temp_file.name).unlink()
    
    def test_optimize_image_resize_large(self):
        """Test image optimization with large image that needs resizing."""
        # Create large image
        large_image = Image.new('RGB', (3000, 2000), color='green')
        
        optimized_data, final_size = self.processor._optimize_image(large_image, 'PNG')
        
        assert isinstance(optimized_data, bytes)
        assert final_size[0] <= self.processor.MAX_IMAGE_WIDTH
        assert final_size[1] <= self.processor.MAX_IMAGE_HEIGHT
        # Check aspect ratio is maintained
        original_ratio = 3000 / 2000
        final_ratio = final_size[0] / final_size[1]
        assert abs(original_ratio - final_ratio) < 0.01
    
    def test_optimize_image_rgba_to_jpeg(self):
        """Test image optimization converting RGBA to JPEG."""
        # Create RGBA image
        rgba_image = Image.new('RGBA', (800, 600), color=(255, 0, 0, 128))
        
        optimized_data, final_size = self.processor._optimize_image(rgba_image, 'JPEG')
        
        assert isinstance(optimized_data, bytes)
        assert final_size == (800, 600)
        
        # Verify it's a valid JPEG
        result_image = Image.open(io.BytesIO(optimized_data))
        assert result_image.mode == 'RGB'
    
    def test_process_document_pdf_integration(self):
        """Test full document processing integration for PDF."""
        with patch.object(self.processor, '_extract_pdf_slides') as mock_extract:
            mock_extract.return_value = [
                SlideImage(1, b'fake_data', 'PNG', (800, 600))
            ]
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(b'fake pdf content')
                temp_file.flush()
                
                try:
                    slides = self.processor.process_document(temp_file.name)
                    
                    assert len(slides) == 1
                    assert slides[0].slide_number == 1
                    mock_extract.assert_called_once_with(temp_file.name)
                    
                finally:
                    Path(temp_file.name).unlink()
    
    def test_process_document_unsupported_format(self):
        """Test document processing with unsupported format."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'some text content')
            temp_file.flush()
            
            try:
                with pytest.raises(DocumentProcessorError):
                    self.processor.process_document(temp_file.name)
            finally:
                Path(temp_file.name).unlink()
    
    def test_cleanup_temp_files(self):
        """Test temporary file cleanup."""
        # Create a temporary file and add to tracking
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b'test content')
            temp_file.flush()
            self.processor.temp_files.append(temp_file.name)
        
        # Verify file exists
        assert Path(temp_file.name).exists()
        
        # Cleanup
        self.processor.cleanup_temp_files()
        
        # Verify file is deleted and list is cleared
        assert not Path(temp_file.name).exists()
        assert self.processor.temp_files == []
    
    def _create_test_image_bytes(self) -> bytes:
        """Create test image bytes for mocking."""
        test_image = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='PNG')
        return img_buffer.getvalue()