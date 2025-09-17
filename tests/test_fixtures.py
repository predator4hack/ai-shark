"""
Test sample data fixtures for Task 2
"""

import pytest
from tests.fixtures.sample_data import SampleDataFixtures


class TestSampleDataFixtures:
    """Test that sample data fixtures work correctly"""

    def test_sample_document_fixture(self):
        """Test sample document fixture"""
        doc = SampleDataFixtures.get_sample_document()
        assert doc.title == "TechStart - AI-Powered Fintech Platform"
        assert doc.document_type == "pitch_deck"
        assert len(doc.content.sections) == 8
        assert "fintech" in doc.tags

    def test_sample_business_analysis_fixture(self):
        """Test sample business analysis fixture"""
        analysis = SampleDataFixtures.get_sample_business_analysis()
        assert len(analysis.revenue_streams) == 4
        assert analysis.scalability == "high"
        assert "AI personalization" in analysis.competitive_position

    def test_sample_financial_analysis_fixture(self):
        """Test sample financial analysis fixture"""
        analysis = SampleDataFixtures.get_sample_financial_analysis()
        assert analysis.projections["revenue_y1"] == 500000
        assert analysis.metrics["ltv_cac_ratio"] == 8.0
        assert analysis.burn_rate == 85000

    def test_sample_questionnaire_fixture(self):
        """Test sample questionnaire fixture"""
        questionnaire = SampleDataFixtures.get_sample_questionnaire()
        assert questionnaire.total_questions == 4
        assert len(questionnaire.categories) == 3
        assert questionnaire.target_audience == "venture_capital"

    def test_complete_dataset_fixture(self):
        """Test complete dataset fixture"""
        dataset = SampleDataFixtures.get_complete_sample_dataset()
        required_keys = [
            "document", "business_analysis", "financial_analysis",
            "market_analysis", "technology_analysis", "risk_analysis",
            "gap_analysis", "questionnaire"
        ]
        for key in required_keys:
            assert key in dataset, f"Missing key: {key}"
            assert dataset[key] is not None, f"None value for key: {key}"

    def test_gap_analysis_fixture(self):
        """Test gap analysis fixture"""
        gap_analysis = SampleDataFixtures.get_sample_gap_analysis()
        assert len(gap_analysis.critical_gaps) == 2
        assert len(gap_analysis.important_gaps) == 3
        assert gap_analysis.document_coverage == 78.5
        assert gap_analysis.overall_completeness == "good"

    def test_risk_analysis_fixture(self):
        """Test risk analysis fixture"""
        risk_analysis = SampleDataFixtures.get_sample_risk_analysis()
        assert len(risk_analysis.business_risks) == 3
        assert len(risk_analysis.market_risks) == 3
        assert risk_analysis.overall_risk_level == "medium"
        high_risks = risk_analysis.get_high_severity_risks()
        assert len(high_risks) > 0


if __name__ == "__main__":
    pytest.main([__file__])