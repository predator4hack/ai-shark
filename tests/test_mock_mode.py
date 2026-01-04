"""
Test mock mode functionality

This module tests that mock mode activates correctly and returns
realistic mock data instead of making actual LLM API calls.
"""

import os
import sys
import pytest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMockModeActivation:
    """Test that mock mode activates with environment variable"""

    def test_mock_mode_environment_llm_manager(self):
        """Test that LLMManager activates mock mode with environment variable"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_manager import LLMManager

        manager = LLMManager()
        assert manager.use_mock == True

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_mode_environment_llm_setup(self):
        """Test that LLMSetup activates mock mode with environment variable"""
        os.environ["USE_MOCK_LLM"] = "true"

        # Need to reload settings to pick up env var
        from importlib import reload
        from config import settings as settings_module
        reload(settings_module)

        from src.utils.llm_setup import LLMSetup

        setup = LLMSetup()
        assert setup.use_mock == True

        # Clean up
        del os.environ["USE_MOCK_LLM"]
        reload(settings_module)


class TestMockMetadataExtraction:
    """Test metadata extraction in mock mode"""

    def test_mock_metadata_returns_fixed_data(self):
        """Test that metadata extraction returns mock data in mock mode"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_manager import LLMManager

        manager = LLMManager()
        metadata = manager.extract_metadata([])  # Empty images list

        assert metadata is not None
        assert metadata["startup_name"] == "TechVenture AI"
        assert "Artificial Intelligence" in metadata["sector"]
        assert "table_of_contents" in metadata
        assert isinstance(metadata["table_of_contents"], dict)

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_metadata_structure(self):
        """Test that mock metadata has correct structure"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_manager import LLMManager

        manager = LLMManager()
        metadata = manager.extract_metadata([])

        # Check required fields
        required_fields = ["startup_name", "sector", "sub_sector", "website", "table_of_contents"]
        for field in required_fields:
            assert field in metadata, f"Missing required field: {field}"

        # Check TOC structure
        toc = metadata["table_of_contents"]
        assert "Problem Statement" in toc
        assert "Solution" in toc
        assert "Business Model" in toc

        # Clean up
        del os.environ["USE_MOCK_LLM"]


class TestMockTopicExtraction:
    """Test topic data extraction in mock mode"""

    def test_mock_topic_extraction(self):
        """Test that topic extraction returns mock content"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_manager import LLMManager

        manager = LLMManager()
        content = manager.extract_topic_data("Problem Statement", [])

        assert len(content) > 0
        assert "Problem Statement" in content
        assert "business" in content.lower() or "data" in content.lower()

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_topic_extraction_multiple_topics(self):
        """Test extraction for multiple topics"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_manager import LLMManager

        manager = LLMManager()

        topics = ["Problem Statement", "Solution", "Business Model", "Technology"]
        for topic in topics:
            content = manager.extract_topic_data(topic, [])
            assert len(content) > 0
            assert topic in content or topic.lower() in content.lower()

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_topic_extraction_unknown_topic(self):
        """Test extraction for undefined topic returns generic mock"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_manager import LLMManager

        manager = LLMManager()
        content = manager.extract_topic_data("Unknown Topic XYZ", [])

        assert len(content) > 0
        assert "Unknown Topic XYZ" in content or "Mock content" in content

        # Clean up
        del os.environ["USE_MOCK_LLM"]


