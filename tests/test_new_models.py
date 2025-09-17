"""
Unit tests for new Pydantic models created in Task 2
Tests for document_models, analysis_models, and output_models
"""

import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

from src.models.document_models import (
    DocumentMetadata, ParsedContent, StartupDocument, create_sample_document
)
from src.models.analysis_models import (
    BusinessAnalysis, FinancialAnalysis, MarketAnalysis,
    TechnologyAnalysis, RiskAnalysis, create_sample_analysis
)
from src.models.output_models import (
    GapAnalysis, Question, QuestionCategory, InvestorQuestionnaire,
    Priority, QuestionType, create_sample_questionnaire, create_sample_gap_analysis
)


class TestDocumentModels:
    """Test document models validation and functionality"""

    def test_document_metadata_creation(self):
        """Test DocumentMetadata model creation"""
        metadata = DocumentMetadata(
            file_path="/test/path.md",
            size=1024,
            last_modified=datetime.now(),
            file_extension=".md"
        )
        assert metadata.file_path == "/test/path.md"
        assert metadata.size == 1024
        assert metadata.file_extension == ".md"

    def test_document_metadata_validation(self):
        """Test DocumentMetadata validation"""
        # Test empty file path
        with pytest.raises(ValidationError):
            DocumentMetadata(
                file_path="",
                size=1024,
                last_modified=datetime.now(),
                file_extension=".md"
            )

        # Test negative size
        with pytest.raises(ValidationError):
            DocumentMetadata(
                file_path="/test/path.md",
                size=-1,
                last_modified=datetime.now(),
                file_extension=".md"
            )

    def test_parsed_content_creation(self):
        """Test ParsedContent model creation"""
        content = ParsedContent(
            sections={"intro": "Introduction text"},
            raw_text="Introduction text and more content here",
            word_count=6,
            headers=["Introduction"]
        )
        assert content.has_section("intro")
        assert content.get_section_content("intro") == "Introduction text"
        assert not content.has_section("nonexistent")

    def test_startup_document_creation(self):
        """Test StartupDocument model creation"""
        doc = create_sample_document()
        assert doc.document_type == "pitch_deck"
        assert doc.title == "Sample Startup Pitch"
        assert "Executive Summary" in doc.content.sections

    def test_startup_document_validation(self):
        """Test StartupDocument validation"""
        sample_doc = create_sample_document()

        # Test invalid document type - create new instance to trigger validation
        with pytest.raises(ValidationError):
            StartupDocument(
                content=sample_doc.content,
                metadata=sample_doc.metadata,
                document_type="invalid_type",
                title=sample_doc.title,
                author=sample_doc.author,
                tags=sample_doc.tags
            )

        # Test invalid language code
        with pytest.raises(ValidationError):
            StartupDocument(
                content=sample_doc.content,
                metadata=sample_doc.metadata,
                document_type=sample_doc.document_type,
                title=sample_doc.title,
                author=sample_doc.author,
                language="invalid",
                tags=sample_doc.tags
            )

    def test_document_search_functionality(self):
        """Test document search functionality"""
        doc = create_sample_document()
        results = doc.search_content("revolutionary")
        assert len(results) > 0
        assert any("main content" in result for result in results)

    def test_document_summary(self):
        """Test document summary generation"""
        doc = create_sample_document()
        summary = doc.get_summary()
        assert "title" in summary
        assert "word_count" in summary
        assert summary["type"] == "pitch_deck"


