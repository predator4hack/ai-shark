"""
Founder Simulation Models

Data structures and models for the founder simulation agent
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class FounderSimulationConfig:
    """Configuration for founder simulation processing"""
    company_dir: str
    simulation_type: str  # "reference_docs" or "direct_qa"
    use_real_llm: bool = True
    max_retries: int = 3
    output_format: str = "markdown"


@dataclass
class SimulationResult:
    """Result of founder simulation processing"""
    success: bool
    output_file: Optional[str] = None
    processing_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.generated_at is None:
            self.generated_at = datetime.now()


@dataclass
class QAEntry:
    """Individual question-answer entry"""
    question: str
    answer: str
    confidence: float = 1.0
    source_documents: List[str] = None
    
    def __post_init__(self):
        if self.source_documents is None:
            self.source_documents = []


@dataclass
class ReferenceDocument:
    """Reference document information"""
    filename: str
    filepath: str
    content: str
    word_count: int = 0
    
    def __post_init__(self):
        if self.word_count == 0:
            self.word_count = len(self.content.split())


@dataclass
class ProcessingStatus:
    """Processing status for UI updates"""
    stage: str
    progress: float
    message: str
    error: Optional[str] = None