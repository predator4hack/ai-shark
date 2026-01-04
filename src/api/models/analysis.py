"""
Pydantic models for analysis API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any


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
