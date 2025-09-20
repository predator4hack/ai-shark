"""
Base Agent Architecture for Multi-Agent Startup Analysis System
Task 4: Google AI LLM Integration and Base Agent

Abstract base class for all analysis agents with common functionality.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union
import json

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from pydantic import BaseModel, ValidationError

from src.utils.llm_setup import get_llm, llm_setup
from src.models.document_models import StartupDocument

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base exception for agent-related errors"""
    pass


class AnalysisError(AgentError):
    """Exception for analysis-related errors"""
    pass


class OutputParsingError(AgentError):
    """Exception for output parsing errors"""
    pass


class BaseAnalysisAgent(ABC):
    """
    Abstract base class for all analysis agents

    Provides common functionality for LLM interaction, prompt management,
    output parsing, and error handling.
    """

    def __init__(self,
                 agent_name: str,
                 llm: Optional[BaseLanguageModel] = None,
                 output_model: Optional[Type[BaseModel]] = None,
                 temperature: float = None,
                 max_retries: int = 3):
        """
        Initialize base agent

        Args:
            agent_name: Name of the agent for logging
            llm: Language model instance (uses default if None)
            output_model: Pydantic model for structured output
            temperature: Override default temperature
            max_retries: Maximum retry attempts for failed requests
        """
        self.agent_name = agent_name
        self.llm = llm or get_llm()
        self.output_model = output_model
        self.max_retries = max_retries
        self.temperature = temperature

        # Performance tracking
        self.analysis_count = 0
        self.total_processing_time = 0.0
        self.error_count = 0

        # Setup output parser if model provided
        self.output_parser = None
        if output_model:
            self.output_parser = PydanticOutputParser(pydantic_object=output_model)

        logger.info(f"Initialized {agent_name} agent")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent

        Returns:
            System prompt as string
        """
        pass

    @abstractmethod
    def get_analysis_prompt_template(self) -> PromptTemplate:
        """
        Get the prompt template for analysis

        Returns:
            LangChain PromptTemplate instance
        """
        pass

    @abstractmethod
    def analyze(self, document: StartupDocument, **kwargs) -> Union[BaseModel, Dict[str, Any]]:
        """
        Perform analysis on the startup document

        Args:
            document: StartupDocument to analyze
            **kwargs: Additional analysis parameters

        Returns:
            Analysis result as Pydantic model or dictionary
        """
        pass

    def create_prompt_template(self,
                               template: str,
                               input_variables: List[str],
                               partial_variables: Optional[Dict[str, str]] = None) -> PromptTemplate:
        """
        Create a PromptTemplate with validation

        Args:
            template: Template string
            input_variables: List of input variable names
            partial_variables: Optional partial variables

        Returns:
            Configured PromptTemplate
        """
        try:
            prompt_template = PromptTemplate(
                template=template,
                input_variables=input_variables,
                partial_variables=partial_variables or {}
            )

            # Add format instructions if we have an output parser
            if self.output_parser:
                prompt_template = prompt_template.partial(
                    format_instructions=self.output_parser.get_format_instructions()
                )

            return prompt_template

        except Exception as e:
            logger.error(f"Failed to create prompt template: {e}")
            raise AgentError(f"Prompt template creation failed: {e}")

    def _validate_document(self, document: StartupDocument) -> bool:
        """
        Validate input document

        Args:
            document: Document to validate

        Returns:
            True if valid, raises exception if invalid
        """
        if not isinstance(document, StartupDocument):
            raise AnalysisError(f"Expected StartupDocument, got {type(document)}")

        if not document.content:
            raise AnalysisError("Document content is empty")

        if not document.content.raw_text.strip():
            raise AnalysisError("Document raw text is empty")

        logger.debug(f"Document validation passed: {len(document.content.raw_text)} characters")
        return True

    def _prepare_analysis_input(self, document: StartupDocument, **kwargs) -> Dict[str, Any]:
        """
        Prepare input variables for analysis

        Args:
            document: Document to analyze
            **kwargs: Additional parameters

        Returns:
            Dictionary of input variables
        """
        # Handle sections as dictionary or list
        sections_text = "No sections detected"
        if document.content.sections:
            if isinstance(document.content.sections, dict):
                sections_text = "\n".join(f"{k}: {v}" for k, v in document.content.sections.items())
            else:
                sections_text = "\n".join(document.content.sections)

        input_vars = {
            "document_content": document.content.raw_text,
            "document_type": document.document_type,
            "word_count": document.content.word_count,
            "sections": sections_text
        }

        # Add document metadata if available
        if document.metadata:
            # Handle file_path as string or Path object
            file_name = "Unknown"
            if document.metadata.file_path:
                if hasattr(document.metadata.file_path, 'name'):
                    # It's a Path object
                    file_name = document.metadata.file_path.name
                else:
                    # It's a string, extract filename
                    from pathlib import Path
                    file_name = Path(document.metadata.file_path).name

            input_vars.update({
                "file_name": file_name,
                "file_size": document.metadata.size if document.metadata.size else 0,
                "last_modified": document.metadata.last_modified.isoformat() if document.metadata.last_modified else "Unknown"
            })

        # Add any additional kwargs
        input_vars.update(kwargs)

        return input_vars

    def _execute_llm_call(self, prompt: str, **kwargs) -> str:
        """
        Execute LLM call with error handling and retries

        Args:
            prompt: Formatted prompt string
            **kwargs: Additional LLM parameters

        Returns:
            LLM response as string
        """
        try:
            # Override temperature if specified
            if self.temperature is not None:
                kwargs['temperature'] = self.temperature

            # Check if we have a mock LLM (for testing)
            if hasattr(self.llm, 'invoke') and hasattr(self.llm, 'call_count'):
                # This is our MockLLM
                response_obj = self.llm.invoke(prompt, **kwargs)
                response = response_obj.content
            else:
                # Use the real LLM setup
                response = llm_setup.invoke_with_retry(self.llm, prompt, **kwargs)

            if not response or not response.strip():
                raise AnalysisError("LLM returned empty response")

            logger.debug(f"LLM call successful for {self.agent_name}")
            return response.strip()

        except Exception as e:
            self.error_count += 1
            logger.error(f"LLM call failed for {self.agent_name}: {e}")
            raise AnalysisError(f"LLM execution failed: {e}")

    def _parse_output(self, raw_output: str) -> Union[BaseModel, Dict[str, Any]]:
        """
        Parse LLM output using configured parser

        Args:
            raw_output: Raw LLM response

        Returns:
            Parsed output as Pydantic model or dictionary
        """
        if not self.output_parser:
            # Try to parse as JSON if no specific parser
            try:
                return json.loads(raw_output)
            except json.JSONDecodeError:
                logger.warning("No output parser configured and JSON parsing failed, returning raw output")
                return {"raw_output": raw_output}

        try:
            parsed = self.output_parser.parse(raw_output)
            logger.debug(f"Output parsing successful for {self.agent_name}")
            return parsed

        except ValidationError as e:
            logger.error(f"Output validation failed for {self.agent_name}: {e}")
            # Try to extract JSON from the response if validation fails
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    parsed_json = json.loads(json_str)
                    # Try to create model from JSON
                    if self.output_model:
                        return self.output_model(**parsed_json)
                    return parsed_json
            except Exception:
                pass

            raise OutputParsingError(f"Failed to parse output: {e}")

        except Exception as e:
            logger.error(f"Unexpected parsing error for {self.agent_name}: {e}")
            raise OutputParsingError(f"Output parsing failed: {e}")

    def format_output(self, analysis_result: Union[BaseModel, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format analysis result for consistent output

        Args:
            analysis_result: Raw analysis result

        Returns:
            Formatted result dictionary
        """
        formatted = {
            "agent_name": self.agent_name,
            "timestamp": time.time(),
            "analysis_count": self.analysis_count,
            "success": True
        }

        if isinstance(analysis_result, BaseModel):
            formatted["analysis"] = analysis_result.model_dump()
            formatted["model_type"] = analysis_result.__class__.__name__
        else:
            formatted["analysis"] = analysis_result
            formatted["model_type"] = "dict"

        return formatted

    def handle_errors(self, error: Exception, document: StartupDocument) -> Dict[str, Any]:
        """
        Handle and format errors consistently

        Args:
            error: Exception that occurred
            document: Document being processed

        Returns:
            Error information dictionary
        """
        self.error_count += 1

        error_info = {
            "agent_name": self.agent_name,
            "timestamp": time.time(),
            "success": False,
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "document_info": {
                "type": document.document_type,
                "content_length": len(document.content.raw_text) if document.content else 0
            }
        }

        logger.error(f"Error in {self.agent_name}: {error_info}")
        return error_info

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for this agent

        Returns:
            Performance statistics dictionary
        """
        avg_time = self.total_processing_time / max(self.analysis_count, 1)

        return {
            "agent_name": self.agent_name,
            "total_analyses": self.analysis_count,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": avg_time,
            "error_count": self.error_count,
            "success_rate": (self.analysis_count - self.error_count) / max(self.analysis_count, 1)
        }

    def _track_performance(self, processing_time: float):
        """
        Track performance metrics

        Args:
            processing_time: Time taken for the analysis
        """
        self.analysis_count += 1
        self.total_processing_time += processing_time

    def reset_stats(self):
        """Reset performance statistics"""
        self.analysis_count = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        logger.info(f"Reset statistics for {self.agent_name}")


class BaseStructuredAgent(BaseAnalysisAgent):
    """
    Base class for agents that produce structured output using Pydantic models
    """

    def __init__(self,
                 agent_name: str,
                 output_model: Type[BaseModel],
                 llm: Optional[BaseLanguageModel] = None,
                 **kwargs):
        """
        Initialize structured agent

        Args:
            agent_name: Name of the agent
            output_model: Required Pydantic model for output
            llm: Language model instance
            **kwargs: Additional parameters
        """
        super().__init__(agent_name, llm, output_model, **kwargs)

    def analyze(self, document: StartupDocument, **kwargs) -> BaseModel:
        """
        Perform structured analysis

        Args:
            document: Document to analyze
            **kwargs: Additional parameters

        Returns:
            Analysis result as Pydantic model
        """
        start_time = time.time()

        try:
            # Validate input
            self._validate_document(document)

            # Prepare input variables
            input_vars = self._prepare_analysis_input(document, **kwargs)
            # print(f"Input variables for {self.agent_name}: {input_vars}")
            # Get prompt template
            prompt_template = self.get_analysis_prompt_template()
            # print(f"Prompt template for {self.agent_name}: {prompt_template.template}")
            # Format prompt
            formatted_prompt = prompt_template.format(**input_vars)
            print(f"Formatted prompt for {self.agent_name}: {formatted_prompt}")
            # Execute LLM call
            raw_response = self._execute_llm_call(formatted_prompt)

            # Parse output
            parsed_result = self._parse_output(raw_response)

            # Track performance
            processing_time = time.time() - start_time
            self._track_performance(processing_time)

            logger.info(f"{self.agent_name} analysis completed in {processing_time:.2f}s")
            return parsed_result

        except Exception as e:
            processing_time = time.time() - start_time
            self._track_performance(processing_time)
            logger.error(f"{self.agent_name} analysis failed after {processing_time:.2f}s: {e}")
            raise


if __name__ == "__main__":
    # Basic test of base agent functionality
    from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent
    from src.models.analysis_models import BusinessAnalysis
    from pathlib import Path

    # Create test agent
    class TestAgent(BaseStructuredAgent):
        def __init__(self):
            super().__init__("test_agent", BusinessAnalysis)

        def get_system_prompt(self) -> str:
            return "You are a test agent for validation."

        def get_analysis_prompt_template(self) -> PromptTemplate:
            return self.create_prompt_template(
                template="Analyze this: {document_content}",
                input_variables=["document_content"]
            )

    # Test with mock data
    try:
        agent = TestAgent()
        print(f"✓ Created test agent: {agent.agent_name}")
        print(f"Performance stats: {agent.get_performance_stats()}")
    except Exception as e:
        print(f"✗ Test agent creation failed: {e}")