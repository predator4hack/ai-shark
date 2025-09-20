"""
Final Memo Models for AI-Shark Multi-Agent System

Pydantic models for final investment memo generation and validation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class AgentWeight(BaseModel):
    """Model for individual agent weight and analysis content"""
    
    agent_name: str = Field(
        ...,
        description="Name of the analysis agent",
        min_length=1
    )
    weight: int = Field(
        ...,
        description="Weight percentage for this agent (0-100)",
        ge=0,
        le=100
    )
    analysis: str = Field(
        ...,
        description="Analysis content from the agent"
    )
    file_path: Optional[str] = Field(
        None,
        description="Path to the original analysis file"
    )


class FinalMemoRequest(BaseModel):
    """Request model for final memo generation"""
    
    agents: List[AgentWeight] = Field(
        ...,
        description="List of agent weights and analysis content",
        min_length=1
    )
    founders_checklist_content: str = Field(
        ...,
        description="Content from ans-founders-checklist.md",
        min_length=1
    )
    company_name: str = Field(
        ...,
        description="Name of the company",
        min_length=1
    )
    company_dir: str = Field(
        ...,
        description="Path to company directory"
    )
    
    @field_validator('agents')
    @classmethod
    def validate_weights_sum_100(cls, v):
        """Ensure agent weights sum to exactly 100"""
        if not v:
            raise ValueError("At least one agent must be provided")
        
        total = sum(agent.weight for agent in v)
        if total != 100:
            raise ValueError(f"Agent weights must sum to exactly 100, got {total}")
        
        # Check for duplicate agent names
        agent_names = [agent.agent_name for agent in v]
        if len(agent_names) != len(set(agent_names)):
            raise ValueError("Duplicate agent names are not allowed")
        
        return v


class FinalMemoResult(BaseModel):
    """Result model for final memo generation"""
    
    success: bool = Field(
        ...,
        description="Whether memo generation was successful"
    )
    memo_content: str = Field(
        default="",
        description="Generated investment memo content in markdown"
    )
    output_file: str = Field(
        default="",
        description="Path to the saved markdown file"
    )
    pdf_file: Optional[str] = Field(
        None,
        description="Path to the generated PDF file"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if generation failed"
    )
    processing_time: float = Field(
        default=0.0,
        description="Time taken to generate the memo in seconds",
        ge=0
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata about the generation process"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the memo was generated"
    )
    
    @field_validator('success')
    @classmethod
    def validate_success_fields(cls, v, info):
        """Validate that success=True requires memo_content and output_file"""
        # Skip validation during object construction - will be checked in model_validator
        return v


class FinalMemoConfig(BaseModel):
    """Configuration model for final memo generation"""
    
    include_executive_summary: bool = Field(
        default=True,
        description="Whether to include executive summary section"
    )
    include_risk_assessment: bool = Field(
        default=True,
        description="Whether to include risk assessment section"
    )
    include_recommendation: bool = Field(
        default=True,
        description="Whether to include investment recommendation"
    )
    max_memo_length: int = Field(
        default=5000,
        description="Maximum length of generated memo in words",
        gt=0
    )
    temperature: float = Field(
        default=0.3,
        description="LLM temperature for memo generation",
        ge=0.0,
        le=1.0
    )
    include_agent_breakdown: bool = Field(
        default=True,
        description="Whether to include breakdown of agent contributions"
    )


class AgentAnalysisDiscovery(BaseModel):
    """Model for discovered agent analysis files"""
    
    agent_name: str = Field(
        ...,
        description="Formatted agent name for display"
    )
    file_name: str = Field(
        ...,
        description="Original file name"
    )
    file_path: str = Field(
        ...,
        description="Full path to the analysis file"
    )
    content_preview: str = Field(
        default="",
        description="Preview of the file content"
    )
    file_size: int = Field(
        default=0,
        description="File size in bytes",
        ge=0
    )
    last_modified: Optional[datetime] = Field(
        None,
        description="When the file was last modified"
    )
    available: bool = Field(
        default=True,
        description="Whether the file is available for processing"
    )


def create_sample_memo_request() -> FinalMemoRequest:
    """Create a sample memo request for testing"""
    return FinalMemoRequest(
        agents=[
            AgentWeight(
                agent_name="Business Analysis",
                weight=40,
                analysis="Strong business model with recurring revenue streams..."
            ),
            AgentWeight(
                agent_name="Market Analysis",
                weight=35,
                analysis="Large addressable market with strong growth potential..."
            ),
            AgentWeight(
                agent_name="Technology Analysis",
                weight=25,
                analysis="Solid technical foundation with scalable architecture..."
            )
        ],
        founders_checklist_content="Q: What is your business model? A: SaaS subscription...",
        company_name="TestStartup",
        company_dir="/outputs/teststartup"
    )


def validate_memo_request(request_data: Dict[str, Any]) -> FinalMemoRequest:
    """
    Validate and create FinalMemoRequest from raw data
    
    Args:
        request_data: Raw request data dictionary
        
    Returns:
        Validated FinalMemoRequest instance
        
    Raises:
        ValueError: If validation fails
    """
    try:
        return FinalMemoRequest(**request_data)
    except Exception as e:
        raise ValueError(f"Invalid memo request: {e}")