class TestAnalysisModels:
    """Test analysis models validation and functionality"""

    def test_business_analysis_creation(self):
        """Test BusinessAnalysis model creation"""
        analysis = BusinessAnalysis(
            revenue_streams=["Subscriptions", "Ads"],
            scalability="high",
            competitive_position="Strong",
            business_model="SaaS",
            value_proposition="AI-powered insights"
        )
        assert len(analysis.revenue_streams) == 2
        assert analysis.scalability == "high"

    def test_business_analysis_validation(self):
        """Test BusinessAnalysis validation"""
        # Test invalid scalability
        with pytest.raises(ValidationError):
            BusinessAnalysis(
                revenue_streams=["Subscriptions"],
                scalability="invalid",
                competitive_position="Strong",
                business_model="SaaS",
                value_proposition="AI-powered insights"
            )

        # Test empty revenue streams
        with pytest.raises(ValidationError):
            BusinessAnalysis(
                revenue_streams=[],
                scalability="high",
                competitive_position="Strong",
                business_model="SaaS",
                value_proposition="AI-powered insights"
            )

    def test_financial_analysis_creation(self):
        """Test FinancialAnalysis model creation"""
        analysis = FinancialAnalysis(
            projections={"revenue": 1000000, "expenses": 800000},
            metrics={"gross_margin": 0.2},
            funding_requirements={"seed": 500000},
            revenue_model="Subscription"
        )
        assert analysis.projections["revenue"] == 1000000
        assert analysis.metrics["gross_margin"] == 0.2

    def test_financial_analysis_validation(self):
        """Test FinancialAnalysis validation"""
        # Test negative financial values
        with pytest.raises(ValidationError):
            FinancialAnalysis(
                projections={"revenue": -1000},
                metrics={"gross_margin": 0.2},
                funding_requirements={"seed": 500000},
                revenue_model="Subscription"
            )

    def test_market_analysis_creation(self):
        """Test MarketAnalysis model creation"""
        analysis = MarketAnalysis(
            market_size={"tam": "10B", "sam": "1B"},
            competition=[{"name": "Competitor A", "strength": "Market leader"}],
            positioning="Premium segment"
        )
        assert "tam" in analysis.market_size
        assert len(analysis.competition) == 1

    def test_technology_analysis_creation(self):
        """Test TechnologyAnalysis model creation"""
        analysis = TechnologyAnalysis(
            tech_stack=["Python", "React"],
            roadmap={"Q1": ["Feature A"], "Q2": ["Feature B"]},
            scalability_assessment="excellent"
        )
        assert len(analysis.tech_stack) == 2
        assert analysis.scalability_assessment == "excellent"

    def test_technology_analysis_validation(self):
        """Test TechnologyAnalysis validation"""
        # Test invalid scalability assessment
        with pytest.raises(ValidationError):
            TechnologyAnalysis(
                tech_stack=["Python"],
                roadmap={"Q1": ["Feature A"]},
                scalability_assessment="invalid"
            )

    def test_risk_analysis_creation(self):
        """Test RiskAnalysis model creation"""
        analysis = RiskAnalysis(
            business_risks=[{"description": "Competition", "severity": "medium"}],
            market_risks=[{"description": "Market downturn", "severity": "high"}],
            overall_risk_level="medium"
        )
        assert len(analysis.business_risks) == 1
        assert analysis.overall_risk_level == "medium"

    def test_risk_analysis_validation(self):
        """Test RiskAnalysis validation"""
        # Test invalid risk structure
        with pytest.raises(ValidationError):
            RiskAnalysis(
                business_risks=[{"description": "Competition"}],  # Missing severity
                market_risks=[{"description": "Market downturn", "severity": "high"}],
                overall_risk_level="medium"
            )

        # Test invalid risk level
        with pytest.raises(ValidationError):
            RiskAnalysis(
                business_risks=[{"description": "Competition", "severity": "medium"}],
                market_risks=[{"description": "Market downturn", "severity": "high"}],
                overall_risk_level="invalid"
            )

    def test_risk_analysis_functionality(self):
        """Test RiskAnalysis functionality"""
        analysis = RiskAnalysis(
            business_risks=[{"description": "Competition", "severity": "high"}],
            market_risks=[{"description": "Market downturn", "severity": "medium"}],
            tech_risks=[{"description": "Scalability", "severity": "critical"}],
            overall_risk_level="high"
        )
        high_risks = analysis.get_high_severity_risks()
        assert len(high_risks) == 2  # high and critical severity

    def test_sample_analysis_creation(self):
        """Test creation of sample analysis models"""
        samples = create_sample_analysis()
        assert "business" in samples
        assert "financial" in samples
        assert "market" in samples
        assert "technology" in samples
        assert "risk" in samples


