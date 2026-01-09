"""
Multi-Agent System for Startup Analysis
Task 4 & 5: Agent Architecture

This module contains the base agent classes and specialized agents
for startup document analysis.
"""

from .base_agent import BaseAnalysisAgent, BaseStructuredAgent
from .business_agent import BusinessAnalysisAgent, create_business_agent
from .market_agent import MarketAnalysisAgent, create_market_agent
from .tech_agent import TechnicalAnalysisAgent, create_tech_agent
from .risk_agent import RiskAssessmentAgent, create_risk_agent

__all__ = [
    'BaseAnalysisAgent',
    'BaseStructuredAgent',
    'BusinessAnalysisAgent',
    'create_business_agent',
    'MarketAnalysisAgent',
    'create_market_agent',
    'TechnicalAnalysisAgent',
    'create_tech_agent',
    'RiskAssessmentAgent',
    'create_risk_agent'
]