"""
Output Models for Multi-Agent Startup Analysis System
Task 2: Data Models and Document Structure

Pydantic models for gap analysis and investor questionnaire generation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class Priority(str, Enum):
    """Priority levels for questions and gaps"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class QuestionType(str, Enum):
    """Types of questions in the questionnaire"""
    MULTIPLE_CHOICE = "multiple_choice"
    OPEN_ENDED = "open_ended"
    YES_NO = "yes_no"
    NUMERIC = "numeric"
    SCALE = "scale"


class GapAnalysis(BaseModel):
    """Model for analyzing gaps in startup documentation"""

    critical_gaps: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Critical information gaps that must be addressed"
    )
    important_gaps: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Important gaps that should be addressed"
    )
    minor_gaps: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Minor gaps that could be addressed"
    )
    analysis_date: datetime = Field(
        default_factory=datetime.now,
        description="When the gap analysis was performed"
    )
    document_coverage: float = Field(
        ...,
        description="Percentage of expected content coverage",
        ge=0.0,
        le=100.0
    )
    overall_completeness: str = Field(
        ...,
        description="Overall assessment of document completeness"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for addressing gaps"
    )

    @field_validator('critical_gaps', 'important_gaps', 'minor_gaps')
    @classmethod
    def validate_gap_structure(cls, v):
        """Validate gap structure contains required fields"""
        for gap in v:
            if not isinstance(gap, dict):
                raise ValueError("Each gap must be a dictionary")
            required_fields = {'category', 'description', 'impact'}
            if not all(field in gap for field in required_fields):
                raise ValueError(f"Each gap must contain: {required_fields}")
        return v

    @field_validator('overall_completeness')
    @classmethod
    def validate_completeness(cls, v):
        """Validate overall completeness assessment"""
        allowed_values = {'excellent', 'good', 'fair', 'poor', 'inadequate'}
        if v.lower() not in allowed_values:
            raise ValueError(f"Completeness must be one of: {allowed_values}")
        return v.lower()

    def get_total_gaps(self) -> int:
        """Get total number of gaps identified"""
        return len(self.critical_gaps) + len(self.important_gaps) + len(self.minor_gaps)

    def get_gaps_by_category(self) -> Dict[str, List[Dict[str, str]]]:
        """Group gaps by category"""
        categories = {}
        all_gaps = self.critical_gaps + self.important_gaps + self.minor_gaps

        for gap in all_gaps:
            category = gap.get('category', 'uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(gap)

        return categories

    def get_priority_summary(self) -> Dict[str, int]:
        """Get summary of gaps by priority"""
        return {
            'critical': len(self.critical_gaps),
            'important': len(self.important_gaps),
            'minor': len(self.minor_gaps),
            'total': self.get_total_gaps()
        }


class Question(BaseModel):
    """Individual question model"""

    id: str = Field(..., description="Unique question identifier")
    text: str = Field(..., description="Question text", min_length=10)
    question_type: QuestionType = Field(..., description="Type of question")
    options: Optional[List[str]] = Field(
        None,
        description="Answer options for multiple choice questions"
    )
    rationale: str = Field(
        ...,
        description="Why this question is important",
        min_length=20
    )
    expected_answer_guidance: Optional[str] = Field(
        None,
        description="Guidance on what constitutes a good answer"
    )
    follow_up_questions: Optional[List[str]] = Field(
        None,
        description="Potential follow-up questions"
    )
    related_documents: Optional[List[str]] = Field(
        None,
        description="Documents that should contain relevant information"
    )

    @field_validator('options')
    @classmethod
    def validate_options(cls, v, info):
        """Validate options for multiple choice questions"""
        question_type = info.data.get('question_type') if info.data else None
        if question_type == QuestionType.MULTIPLE_CHOICE and (not v or len(v) < 2):
            raise ValueError("Multiple choice questions must have at least 2 options")
        elif question_type == QuestionType.YES_NO and v and len(v) != 2:
            raise ValueError("Yes/No questions should have exactly 2 options or none")
        return v


class QuestionCategory(BaseModel):
    """Category of questions in the questionnaire"""

    category_name: str = Field(..., description="Name of the question category")
    questions: List[Question] = Field(
        ...,
        description="Questions in this category",
        min_length=1
    )
    priority: Priority = Field(..., description="Priority level of this category")
    description: Optional[str] = Field(
        None,
        description="Description of what this category covers"
    )
    estimated_time: Optional[int] = Field(
        None,
        description="Estimated time to complete in minutes",
        ge=1
    )
    category_weight: float = Field(
        default=1.0,
        description="Relative importance weight of this category",
        ge=0.1,
        le=10.0
    )

    @field_validator('category_name')
    @classmethod
    def validate_category_name(cls, v):
        """Validate category name is not empty"""
        if not v or not v.strip():
            raise ValueError("Category name cannot be empty")
        return v.strip()

    def get_question_count(self) -> int:
        """Get number of questions in this category"""
        return len(self.questions)

    def get_questions_by_type(self) -> Dict[QuestionType, List[Question]]:
        """Group questions by type"""
        by_type = {}
        for question in self.questions:
            if question.question_type not in by_type:
                by_type[question.question_type] = []
            by_type[question.question_type].append(question)
        return by_type


class InvestorQuestionnaire(BaseModel):
    """Complete investor questionnaire model"""

    categories: List[QuestionCategory] = Field(
        ...,
        description="Question categories",
        min_length=1
    )
    total_questions: int = Field(..., description="Total number of questions", ge=1)
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the questionnaire"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="When the questionnaire was generated"
    )
    version: str = Field(default="1.0", description="Questionnaire version")
    target_audience: str = Field(
        default="institutional_investors",
        description="Target audience for the questionnaire"
    )
    estimated_completion_time: Optional[int] = Field(
        None,
        description="Estimated total completion time in minutes",
        ge=1
    )
    instructions: Optional[str] = Field(
        None,
        description="Instructions for completing the questionnaire"
    )

    @field_validator('total_questions')
    @classmethod
    def validate_total_questions(cls, v, info):
        """Validate total questions matches actual count"""
        if info.data and 'categories' in info.data:
            actual_total = sum(len(cat.questions) for cat in info.data['categories'])
            if v != actual_total:
                raise ValueError(f"Total questions {v} doesn't match actual count {actual_total}")
        return v

    @field_validator('target_audience')
    @classmethod
    def validate_target_audience(cls, v):
        """Validate target audience"""
        allowed_audiences = {
            'institutional_investors', 'angel_investors', 'venture_capital',
            'private_equity', 'family_office', 'corporate_venture', 'general'
        }
        if v.lower() not in allowed_audiences:
            raise ValueError(f"Target audience must be one of: {allowed_audiences}")
        return v.lower()

    def get_questions_by_priority(self) -> Dict[Priority, List[Question]]:
        """Group all questions by priority"""
        by_priority = {priority: [] for priority in Priority}

        for category in self.categories:
            for question in category.questions:
                by_priority[category.priority].append(question)

        return by_priority

    def get_category_summary(self) -> List[Dict[str, Any]]:
        """Get summary information for each category"""
        summary = []
        for category in self.categories:
            summary.append({
                'name': category.category_name,
                'question_count': category.get_question_count(),
                'priority': category.priority.value,
                'estimated_time': category.estimated_time,
                'weight': category.category_weight
            })
        return summary

    def calculate_total_estimated_time(self) -> int:
        """Calculate total estimated completion time"""
        total_time = 0
        for category in self.categories:
            if category.estimated_time:
                total_time += category.estimated_time
        return total_time

    def export_summary(self) -> Dict[str, Any]:
        """Export questionnaire summary"""
        return {
            'total_questions': self.total_questions,
            'total_categories': len(self.categories),
            'generated_at': self.generated_at.isoformat(),
            'version': self.version,
            'target_audience': self.target_audience,
            'estimated_time': self.calculate_total_estimated_time(),
            'priority_distribution': {
                priority.value: len(questions)
                for priority, questions in self.get_questions_by_priority().items()
            },
            'category_summary': self.get_category_summary()
        }


