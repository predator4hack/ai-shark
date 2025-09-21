"""
Evaluation Agent Data Models

This module defines Pydantic data structures for the Evaluation Agent, ensuring
structured, type-safe inputs and outputs for the evaluation process.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class EvaluationCriterion(BaseModel):
    """
    Represents a single criterion used for evaluation, including its score
    and the justification for that score.
    """
    criterion: str = Field(..., description="The name of the evaluation criterion (e.g., 'Coverage', 'Specificity').")
    score: float = Field(..., ge=0, le=10, description="The score assigned to the criterion, on a scale of 0 to 10.")
    justification: str = Field(..., description="A detailed explanation for why the score was given.")

class EvaluationResult(BaseModel):
    """
    The final output of the Evaluation Agent, summarizing the complete
    evaluation of the generated questions.
    """
    summary: str = Field(..., description="A high-level summary of the overall evaluation findings.")
    criteria: List[EvaluationCriterion] = Field(..., description="A list of detailed evaluations for each specific criterion.")
    suggestions: List[str] = Field(default_factory=list, description="Actionable suggestions for improving the generated questions.")
    notes: Optional[str] = Field(None, description="Optional notes, such as mentioning if the founder checklist was missing.")

