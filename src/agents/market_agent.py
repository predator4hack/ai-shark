"""
Market Analysis Agent for Multi-Agent Startup Analysis System

Specialized agent for comprehensive market opportunity, competition, and positioning analysis.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json

from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel

from src.agents.base_agent import BaseStructuredAgent, AnalysisError
from src.models.document_models import StartupDocument
from src.models.analysis_models import MarketAnalysis
from src.utils.prompt_manager import PromptManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class MarketAnalysisAgent(BaseStructuredAgent):
    """
    Specialized agent for market analysis and evaluation

    Focuses on market size, competitive landscape, positioning,
    timing, and entry barriers for startup evaluation.
    """

    def __init__(self,
                 llm: Optional[BaseLanguageModel] = None,
                 temperature: float = 0.1,
                 **kwargs):
        """
        Initialize Market Analysis Agent

        Args:
            llm: Language model instance
            temperature: Sampling temperature for market analysis
            **kwargs: Additional parameters
        """
        super().__init__(
            agent_name="MarketAnalysisAgent",
            output_model=MarketAnalysis,
            llm=llm,
            temperature=temperature,
            **kwargs
        )

        # Initialize prompt manager
        self.prompt_manager = PromptManager()

        # Market analysis configuration
        self.market_frameworks = {
            "market_size_metrics": ["tam", "sam", "som", "market_size", "addressable_market"],
            "competitive_factors": [
                "market_leader", "competitor", "competition", "market_share",
                "competitive_advantage", "differentiation", "barriers"
            ],
            "market_trends": [
                "growth", "expansion", "emerging", "trend", "shift",
                "adoption", "market_dynamics", "disruption"
            ],
            "entry_barriers": [
                "regulation", "capital_intensive", "network_effects",
                "switching_costs", "brand_loyalty", "economies_of_scale"
            ]
        }

        logger.info("MarketAnalysisAgent initialized with market frameworks")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for market analysis

        Returns:
            Market analysis system prompt
        """
        try:
            return self.prompt_manager.get_prompt_template("market_analysis_system")
        except Exception as e:
            logger.warning(f"Could not load market_analysis_system prompt: {e}")
            return """You are a senior market analyst specializing in startup market evaluation.
                     Your expertise includes market sizing, competitive landscape analysis,
                     market positioning, timing assessment, and entry barrier identification.
                     You excel at identifying market opportunities and potential challenges."""

    def get_analysis_prompt_template(self) -> PromptTemplate:
        """
        Get the main market analysis prompt template

        Returns:
            Configured PromptTemplate for market analysis
        """
        try:
            template_content = self.prompt_manager.get_prompt_template("market_analysis_main")
            input_variables = [
                "document_content", "document_type", "word_count",
                "file_name", "sections"
            ]
        except Exception as e:
            logger.warning(f"Could not load market_analysis_main prompt: {e}")
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
        Analyze the following startup document and provide a comprehensive market analysis:

        DOCUMENT CONTENT:
        {document_content}

        DOCUMENT METADATA:
        - Type: {document_type}
        - Word Count: {word_count}
        - File Name: {file_name}
        - Sections: {sections}

        Please analyze the market comprehensively and provide your analysis in JSON format with these fields:

        {format_instructions}

        Focus on these key areas:
        1. MARKET SIZE: Identify TAM, SAM, SOM and overall market sizing
        2. COMPETITION: Analyze competitive landscape and key competitors
        3. POSITIONING: Evaluate market positioning strategy and differentiation
        4. MARKET TRENDS: Identify relevant market trends and dynamics
        5. CUSTOMER SEGMENTS: Define target customer segments and characteristics
        6. GO-TO-MARKET: Evaluate go-to-market strategy and approach
        7. GEOGRAPHIC FOCUS: Identify geographic markets and expansion plans
        8. MARKET BARRIERS: Assess market entry barriers and challenges
        9. MARKET OPPORTUNITIES: Identify key market opportunities and timing

        Be specific and cite evidence from the document. If information is missing
        or unclear, note this explicitly in your analysis. Include specific data
        points where available (market size figures, competitor names, etc.).
        """

    def _get_combined_markdown_template(self) -> str:
        """
        Get template for combined document analysis with markdown output

        Returns:
            Markdown template string for combined market analysis
        """
        return """You are a senior market analyst. Analyze this startup using BOTH documents provided:

PITCH DECK: {pitch_deck_content}

PUBLIC DATA: {public_data_content}

Create a comprehensive market analysis in markdown format with these sections:

# Market & Competition Analysis Report

## Executive Summary
Brief market overview combining insights from both sources.

## Market Size & Opportunity
Detail total addressable market (TAM), serviceable addressable market (SAM),
serviceable obtainable market (SOM), and growth projections.

## Competitive Landscape
Comprehensive competitor analysis, market positioning, and competitive advantages.

## Market Segmentation
Customer segments, market penetration strategy, and addressable segments.

## Market Trends & Dynamics
Industry trends, market timing, adoption patterns, and growth drivers.

## Geographic Analysis
Target markets, regional opportunities, and expansion strategy.

## Market Entry Strategy
Go-to-market approach, customer acquisition strategy, and market penetration plan.

## Entry Barriers & Challenges
Market barriers, regulatory challenges, and competitive threats.

## Market Timing & Validation
Market readiness, product-market fit indicators, and timing analysis.

## Customer Validation
Evidence of customer demand, market testing, and validation metrics.

## Competitive Positioning
Differentiation strategy, competitive moats, and positioning advantages.

## Market Risk Assessment
Market risks, competitive threats, and potential challenges.

## Strategic Market Recommendations
Actionable market insights and strategic recommendations.

## Information Gaps & Questions for Founders
Missing market data that would enhance investment decision-making.
Questions to ask the startup founders for better market assessment.