# Example data for testing
def create_sample_questionnaire() -> InvestorQuestionnaire:
    """Create a sample investor questionnaire for testing"""

    # Sample questions
    business_questions = [
        Question(
            id="bus_001",
            text="What is your primary revenue model and how does it scale?",
            question_type=QuestionType.OPEN_ENDED,
            rationale="Understanding revenue scalability is crucial for investment potential",
            expected_answer_guidance="Look for clear monetization strategy with growth potential"
        ),
        Question(
            id="bus_002",
            text="Do you have any existing revenue or paying customers?",
            question_type=QuestionType.YES_NO,
            rationale="Validates market demand and reduces execution risk"
        )
    ]

    financial_questions = [
        Question(
            id="fin_001",
            text="What is your current monthly burn rate?",
            question_type=QuestionType.NUMERIC,
            rationale="Essential for understanding cash flow and runway",
            related_documents=["financial_projections.pdf", "cash_flow_statement.xlsx"]
        )
    ]

    # Sample categories
    business_category = QuestionCategory(
        category_name="Business Model",
        questions=business_questions,
        priority=Priority.CRITICAL,
        description="Questions about the core business model and strategy",
        estimated_time=15,
        category_weight=2.0
    )

    financial_category = QuestionCategory(
        category_name="Financial Position",
        questions=financial_questions,
        priority=Priority.HIGH,
        description="Questions about current and projected financial status",
        estimated_time=10,
        category_weight=1.5
    )

    # Create questionnaire
    questionnaire = InvestorQuestionnaire(
        categories=[business_category, financial_category],
        total_questions=3,
        metadata={
            "analysis_source": "pitch_deck_analysis",
            "startup_stage": "series_a"
        },
        target_audience="venture_capital",
        instructions="Please provide detailed answers to help us evaluate your investment potential."
    )

    return questionnaire


def create_sample_gap_analysis() -> GapAnalysis:
    """Create a sample gap analysis for testing"""
    return GapAnalysis(
        critical_gaps=[
            {
                "category": "financial",
                "description": "Missing detailed financial projections beyond year 1",
                "impact": "Cannot assess long-term viability and scaling potential"
            }
        ],
        important_gaps=[
            {
                "category": "market",
                "description": "Competitive analysis lacks specific competitor comparison",
                "impact": "Difficult to assess competitive advantages"
            }
        ],
        minor_gaps=[
            {
                "category": "team",
                "description": "Limited information about advisory board",
                "impact": "Missing insight into strategic guidance and network"
            }
        ],
        document_coverage=75.5,
        overall_completeness="good",
        recommendations=[
            "Provide 3-year financial projections with key assumptions",
            "Include detailed competitive matrix with feature comparison"
        ]
    )