"""
Final Memo Agent for AI-Shark Multi-Agent System

Agent specialized in generating final investment memos based on weighted 
analysis from multiple agents and founder questionnaire responses.
"""

import logging
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel

from src.agents.base_agent import BaseAnalysisAgent, AnalysisError
from src.models.final_memo_models import FinalMemoRequest, FinalMemoResult, FinalMemoConfig
from src.utils.llm_manager import LLMManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class FinalMemoAgent(BaseAnalysisAgent):
    """
    Specialized agent for generating final investment memos
    
    This agent takes weighted analysis from multiple agents and founder 
    questionnaire responses to generate a comprehensive investment memo.
    """
    
    def __init__(self, 
                 llm: Optional[BaseLanguageModel] = None,
                 config: Optional[FinalMemoConfig] = None,
                 **kwargs):
        """
        Initialize Final Memo Agent
        
        Args:
            llm: Language model instance
            config: Configuration for memo generation
            **kwargs: Additional parameters
        """
        super().__init__(
            agent_name="FinalMemoAgent",
            llm=llm,
            temperature=config.temperature if config else 0.3,
            **kwargs
        )
        
        self.config = config or FinalMemoConfig()
        self.llm_manager = LLMManager()
        
        logger.info(f"Initialized {self.agent_name} with config: {self.config}")
    
    def generate_final_memo(self, request: FinalMemoRequest) -> FinalMemoResult:
        """
        Generate final investment memo based on weighted agent analysis
        
        Args:
            request: Validated memo generation request
            
        Returns:
            FinalMemoResult with generated memo or error information
        """
        start_time = time.time()
        
        try:
            logger.info(f"Generating final memo for {request.company_name}")
            logger.info(f"Using {len(request.agents)} agents with weights: {[(a.agent_name, a.weight) for a in request.agents]}")
            
            # Prepare the prompt for LLM
            prompt = self._create_memo_prompt(request)
            
            # Generate memo using LLM
            raw_response = self._execute_llm_call(prompt)
            
            # Process and format the response
            memo_content = self._format_memo_content(raw_response, request)
            
            processing_time = time.time() - start_time
            
            # Create successful result
            result = FinalMemoResult(
                success=True,
                memo_content=memo_content,
                output_file="",  # Will be set by processor
                processing_time=processing_time,
                metadata={
                    "agent_count": len(request.agents),
                    "total_analysis_chars": sum(len(agent.analysis) for agent in request.agents),
                    "founders_checklist_chars": len(request.founders_checklist_content),
                    "company_name": request.company_name,
                    "generation_timestamp": datetime.now().isoformat(),
                    "agent_weights": {agent.agent_name: agent.weight for agent in request.agents}
                }
            )
            
            logger.info(f"Successfully generated memo for {request.company_name} in {processing_time:.2f}s")
            logger.info(f"Generated memo length: {len(memo_content)} characters")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Failed to generate final memo: {str(e)}"
            
            logger.error(f"Memo generation failed for {request.company_name}: {error_msg}")
            
            return FinalMemoResult(
                success=False,
                error_message=error_msg,
                processing_time=processing_time,
                metadata={
                    "company_name": request.company_name,
                    "error_timestamp": datetime.now().isoformat(),
                    "agent_count": len(request.agents) if request.agents else 0
                }
            )
    
    def _create_memo_prompt(self, request: FinalMemoRequest) -> str:
        """
        Create the LLM prompt for memo generation
        
        Args:
            request: Memo generation request
            
        Returns:
            Formatted prompt string
        """
        # Prepare agent analysis data
        agents_data = []
        for agent in request.agents:
            agents_data.append({
                "agent_name": agent.agent_name,
                "weight": agent.weight,
                "analysis": agent.analysis[:3000]  # Limit to avoid token limits
            })
        
        # Create the prompt using the template
        prompt_template = self.get_analysis_prompt_template()
        
        formatted_prompt = prompt_template.format(
            company_name=request.company_name,
            agents_data=json.dumps(agents_data, indent=2),
            founders_checklist=request.founders_checklist_content[:2000],  # Limit for tokens
            include_executive_summary=self.config.include_executive_summary,
            include_risk_assessment=self.config.include_risk_assessment,
            include_recommendation=self.config.include_recommendation,
            include_agent_breakdown=self.config.include_agent_breakdown,
            max_words=self.config.max_memo_length
        )
        
        return formatted_prompt
    
    def _format_memo_content(self, raw_response: str, request: FinalMemoRequest) -> str:
        """
        Format and enhance the LLM-generated memo content
        
        Args:
            raw_response: Raw response from LLM
            request: Original request for context
            
        Returns:
            Formatted memo content
        """
        # Add header information
        header = f"""# Investment Memo: {request.company_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Analysis Engine:** AI-Shark Multi-Agent Investment Analysis System  
**Analysts:** {', '.join([agent.agent_name for agent in request.agents])}  
**Agent Weights:** {', '.join([f"{agent.agent_name} ({agent.weight}%)" for agent in request.agents])}

---

"""
        
        # Clean and format the LLM response
        cleaned_response = raw_response.strip()
        
        # Remove any duplicate headers if LLM added them
        if cleaned_response.startswith('#'):
            lines = cleaned_response.split('\n')
            # Skip the first line if it's a header
            if lines[0].startswith('# '):
                cleaned_response = '\n'.join(lines[1:]).strip()
        
        # Combine header with content
        formatted_memo = header + cleaned_response
        
        # Add footer with generation details
        footer = f"""

---

## Generation Details

**Analysis Sources:**
{chr(10).join([f"- **{agent.agent_name}** ({agent.weight}% weight): {len(agent.analysis)} characters" for agent in request.agents])}

**Founder Input:** {len(request.founders_checklist_content)} characters from questionnaire responses

**Generated by:** AI-Shark Final Memo Agent  
**Generation Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*This memo was generated using AI analysis and should be reviewed by human investment professionals.*
"""
        
        return formatted_memo + footer
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent
        
        Returns:
            System prompt as string
        """
        return """You are an expert investment analyst specializing in startup evaluation and investment memo creation. 
        You have extensive experience in venture capital, due diligence, and investment decision-making.
        
        Your role is to synthesize analysis from multiple specialized agents along with founder questionnaire responses 
        to create comprehensive, balanced, and insightful investment memos.
        
        You excel at:
        - Weighing different types of analysis based on specified importance
        - Identifying key investment opportunities and risks
        - Providing clear, actionable investment recommendations
        - Writing professional, well-structured investment memos
        - Balancing optimism with realistic risk assessment"""
    
    def get_analysis_prompt_template(self) -> PromptTemplate:
        """
        Get the prompt template for analysis
        
        Returns:
            LangChain PromptTemplate instance
        """
        template = """As an expert investment analyst, create a comprehensive investment memo for {company_name} based on the weighted analysis from multiple specialized agents and founder questionnaire responses.

