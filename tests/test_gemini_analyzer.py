"""
Unit tests for the GeminiAnalyzer class.

This module contains comprehensive tests for the Gemini API integration,
including mocked API responses and error handling scenarios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io
import time

from src.analyzers.gemini_analyzer import GeminiAnalyzer
from src.models.data_models import SlideImage, SlideAnalysis


class TestGeminiAnalyzer:
    """Test cases for GeminiAnalyzer class."""
    
    @pytest.fixture
    def mock_api_key(self):
        """Provide a mock API key for testing."""
        return "test_api_key_12345"
    
    @pytest.fixture
    def sample_slide_image(self):
        """Create a sample SlideImage for testing."""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return SlideImage(
            slide_number=1,
            image_data=img_bytes.getvalue(),
            image_format='PNG',
            original_size=(100, 100)
        )
    
    @pytest.fixture
    def mock_gemini_response(self):
        """Create a mock Gemini API response."""
        mock_response = Mock()
        mock_response.text = """
HEADING: Company Overview

IMAGE_DESCRIPTIONS: Logo of TechCorp in the top left corner. Bar chart showing revenue growth over 3 years.

CHART_TABLE_DATA: Revenue growth from $1M in 2021 to $5M in 2023, showing 150% year-over-year growth.

INTERPRETATION: This slide introduces the company and demonstrates strong financial performance with consistent revenue growth, positioning the company as a high-growth opportunity for investors.
"""
        return mock_response
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_init_with_api_key(self, mock_model_class, mock_configure, mock_api_key):
        """Test GeminiAnalyzer initialization with API key."""
        analyzer = GeminiAnalyzer(api_key=mock_api_key)
        
        mock_configure.assert_called_once_with(api_key=mock_api_key)
        mock_model_class.assert_called_once()
        assert analyzer.api_key == mock_api_key
    
    @patch('src.analyzers.gemini_analyzer.settings')
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_init_with_settings_api_key(self, mock_model_class, mock_configure, mock_settings, mock_api_key):
        """Test GeminiAnalyzer initialization using settings API key."""
        mock_settings.GOOGLE_API_KEY = mock_api_key
        mock_settings.GEMINI_MODEL = "gemini-pro-vision"
        mock_settings.GEMINI_TEMPERATURE = 0.1
        mock_settings.GEMINI_MAX_TOKENS = 2048
        
        analyzer = GeminiAnalyzer()
        
        mock_configure.assert_called_once_with(api_key=mock_api_key)
        assert analyzer.api_key == mock_api_key
    
    def test_init_without_api_key(self):
        """Test GeminiAnalyzer initialization fails without API key."""
        with patch('src.analyzers.gemini_analyzer.settings') as mock_settings:
            mock_settings.GOOGLE_API_KEY = ""
            
            with pytest.raises(ValueError, match="Google API key is required"):
                GeminiAnalyzer()
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_analyze_slide_success(self, mock_model_class, mock_configure, 
                                 mock_api_key, sample_slide_image, mock_gemini_response):
        """Test successful slide analysis."""
        # Setup mocks
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_gemini_response
        mock_model_class.return_value = mock_model
        
        analyzer = GeminiAnalyzer(api_key=mock_api_key)
        
        # Analyze slide
        result = analyzer.analyze_slide(sample_slide_image)
        
        # Verify results
        assert isinstance(result, SlideAnalysis)
        assert result.slide_number == 1
        assert result.heading == "Company Overview"
        assert len(result.image_descriptions) > 0
        assert "Logo of TechCorp" in result.image_descriptions[0]
        assert len(result.chart_table_data) > 0
        assert "Revenue growth" in result.chart_table_data[0]
        assert "strong financial performance" in result.interpretation
        assert result.confidence_score > 0
        assert result.processing_time > 0
        assert len(result.errors) == 0
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_analyze_slide_api_error(self, mock_model_class, mock_configure, 
                                   mock_api_key, sample_slide_image):
        """Test slide analysis with API error."""
        # Setup mocks
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API rate limit exceeded")
        mock_model_class.return_value = mock_model
        
        analyzer = GeminiAnalyzer(api_key=mock_api_key)
        
        # Analyze slide
        result = analyzer.analyze_slide(sample_slide_image)
        
        # Verify error handling
        assert isinstance(result, SlideAnalysis)
        assert result.slide_number == 1
        assert result.heading == ""
        assert len(result.image_descriptions) == 0
        assert len(result.chart_table_data) == 0
        assert result.interpretation == ""
        assert result.confidence_score == 0.0
        assert len(result.errors) == 1
        assert "rate limit" in result.errors[0]
    
    def test_create_analysis_prompt(self, mock_api_key):
        """Test prompt creation."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            prompt = analyzer._create_analysis_prompt()
            
            assert "HEADING:" in prompt
            assert "IMAGE_DESCRIPTIONS:" in prompt
            assert "CHART_TABLE_DATA:" in prompt
            assert "INTERPRETATION:" in prompt
    
    def test_parse_response_complete(self, mock_api_key):
        """Test parsing a complete response."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            response_text = """
HEADING: Market Analysis

IMAGE_DESCRIPTIONS: Pie chart showing market segments. Company logos of competitors.