Instructions: Focus on market opportunity assessment from an investor perspective.
Identify data gaps and red flags. Provide sector-specific insights.
Cite evidence from documents. Highlight any concerns or clarifications needed
for investment decisions."""

    def analyze_market_size(self, document: StartupDocument) -> Dict[str, Any]:
        """
        Specialized analysis for market size identification

        Args:
            document: Startup document to analyze

        Returns:
            Dictionary of market size metrics
        """
        content = document.content.raw_text.lower()
        market_data = {}

        # Pattern matching for market size
        import re

        # Market size patterns
        tam_pattern = r'tam[:\s]*\$?(\d+(?:\.\d+)?)\s*([bmk]?)'
        sam_pattern = r'sam[:\s]*\$?(\d+(?:\.\d+)?)\s*([bmk]?)'
        som_pattern = r'som[:\s]*\$?(\d+(?:\.\d+)?)\s*([bmk]?)'
        market_pattern = r'market[:\s]*\$?(\d+(?:\.\d+)?)\s*([bmk]?)'

        for pattern_name, pattern in [
            ("tam", tam_pattern), ("sam", sam_pattern),
            ("som", som_pattern), ("market", market_pattern)
        ]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                market_data[pattern_name] = matches

        logger.debug(f"Identified market size data: {market_data}")
        return market_data

    def identify_competitors(self, document: StartupDocument) -> List[Dict[str, str]]:
        """
        Identify competitors and competitive information

        Args:
            document: Startup document to analyze

        Returns:
            List of competitor information
        """
        content = document.content.raw_text
        competitors = []

        # Common competitor indicators
        competitor_patterns = [
            r'competitor[s]?[:\s]*([A-Z][a-zA-Z\s&.,-]+?)(?:\n|\.|\,|;)',
            r'competing with[:\s]*([A-Z][a-zA-Z\s&.,-]+?)(?:\n|\.|\,|;)',
            r'vs[:\s]*([A-Z][a-zA-Z\s&.,-]+?)(?:\n|\.|\,|;)',
            r'alternative[s]?[:\s]*([A-Z][a-zA-Z\s&.,-]+?)(?:\n|\.|\,|;)',
            r'similar to[:\s]*([A-Z][a-zA-Z\s&.,-]+?)(?:\n|\.|\,|;)'
        ]

        import re
        for pattern in competitor_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                competitor_name = match.strip()
                if len(competitor_name) > 3 and len(competitor_name) < 50:
                    competitors.append({
                        "name": competitor_name,
                        "type": "identified_competitor"
                    })

        # Remove duplicates while preserving order
        seen = set()
        unique_competitors = []
        for comp in competitors:
            if comp["name"] not in seen:
                seen.add(comp["name"])
                unique_competitors.append(comp)

        return unique_competitors[:10]  # Limit to top 10

    def assess_market_trends(self, document: StartupDocument) -> List[str]:
        """
        Identify market trends and dynamics

        Args:
            document: Startup document to analyze

        Returns:
            List of identified market trends
        """
        content = document.content.raw_text.lower()
        trends = []

        trend_indicators = {
            "growth": ["growing", "expanding", "increasing", "growth rate", "cagr"],
            "digital_transformation": ["digital", "digitization", "automation", "ai", "cloud"],
            "market_shift": ["shift", "transition", "evolution", "changing", "disruption"],
            "adoption": ["adoption", "uptake", "penetration", "mainstream", "widespread"],
            "emerging": ["emerging", "new", "innovative", "novel", "breakthrough"],
            "consolidation": ["consolidation", "merger", "acquisition", "consolidating"],
            "regulation": ["regulation", "compliance", "regulatory", "policy", "government"]
        }

        for trend_type, keywords in trend_indicators.items():
            if any(keyword in content for keyword in keywords):
                trends.append(trend_type.replace("_", " ").title())

        return trends

    def identify_market_barriers(self, document: StartupDocument) -> List[str]:
        """
        Identify market entry barriers

        Args:
            document: Startup document to analyze

        Returns:
            List of identified market barriers
        """
        content = document.content.raw_text.lower()
        barriers = []

        barrier_patterns = {
            "regulatory": ["regulation", "compliance", "approval", "certification", "license"],
            "capital_intensive": ["capital", "investment", "funding", "expensive", "costly"],
            "network_effects": ["network", "ecosystem", "platform", "community"],
            "switching_costs": ["switching", "lock-in", "migration", "transition"],
            "brand_loyalty": ["brand", "loyalty", "trust", "reputation"],
            "economies_of_scale": ["scale", "volume", "efficiency", "cost_advantage"],
            "technology": ["proprietary", "patent", "ip", "technology", "technical"],
            "distribution": ["distribution", "channel", "partnership", "access"]
        }

        for barrier_type, keywords in barrier_patterns.items():
            if any(keyword in content for keyword in keywords):
                barriers.append(barrier_type.replace("_", " ").title())

        return barriers

    def extract_market_metrics(self, document: StartupDocument) -> Dict[str, Any]:
        """
        Extract key market metrics from document

        Args:
            document: Startup document to analyze

        Returns:
            Dictionary of extracted market metrics
        """
        content = document.content.raw_text
        metrics = {}

        import re

        # Market growth rates
        growth_pattern = r'(\d+)%\s*(?:growth|increase|cagr|annually|yearly)'
        growth_matches = re.findall(growth_pattern, content, re.IGNORECASE)
        if growth_matches:
            metrics["growth_rates"] = growth_matches

        # Market share
        share_pattern = r'(\d+)%\s*(?:market\s*share|share)'
        share_matches = re.findall(share_pattern, content, re.IGNORECASE)
        if share_matches:
            metrics["market_share"] = share_matches

        # Customer numbers
        customer_pattern = r'(\d+(?:,\d+)*)\s*(?:customers|users|clients)'
        customer_matches = re.findall(customer_pattern, content, re.IGNORECASE)
        if customer_matches:
            metrics["customer_numbers"] = customer_matches

        # Geographic markets
        geo_pattern = r'\b(US|USA|United States|Europe|Asia|China|India|Canada|UK|Australia|Global|International)\b'
        geo_matches = re.findall(geo_pattern, content, re.IGNORECASE)
        if geo_matches:
            metrics["geographic_markets"] = list(set(geo_matches))

        return metrics

    def analyze_combined_documents(self, pitch_deck_content: str, public_data_content: str) -> str:
        """
        Analyze startup market using both pitch deck and public data together

        Args:
            pitch_deck_content: Content from pitch deck analysis
            public_data_content: Content from public data scraping

        Returns:
            Markdown formatted market analysis
        """
        logger.info("Starting combined market document analysis")

        # Create the combined prompt
        template = self._get_combined_markdown_template()

        prompt = PromptTemplate(
            template=template,
            input_variables=["pitch_deck_content", "public_data_content"]
        )

        # Format the prompt with both documents
        formatted_prompt = prompt.format(
            pitch_deck_content=pitch_deck_content,
            public_data_content=public_data_content
        )

        try:
            # Get response from LLM
            if self.llm:
                logger.info(f"Sending prompt to LLM (length: {len(formatted_prompt)} characters)")
                response = self.llm.invoke(formatted_prompt)
                if hasattr(response, 'content'):
                    result = response.content
                else:
                    result = str(response)

                # Check if the response seems truncated
                if len(result) < 1000:
                    logger.warning(f"Analysis response is unusually short ({len(result)} characters). May be truncated due to token limits.")
                elif not result.strip().endswith(('.', '!', '?', '```', '"""')):
                    logger.warning("Analysis response appears to be truncated (doesn't end with proper punctuation)")

                logger.info(f"Generated market analysis: {len(result)} characters")
            else:
                # Mock response for testing
                result = self._get_mock_combined_analysis()

            logger.info("Combined market document analysis completed successfully")
            return result.strip()

        except Exception as e:
            error_msg = str(e).lower()
            if "token" in error_msg or "length" in error_msg or "limit" in error_msg:
                logger.error(f"Token limit exceeded in combined market document analysis: {e}")
                logger.info("Consider reducing document size or splitting analysis into smaller chunks")
                raise AnalysisError(f"Token limit exceeded. Try reducing document size or check max_tokens settings: {e}")
            else:
                logger.error(f"Error in combined market document analysis: {e}")
                raise AnalysisError(f"Combined market analysis failed: {e}")

    def _get_mock_combined_analysis(self) -> str:
        """
        Generate mock combined market analysis for testing

        Returns:
            Mock markdown market analysis
        """
        return """# Market & Competition Analysis Report

## Executive Summary
Based on analysis of both the pitch deck and public data sources, this startup operates in the rapidly growing AI-powered data analytics market. The company targets the underserved SMB segment with an estimated TAM of $50B, demonstrating strong market opportunity with significant growth potential in the democratization of data analytics.

## Market Size & Opportunity
**Total Addressable Market (TAM):** $50 billion globally
**Serviceable Addressable Market (SAM):** $5 billion (AI analytics for SMBs)
**Serviceable Obtainable Market (SOM):** $500 million (realistic capture potential)

The market is experiencing strong growth with a 15-20% CAGR driven by:
- Increasing demand for data-driven decision making
- SMB digital transformation acceleration
- Growing accessibility of AI/ML technologies
- Shift from traditional BI tools to conversational interfaces

## Competitive Landscape
**Primary Competitors:**
- Tableau (market leader in visualization)
- Power BI (Microsoft's enterprise solution)
- Looker (Google's business intelligence platform)
- Sisense (AI-driven analytics platform)

**Competitive Positioning:**
- Differentiates through conversational AI interface
- Focuses on underserved SMB market segment
- Emphasizes ease-of-use for non-technical users
- Offers agentic automation capabilities

**Market Share Dynamics:**
- Established players dominate enterprise market
- SMB segment remains fragmented and underserved
- Opportunity for specialized players focusing on accessibility

## Market Segmentation
**Primary Target Segments:**
1. **Small-Medium Businesses (10-500 employees)**
   - Limited technical data science capabilities
   - Need for accessible analytics tools
   - Budget-conscious with growth-oriented mindset

2. **Non-Technical Business Users**
   - Marketing managers, sales directors, operations teams
   - Require insights without technical complexity
   - Value time-saving and automated reporting

3. **Enterprise Departments**
   - Individual teams within larger organizations
   - Seeking departmental analytics solutions
   - Need quick deployment and results

## Market Trends & Dynamics
**Key Market Trends:**
- **Democratization of Analytics:** Growing demand for self-service BI tools
- **Conversational AI Adoption:** Users prefer natural language interfaces
- **AI/ML Integration:** Automated insights becoming standard expectation
- **Cloud-First Approach:** Migration from on-premise to cloud solutions
- **Real-Time Analytics:** Increasing demand for immediate insights

**Market Drivers:**
- SMB digital transformation acceleration
- Shortage of data science talent
- Decreasing cost of cloud computing
- Increasing data volume and complexity

## Geographic Analysis
**Primary Markets:**
- North America (initial focus)
- Europe (planned expansion)
- Asia-Pacific (future opportunity)

**Market Characteristics:**
- US leads in SMB technology adoption
- Europe shows strong data privacy focus
- Asia offers high growth potential but regulatory complexity

## Market Entry Strategy
**Go-to-Market Approach:**
- Product-led growth with freemium model
- Self-service onboarding and trials
- Content marketing and SEO for organic acquisition
- Strategic partnerships with complementary tools

**Customer Acquisition Strategy:**
- Focus on immediate value demonstration
- Emphasize ease-of-use in marketing
- Target marketing and sales departments first
- Leverage user success stories and case studies

## Entry Barriers & Challenges
**Market Barriers:**
- **Brand Recognition:** Established competitors have strong market presence
- **Integration Complexity:** Need to connect with multiple data sources
- **Customer Education:** Market requires education on conversational analytics
- **Regulatory Compliance:** Data privacy and industry-specific requirements

**Competitive Challenges:**
- Large competitors with significant resources
- Customer switching costs from existing solutions
- Need for continuous AI/ML innovation
- Scaling customer support for SMB segment

## Market Timing & Validation
**Market Readiness Indicators:**
- Growing awareness of AI/ML capabilities
- Increasing dissatisfaction with complex BI tools
- SMB digital transformation acceleration post-COVID
- Rising demand for self-service analytics

**Product-Market Fit Indicators:**
- Strong user engagement in conversational interface
- Positive customer feedback on ease-of-use
- Reduced time-to-insight compared to alternatives
- Growing organic user acquisition

## Customer Validation
**Demand Evidence:**
- Growing search volume for "conversational analytics"
- Increasing investment in AI-powered BI tools
- SMB surveys showing analytics as top priority
- Customer interviews confirming pain points

**Market Testing Results:**
- Beta users demonstrate high engagement
- Positive feedback on user experience
- Strong word-of-mouth referral potential
- Clear value proposition validation

## Competitive Positioning
**Key Differentiators:**
1. **Conversational Interface:** Natural language queries vs. complex dashboards
2. **SMB Focus:** Designed for non-technical users vs. enterprise complexity
3. **Agentic Automation:** Automated insights vs. manual analysis
4. **Rapid Deployment:** Quick setup vs. lengthy implementation

**Competitive Advantages:**
- First-mover advantage in conversational analytics for SMBs
- Purpose-built for non-technical users
- Strong technology foundation with AI capabilities
- Agile development and rapid iteration capability

## Market Risk Assessment
**Market Risks:**
- **Economic Downturn:** SMB technology spending reduction
- **Competitive Response:** Large players entering conversational analytics
- **Technology Evolution:** Rapid AI advancement changing expectations
- **Regulation:** Data privacy laws affecting analytics tools

**Mitigation Strategies:**
- Diversify across customer segments and geographies
- Continuous innovation and technology advancement
- Strong compliance and security framework
- Flexible pricing models for economic uncertainty

## Strategic Market Recommendations
1. **Focus on Product-Market Fit:** Continue refining conversational interface based on user feedback
2. **Accelerate Partnership Strategy:** Build integrations with popular SMB tools
3. **Invest in Market Education:** Create content demonstrating value of conversational analytics
4. **Expand Customer Success:** Ensure high retention and expansion within existing accounts
5. **Geographic Expansion:** Plan systematic expansion to European markets
6. **Competitive Monitoring:** Track large competitors' moves into conversational analytics

## Information Gaps & Questions for Founders

**Critical Data Needed for Investment Decision:**

**Market Intelligence:**
- Detailed competitive analysis with specific feature comparisons
- Customer acquisition cost (CAC) and lifetime value (LTV) metrics
- Market penetration rates and addressable customer counts
- Pricing sensitivity analysis for target segments

**Customer Validation:**
- Customer churn rates and reasons for churn
- Net Promoter Score (NPS) and customer satisfaction metrics
- Case studies with specific ROI measurements
- Pipeline conversion rates and sales cycle length

**Financial Market Data:**
- Unit economics and gross margin by customer segment
- Customer acquisition channel effectiveness and costs
- Revenue expansion rates within existing accounts
- Seasonal or cyclical market demand patterns

**Questions for Startup Founders:**
1. **Market Strategy:** How do you plan to compete against Microsoft Power BI's aggressive pricing and distribution?
2. **Customer Retention:** What are your current customer churn rates and primary retention strategies?
3. **Technology Moat:** How defensible is your conversational AI technology against competitors?
4. **Scaling Challenges:** What are the primary bottlenecks in scaling customer acquisition?
5. **International Expansion:** What's your timeline and strategy for European market entry?
6. **Partnership Strategy:** Which strategic partnerships are most critical for market penetration?
7. **Economic Sensitivity:** How resilient is your target market to economic downturns?

**Red Flags to Investigate:**
- Lack of customer retention data or high churn rates
- Insufficient differentiation from existing solutions
- Unrealistic market share projections
- Limited evidence of product-market fit
- Weak competitive positioning against established players"""

    def get_market_insights(self, analysis: MarketAnalysis) -> Dict[str, Any]:
        """
        Generate additional market insights from analysis

        Args:
            analysis: Completed market analysis

        Returns:
            Dictionary of market insights and recommendations
        """
        insights = {
            "market_opportunity_assessment": self._assess_market_opportunity(analysis),
            "competitive_strength": self._assess_competitive_position(analysis),
            "market_timing": self._assess_market_timing(analysis),
            "expansion_potential": self._assess_expansion_potential(analysis),
            "market_risks": self._identify_market_risks(analysis)
        }

        return insights

    def _assess_market_opportunity(self, analysis: MarketAnalysis) -> Dict[str, Any]:
        """Assess overall market opportunity"""
        opportunity = {
            "market_size_score": self._calculate_market_size_score(analysis.market_size),
            "growth_potential": "high" if analysis.market_trends else "medium",
            "market_maturity": self._assess_market_maturity(analysis)
        }

        return opportunity

    def _calculate_market_size_score(self, market_size: Dict[str, Any]) -> str:
        """Calculate market size score based on TAM/SAM/SOM"""
        if not market_size:
            return "unknown"

        # Simple scoring based on presence of market size data
        if "tam" in market_size or "sam" in market_size:
            return "large"
        elif "som" in market_size:
            return "medium"
        else:
            return "small"

    def _assess_market_maturity(self, analysis: MarketAnalysis) -> str:
        """Assess market maturity stage"""
        if any("emerging" in trend.lower() for trend in analysis.market_trends):
            return "emerging"
        elif any("growth" in trend.lower() for trend in analysis.market_trends):
            return "growth"
        else:
            return "mature"

    def _assess_competitive_position(self, analysis: MarketAnalysis) -> str:
        """Assess competitive positioning strength"""
        if len(analysis.competition) == 0:
            return "no_competition_identified"
        elif len(analysis.competition) < 3:
            return "limited_competition"
        elif len(analysis.competition) < 6:
            return "moderate_competition"
        else:
            return "highly_competitive"

    def _assess_market_timing(self, analysis: MarketAnalysis) -> str:
        """Assess market entry timing"""
        positive_indicators = ["growth", "emerging", "adoption"]
        negative_indicators = ["mature", "declining", "saturated"]

        trend_text = " ".join(analysis.market_trends).lower()

        if any(indicator in trend_text for indicator in positive_indicators):
            return "favorable"
        elif any(indicator in trend_text for indicator in negative_indicators):
            return "challenging"
        else:
            return "neutral"

    def _assess_expansion_potential(self, analysis: MarketAnalysis) -> str:
        """Assess geographic and segment expansion potential"""
        geo_count = len(analysis.geographic_focus)
        segment_count = len(analysis.customer_segments)

        if geo_count > 3 or segment_count > 3:
            return "high"
        elif geo_count > 1 or segment_count > 1:
            return "medium"
        else:
            return "limited"

    def _identify_market_risks(self, analysis: MarketAnalysis) -> List[str]:
        """Identify potential market risks from analysis"""
        risks = []

        # High competition risk
        if len(analysis.competition) > 5:
            risks.append("High competitive intensity")

        # Market barrier risks
        if analysis.market_barriers:
            risks.append("Significant market entry barriers")

        # Limited geographic focus
        if len(analysis.geographic_focus) <= 1:
            risks.append("Limited geographic diversification")

        # Customer segment concentration
        if len(analysis.customer_segments) <= 1:
            risks.append("Customer segment concentration risk")

        return risks