class TestMockAgentResponses:
    """Test agent-specific mock responses"""

    def test_mock_llm_business_agent_detection(self):
        """Test that MockLLM detects business agent prompts"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_setup import MockLLM

        mock_llm = MockLLM()

        # Test business-related prompt
        business_prompt = "Analyze the business model and revenue streams for this startup"
        response = mock_llm.invoke(business_prompt)

        assert "Business Analysis" in response.content or "business" in response.content.lower()

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_llm_market_agent_detection(self):
        """Test that MockLLM detects market agent prompts"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_setup import MockLLM

        mock_llm = MockLLM()

        # Test market-related prompt
        market_prompt = "Analyze the market size and competition for this startup"
        response = mock_llm.invoke(market_prompt)

        assert "Market Analysis" in response.content or "market" in response.content.lower()

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_llm_tech_agent_detection(self):
        """Test that MockLLM detects technical agent prompts"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_setup import MockLLM

        mock_llm = MockLLM()

        # Test tech-related prompt
        tech_prompt = "Analyze the technology stack and technical feasibility"
        response = mock_llm.invoke(tech_prompt)

        assert "Technical Analysis" in response.content or "technology" in response.content.lower()

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_llm_risk_agent_detection(self):
        """Test that MockLLM detects risk agent prompts"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_setup import MockLLM

        mock_llm = MockLLM()

        # Test risk-related prompt
        risk_prompt = "Identify and assess the key risks for this startup"
        response = mock_llm.invoke(risk_prompt)

        assert "Risk Assessment" in response.content or "risk" in response.content.lower()

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_llm_caching(self):
        """Test that MockLLM caches agent-specific responses"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_setup import MockLLM

        mock_llm = MockLLM()

        # First call should cache the response
        prompt1 = "Analyze the business model"
        response1 = mock_llm.invoke(prompt1)

        # Second call with similar prompt should use cached response
        prompt2 = "Tell me about the business model and revenue streams"
        response2 = mock_llm.invoke(prompt2)

        # Both should be business analysis responses
        assert response1.content == response2.content

        # Clean up
        del os.environ["USE_MOCK_LLM"]


class TestMockPDFProcessing:
    """Test PDF processing in mock mode"""

    def test_mock_pdf_to_images_returns_empty(self):
        """Test that PDF conversion returns empty list in mock mode"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.llm_manager import LLMManager

        manager = LLMManager()
        images = manager.pdf_to_images("dummy_path.pdf")  # Path doesn't need to exist

        assert isinstance(images, list)
        assert len(images) == 0

        # Clean up
        del os.environ["USE_MOCK_LLM"]


class TestMockPitchDeckProcessor:
    """Test PitchDeckProcessor in mock mode"""

    def test_processor_activates_mock_mode(self):
        """Test that PitchDeckProcessor detects mock mode"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.processors.pitch_deck_processor import PitchDeckProcessor

        processor = PitchDeckProcessor()
        assert processor.use_mock == True

        # Clean up
        del os.environ["USE_MOCK_LLM"]


class TestMockAnalysisPipeline:
    """Test AnalysisPipeline respects mock mode"""

    def test_pipeline_respects_env_var(self):
        """Test that pipeline respects USE_MOCK_LLM environment variable"""
        os.environ["USE_MOCK_LLM"] = "true"

        # Create a dummy company directory
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.processors.analysis_pipeline import AnalysisPipeline

            # Even if we pass use_real_llm=True, env var should override
            pipeline = AnalysisPipeline(tmpdir, use_real_llm=True)
            assert pipeline.use_real_llm == False  # Overridden by env var

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_pipeline_uses_real_when_env_false(self):
        """Test that pipeline uses real LLM when env var is false"""
        os.environ["USE_MOCK_LLM"] = "false"

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.processors.analysis_pipeline import AnalysisPipeline

            pipeline = AnalysisPipeline(tmpdir, use_real_llm=True)
            assert pipeline.use_real_llm == True

        # Clean up
        del os.environ["USE_MOCK_LLM"]


class TestMockResponseQuality:
    """Test quality and realism of mock responses"""

    def test_mock_metadata_is_realistic(self):
        """Test that mock metadata looks realistic"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.mock_responses import MOCK_METADATA

        # Should have reasonable values
        assert len(MOCK_METADATA["startup_name"]) > 0
        assert len(MOCK_METADATA["sector"]) > 5
        assert "http" in MOCK_METADATA["website"].lower()
        assert len(MOCK_METADATA["table_of_contents"]) > 5

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_business_analysis_is_substantial(self):
        """Test that mock business analysis has substantial content"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.mock_responses import MOCK_BUSINESS_ANALYSIS

        # Should be a substantial report
        assert len(MOCK_BUSINESS_ANALYSIS) > 1000  # At least 1000 characters
        assert "Business Analysis" in MOCK_BUSINESS_ANALYSIS
        assert "risk" in MOCK_BUSINESS_ANALYSIS.lower()
        assert "revenue" in MOCK_BUSINESS_ANALYSIS.lower()

        # Clean up
        del os.environ["USE_MOCK_LLM"]

    def test_mock_market_analysis_is_substantial(self):
        """Test that mock market analysis has substantial content"""
        os.environ["USE_MOCK_LLM"] = "true"

        from src.utils.mock_responses import MOCK_MARKET_ANALYSIS

        # Should be a substantial report
        assert len(MOCK_MARKET_ANALYSIS) > 1000
        assert "Market Analysis" in MOCK_MARKET_ANALYSIS
        assert "competition" in MOCK_MARKET_ANALYSIS.lower() or "competitive" in MOCK_MARKET_ANALYSIS.lower()
        assert "market size" in MOCK_MARKET_ANALYSIS.lower() or "TAM" in MOCK_MARKET_ANALYSIS

        # Clean up
        del os.environ["USE_MOCK_LLM"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
