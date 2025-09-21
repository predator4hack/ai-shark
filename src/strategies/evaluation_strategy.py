"""
Evaluation Strategies for the Evaluation Agent

This module defines the Strategy design pattern for evaluating generated
questionnaires. It provides an abstract base class and concrete implementations
for different evaluation methods, such as using a founder checklist or relying
on expert knowledge.
"""

from abc import ABC, abstractmethod
from langchain_core.prompts import PromptTemplate
from src.utils.prompt_manager import PromptManager

class EvaluationStrategy(ABC):
    """
    Abstract base class for an evaluation strategy. Defines the common
    interface for all concrete evaluation strategies.
    """
    def __init__(self, prompt_manager: PromptManager):
        self.prompt_manager = prompt_manager

    @abstractmethod
    def get_analysis_prompt_template(self, **kwargs) -> PromptTemplate:
        """
        Returns the LangChain PromptTemplate for the specific strategy.

        Args:
            **kwargs: Additional parameters needed to format the prompt.

        Returns:
            A configured PromptTemplate instance.
        """
        pass


class ChecklistEvaluationStrategy(EvaluationStrategy):
    """
    An evaluation strategy that scores generated questions against a provided
    founder checklist. This is the preferred strategy when a checklist is available.
    """
    def get_analysis_prompt_template(self, **kwargs) -> PromptTemplate:
        """
        Uses the 'evaluation_agent_with_checklist' prompt, which requires
        'founder_checklist' and 'generated_questions' as input.
        """
        return self.prompt_manager.get_prompt_template(
            'evaluation_agent_with_checklist'
        )


class ExpertEvaluationStrategy(EvaluationStrategy):
    """
    An evaluation strategy that uses general expert knowledge to score generated
    questions. This is used as a fallback when the founder checklist is not available.
    """
    def get_analysis_prompt_template(self, **kwargs) -> PromptTemplate:
        """
        Uses the 'evaluation_agent_expert' prompt, which only requires
        'generated_questions' as input.
        """
        return self.prompt_manager.get_prompt_template(
            'evaluation_agent_expert'
        )

