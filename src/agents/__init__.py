"""
Multi-Agent System for Startup Analysis
Task 4 & 5: Agent Architecture

This module contains the base agent classes and specialized agents
for startup document analysis.
"""

from .base_agent import BaseAnalysisAgent, BaseStructuredAgent
from .business_agent import BusinessAnalysisAgent, create_business_agent
from .market_agent import MarketAnalysisAgent, create_market_agent
from .evaluation_agent import EvaluationAgent

__all__ = [
    'BaseAnalysisAgent',
    'BaseStructuredAgent',
    'BusinessAnalysisAgent',
    'create_business_agent',
    'MarketAnalysisAgent',
    'create_market_agent',
    'EvaluationAgent'
]