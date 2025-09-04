"""
Unit tests for the OutputManager class.

Tests cover file operations, markdown formatting, filename generation,
metadata creation, and error handling scenarios.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open

from src.output.output_manager import OutputManager
from src.models.data_models import SlideAnalysis


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def output_manager(temp_output_dir):
    """Create OutputManager instance with temporary directory."""
    return OutputManager(output_directory=temp_output_dir)


@pytest.fixture
def sample_slide_analysis():
    """Create a sample SlideAnalysis object for testing."""
    return SlideAnalysis(
        slide_number=1,
        heading="Company Overview",
        image_descriptions=["Company logo", "Team photo"],
        chart_table_data=["Revenue chart showing 50% growth"],
        interpretation="This slide introduces the company and shows strong growth metrics",
        confidence_score=0.85,
        processing_time=2.5,
        errors=[]
    )


@pytest.fixture
def sample_slide_with_errors():
    """Create a SlideAnalysis object with errors for testing."""
    return SlideAnalysis(
        slide_number=2,
        heading="Market Analysis",
        image_descriptions=[],
        chart_table_data=["Market size data unclear"],
        interpretation="Market analysis with some processing issues",
        confidence_score=0.45,
        processing_time=3.2,
        errors=["Failed to extract chart data", "Low image quality"]
    )


class TestFilenameGeneration:
    """Test filename generation and sanitization."""
    
    def test_generate_filename_basic(self):
        """Test basic filename generation with timestamp."""
        manager = OutputManager()
        
        with patch('src.output.output_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-15_14-30-45"
            
            filename = manager.generate_filename("test_document.pdf")
            
            assert filename == "test_document_2024-01-15_14-30-45.md"
    
    def test_generate_filename_sanitization(self):
        """Test filename sanitization of invalid characters."""
        manager = OutputManager()
        
        with patch('src.output.output_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-15_14-30-45"
            
            # Test various invalid characters - they all get replaced with underscores
            # and consecutive underscores get collapsed, so "test<>:\"/\\|?*document" becomes "test_document"
            filename = manager.generate_filename("test<>:\"/\\|?*document.pdf")
            
            assert filename == "test_document_2024-01-15_14-30-45.md"
    
    def test_generate_filename_empty_name(self):
        """Test filename generation with empty or invalid input."""
        manager = OutputManager()
        
        with patch('src.output.output_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-15_14-30-45"
            
            filename = manager.generate_filename("   ")
            
            assert filename == "document_2024-01-15_14-30-45.md"
    
    def test_generate_filename_long_name(self):
        """Test filename generation with very long names."""
        manager = OutputManager()
        long_name = "a" * 150 + ".pdf"
        
        with patch('src.output.output_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-15_14-30-45"
            
            filename = manager.generate_filename(long_name)
            
            # Should be truncated to 100 characters plus timestamp and extension
            assert len(filename.split('_')[0]) <= 100
            assert filename.endswith("_2024-01-15_14-30-45.md")


class TestMarkdownFormatting:
    """Test Markdown formatting functionality."""
    
    def test_format_slide_markdown_complete(self, sample_slide_analysis):
        """Test formatting a complete slide analysis."""
        manager = OutputManager()
        
        markdown = manager.format_slide_markdown(sample_slide_analysis)
        
        # Check all sections are present
        assert "## Slide 1: Company Overview" in markdown
        assert "### Visual Elements" in markdown
        assert "**Image 1**: Company logo" in markdown
        assert "**Image 2**: Team photo" in markdown
        assert "### Charts and Tables" in markdown
        assert "**Data 1**: Revenue chart showing 50% growth" in markdown
        assert "### Interpretation" in markdown
        assert "This slide introduces the company" in markdown
        assert "### Metadata" in markdown
        assert "**Confidence Score**: 0.85" in markdown
        assert "**Processing Time**: 2.50s" in markdown
    
    def test_format_slide_markdown_with_errors(self, sample_slide_with_errors):
        """Test formatting a slide analysis with errors."""
        manager = OutputManager()
        
        markdown = manager.format_slide_markdown(sample_slide_with_errors)
        
        # Check error information is included
        assert "**Errors**: 2 error(s)" in markdown
        assert "Failed to extract chart data" in markdown
        assert "Low image quality" in markdown
    
    def test_format_slide_markdown_minimal(self):
        """Test formatting a minimal slide analysis."""
        minimal_slide = SlideAnalysis(
            slide_number=3,
            heading="",
            image_descriptions=[],
            chart_table_data=[],
            interpretation="",
            confidence_score=0.0,
            processing_time=0.0,
            errors=[]
        )
        
        manager = OutputManager()
        markdown = manager.format_slide_markdown(minimal_slide)
        
        # Should still have basic structure
        assert "## Slide 3" in markdown
        assert "### Metadata" in markdown
        assert "**Confidence Score**: 0.00" in markdown


class TestMetadataGeneration:
    """Test metadata generation functionality."""
    
    def test_create_summary_metadata(self, sample_slide_analysis, sample_slide_with_errors):
        """Test creating summary metadata from slide analyses."""
        manager = OutputManager()
        results = [sample_slide_analysis, sample_slide_with_errors]
        
        metadata = manager.create_summary_metadata(results, "test_document.pdf")
        
        assert metadata["document_name"] == "test_document.pdf"
        assert metadata["total_slides"] == 2
        assert metadata["successful_slides"] == 1  # Only first slide has no errors
        assert metadata["failed_slides"] == [2]  # Second slide has errors
        assert metadata["success_rate"] == 50.0
        assert metadata["total_processing_time"] == 5.7  # 2.5 + 3.2
        assert metadata["average_confidence"] == 0.65  # (0.85 + 0.45) / 2
        assert "processing_date" in metadata
    
    def test_create_summary_metadata_with_stats(self, sample_slide_analysis):
        """Test creating metadata with additional processing stats."""
        manager = OutputManager()
        results = [sample_slide_analysis]
        processing_stats = {"api_calls": 5, "total_tokens": 1500}
        
        metadata = manager.create_summary_metadata(
            results, "test.pdf", processing_stats
        )
        
        assert metadata["api_calls"] == 5
        assert metadata["total_tokens"] == 1500
    
    def test_create_summary_metadata_empty_results(self):
        """Test metadata generation with empty results."""
        manager = OutputManager()
        
        metadata = manager.create_summary_metadata([], "test.pdf")
        
        assert metadata["total_slides"] == 0
        assert metadata["successful_slides"] == 0
        assert metadata["success_rate"] == 0.0
        assert metadata["average_confidence"] == 0.0


class TestFileSaving:
    """Test file saving functionality."""
    
    def test_save_analysis_success(self, output_manager, sample_slide_analysis, temp_output_dir):
        """Test successful saving of analysis results."""
        results = [sample_slide_analysis]
        
        with patch('src.output.output_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-15_14-30-45"
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-15T14:30:45"
            
            output_path = output_manager.save_analysis(results, "test_document.pdf")
            
            # Check file was created
            assert Path(output_path).exists()
            assert output_path.endswith("test_document_2024-01-15_14-30-45.md")
            
            # Check file content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert "# Pitch Deck Analysis: test_document.pdf" in content
            assert "## Slide 1: Company Overview" in content
            assert "Company logo" in content
    
    def test_save_analysis_empty_results(self, output_manager):
        """Test saving with empty results raises ValueError."""
        with pytest.raises(ValueError, match="Cannot save empty results list"):
            output_manager.save_analysis([], "test.pdf")
    
    def test_save_analysis_file_error(self, output_manager, sample_slide_analysis):
        """Test handling of file saving errors."""
        results = [sample_slide_analysis]
        
        # Mock file operations to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with pytest.raises(OSError, match="Failed to save analysis to file"):
                output_manager.save_analysis(results, "test.pdf")
    
    def test_save_analysis_creates_directory(self, sample_slide_analysis):
        """Test that OutputManager creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_dir = Path(temp_dir) / "new_output_dir"
            
            manager = OutputManager(output_directory=str(non_existent_dir))
            
            # Directory should be created during initialization
            assert non_existent_dir.exists()
            
            # Should be able to save files
            results = [sample_slide_analysis]
            output_path = manager.save_analysis(results, "test.pdf")
            
            assert Path(output_path).exists()