CHART_TABLE_DATA: Market size of $10B with 25% CAGR. Company holds 5% market share.

INTERPRETATION: This slide demonstrates the large addressable market and growth potential, with the company positioned to capture significant market share.
"""
            
            result = analyzer._parse_response(response_text)
            
            assert result["heading"] == "Market Analysis"
            assert len(result["image_descriptions"]) == 2
            assert "Pie chart" in result["image_descriptions"][0]
            assert len(result["chart_table_data"]) == 2
            assert "Market size" in result["chart_table_data"][0]
            assert "large addressable market" in result["interpretation"]
    
    def test_parse_response_with_none_values(self, mock_api_key):
        """Test parsing response with 'None' values."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            response_text = """
HEADING: Team Introduction

IMAGE_DESCRIPTIONS: None

CHART_TABLE_DATA: None

INTERPRETATION: This slide introduces the founding team and their relevant experience in the industry.
"""
            
            result = analyzer._parse_response(response_text)
            
            assert result["heading"] == "Team Introduction"
            assert len(result["image_descriptions"]) == 0
            assert len(result["chart_table_data"]) == 0
            assert "founding team" in result["interpretation"]
    
    def test_parse_response_malformed(self, mock_api_key):
        """Test parsing malformed response."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            response_text = "This is a malformed response without proper structure."
            
            result = analyzer._parse_response(response_text)
            
            # Should fallback to using entire response as interpretation
            assert result["interpretation"] == response_text
            assert result["heading"] == ""
    
    def test_bytes_to_pil_image_success(self, mock_api_key, sample_slide_image):
        """Test successful image conversion."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            pil_image = analyzer._bytes_to_pil_image(sample_slide_image.image_data)
            
            assert isinstance(pil_image, Image.Image)
            assert pil_image.size == (100, 100)
    
    def test_bytes_to_pil_image_failure(self, mock_api_key):
        """Test image conversion failure."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            invalid_data = b"invalid image data"
            
            with pytest.raises(Exception, match="Failed to convert image data"):
                analyzer._bytes_to_pil_image(invalid_data)
    
    def test_handle_api_error_rate_limit(self, mock_api_key):
        """Test rate limit error handling."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            error = Exception("Quota exceeded for requests")
            result = analyzer._handle_api_error(error)
            
            assert "rate limit exceeded" in result.lower()
    
    def test_handle_api_error_authentication(self, mock_api_key):
        """Test authentication error handling."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            error = Exception("Invalid API key provided")
            result = analyzer._handle_api_error(error)
            
            assert "authentication failed" in result.lower()
    
    def test_handle_api_error_network(self, mock_api_key):
        """Test network error handling."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            error = Exception("Network connection failed")
            result = analyzer._handle_api_error(error)
            
            assert "network error" in result.lower()
    
    def test_handle_api_error_safety(self, mock_api_key):
        """Test safety filter error handling."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            error = Exception("Content blocked by safety filters")
            result = analyzer._handle_api_error(error)
            
            assert "blocked by safety filters" in result.lower()
    
    def test_handle_api_error_generic(self, mock_api_key):
        """Test generic error handling."""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            analyzer = GeminiAnalyzer(api_key=mock_api_key)
            
            error = Exception("Unknown error occurred")
            result = analyzer._handle_api_error(error)
            
            assert "API error" in result
            assert "Unknown error occurred" in result
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_test_connection_success(self, mock_model_class, mock_configure, mock_api_key):
        """Test successful API connection test."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "I see a white image."
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        analyzer = GeminiAnalyzer(api_key=mock_api_key)
        result = analyzer.test_connection()
        
        assert result is True
        mock_model.generate_content.assert_called_once()
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_test_connection_failure(self, mock_model_class, mock_configure, mock_api_key):
        """Test failed API connection test."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("Connection failed")
        mock_model_class.return_value = mock_model
        
        analyzer = GeminiAnalyzer(api_key=mock_api_key)
        result = analyzer.test_connection()
        
        assert result is False


class TestGeminiAnalyzerIntegration:
    """Integration tests for GeminiAnalyzer (require actual API key)."""
    
    @pytest.mark.integration
    def test_real_api_connection(self):
        """Test connection with real API (requires valid API key in environment)."""
        try:
            analyzer = GeminiAnalyzer()
            result = analyzer.test_connection()
            assert isinstance(result, bool)
        except ValueError:
            pytest.skip("No API key available for integration test")
    
    @pytest.mark.integration
    def test_real_slide_analysis(self):
        """Test slide analysis with real API (requires valid API key in environment)."""
        try:
            analyzer = GeminiAnalyzer()
            
            # Create a simple test slide
            img = Image.new('RGB', (800, 600), color='white')
            # Add some text (this would normally be done with PIL ImageDraw)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            slide = SlideImage(
                slide_number=1,
                image_data=img_bytes.getvalue(),
                image_format='PNG',
                original_size=(800, 600)
            )
            
            result = analyzer.analyze_slide(slide)
            
            assert isinstance(result, SlideAnalysis)
            assert result.slide_number == 1
            assert isinstance(result.processing_time, float)
            assert result.processing_time > 0
            
        except ValueError:
            pytest.skip("No API key available for integration test")