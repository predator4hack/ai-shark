"""
Tests for the Streamlit interface components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import io

from src.ui.streamlit_interface import StreamlitInterface, ProgressTracker, SidebarManager
from src.models.data_models import SlideAnalysis


class TestStreamlitInterface:
    """Test cases for StreamlitInterface class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ui = StreamlitInterface()
    
    def test_init(self):
        """Test StreamlitInterface initialization."""
        assert self.ui.document_processor is None
        assert self.ui.gemini_analyzer is None
        assert self.ui.output_manager is None
    
    @patch('src.ui.streamlit_interface.st')
    def test_validate_uploaded_file_valid(self, mock_st):
        """Test file validation with valid file."""
        # Mock uploaded file
        mock_file = Mock()
        mock_file.getvalue.return_value = b"x" * (5 * 1024 * 1024)  # 5MB file
        
        result = self.ui._validate_uploaded_file(mock_file)
        assert result is True
        mock_st.error.assert_not_called()
    
    @patch('src.ui.streamlit_interface.st')
    def test_validate_uploaded_file_too_large(self, mock_st):
        """Test file validation with oversized file."""
        # Mock uploaded file that's too large
        mock_file = Mock()
        mock_file.getvalue.return_value = b"x" * (15 * 1024 * 1024)  # 15MB file
        
        result = self.ui._validate_uploaded_file(mock_file)
        assert result is False
        mock_st.error.assert_called_once()
    
    @patch('src.ui.streamlit_interface.st')
    def test_display_file_info(self, mock_st):
        """Test file information display."""
        mock_file = Mock()
        mock_file.name = "test.pdf"
        mock_file.type = "application/pdf"
        mock_file.getvalue.return_value = b"x" * (2 * 1024 * 1024)  # 2MB
        
        # Mock streamlit columns
        mock_columns = [Mock(), Mock(), Mock()]
        mock_st.columns.return_value = mock_columns
        
        self.ui._display_file_info(mock_file)
        
        # Verify columns were created and metrics were called
        mock_st.columns.assert_called_once_with(3)
        assert all(col.metric.called for col in mock_columns)
    
    @patch('src.ui.streamlit_interface.st')
    def test_show_progress(self, mock_st):
        """Test progress display functionality."""
        # Mock session state
        mock_st.session_state = {}
        mock_progress_bar = Mock()
        mock_status_text = Mock()
        mock_st.progress.return_value = mock_progress_bar
        mock_st.empty.return_value = mock_status_text
        
        self.ui.show_progress(50, 100, "Test message")
        
        # Verify progress bar and status text were updated
        mock_progress_bar.progress.assert_called_with(50)
        mock_status_text.text.assert_called_with("Test message")
    
    @patch('src.ui.streamlit_interface.st')
    def test_display_summary_metrics(self, mock_st):
        """Test summary metrics display."""
        # Create test results
        results = [
            SlideAnalysis(1, "Test 1", [], [], "Interpretation 1", 0.8, 1.0, []),
            SlideAnalysis(2, "Test 2", [], [], "Interpretation 2", 0.9, 1.5, ["Error"]),
            SlideAnalysis(3, "Test 3", [], [], "Interpretation 3", 0.7, 2.0, [])
        ]
        
        # Mock streamlit columns
        mock_columns = [Mock(), Mock(), Mock(), Mock()]
        mock_st.columns.return_value = mock_columns
        
        self.ui._display_summary_metrics(results)
        
        # Verify metrics were displayed
        mock_st.columns.assert_called_once_with(4)
        assert all(col.metric.called for col in mock_columns)
    
    @patch('src.ui.streamlit_interface.st')
    @patch('src.ui.streamlit_interface.Path')
    def test_display_download_button(self, mock_path, mock_st):
        """Test download button display."""
        # Mock file path
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.name = "test_output.md"
        mock_path.return_value = mock_path_obj
        
        # Mock file content
        with patch('builtins.open', mock_open(read_data=b"test content")):
            self.ui._display_download_button("/path/to/output.md")
        
        # Verify download button was created
        mock_st.download_button.assert_called_once()
    
    @patch('src.ui.streamlit_interface.st')
    def test_show_error(self, mock_st):
        """Test error message display."""
        self.ui.show_error("Test error message")
        mock_st.error.assert_called_once_with("❌ Test error message")
    
    @patch('src.ui.streamlit_interface.st')
    def test_show_success(self, mock_st):
        """Test success message display."""
        self.ui.show_success("Test success message")
        mock_st.success.assert_called_once_with("✅ Test success message")
    
    @patch('src.ui.streamlit_interface.st')
    def test_show_info(self, mock_st):
        """Test info message display."""
        self.ui.show_info("Test info message")
        mock_st.info.assert_called_once_with("ℹ️ Test info message")
    
    @patch('src.ui.streamlit_interface.st')
    def test_show_warning(self, mock_st):
        """Test warning message display."""
        self.ui.show_warning("Test warning message")
        mock_st.warning.assert_called_once_with("⚠️ Test warning message")