class TestMarkdownContentGeneration:
    """Test complete Markdown content generation."""
    
    def test_generate_markdown_content_complete(self, sample_slide_analysis, sample_slide_with_errors):
        """Test generating complete Markdown content."""
        manager = OutputManager()
        results = [sample_slide_analysis, sample_slide_with_errors]
        
        with patch('src.output.output_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-15T14:30:45"
            
            content = manager._generate_markdown_content(results, "test.pdf")
            
            # Check document structure
            assert content.startswith("# Pitch Deck Analysis: test.pdf")
            assert "## Document Summary" in content
            assert "- **Total Slides**: 2" in content
            assert "- **Successfully Processed**: 1" in content
            assert "- **Success Rate**: 50.0%" in content
            assert "- **Failed Slides**: 2" in content
            assert "# Slide-by-Slide Analysis" in content
            
            # Check slides are in order
            slide1_pos = content.find("## Slide 1:")
            slide2_pos = content.find("## Slide 2:")
            assert slide1_pos < slide2_pos


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_sanitize_filename_edge_cases(self):
        """Test filename sanitization with various edge cases."""
        manager = OutputManager()
        
        # Test all invalid characters
        result = manager._sanitize_filename("<>:\"/\\|?*")
        assert result == "document"  # Should fallback to default
        
        # Test multiple underscores
        result = manager._sanitize_filename("test___multiple___underscores")
        assert result == "test_multiple_underscores"
        
        # Test leading/trailing underscores
        result = manager._sanitize_filename("___test___")
        assert result == "test"
    
    def test_output_manager_logging(self, output_manager, sample_slide_analysis, caplog):
        """Test that OutputManager logs appropriately."""
        import logging
        
        # Set the log level to capture INFO messages
        caplog.set_level(logging.INFO)
        
        results = [sample_slide_analysis]
        
        output_path = output_manager.save_analysis(results, "test.pdf")
        
        # Check that success was logged
        assert "Analysis saved to:" in caplog.text
        assert output_path in caplog.text


if __name__ == "__main__":
    pytest.main([__file__])