AGENT ANALYSIS DATA (with weights):
{agents_data}

FOUNDER QUESTIONNAIRE RESPONSES:
{founders_checklist}

MEMO REQUIREMENTS:
- Maximum {max_words} words
- Include Executive Summary: {include_executive_summary}
- Include Risk Assessment: {include_risk_assessment}
- Include Investment Recommendation: {include_recommendation}
- Include Agent Analysis Breakdown: {include_agent_breakdown}

IMPORTANT WEIGHTING INSTRUCTIONS:
The agents have different weights indicating their importance to the final recommendation. 
Weight the insights and conclusions from each agent according to their specified percentage.
For example, if Business Analysis has 60% weight, it should influence 60% of your final recommendation.

MEMO STRUCTURE:
1. Executive Summary (key findings and recommendation)
2. Company Overview (based on founder responses)
3. Weighted Analysis Summary (synthesize agent findings according to weights)
4. Investment Opportunity (highlight key strengths)
5. Risk Assessment (identify and assess risks)
6. Financial Analysis (if available from agents)
7. Market Position (market analysis synthesis)
8. Technology Assessment (if available)
9. Investment Recommendation (final verdict with reasoning)
10. Next Steps (recommended due diligence actions)

Write a professional, balanced investment memo that appropriately weights each agent's analysis according to the specified percentages. Be specific about opportunities and risks, and provide a clear investment recommendation."""

        return self.create_prompt_template(
            template=template,
            input_variables=[
                "company_name", "agents_data", "founders_checklist",
                "include_executive_summary", "include_risk_assessment", 
                "include_recommendation", "include_agent_breakdown", "max_words"
            ]
        )
    
    def analyze(self, document, **kwargs):
        """
        Implement abstract method from BaseAnalysisAgent
        This agent doesn't analyze documents directly, but generates memos from requests
        """
        raise NotImplementedError("FinalMemoAgent uses generate_final_memo() instead of analyze()")


def create_final_memo_agent(config: Optional[FinalMemoConfig] = None) -> FinalMemoAgent:
    """
    Factory function to create FinalMemoAgent instance
    
    Args:
        config: Optional configuration for the agent
        
    Returns:
        Configured FinalMemoAgent instance
    """
    try:
        from src.utils.llm_setup import get_llm
        llm = get_llm()
        return FinalMemoAgent(llm=llm, config=config)
    except Exception as e:
        logger.warning(f"Failed to create LLM instance, using default: {e}")
        return FinalMemoAgent(config=config)