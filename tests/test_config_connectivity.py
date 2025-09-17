"""
Test configuration and Google AI connectivity for Task 1
"""

import pytest
import os
from pathlib import Path
import google.generativeai as genai
from task_config import Config, config


class TestConfigurationSetup:
    """Test configuration management and setup"""

    def test_config_validation(self):
        """Test that configuration validation works"""
        # This will pass if GOOGLE_API_KEY is set in environment
        if os.getenv("GOOGLE_API_KEY"):
            assert Config.validate_config() is True
        else:
            with pytest.raises(ValueError, match="GOOGLE_API_KEY environment variable is required"):
                Config.validate_config()

    def test_directory_structure(self):
        """Test that all required directories exist"""
        required_dirs = [
            Config.SRC_DIR,
            Config.AGENTS_DIR,
            Config.MODELS_DIR,
            Config.UTILS_DIR,
            Config.TESTS_DIR,
            Config.RESULTS_DIR,
            Config.OUTPUT_DIR
        ]

        for directory in required_dirs:
            assert directory.exists(), f"Directory {directory} should exist"
            assert directory.is_dir(), f"{directory} should be a directory"

    def test_config_values(self):
        """Test that configuration values are properly loaded"""
        assert isinstance(Config.MODEL_NAME, str)
        assert Config.MODEL_NAME == "gemini-flash-2.5"
        assert isinstance(Config.MAX_TOKENS, int)
        assert Config.MAX_TOKENS == 8192
        assert isinstance(Config.TEMPERATURE, float)
        assert Config.TEMPERATURE == 0.1

    def test_logging_setup(self):
        """Test that logging can be configured"""
        Config.setup_logging()
        # If this doesn't raise an exception, logging is properly configured
        assert True


class TestGoogleAIConnectivity:
    """Test Google AI API connectivity"""

    @pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set")
    def test_google_ai_api_connection(self):
        """Test that we can connect to Google AI API"""
        try:
            # Configure the API
            genai.configure(api_key=Config.GOOGLE_API_KEY)

            # Try to list models to verify connection
            models = list(genai.list_models())
            assert len(models) > 0, "Should be able to list Google AI models"

            # Verify our target model is available
            model_names = [model.name for model in models]
            # Check if any gemini model is available (since exact model names may vary)
            gemini_models = [name for name in model_names if 'gemini' in name.lower()]
            assert len(gemini_models) > 0, "At least one Gemini model should be available"

        except Exception as e:
            pytest.fail(f"Failed to connect to Google AI API: {str(e)}")

    @pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set")
    def test_basic_generation(self):
        """Test basic text generation with Google AI"""
        try:
            genai.configure(api_key=Config.GOOGLE_API_KEY)

            # Create a model instance
            model = genai.GenerativeModel('gemini-pro')

            # Test basic generation
            response = model.generate_content("Hello, this is a test.")
            assert response.text is not None, "Should receive a text response"
            assert len(response.text) > 0, "Response should not be empty"

        except Exception as e:
            pytest.fail(f"Failed to generate content with Google AI: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__])