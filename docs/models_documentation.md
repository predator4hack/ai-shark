# Data Models Documentation

## Overview

This document describes the Pydantic data models created for the Multi-Agent Startup Analysis System (Task 2). These models provide structured data handling for startup documents, analysis results, and investor questionnaire generation.

## Model Categories

### 1. Document Models (`src/models/document_models.py`)

#### DocumentMetadata
Stores metadata about startup documents.

**Fields:**
- `file_path`: Full path to the document file
- `size`: File size in bytes
- `last_modified`: Last modification timestamp
- `file_extension`: File extension (auto-formats with dot)
- `encoding`: Text encoding (default: utf-8)

#### ParsedContent
Represents parsed content from a document.

**Fields:**
- `sections`: Document sections mapped by title
- `raw_text`: Complete raw text content
- `word_count`: Total word count (validated against raw_text)
- `headers`: Extracted headers/titles
- `tables`: Extracted table data
- `links`: Extracted URLs/links

#### StartupDocument
Main model combining content and metadata.

**Fields:**
- `content`: ParsedContent instance
- `metadata`: DocumentMetadata instance
- `document_type`: Type validation (pitch_deck, business_plan, etc.)
- `title`: Document title
- `author`: Document author
- `tags`: Document tags
- `language`: 2-letter language code

**Methods:**
- `get_summary()`: Returns document summary dict
- `search_content(query)`: Searches content for query string

### 2. Analysis Models (`src/models/analysis_models.py`)

#### BusinessAnalysis
Business evaluation model.

**Key Fields:**
- `revenue_streams`: List of revenue sources (min 1 required)
- `scalability`: Assessment level (high/medium/low)
- `competitive_position`: Competitive analysis
- `value_proposition`: Unique value proposition

#### FinancialAnalysis
Financial evaluation model.

**Key Fields:**
- `projections`: Financial projections dict
- `metrics`: Key financial metrics (CAC, LTV, etc.)
- `funding_requirements`: Funding needs breakdown
- `burn_rate`: Monthly burn rate
- `runway`: Runway in months

#### MarketAnalysis
Market opportunity evaluation.

**Key Fields:**
- `market_size`: TAM/SAM/SOM market sizing
- `competition`: Competitive landscape analysis
- `positioning`: Market positioning strategy
- `customer_segments`: Target customer analysis

#### TechnologyAnalysis
Technology stack and roadmap evaluation.

**Key Fields:**
- `tech_stack`: Technology components (min 1 required)
- `roadmap`: Development roadmap by timeframe
- `scalability_assessment`: Technical scalability (excellent/good/fair/poor)
- `security_measures`: Security implementation details

#### RiskAnalysis
Comprehensive risk assessment.

**Key Fields:**
- `business_risks`: Business-related risks (min 1 required)
- `market_risks`: Market-related risks (min 1 required)
- `tech_risks`: Technology risks
- `overall_risk_level`: Overall assessment (low/medium/high/critical)

**Methods:**
- `get_high_severity_risks()`: Returns high/critical severity risks

### 3. Output Models (`src/models/output_models.py`)

#### GapAnalysis
Identifies gaps in startup documentation.

**Key Fields:**
- `critical_gaps`: Must-address gaps
- `important_gaps`: Should-address gaps
- `minor_gaps`: Could-address gaps
- `document_coverage`: Coverage percentage (0-100)
- `overall_completeness`: Assessment level

**Methods:**
- `get_total_gaps()`: Total gap count
- `get_gaps_by_category()`: Groups gaps by category
- `get_priority_summary()`: Gap count by priority

#### Question
Individual questionnaire question.

**Key Fields:**
- `id`: Unique identifier
- `text`: Question text (min 10 chars)
- `question_type`: Question type enum
- `rationale`: Why question is important (min 20 chars)
- `options`: Answer options for multiple choice

#### QuestionCategory
Groups related questions.

**Key Fields:**
- `category_name`: Category name
- `questions`: List of questions (min 1 required)
- `priority`: Priority level enum
- `estimated_time`: Completion time in minutes

**Methods:**
- `get_question_count()`: Number of questions
- `get_questions_by_type()`: Groups questions by type

#### InvestorQuestionnaire
Complete questionnaire with categories.

**Key Fields:**
- `categories`: Question categories (min 1 required)
- `total_questions`: Total question count (validated)
- `target_audience`: Target investor type
- `estimated_completion_time`: Total time estimate

**Methods:**
- `get_questions_by_priority()`: Groups by priority
- `get_category_summary()`: Category summary info
- `calculate_total_estimated_time()`: Calculates total time
- `export_summary()`: Exports questionnaire summary

## Enums

### Priority
Question/gap priority levels: CRITICAL, HIGH, MEDIUM, LOW

### QuestionType
Question types: MULTIPLE_CHOICE, OPEN_ENDED, YES_NO, NUMERIC, SCALE

## Validation Features

All models include comprehensive validation:

- **Field validation**: Type checking, length constraints, value ranges
- **Cross-field validation**: Word count vs text length, total questions count
- **Enum validation**: Restricted value sets for categorical fields
- **Custom validators**: Business logic validation using Pydantic V2 field_validator

## Sample Data and Testing

### Test Fixtures
`tests/fixtures/sample_data.py` provides comprehensive sample data:

- `SampleDataFixtures.get_sample_document()`: Complete startup document
- `SampleDataFixtures.get_sample_business_analysis()`: Business analysis
- `SampleDataFixtures.get_complete_sample_dataset()`: Full dataset

### Unit Tests
`tests/test_new_models.py` provides complete test coverage:

- Model creation and validation
- Error handling and edge cases
- Serialization/deserialization
- Method functionality testing

## Usage Examples

### Creating a Document
```python
from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent

metadata = DocumentMetadata(
    file_path="/path/to/doc.md",
    size=1024,
    last_modified=datetime.now(),
    file_extension=".md"
)

content = ParsedContent(
    sections={"intro": "Introduction text"},
    raw_text="Introduction text",
    word_count=2
)

document = StartupDocument(
    content=content,
    metadata=metadata,
    document_type="pitch_deck",
    title="My Startup"
)
```

### Creating Analysis
```python
from src.models.analysis_models import BusinessAnalysis

analysis = BusinessAnalysis(
    revenue_streams=["Subscriptions", "Ads"],
    scalability="high",
    competitive_position="Strong differentiation",
    business_model="SaaS",
    value_proposition="AI-powered insights"
)
```

### Creating Questionnaire
```python
from src.models.output_models import InvestorQuestionnaire, QuestionCategory, Question, Priority, QuestionType

question = Question(
    id="q1",
    text="What is your revenue model?",
    question_type=QuestionType.OPEN_ENDED,
    rationale="Revenue model is crucial for investment decisions"
)

category = QuestionCategory(
    category_name="Business Model",
    questions=[question],
    priority=Priority.CRITICAL
)

questionnaire = InvestorQuestionnaire(
    categories=[category],
    total_questions=1,
    target_audience="venture_capital"
)
```

## Integration with Multi-Agent System

These models serve as the foundation for:

1. **Document Processing**: Structured parsing and storage of startup documents
2. **Analysis Agents**: Standardized output format for different analysis types
3. **Gap Detection**: Systematic identification of missing information
4. **Questionnaire Generation**: Automated creation of investor due diligence questions
5. **Data Persistence**: JSON serialization for storage and API communication

The models ensure type safety, data validation, and consistent structure across the entire multi-agent analysis pipeline.