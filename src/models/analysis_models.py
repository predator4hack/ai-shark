"""
Analysis Models for Multi-Agent Startup Analysis System
Task 2: Data Models and Document Structure

Pydantic models for different types of startup analysis results.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator


class BusinessAnalysis(BaseModel):
    """Business analysis model for startup evaluation"""

    revenue_streams: List[str] = Field(
        ...,
        description="List of identified revenue streams",
        min_length=1
    )
    scalability: str = Field(
        ...,
        description="Assessment of business scalability"
    )
    competitive_position: str = Field(
        ...,
        description="Analysis of competitive positioning"
    )
    business_model: str = Field(
        ...,
        description="Description of the business model"
    )
    target_market: List[str] = Field(
        default_factory=list,
        description="Target market segments"
    )
    value_proposition: str = Field(
        ...,
        description="Unique value proposition"
    )
    growth_strategy: Optional[str] = Field(
        None,
        description="Growth and expansion strategy"
    )
    partnerships: List[str] = Field(
        default_factory=list,
        description="Strategic partnerships or potential partners"
    )
    regulatory_considerations: List[str] = Field(
        default_factory=list,
        description="Regulatory challenges or requirements"
    )

    @field_validator('scalability')
    @classmethod
    def validate_scalability(cls, v):
        """Validate scalability assessment"""
        allowed_values = {'high', 'medium', 'low', 'unknown'}
        if v.lower() not in allowed_values:
            raise ValueError(f"Scalability must be one of: {allowed_values}")
        return v.lower()


class FinancialAnalysis(BaseModel):
    """Financial analysis model for startup evaluation"""

    projections: Dict[str, Union[int, float, Decimal]] = Field(
        ...,
        description="Financial projections (revenue, expenses, etc.)"
    )
    metrics: Dict[str, Union[int, float, Decimal]] = Field(
        ...,
        description="Key financial metrics"
    )
    funding_requirements: Dict[str, Union[int, float, Decimal]] = Field(
        ...,
        description="Funding needs and allocation"
    )
    revenue_model: str = Field(
        ...,
        description="Revenue model description"
    )
    unit_economics: Optional[Dict[str, Union[int, float, Decimal]]] = Field(
        None,
        description="Unit economics metrics (CAC, LTV, etc.)"
    )
    burn_rate: Optional[Union[int, float, Decimal]] = Field(
        None,
        description="Monthly burn rate",
        ge=0
    )
    runway: Optional[int] = Field(
        None,
        description="Runway in months",
        ge=0
    )
    profitability_timeline: Optional[str] = Field(
        None,
        description="Expected timeline to profitability"
    )
    financial_risks: List[str] = Field(
        default_factory=list,
        description="Identified financial risks"
    )

    @field_validator('projections', 'metrics', 'funding_requirements')
    @classmethod
    def validate_financial_values(cls, v):
        """Ensure all financial values are non-negative"""
        for key, value in v.items():
            if isinstance(value, (int, float, Decimal)) and value < 0:
                raise ValueError(f"Financial value for {key} cannot be negative")
        return v


class MarketAnalysis(BaseModel):
    """Market analysis model for startup evaluation"""

    market_size: Dict[str, Union[int, float, str]] = Field(
        ...,
        description="Market size information (TAM, SAM, SOM)"
    )
    competition: List[Dict[str, str]] = Field(
        ...,
        description="Competitive landscape analysis"
    )
    positioning: str = Field(
        ...,
        description="Market positioning strategy"
    )
    market_trends: List[str] = Field(
        default_factory=list,
        description="Relevant market trends"
    )
    customer_segments: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Target customer segments"
    )
    go_to_market_strategy: Optional[str] = Field(
        None,
        description="Go-to-market strategy"
    )
    geographic_focus: List[str] = Field(
        default_factory=list,
        description="Geographic markets of focus"
    )
    market_barriers: List[str] = Field(
        default_factory=list,
        description="Market entry barriers"
    )
    market_opportunities: List[str] = Field(
        default_factory=list,
        description="Identified market opportunities"
    )

    @field_validator('market_size')
    @classmethod
    def validate_market_size(cls, v):
        """Validate market size contains required fields"""
        required_fields = {'tam', 'sam', 'som'}
        provided_fields = {key.lower() for key in v.keys()}
        if not required_fields.intersection(provided_fields):
            raise ValueError("Market size should include at least one of: TAM, SAM, SOM")
        return v


class TechnologyAnalysis(BaseModel):
    """Technology analysis model for startup evaluation"""

    tech_stack: List[str] = Field(
        ...,
        description="Technology stack components",
        min_length=1
    )
    roadmap: Dict[str, List[str]] = Field(
        ...,
        description="Technology roadmap by timeframe"
    )
    ip_assets: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Intellectual property assets"
    )
    scalability_assessment: str = Field(
        ...,
        description="Technical scalability assessment"
    )
    security_measures: List[str] = Field(
        default_factory=list,
        description="Security and data protection measures"
    )
    data_strategy: Optional[str] = Field(
        None,
        description="Data collection and usage strategy"
    )
    infrastructure: Dict[str, str] = Field(
        default_factory=dict,
        description="Infrastructure and deployment details"
    )
    technical_debt: Optional[str] = Field(
        None,
        description="Assessment of technical debt"
    )
    development_team: Optional[Dict[str, Union[int, str]]] = Field(
        None,
        description="Development team size and expertise"
    )

    @field_validator('scalability_assessment')
    @classmethod
    def validate_tech_scalability(cls, v):
        """Validate technical scalability assessment"""
        allowed_values = {'excellent', 'good', 'fair', 'poor', 'unknown'}
        if v.lower() not in allowed_values:
            raise ValueError(f"Technical scalability must be one of: {allowed_values}")
        return v.lower()


class RiskAnalysis(BaseModel):
    """Risk analysis model for startup evaluation"""

    business_risks: List[Dict[str, str]] = Field(
        ...,
        description="Business-related risks",
        min_length=1
    )
    market_risks: List[Dict[str, str]] = Field(
        ...,
        description="Market-related risks",
        min_length=1
    )
    tech_risks: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Technology-related risks"
    )
    financial_risks: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Financial risks"
    )
    regulatory_risks: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Regulatory and compliance risks"
    )
    operational_risks: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Operational risks"
    )
    mitigation_strategies: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Risk mitigation strategies by risk category"
    )
    overall_risk_level: str = Field(
        ...,
        description="Overall risk assessment"
    )

    @field_validator('business_risks', 'market_risks', 'tech_risks', 'financial_risks', 'regulatory_risks', 'operational_risks')
    @classmethod
    def validate_risk_structure(cls, v):
        """Validate risk structure contains required fields"""
        for risk in v:
            if not isinstance(risk, dict):
                raise ValueError("Each risk must be a dictionary")
            required_fields = {'description', 'severity'}
            if not all(field in risk for field in required_fields):
                raise ValueError(f"Each risk must contain: {required_fields}")
        return v

    @field_validator('overall_risk_level')
    @classmethod
    def validate_risk_level(cls, v):
        """Validate overall risk level"""
        allowed_levels = {'low', 'medium', 'high', 'critical'}
        if v.lower() not in allowed_levels:
            raise ValueError(f"Risk level must be one of: {allowed_levels}")
        return v.lower()

    def get_high_severity_risks(self) -> List[Dict[str, str]]:
        """Get all high severity risks across categories"""
        high_risks = []
        all_risks = (
            self.business_risks + self.market_risks + self.tech_risks +
            self.financial_risks + self.regulatory_risks + self.operational_risks
        )
        for risk in all_risks:
            if risk.get('severity', '').lower() in ['high', 'critical']:
                high_risks.append(risk)
        return high_risks


# Example data for testing
def create_sample_analysis() -> Dict[str, BaseModel]:
    """Create sample analysis models for testing"""

    business = BusinessAnalysis(
        revenue_streams=["Subscription fees", "Transaction fees", "Premium features"],
        scalability="high",
        competitive_position="Strong differentiation in AI-powered features",
        business_model="SaaS with freemium tier",
        value_proposition="AI-powered financial insights for SMBs"
    )

    financial = FinancialAnalysis(
        projections={"revenue_y1": 500000, "revenue_y2": 1500000, "revenue_y3": 4000000},
        metrics={"gross_margin": 0.85, "cac": 150, "ltv": 2400},
        funding_requirements={"seed_round": 2000000, "series_a": 8000000},
        revenue_model="Monthly subscription with usage-based pricing"
    )

    market = MarketAnalysis(
        market_size={"tam": "50B", "sam": "5B", "som": "500M"},
        competition=[
            {"name": "Competitor A", "strength": "Market leader"},
            {"name": "Competitor B", "strength": "Strong enterprise focus"}
        ],
        positioning="Mid-market SMB focus with AI differentiation"
    )

    technology = TechnologyAnalysis(
        tech_stack=["Python", "React", "PostgreSQL", "AWS", "Docker"],
        roadmap={"Q1": ["API v2"], "Q2": ["Mobile app"], "Q3": ["ML pipeline"]},
        scalability_assessment="excellent"
    )

    risk = RiskAnalysis(
        business_risks=[
            {"description": "High customer acquisition costs", "severity": "medium"}
        ],
        market_risks=[
            {"description": "Market saturation", "severity": "low"}
        ],
        overall_risk_level="medium"
    )

    return {
        "business": business,
        "financial": financial,
        "market": market,
        "technology": technology,
        "risk": risk
    }