"""
Integration tests for the main document processing pipeline.

Tests the complete workflow from file upload through analysis to output generation.
"""

import pytest
import tempfile
import io
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from src.main import DocumentProcessingPipeline, ProcessingError
from src.models.data_models import SlideImage, SlideAnalysis
from src.ui.streamlit_interface import StreamlitInterface


class TestDocumentProcessingPipeline:
    """Test cases for the DocumentProcessingPipeline class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ui = Mock(spec=StreamlitInterface)
        self.pipeline = DocumentProcessingPipeline(self.mock_ui)
    
    def create_mock_uploaded_file(self, filename="test.pdf", content=b"test content"):
        """Create a mock uploaded file for testing."""
        mock_file = Mock()
        mock_file.name = filename
        mock_file.getvalue.return_value = content
        return mock_file
    
    def create_sample_slide_image(self, slide_number=1):
        """Create a sample SlideImage for testing."""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        
        return SlideImage(
            slide_number=slide_number,
            image_data=img_data,
            image_format='PNG',
            original_size=(100, 100)
        )
    
    def create_sample_slide_analysis(self, slide_number=1, has_errors=False):
        """Create a sample SlideAnalysis for testing."""
        errors = ["Test error"] if has_errors else []
        
        return SlideAnalysis(
            slide_number=slide_number,
            heading="Test Slide",
            image_descriptions=["Test image description"],
            chart_table_data=["Test chart data"],
            interpretation="Test interpretation",
            confidence_score=0.8,
            processing_time=1.0,
            errors=errors
        )
    
    @patch('src.main.tempfile.NamedTemporaryFile')
    def test_prepare_temporary_file_success(self, mock_temp_file):
        """Test successful temporary file preparation."""
        # Setup mock
        mock_temp_file.return_value.__enter__.return_value.name = "/tmp/test_file.pdf"
        mock_uploaded_file = self.create_mock_uploaded_file()
        self.pipeline.progress = Mock()  # Initialize progress tracker
        
        # Execute
        result = self.pipeline._prepare_temporary_file(mock_uploaded_file)
        
        # Verify
        assert result == "/tmp/test_file.pdf"
        assert "/tmp/test_file.pdf" in self.pipeline.temp_files
        mock_uploaded_file.getvalue.assert_called_once()
        self.pipeline.progress.update.assert_called_with(10, "📄 Preparing uploaded file...")
    
    @patch('src.main.tempfile.NamedTemporaryFile')
    def test_prepare_temporary_file_failure(self, mock_temp_file):
        """Test temporary file preparation failure."""
        # Setup mock to raise exception
        mock_temp_file.side_effect = OSError("Disk full")
        mock_uploaded_file = self.create_mock_uploaded_file()
        
        # Execute and verify exception
        with pytest.raises(ProcessingError, match="Failed to prepare temporary file"):
            self.pipeline._prepare_temporary_file(mock_uploaded_file)
    
    @patch('src.main.DocumentProcessor')
    @patch('src.main.GeminiAnalyzer')
    @patch('src.main.OutputManager')
    def test_initialize_processors_success(self, mock_output, mock_gemini, mock_doc):
        """Test successful processor initialization."""
        # Setup mocks
        self.pipeline.progress = Mock()
        
        # Execute
        self.pipeline._initialize_processors()
        
        # Verify
        assert self.pipeline.document_processor is not None
        assert self.pipeline.gemini_analyzer is not None
        assert self.pipeline.output_manager is not None
        self.pipeline.progress.update.assert_called_with(20, "🔧 Initializing processors...")
    
    @patch('src.main.DocumentProcessor')
    def test_initialize_processors_failure(self, mock_doc):
        """Test processor initialization failure."""
        # Setup mock to raise exception
        mock_doc.side_effect = Exception("Initialization failed")
        self.pipeline.progress = Mock()
        
        # Execute and verify exception
        with pytest.raises(ProcessingError, match="Failed to initialize processors"):
            self.pipeline._initialize_processors()
    
    def test_validate_api_connection_success(self):
        """Test successful API connection validation."""
        # Setup mocks
        self.pipeline.progress = Mock()
        self.pipeline.gemini_analyzer = Mock()
        self.pipeline.gemini_analyzer.test_connection.return_value = True
        
        # Execute
        self.pipeline._validate_api_connection()
        
        # Verify
        self.pipeline.progress.update.assert_called_with(25, "🔗 Testing API connection...")
        self.pipeline.gemini_analyzer.test_connection.assert_called_once()
    
    def test_validate_api_connection_failure(self):
        """Test API connection validation failure."""
        # Setup mocks
        self.pipeline.progress = Mock()
        self.pipeline.gemini_analyzer = Mock()
        self.pipeline.gemini_analyzer.test_connection.return_value = False
        
        # Execute and verify exception
        with pytest.raises(ProcessingError, match="Failed to connect to Gemini API"):
            self.pipeline._validate_api_connection()
    
    def test_extract_slides_success(self):
        """Test successful slide extraction."""
        # Setup mocks
        self.pipeline.progress = Mock()
        self.pipeline.document_processor = Mock()
        
        sample_slides = [
            self.create_sample_slide_image(1),
            self.create_sample_slide_image(2)
        ]
        self.pipeline.document_processor.process_document.return_value = sample_slides
        
        # Execute
        result = self.pipeline._extract_slides("/tmp/test.pdf")
        
        # Verify
        assert len(result) == 2
        assert result[0].slide_number == 1
        assert result[1].slide_number == 2
        self.pipeline.progress.update.assert_called_with(30, "📊 Extracting slides from document...")
        self.mock_ui.show_success.assert_called_with("Successfully extracted 2 slides")
    
    def test_extract_slides_no_slides(self):
        """Test slide extraction with no slides found."""
        # Setup mocks
        self.pipeline.progress = Mock()
        self.pipeline.document_processor = Mock()
        self.pipeline.document_processor.process_document.return_value = []
        
        # Execute and verify exception
        with pytest.raises(ProcessingError, match="No slides could be extracted"):
            self.pipeline._extract_slides("/tmp/test.pdf")
    
    @patch('src.main.st')
    @patch('src.main.time.sleep')
    def test_analyze_slides_success(self, mock_sleep, mock_st):
        """Test successful slide analysis."""
        # Setup mocks
        self.pipeline.progress = Mock()
        self.pipeline.gemini_analyzer = Mock()
        
        # Mock streamlit container
        mock_container = Mock()
        mock_st.container.return_value = mock_container
        mock_container.__enter__ = Mock(return_value=mock_container)
        mock_container.__exit__ = Mock(return_value=None)
        
        # Create sample slides and expected analyses
        sample_slides = [
            self.create_sample_slide_image(1),
            self.create_sample_slide_image(2)
        ]
        
        sample_analyses = [
            self.create_sample_slide_analysis(1),
            self.create_sample_slide_analysis(2)
        ]
        
        self.pipeline.gemini_analyzer.analyze_slide.side_effect = sample_analyses
        
        # Execute
        result = self.pipeline._analyze_slides(sample_slides)
        
        # Verify
        assert len(result) == 2
        assert result[0].slide_number == 1
        assert result[1].slide_number == 2
        assert self.pipeline.gemini_analyzer.analyze_slide.call_count == 2
    
    @patch('src.main.st')
    @patch('src.main.time.sleep')
    def test_analyze_slides_all_failures(self, mock_sleep, mock_st):
        """Test slide analysis with all slides failing."""
        # Setup mocks
        self.pipeline.progress = Mock()
        self.pipeline.gemini_analyzer = Mock()
        
        # Mock streamlit container
        mock_container = Mock()
        mock_st.container.return_value = mock_container
        mock_container.__enter__ = Mock(return_value=mock_container)
        mock_container.__exit__ = Mock(return_value=None)
        
        # Create sample slides
        sample_slides = [self.create_sample_slide_image(1)]
        
        # Mock analyzer to always raise exception
        self.pipeline.gemini_analyzer.analyze_slide.side_effect = Exception("API Error")
        
        # Execute and verify exception
        with pytest.raises(ProcessingError, match="All slide analyses failed"):
            self.pipeline._analyze_slides(sample_slides)
    
    @patch('src.main.st')
    @patch('src.main.time.time')
    def test_save_and_complete_processing_success(self, mock_time, mock_st):
        """Test successful processing completion and saving."""
        # Setup mocks
        self.pipeline.progress = Mock()
        self.pipeline.output_manager = Mock()
        self.pipeline.start_time = 1000.0
        
        mock_time.return_value = 1010.0  # 10 seconds processing time
        
        # Create a proper mock session state object
        mock_session_state = Mock()
        mock_st.session_state = mock_session_state
        
        sample_analyses = [
            self.create_sample_slide_analysis(1),
            self.create_sample_slide_analysis(2, has_errors=True)  # One with errors
        ]
        
        self.pipeline.output_manager.save_analysis.return_value = "/tmp/output.md"
        
        # Execute
        self.pipeline._save_and_complete_processing(sample_analyses, "test.pdf")
        
        # Verify
        self.pipeline.output_manager.save_analysis.assert_called_once()
        args, kwargs = self.pipeline.output_manager.save_analysis.call_args
        
        assert args[0] == sample_analyses
        assert args[1] == "test.pdf"
        assert "total_processing_time" in args[2]
        assert args[2]["successful_slides"] == 1  # Only one without errors
        
        # Verify session state updates
        assert mock_session_state.analysis_results == sample_analyses
        assert mock_session_state.output_file_path == "/tmp/output.md"
        assert mock_session_state.processing_complete is True
    
    def test_cleanup_temporary_files(self):
        """Test temporary file cleanup."""
        # Create actual temporary files for testing
        with tempfile.NamedTemporaryFile(delete=False) as tmp1:
            temp_file1 = tmp1.name
        with tempfile.NamedTemporaryFile(delete=False) as tmp2:
            temp_file2 = tmp2.name
        
        # Add to pipeline temp files
        self.pipeline.temp_files = [temp_file1]
        
        # Execute cleanup
        self.pipeline._cleanup_temporary_files(temp_file2)
        
        # Verify files are deleted
        assert not Path(temp_file1).exists()
        assert not Path(temp_file2).exists()
        assert len(self.pipeline.temp_files) == 0
    
    @patch('src.main.st')
    @patch('src.main.time.time')
    @patch('src.main.tempfile.NamedTemporaryFile')
    def test_execute_complete_pipeline_success(self, mock_temp_file, mock_time, mock_st):
        """Test complete pipeline execution success."""
        # Setup comprehensive mocks
        mock_time.return_value = 1000.0
        mock_st.session_state = {}
        
        # Mock temporary file
        mock_temp_file.return_value.__enter__.return_value.name = "/tmp/test.pdf"
        
        # Mock uploaded file
        mock_uploaded_file = self.create_mock_uploaded_file()
        
        # Mock all pipeline methods
        with patch.object(self.pipeline, '_prepare_temporary_file', return_value="/tmp/test.pdf"), \
             patch.object(self.pipeline, '_initialize_processors'), \
             patch.object(self.pipeline, '_validate_api_connection'), \
             patch.object(self.pipeline, '_extract_slides', return_value=[self.create_sample_slide_image()]), \
             patch.object(self.pipeline, '_analyze_slides', return_value=[self.create_sample_slide_analysis()]), \
             patch.object(self.pipeline, '_save_and_complete_processing'), \
             patch.object(self.pipeline, '_cleanup_temporary_files'):
            
            # Execute
            self.pipeline.execute(mock_uploaded_file)
            
            # Verify all methods were called
            self.pipeline._prepare_temporary_file.assert_called_once_with(mock_uploaded_file)
            self.pipeline._initialize_processors.assert_called_once()
            self.pipeline._validate_api_connection.assert_called_once()
            self.pipeline._extract_slides.assert_called_once_with("/tmp/test.pdf")
            self.pipeline._analyze_slides.assert_called_once()
            self.pipeline._save_and_complete_processing.assert_called_once()
            self.pipeline._cleanup_temporary_files.assert_called_once_with("/tmp/test.pdf")
    
    @patch('src.main.st')
    def test_execute_pipeline_with_processing_error(self, mock_st):
        """Test pipeline execution with ProcessingError."""
        mock_st.session_state = {}
        mock_uploaded_file = self.create_mock_uploaded_file()
        
        # Mock method to raise ProcessingError
        with patch.object(self.pipeline, '_prepare_temporary_file', 
                         side_effect=ProcessingError("Test error")), \
             patch.object(self.pipeline, '_cleanup_on_error') as mock_cleanup_error, \
             patch.object(self.pipeline, '_cleanup_temporary_files') as mock_cleanup_files:
            
            # Execute
            self.pipeline.execute(mock_uploaded_file)
            
            # Verify error handling
            self.mock_ui.show_error.assert_called_with("Test error")
            mock_cleanup_error.assert_called_once()
            mock_cleanup_files.assert_called_once()
    
    @patch('src.main.st')
    def test_execute_pipeline_with_unexpected_error(self, mock_st):
        """Test pipeline execution with unexpected error."""
        mock_st.session_state = {}
        mock_uploaded_file = self.create_mock_uploaded_file()
        
        # Mock method to raise unexpected exception
        with patch.object(self.pipeline, '_prepare_temporary_file', 
                         side_effect=ValueError("Unexpected error")), \
             patch.object(self.pipeline, '_cleanup_on_error') as mock_cleanup_error, \
             patch.object(self.pipeline, '_cleanup_temporary_files') as mock_cleanup_files:
            
            # Execute
            self.pipeline.execute(mock_uploaded_file)
            
            # Verify error handling
            self.mock_ui.show_error.assert_called_with("An unexpected error occurred: Unexpected error")
            mock_cleanup_error.assert_called_once()
            mock_cleanup_files.assert_called_once()


class TestProcessingError:
    """Test cases for the ProcessingError exception."""
    
    def test_processing_error_creation(self):
        """Test ProcessingError exception creation."""
        error = ProcessingError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)