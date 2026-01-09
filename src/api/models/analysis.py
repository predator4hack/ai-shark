"""
Pydantic models for analysis API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any, Dict


class RunAnalysisRequest(BaseModel):
    """Request model for running multi-agent analysis"""
    company_name: str = Field(..., description="Company name from Phase 1")
    selected_agents: List[str] = Field(
        ...,
        description="List of agent types to run (e.g., ['business', 'market'])",
        min_length=1
    )


class AgentInfo(BaseModel):
    """Information about an available agent"""
    agent_type: str = Field(..., description="Agent identifier (e.g., 'business', 'market')")
    agent_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Agent description")
    available: bool = Field(..., description="Whether agent is available/discovered")


class DiscoverAgentsResponse(BaseModel):
    """Response model for agent discovery"""
    agents: List[AgentInfo]
    total_agents: int
    available_agents: int


class RunAnalysisResponse(BaseModel):
    """Response model for starting analysis"""
    job_id: str
    message: str
    company_name: str
    selected_agents: List[str]


class SimulateQARequest(BaseModel):
    """Request model for simulating Q&A responses"""
    company_name: str = Field(..., description="Company name from Phase 1")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "TechVenture AI"
            }
        }


class GenerateMemoRequest(BaseModel):
    """Request model for generating final investment memo"""
    company_name: str = Field(..., description="Company name")
    agent_weights: Dict[str, int] = Field(
        ...,
        description="Agent weights as key-value pairs (e.g., {'business': 25, 'market': 25, ...})"
    )

    @validator('agent_weights')
    def validate_weights(cls, v):
        """Validate that weights sum to 100"""
        total = sum(v.values())
        if total != 100:
            raise ValueError(f"Agent weights must sum to 100, got {total}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "TechVenture AI",
                "agent_weights": {
                    "business": 25,
                    "market": 25,
                    "tech": 25,
                    "risk": 25
                }
            }
        }


class GenerateMemoResponse(BaseModel):
    """Response model for memo generation job"""
    job_id: str
    message: str
    company_name: str
