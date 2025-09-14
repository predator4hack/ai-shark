"""
Business Analysis Agent for Multi-Agent Startup Analysis System
Task 5: Business Analysis Agent

Specialized agent for comprehensive business model evaluation and analysis.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json

from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel

from src.agents.base_agent import BaseStructuredAgent, AnalysisError
from src.models.document_models import StartupDocument
from src.models.analysis_models import BusinessAnalysis
from src.utils.prompt_manager import PromptManager


logger = logging.getLogger(__name__)


class BusinessAnalysisAgent(BaseStructuredAgent):
    """
    Specialized agent for business model analysis and evaluation

    Focuses on revenue streams, scalability, competitive positioning,
    and business strategy assessment for startup documents.
    """

    def __init__(self,
                 llm: Optional[BaseLanguageModel] = None,
                 temperature: float = 0.1,
                 **kwargs):
        """
        Initialize Business Analysis Agent

        Args:
            llm: Language model instance
            temperature: Sampling temperature for business analysis
            **kwargs: Additional parameters
        """
        super().__init__(
            agent_name="BusinessAnalysisAgent",
            output_model=BusinessAnalysis,
            llm=llm,
            temperature=temperature,
            **kwargs
        )

        # Initialize prompt manager
        self.prompt_manager = PromptManager()

        # Business analysis configuration
        self.business_frameworks = {
            "revenue_models": [
                "subscription", "transaction", "freemium", "enterprise",
                "marketplace", "advertising", "licensing", "usage-based"
            ],
            "scalability_factors": [
                "network_effects", "economies_of_scale", "automation",
                "viral_growth", "platform_dynamics", "data_advantages"
            ],
            "competitive_moats": [
                "brand", "network_effects", "switching_costs", "regulatory",
                "technology", "data", "cost_advantages", "customer_lock_in"
            ]
        }

        logger.info("BusinessAnalysisAgent initialized with business frameworks")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for business analysis

        Returns:
            Business analysis system prompt
        """
        try:
            return self.prompt_manager.get_prompt_template("business_analysis_system")
        except Exception as e:
            logger.warning(f"Could not load business_analysis_system prompt: {e}")
            return """You are a senior business analyst specializing in startup evaluation.
                     Your expertise includes business model analysis, revenue stream identification,
                     competitive positioning, and scalability assessment. You excel at identifying
                     both opportunities and potential red flags in business strategies."""

    def get_analysis_prompt_template(self) -> PromptTemplate:
        """
        Get the main business analysis prompt template

        Returns:
            Configured PromptTemplate for business analysis
        """
        try:
            template_content = self.prompt_manager.get_prompt_template("business_analysis_main")
            input_variables = [
                "document_content", "document_type", "word_count",
                "file_name", "sections"
            ]
        except Exception as e:
            logger.warning(f"Could not load business_analysis_main prompt: {e}")
            # Fallback template
            template_content = self._get_fallback_template()
            input_variables = [
                "document_content", "document_type", "word_count",
                "file_name", "sections"
            ]

        return self.create_prompt_template(
            template=template_content,
            input_variables=input_variables
        )

    def _get_fallback_template(self) -> str:
        """
        Get fallback template if prompt manager fails

        Returns:
            Fallback template string
        """
        return """
        Analyze the following startup document and provide a comprehensive business analysis:

        DOCUMENT CONTENT:
        {document_content}

        DOCUMENT METADATA:
        - Type: {document_type}
        - Word Count: {word_count}
        - File Name: {file_name}
        - Sections: {sections}

        Please analyze the business comprehensively and provide your analysis in JSON format with these fields:

        {format_instructions}

        Focus on these key areas:
        1. REVENUE STREAMS: Identify all mentioned and implied revenue streams
        2. BUSINESS MODEL: Describe and evaluate the business model approach
        3. SCALABILITY: Assess how well the business can scale (high/medium/low)
        4. COMPETITIVE POSITION: Analyze competitive advantages and positioning
        5. VALUE PROPOSITION: Extract and evaluate the unique value proposition
        6. TARGET MARKET: Identify target market segments and customer base
        7. GROWTH STRATEGY: Evaluate expansion and growth plans
        8. PARTNERSHIPS: Identify strategic partnerships or opportunities
        9. REGULATORY CONSIDERATIONS: Note any regulatory challenges or requirements

        Be specific and cite evidence from the document. If information is missing
        or unclear, note this explicitly in your analysis.
        """

    def analyze_revenue_streams(self, document: StartupDocument) -> List[str]:
        """
        Specialized analysis for revenue stream identification

        Args:
            document: Startup document to analyze

        Returns:
            List of identified revenue streams
        """
        content = document.content.raw_text.lower()
        identified_streams = []

        # Pattern matching for revenue models
        revenue_patterns = {
            "subscription": ["subscription", "monthly fee", "annual plan", "recurring"],
            "transaction": ["transaction fee", "per transaction", "commission"],
            "freemium": ["freemium", "free tier", "premium features"],
            "enterprise": ["enterprise license", "B2B sales", "corporate"],
            "marketplace": ["marketplace", "platform fee", "listing fee"],
            "advertising": ["advertising", "ads", "sponsored"],
            "licensing": ["licensing", "IP licensing", "royalty"],
            "usage-based": ["usage-based", "pay-per-use", "consumption"]
        }

        for model_type, patterns in revenue_patterns.items():
            if any(pattern in content for pattern in patterns):
                identified_streams.append(model_type)

        logger.debug(f"Identified revenue streams: {identified_streams}")
        return identified_streams

    def assess_scalability(self, document: StartupDocument) -> str:
        """
        Assess business scalability based on document content

        Args:
            document: Startup document to analyze

        Returns:
            Scalability assessment (high/medium/low)
        """
        content = document.content.raw_text.lower()
        scalability_score = 0

        # Positive scalability indicators
        positive_indicators = [
            "network effects", "viral", "automation", "self-service",
            "platform", "marketplace", "API", "cloud", "digital",
            "software", "scalable", "global", "international"
        ]

        # Negative scalability indicators
        negative_indicators = [
            "manual", "human-intensive", "local only", "brick and mortar",
            "consulting", "service-heavy", "custom", "bespoke"
        ]

        for indicator in positive_indicators:
            if indicator in content:
                scalability_score += 1

        for indicator in negative_indicators:
            if indicator in content:
                scalability_score -= 1

        # Determine scalability level
        if scalability_score >= 3:
            return "high"
        elif scalability_score >= 0:
            return "medium"
        else:
            return "low"

    def identify_competitive_advantages(self, document: StartupDocument) -> List[str]:
        """
        Identify competitive advantages and moats

        Args:
            document: Startup document to analyze

        Returns:
            List of identified competitive advantages
        """
        content = document.content.raw_text.lower()
        advantages = []

        advantage_patterns = {
            "technology": ["proprietary technology", "patent", "AI", "machine learning", "algorithm"],
            "data": ["data advantage", "unique dataset", "data network", "analytics"],
            "network_effects": ["network effects", "network", "community", "viral"],
            "brand": ["brand recognition", "trusted brand", "market leader"],
            "cost": ["cost advantage", "economies of scale", "efficiency"],
            "regulatory": ["regulatory approval", "compliance", "certification"],
            "partnerships": ["exclusive partnership", "strategic alliance", "integration"]
        }

        for advantage_type, patterns in advantage_patterns.items():
            if any(pattern in content for pattern in patterns):
                advantages.append(advantage_type)

        return advantages

    def extract_business_metrics(self, document: StartupDocument) -> Dict[str, Any]:
        """
        Extract key business metrics from document

        Args:
            document: Startup document to analyze

        Returns:
            Dictionary of extracted metrics
        """
        content = document.content.raw_text
        metrics = {}

        # Pattern matching for common business metrics
        import re

        # Revenue projections - improved pattern
        revenue_pattern = r'\$(\d+(?:\.\d+)?)\s*([MmBbKk]?)\s*(?:revenue|sales|ARR|MRR)|(\d+(?:\.\d+)?)\s*([MmBbKk]?)\s*(?:revenue|ARR|MRR)'
        revenue_matches = re.findall(revenue_pattern, content, re.IGNORECASE)
        if revenue_matches:
            # Flatten and clean the matches
            cleaned_matches = []
            for match in revenue_matches:
                if match[0] and match[1]:  # $2.5M format
                    cleaned_matches.append((match[0], match[1]))
                elif match[2] and match[3]:  # 2.5M format
                    cleaned_matches.append((match[2], match[3]))
            if cleaned_matches:
                metrics["revenue_projections"] = cleaned_matches

        # Customer metrics - improved pattern
        customer_pattern = r'(\d+(?:,\d+)*)\s*(?:active\s+)?(?:customers|users|subscribers)'
        customer_matches = re.findall(customer_pattern, content, re.IGNORECASE)
        if customer_matches:
            metrics["customer_numbers"] = customer_matches

        # Growth rates - improved pattern
        growth_pattern = r'(\d+)%\s*(?:growth|increase|CAGR|annually)'
        growth_matches = re.findall(growth_pattern, content, re.IGNORECASE)
        if growth_matches:
            metrics["growth_rates"] = growth_matches

        # Market size - improved pattern
        market_pattern = r'\$(\d+(?:\.\d+)?)\s*([MmBbKk]?)\s*(?:market|TAM|SAM|SOM|globally)'
        market_matches = re.findall(market_pattern, content, re.IGNORECASE)
        if market_matches:
            metrics["market_size"] = market_matches

        return metrics

    def _enhance_analysis_with_domain_expertise(self, raw_analysis: BusinessAnalysis) -> BusinessAnalysis:
        """
        Enhance analysis with domain-specific insights

        Args:
            raw_analysis: Raw analysis from LLM

        Returns:
            Enhanced analysis with additional insights
        """
        # Validate revenue stream classifications
        validated_streams = []
        for stream in raw_analysis.revenue_streams:
            stream_lower = stream.lower()
            for model_type, keywords in [
                ("subscription", ["subscription", "monthly", "annual", "recurring"]),
                ("transaction", ["transaction", "commission", "fee per"]),
                ("enterprise", ["enterprise", "B2B", "corporate license"]),
                ("freemium", ["freemium", "free tier", "premium"])
            ]:
                if any(keyword in stream_lower for keyword in keywords):
                    if model_type not in [s.lower() for s in validated_streams]:
                        validated_streams.append(model_type.title() + " model")
                    break
            else:
                validated_streams.append(stream)

        raw_analysis.revenue_streams = validated_streams

        # Enhance competitive position with framework analysis
        if raw_analysis.competitive_position:
            position_lower = raw_analysis.competitive_position.lower()
            moat_indicators = []

            for moat, indicators in {
                "technology differentiation": ["AI", "proprietary", "patent", "algorithm"],
                "network effects": ["network", "viral", "community"],
                "data advantages": ["data", "analytics", "insights"],
                "brand strength": ["brand", "recognition", "trusted"]
            }.items():
                if any(indicator in position_lower for indicator in indicators):
                    moat_indicators.append(moat)

            if moat_indicators:
                raw_analysis.competitive_position += f" (Key moats: {', '.join(moat_indicators)})"

        return raw_analysis

    def _validate_business_analysis(self, analysis: BusinessAnalysis) -> BusinessAnalysis:
        """
        Validate and clean up business analysis results

        Args:
            analysis: Raw analysis to validate

        Returns:
            Validated and cleaned analysis
        """
        # Ensure revenue streams are not empty
        if not analysis.revenue_streams:
            analysis.revenue_streams = ["Revenue model not clearly specified"]

        # Validate scalability assessment
        if analysis.scalability.lower() not in ["high", "medium", "low"]:
            logger.warning(f"Invalid scalability value: {analysis.scalability}, defaulting to 'medium'")
            analysis.scalability = "medium"

        # Ensure required fields are not empty
        if not analysis.business_model.strip():
            analysis.business_model = "Business model not clearly defined in document"

        if not analysis.value_proposition.strip():
            analysis.value_proposition = "Value proposition not clearly articulated"

        if not analysis.competitive_position.strip():
            analysis.competitive_position = "Competitive positioning not clearly described"

        return analysis

    def get_business_insights(self, analysis: BusinessAnalysis) -> Dict[str, Any]:
        """
        Generate additional business insights from analysis

        Args:
            analysis: Completed business analysis

        Returns:
            Dictionary of business insights and recommendations
        """
        insights = {
            "revenue_model_assessment": self._assess_revenue_model(analysis),
            "scalability_factors": self._identify_scalability_factors(analysis),
            "competitive_strength": self._assess_competitive_strength(analysis),
            "growth_potential": self._assess_growth_potential(analysis),
            "risk_factors": self._identify_business_risks(analysis)
        }

        return insights

    def _assess_revenue_model(self, analysis: BusinessAnalysis) -> Dict[str, Any]:
        """Assess revenue model strength and diversity"""
        num_streams = len(analysis.revenue_streams)

        assessment = {
            "diversity_score": min(num_streams / 3.0, 1.0),  # Normalized to 0-1
            "model_types": analysis.revenue_streams,
            "recurring_revenue": any("subscription" in stream.lower() or "recurring" in stream.lower()
                                   for stream in analysis.revenue_streams)
        }

        if assessment["recurring_revenue"]:
            assessment["strength"] = "Strong - includes recurring revenue"
        elif num_streams > 2:
            assessment["strength"] = "Good - multiple revenue streams"
        elif num_streams > 1:
            assessment["strength"] = "Fair - limited diversity"
        else:
            assessment["strength"] = "Weak - single revenue stream"

        return assessment

    def _identify_scalability_factors(self, analysis: BusinessAnalysis) -> List[str]:
        """Identify factors contributing to scalability"""
        factors = []

        # Check business model for scalability indicators
        model_text = analysis.business_model.lower()
        if "platform" in model_text or "marketplace" in model_text:
            factors.append("Platform/marketplace model")
        if "saas" in model_text or "software" in model_text:
            factors.append("Software-based delivery")
        if "api" in model_text:
            factors.append("API-driven architecture")

        # Check for network effects
        if any("network" in text.lower() for text in [analysis.value_proposition, analysis.competitive_position]):
            factors.append("Network effects potential")

        return factors

    def _assess_competitive_strength(self, analysis: BusinessAnalysis) -> str:
        """Assess competitive positioning strength"""
        position_text = analysis.competitive_position.lower()

        strong_indicators = ["unique", "proprietary", "first-mover", "patent", "exclusive"]
        moderate_indicators = ["differentiated", "competitive advantage", "better"]
        weak_indicators = ["similar", "comparable", "standard"]

        if any(indicator in position_text for indicator in strong_indicators):
            return "Strong"
        elif any(indicator in position_text for indicator in moderate_indicators):
            return "Moderate"
        elif any(indicator in position_text for indicator in weak_indicators):
            return "Weak"
        else:
            return "Unclear"

    def _assess_growth_potential(self, analysis: BusinessAnalysis) -> str:
        """Assess growth potential based on analysis"""
        high_growth_factors = [
            analysis.scalability == "high",
            len(analysis.target_market) > 2,
            "international" in analysis.growth_strategy.lower() if analysis.growth_strategy else False,
            "viral" in analysis.value_proposition.lower()
        ]

        growth_score = sum(high_growth_factors)

        if growth_score >= 3:
            return "High"
        elif growth_score >= 2:
            return "Moderate"
        else:
            return "Limited"

    def _identify_business_risks(self, analysis: BusinessAnalysis) -> List[str]:
        """Identify potential business risks from analysis"""
        risks = []

        # Single revenue stream risk
        if len(analysis.revenue_streams) == 1:
            risks.append("Revenue concentration risk - single revenue stream")

        # Low scalability risk
        if analysis.scalability == "low":
            risks.append("Scalability limitations may constrain growth")

        # Market size risk
        if len(analysis.target_market) == 1:
            risks.append("Limited target market diversity")

        # Regulatory risk
        if analysis.regulatory_considerations:
            risks.append("Regulatory compliance requirements and risks")

        # Partnership dependency
        if len(analysis.partnerships) > 3:
            risks.append("High dependency on external partnerships")

        return risks