# Convenience function for market analysis
def create_market_agent(**kwargs) -> MarketAnalysisAgent:
    """
    Create a MarketAnalysisAgent with default configuration

    Args:
        **kwargs: Additional configuration parameters

    Returns:
        Configured MarketAnalysisAgent instance
    """
    return MarketAnalysisAgent(**kwargs)


if __name__ == "__main__":
    # Basic test of market agent
    from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent
    from pathlib import Path
    from datetime import datetime

    # Create test document
    test_doc = StartupDocument(
        content=ParsedContent(
            sections=["Market", "Competition", "TAM"],
            raw_text="""
            The AI analytics market is valued at $50B globally with 15% CAGR.
            Our TAM is $50B, SAM is $5B, and SOM is $500M.
            Key competitors include Tableau, Power BI, and Looker.
            We target small-medium businesses in North America and Europe.
            The market is experiencing rapid growth and digital transformation.
            Main barriers include brand recognition and customer acquisition.
            """,
            word_count=65
        ),
        metadata=DocumentMetadata(
            file_path=Path("test_market.md"),
            size=400,
            last_modified=datetime.now()
        ),
        document_type="market_analysis"
    )

    try:
        # Test market agent creation
        agent = create_market_agent()
        print(f"✓ Created MarketAnalysisAgent: {agent.agent_name}")

        # Test specialized methods
        market_size = agent.analyze_market_size(test_doc)
        print(f"✓ Market size data: {market_size}")

        competitors = agent.identify_competitors(test_doc)
        print(f"✓ Competitors identified: {competitors}")

        trends = agent.assess_market_trends(test_doc)
        print(f"✓ Market trends: {trends}")

        barriers = agent.identify_market_barriers(test_doc)
        print(f"✓ Market barriers: {barriers}")

        metrics = agent.extract_market_metrics(test_doc)
        print(f"✓ Market metrics: {metrics}")

        print("✓ MarketAnalysisAgent test completed successfully")

    except Exception as e:
        print(f"✗ MarketAnalysisAgent test failed: {e}")
        import traceback
        traceback.print_exc()