class TestProgressTracker:
    """Test cases for ProgressTracker class."""
    
    @patch('src.ui.streamlit_interface.st')
    def test_init(self, mock_st):
        """Test ProgressTracker initialization."""
        mock_progress_bar = Mock()
        mock_status_text = Mock()
        mock_st.progress.return_value = mock_progress_bar
        mock_st.empty.return_value = mock_status_text
        
        tracker = ProgressTracker()
        
        assert tracker.current_step == 0
        assert tracker.total_steps == 100
        mock_st.progress.assert_called_once_with(0)
        mock_st.empty.assert_called_once()
    
    @patch('src.ui.streamlit_interface.st')
    def test_update(self, mock_st):
        """Test progress update."""
        mock_progress_bar = Mock()
        mock_status_text = Mock()
        mock_st.progress.return_value = mock_progress_bar
        mock_st.empty.return_value = mock_status_text
        
        tracker = ProgressTracker()
        tracker.update(50, "Test message")
        
        assert tracker.current_step == 50
        mock_progress_bar.progress.assert_called_with(50)
        mock_status_text.text.assert_called_with("Test message")
    
    @patch('src.ui.streamlit_interface.st')
    def test_increment(self, mock_st):
        """Test progress increment."""
        mock_progress_bar = Mock()
        mock_status_text = Mock()
        mock_st.progress.return_value = mock_progress_bar
        mock_st.empty.return_value = mock_status_text
        
        tracker = ProgressTracker()
        tracker.increment(25, "Test increment")
        
        assert tracker.current_step == 25
        mock_progress_bar.progress.assert_called_with(25)
        mock_status_text.text.assert_called_with("Test increment")
    
    @patch('src.ui.streamlit_interface.st')
    def test_complete(self, mock_st):
        """Test progress completion."""
        mock_progress_bar = Mock()
        mock_status_text = Mock()
        mock_st.progress.return_value = mock_progress_bar
        mock_st.empty.return_value = mock_status_text
        
        tracker = ProgressTracker()
        tracker.complete("Done!")
        
        assert tracker.current_step == 100
        mock_progress_bar.progress.assert_called_with(100)
        mock_status_text.text.assert_called_with("Done!")


class TestSidebarManager:
    """Test cases for SidebarManager class."""
    
    @patch('src.ui.streamlit_interface.st')
    @patch('src.ui.streamlit_interface.settings')
    def test_render_sidebar(self, mock_settings, mock_st):
        """Test complete sidebar rendering."""
        # Mock settings
        mock_settings.GOOGLE_API_KEY = "test_key"
        mock_settings.MAX_FILE_SIZE_MB = 10
        mock_settings.SUPPORTED_FORMATS = ["pdf", "pptx"]
        mock_settings.OUTPUT_DIR = "/test/output"
        
        # Mock sidebar context
        mock_sidebar = Mock()
        mock_st.sidebar = mock_sidebar
        
        SidebarManager.render_sidebar()
        
        # Verify sidebar components were called
        mock_sidebar.__enter__.assert_called()


def mock_open(read_data=b""):
    """Helper function to mock file opening."""
    mock_file = MagicMock()
    mock_file.read.return_value = read_data
    mock_file.__enter__.return_value = mock_file
    return mock_file


if __name__ == "__main__":
    pytest.main([__file__])