# Convenience function for business analysis
def create_business_agent(**kwargs) -> BusinessAnalysisAgent:
    """
    Create a BusinessAnalysisAgent with default configuration

    Args:
        **kwargs: Additional configuration parameters

    Returns:
        Configured BusinessAnalysisAgent instance
    """
    return BusinessAnalysisAgent(**kwargs)


if __name__ == "__main__":
    # Basic test of business agent
    from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent
    from pathlib import Path
    from datetime import datetime

    # Create test document
    test_doc = StartupDocument(
        content=ParsedContent(
            sections=["Business Model", "Revenue", "Market"],
            raw_text="""
            Our SaaS platform provides AI-powered financial analytics for small businesses.
            We operate on a subscription model with monthly and annual plans.
            Our target market includes SMBs, accounting firms, and freelancers.
            The platform leverages proprietary machine learning algorithms.
            We have strategic partnerships with major accounting software providers.
            """,
            word_count=45
        ),
        metadata=DocumentMetadata(
            file_path=Path("test_business.md"),
            size=300,
            last_modified=datetime.now()
        ),
        document_type="business_plan"
    )

    try:
        # Test business agent creation
        agent = create_business_agent()
        print(f"✓ Created BusinessAnalysisAgent: {agent.agent_name}")

        # Test specialized methods
        revenue_streams = agent.analyze_revenue_streams(test_doc)
        print(f"✓ Revenue streams identified: {revenue_streams}")

        scalability = agent.assess_scalability(test_doc)
        print(f"✓ Scalability assessment: {scalability}")

        advantages = agent.identify_competitive_advantages(test_doc)
        print(f"✓ Competitive advantages: {advantages}")

        metrics = agent.extract_business_metrics(test_doc)
        print(f"✓ Business metrics: {metrics}")

        print("✓ BusinessAnalysisAgent test completed successfully")

    except Exception as e:
        print(f"✗ BusinessAnalysisAgent test failed: {e}")
        import traceback
        traceback.print_exc()