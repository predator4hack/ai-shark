import logging
from typing import Dict, Any

from langchain_core.prompts import PromptTemplate

from src.agents.base_agent import BaseAnalysisAgent, AnalysisError
from src.models.analysis_models import EvaluationAnalysis
from src.utils.prompt_manager import PromptManager

logger = logging.getLogger(__name__)
prompt_manager = PromptManager()


class EvaluationAgent(BaseAnalysisAgent):
    """
    Agent that evaluates generated questions against a founder checklist.
    """

    def __init__(self, **kwargs):
        super().__init__(
            agent_name="Evaluation Agent",
            output_model=EvaluationAnalysis,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return "You are an expert in venture capital and due diligence."

    def get_analysis_prompt_template(self) -> PromptTemplate:
        return self.create_prompt_template(
            template=prompt_manager.get_prompt("evaluation_agent"),
            input_variables=["founder_checklist", "generated_questions"],
        )

    def analyze(self, founder_checklist: str, generated_questions: str, **kwargs) -> EvaluationAnalysis:
        """
        Perform evaluation analysis.

        Args:
            founder_checklist: The content of the founder checklist.
            generated_questions: The content of the generated questions.
            **kwargs: Additional parameters.

        Returns:
            EvaluationAnalysis: The evaluation result.
        """
        if not founder_checklist or not generated_questions:
            raise AnalysisError("Founder checklist and generated questions cannot be empty.")

        prompt = self.get_analysis_prompt_template()
        formatted_prompt = prompt.format(
            founder_checklist=founder_checklist,
            generated_questions=generated_questions,
        )

        raw_response = self._execute_llm_call(formatted_prompt)
        parsed_result = self._parse_output(raw_response)

        return parsed_result
