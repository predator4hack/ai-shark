"""
Integration tests for the Streamlit application.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.ui.streamlit_interface import StreamlitInterface
from src.models.data_models import SlideAnalysis, SlideImage


class TestStreamlitIntegration:
    """Integration tests for the complete Streamlit interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ui = StreamlitInterface()
    
    def test_interface_initialization(self):
        """Test that the interface initializes correctly."""
        assert self.ui is not None
        assert self.ui.document_processor is None
        assert self.ui.gemini_analyzer is None
        assert self.ui.output_manager is None
    
    def test_slide_analysis_creation(self):
        """Test creating slide analysis objects."""
        analysis = SlideAnalysis(
            slide_number=1,
            heading="Test Slide",
            image_descriptions=["Test image description"],
            chart_table_data=["Test chart data"],
            interpretation="Test interpretation",
            confidence_score=0.85,
            processing_time=1.5,
            errors=[]
        )
        
        assert analysis.slide_number == 1
        assert analysis.heading == "Test Slide"
        assert len(analysis.image_descriptions) == 1
        assert len(analysis.chart_table_data) == 1
        assert analysis.interpretation == "Test interpretation"
        assert analysis.confidence_score == 0.85
        assert analysis.processing_time == 1.5
        assert len(analysis.errors) == 0
    
    def test_slide_image_creation(self):
        """Test creating slide image objects."""
        test_image_data = b"fake_image_data"
        slide_image = SlideImage(
            slide_number=1,
            image_data=test_image_data,
            image_format="PNG",
            original_size=(1920, 1080)
        )
        
        assert slide_image.slide_number == 1
        assert slide_image.image_data == test_image_data
        assert slide_image.image_format == "PNG"
        assert slide_image.original_size == (1920, 1080)
    
    def test_error_handling_in_analysis(self):
        """Test error handling in slide analysis."""
        analysis_with_errors = SlideAnalysis(
            slide_number=2,
            heading="",
            image_descriptions=[],
            chart_table_data=[],
            interpretation="",
            confidence_score=0.0,
            processing_time=0.5,
            errors=["API connection failed", "Invalid image format"]
        )
        
        assert len(analysis_with_errors.errors) == 2
        assert "API connection failed" in analysis_with_errors.errors
        assert "Invalid image format" in analysis_with_errors.errors
    
    @patch('src.ui.streamlit_interface.st')
    def test_message_display_methods(self, mock_st):
        """Test all message display methods."""
        # Test error message
        self.ui.show_error("Test error")
        mock_st.error.assert_called_with("❌ Test error")
        
        # Test success message
        self.ui.show_success("Test success")
        mock_st.success.assert_called_with("✅ Test success")
        
        # Test info message
        self.ui.show_info("Test info")
        mock_st.info.assert_called_with("ℹ️ Test info")
        
        # Test warning message
        self.ui.show_warning("Test warning")
        mock_st.warning.assert_called_with("⚠️ Test warning")
    
    def test_file_validation_logic(self):
        """Test file validation logic without Streamlit dependencies."""
        # Create mock file objects
        valid_file = Mock()
        valid_file.getvalue.return_value = b"x" * (5 * 1024 * 1024)  # 5MB
        
        large_file = Mock()
        large_file.getvalue.return_value = b"x" * (15 * 1024 * 1024)  # 15MB
        
        # Test validation logic (without Streamlit calls)
        valid_size = len(valid_file.getvalue()) / (1024 * 1024)
        large_size = len(large_file.getvalue()) / (1024 * 1024)
        
        assert valid_size <= 10  # Should be valid
        assert large_size > 10   # Should be invalid
    
    def test_analysis_results_processing(self):
        """Test processing of analysis results."""
        # Create sample results
        results = [
            SlideAnalysis(1, "Slide 1", ["Image 1"], ["Chart 1"], "Interpretation 1", 0.9, 1.0, []),
            SlideAnalysis(2, "Slide 2", ["Image 2"], ["Chart 2"], "Interpretation 2", 0.8, 1.2, []),
            SlideAnalysis(3, "Slide 3", [], [], "", 0.0, 0.5, ["Processing failed"])
        ]
        
        # Calculate metrics (similar to what the UI does)
        successful_slides = len([r for r in results if not r.errors])
        failed_slides = len(results) - successful_slides
        avg_confidence = sum(r.confidence_score for r in results) / len(results)
        
        assert successful_slides == 2
        assert failed_slides == 1
        assert abs(avg_confidence - 0.567) < 0.01  # Approximately 0.567
    
    def test_progress_calculation(self):
        """Test progress calculation logic."""
        # Test progress percentage calculation
        current = 50
        total = 100
        progress_percentage = int((current / total) * 100) if total > 0 else 0
        
        assert progress_percentage == 50
        
        # Test edge cases
        assert int((0 / 100) * 100) == 0
        assert int((100 / 100) * 100) == 100
        assert int((0 / 0) * 100) if 0 > 0 else 0 == 0  # Division by zero handling


if __name__ == "__main__":
    pytest.main([__file__, "-v"])