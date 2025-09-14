"""
Multi-Agent System for Startup Analysis
Task 4 & 5: Agent Architecture

This module contains the base agent classes and specialized agents
for startup document analysis.
"""

from .base_agent import BaseAnalysisAgent, BaseStructuredAgent
from .business_agent import BusinessAnalysisAgent, create_business_agent

__all__ = [
    'BaseAnalysisAgent',
    'BaseStructuredAgent',
    'BusinessAnalysisAgent',
    'create_business_agent'
]