class TestOutputModels:
    """Test output models validation and functionality"""

    def test_gap_analysis_creation(self):
        """Test GapAnalysis model creation"""
        analysis = create_sample_gap_analysis()
        assert len(analysis.critical_gaps) == 1
        assert len(analysis.important_gaps) == 1
        assert analysis.document_coverage == 75.5
        assert analysis.overall_completeness == "good"

    def test_gap_analysis_validation(self):
        """Test GapAnalysis validation"""
        # Test invalid document coverage
        with pytest.raises(ValidationError):
            GapAnalysis(
                critical_gaps=[],
                important_gaps=[],
                minor_gaps=[],
                document_coverage=150.0,  # Invalid: > 100
                overall_completeness="good"
            )

        # Test invalid completeness assessment
        with pytest.raises(ValidationError):
            GapAnalysis(
                critical_gaps=[],
                important_gaps=[],
                minor_gaps=[],
                document_coverage=75.0,
                overall_completeness="invalid"
            )

    def test_gap_analysis_functionality(self):
        """Test GapAnalysis functionality"""
        analysis = create_sample_gap_analysis()
        total_gaps = analysis.get_total_gaps()
        assert total_gaps == 3

        priority_summary = analysis.get_priority_summary()
        assert priority_summary["critical"] == 1
        assert priority_summary["important"] == 1
        assert priority_summary["minor"] == 1
        assert priority_summary["total"] == 3

        gaps_by_category = analysis.get_gaps_by_category()
        assert "financial" in gaps_by_category
        assert "market" in gaps_by_category

    def test_question_creation(self):
        """Test Question model creation"""
        question = Question(
            id="test_001",
            text="What is your revenue model?",
            question_type=QuestionType.OPEN_ENDED,
            rationale="Revenue model is crucial for investment decisions"
        )
        assert question.id == "test_001"
        assert question.question_type == QuestionType.OPEN_ENDED

    def test_question_validation(self):
        """Test Question validation"""
        # Test short question text
        with pytest.raises(ValidationError):
            Question(
                id="test_001",
                text="Short?",  # Too short
                question_type=QuestionType.OPEN_ENDED,
                rationale="This rationale is long enough to pass validation"
            )

        # Test short rationale
        with pytest.raises(ValidationError):
            Question(
                id="test_002",
                text="What is your business model type and how does it work?",
                question_type=QuestionType.OPEN_ENDED,
                rationale="Short"  # Too short
            )

    def test_question_category_creation(self):
        """Test QuestionCategory model creation"""
        questions = [
            Question(
                id="bus_001",
                text="What is your primary revenue stream?",
                question_type=QuestionType.OPEN_ENDED,
                rationale="Understanding revenue is fundamental"
            )
        ]

        category = QuestionCategory(
            category_name="Business Model",
            questions=questions,
            priority=Priority.CRITICAL,
            estimated_time=10
        )
        assert category.get_question_count() == 1
        assert category.priority == Priority.CRITICAL

    def test_question_category_functionality(self):
        """Test QuestionCategory functionality"""
        questions = [
            Question(
                id="bus_001",
                text="What is your primary revenue stream?",
                question_type=QuestionType.OPEN_ENDED,
                rationale="Understanding revenue is fundamental"
            ),
            Question(
                id="bus_002",
                text="Do you have paying customers?",
                question_type=QuestionType.YES_NO,
                rationale="Validates market demand"
            )
        ]

        category = QuestionCategory(
            category_name="Business Model",
            questions=questions,
            priority=Priority.CRITICAL
        )

        by_type = category.get_questions_by_type()
        assert QuestionType.OPEN_ENDED in by_type
        assert QuestionType.YES_NO in by_type
        assert len(by_type[QuestionType.OPEN_ENDED]) == 1

    def test_investor_questionnaire_creation(self):
        """Test InvestorQuestionnaire model creation"""
        questionnaire = create_sample_questionnaire()
        assert questionnaire.total_questions == 3
        assert len(questionnaire.categories) == 2
        assert questionnaire.target_audience == "venture_capital"

    def test_investor_questionnaire_validation(self):
        """Test InvestorQuestionnaire validation"""
        sample = create_sample_questionnaire()

        # Test mismatched total questions - create new instance to trigger validation
        with pytest.raises(ValidationError):
            InvestorQuestionnaire(
                categories=sample.categories,
                total_questions=10,  # Doesn't match actual count
                metadata=sample.metadata,
                target_audience=sample.target_audience
            )

        # Test invalid target audience
        with pytest.raises(ValidationError):
            InvestorQuestionnaire(
                categories=sample.categories,
                total_questions=sample.total_questions,
                metadata=sample.metadata,
                target_audience="invalid_audience"
            )

    def test_investor_questionnaire_functionality(self):
        """Test InvestorQuestionnaire functionality"""
        questionnaire = create_sample_questionnaire()

        # Test questions by priority
        by_priority = questionnaire.get_questions_by_priority()
        assert Priority.CRITICAL in by_priority
        assert Priority.HIGH in by_priority

        # Test category summary
        summary = questionnaire.get_category_summary()
        assert len(summary) == 2
        assert all("name" in cat for cat in summary)

        # Test time calculation
        total_time = questionnaire.calculate_total_estimated_time()
        assert total_time == 25  # 15 + 10 from sample data

        # Test export summary
        export = questionnaire.export_summary()
        assert "total_questions" in export
        assert "priority_distribution" in export


class TestModelSerialization:
    """Test model serialization and deserialization"""

    def test_document_model_serialization(self):
        """Test document model JSON serialization"""
        doc = create_sample_document()
        json_data = doc.model_dump()
        assert "content" in json_data
        assert "metadata" in json_data

        # Test round-trip
        recreated = StartupDocument.model_validate(json_data)
        assert recreated.title == doc.title
        assert recreated.document_type == doc.document_type

    def test_analysis_model_serialization(self):
        """Test analysis model JSON serialization"""
        samples = create_sample_analysis()
        for model_name, model_instance in samples.items():
            json_data = model_instance.model_dump()
            assert isinstance(json_data, dict)

    def test_output_model_serialization(self):
        """Test output model JSON serialization"""
        questionnaire = create_sample_questionnaire()
        json_data = questionnaire.model_dump()
        assert "categories" in json_data
        assert "total_questions" in json_data

        # Test round-trip
        recreated = InvestorQuestionnaire.model_validate(json_data)
        assert recreated.total_questions == questionnaire.total_questions


if __name__ == "__main__":
    pytest.main([__file__])