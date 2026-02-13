"""
Risk Assessment Agent for Multi-Agent Startup Analysis System

Specialized agent for comprehensive risk identification and mitigation analysis.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel

from src.agents.base_agent import BaseStructuredAgent, AnalysisError
from src.models.document_models import StartupDocument
from src.models.analysis_models import RiskAnalysis
from src.utils.prompt_manager import PromptManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class RiskAssessmentAgent(BaseStructuredAgent):
    """
    Specialized agent for risk identification and assessment

    Focuses on business, market, technical, financial, regulatory, and operational
    risk analysis with mitigation strategy recommendations.
    """

    def __init__(self,
                 llm: Optional[BaseLanguageModel] = None,
                 temperature: float = 0.1,
                 **kwargs):
        """
        Initialize Risk Assessment Agent

        Args:
            llm: Language model instance
            temperature: Sampling temperature for risk analysis
            **kwargs: Additional parameters
        """
        super().__init__(
            agent_name="RiskAssessmentAgent",
            output_model=RiskAnalysis,
            llm=llm,
            temperature=temperature,
            **kwargs
        )

        # Initialize prompt manager
        self.prompt_manager = PromptManager()

        # Risk analysis frameworks
        self.risk_frameworks = {
            "risk_categories": [
                "business", "market", "technical", "financial",
                "regulatory", "operational", "reputational", "strategic"
            ],
            "severity_levels": ["low", "medium", "high", "critical"],
            "business_risk_types": [
                "revenue_concentration", "customer_churn", "dependency",
                "execution", "management", "product_market_fit"
            ],
            "market_risk_types": [
                "competition", "market_size", "timing", "adoption",
                "economic_downturn", "market_saturation"
            ],
            "tech_risk_types": [
                "scalability", "security", "technical_debt", "vendor_lock",
                "technology_obsolescence", "data_breach"
            ],
            "regulatory_risk_types": [
                "compliance", "data_privacy", "licensing", "legal",
                "intellectual_property", "industry_regulations"
            ]
        }

        logger.info("RiskAssessmentAgent initialized with risk frameworks")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for risk analysis

        Returns:
            Risk analysis system prompt
        """
        try:
            return self.prompt_manager.get_prompt_template("risk_analysis_system")
        except Exception as e:
            logger.warning(f"Could not load risk_analysis_system prompt: {e}")
            return """You are a senior risk analyst specializing in startup risk assessment.
                     Your expertise includes identifying business, market, technical, financial,
                     regulatory, and operational risks. You excel at risk prioritization,
                     mitigation strategy development, and comprehensive risk evaluation."""

    def get_analysis_prompt_template(self) -> PromptTemplate:
        """
        Get the main risk analysis prompt template

        Returns:
            Configured PromptTemplate for risk analysis
        """
        try:
            template_content = self.prompt_manager.get_prompt_template("risk_analysis_main")
            input_variables = [
                "document_content", "document_type", "word_count",
                "file_name", "sections"
            ]
        except Exception as e:
            logger.warning(f"Could not load risk_analysis_main prompt: {e}")
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
        Analyze the following startup document and provide a CONCISE risk analysis:

        DOCUMENT CONTENT:
        {document_content}

        DOCUMENT METADATA:
        - Type: {document_type}
        - Word Count: {word_count}
        - File Name: {file_name}
        - Sections: {sections}

        Provide your analysis in JSON format with these fields:

        {format_instructions}

        Focus ONLY on these critical elements (be concise):
        1. TOP 5 CRITICAL RISKS: Identify only the 5 most severe risks across ALL categories (business, market, technical, financial, regulatory, operational). For each risk provide:
           - description: 1-2 sentence description with evidence
           - severity: critical/high/medium
           - mitigation: 1 sentence mitigation approach

        2. RED FLAGS: List 0-3 critical red flags (deal-breakers only)

        3. OVERALL RISK LEVEL: low/medium/high/critical with 1 sentence justification

        Prioritize by severity and likelihood. Cite evidence. Be concise.
        """

    def _get_combined_markdown_template(self) -> str:
        """
        Get template for combined document analysis with markdown output

        Returns:
            Markdown template string for combined analysis
        """
        # Load from prompts.yaml for centralized management
        return self.prompt_manager.get_prompt_template("risk_analysis_combined")

    def identify_business_risks(self, document: StartupDocument) -> List[Dict[str, str]]:
        """
        Identify business-related risks

        Args:
            document: Startup document to analyze

        Returns:
            List of business risks with descriptions and severity
        """
        content = document.content.raw_text.lower()
        risks = []

        # Revenue concentration risk
        if "single customer" in content or "one client" in content or "dependent on" in content:
            risks.append({
                "description": "Revenue concentration risk from dependency on limited customers",
                "severity": "high"
            })

        # Unproven business model
        if "new business model" in content or "untested" in content or "no revenue yet" in content:
            risks.append({
                "description": "Business model not yet proven in market",
                "severity": "medium"
            })

        # Customer acquisition challenges
        if "high cac" in content or "customer acquisition cost" in content or "expensive to acquire" in content:
            risks.append({
                "description": "High customer acquisition costs impacting unit economics",
                "severity": "high"
            })

        # Churn risk
        if "churn" in content or "retention challenge" in content:
            risks.append({
                "description": "Customer churn and retention challenges",
                "severity": "medium"
            })

        logger.debug(f"Identified business risks: {len(risks)}")
        return risks if risks else [{"description": "No significant business risks identified", "severity": "low"}]

    def identify_market_risks(self, document: StartupDocument) -> List[Dict[str, str]]:
        """
        Identify market-related risks

        Args:
            document: Startup document to analyze

        Returns:
            List of market risks
        """
        content = document.content.raw_text.lower()
        risks = []

        # Intense competition
        if "competitive" in content or "many competitors" in content or "crowded market" in content:
            risks.append({
                "description": "Intense competition in saturated market",
                "severity": "high"
            })

        # Market size concerns
        if "niche market" in content or "small market" in content or "limited addressable market" in content:
            risks.append({
                "description": "Limited total addressable market size",
                "severity": "medium"
            })

        # Market timing
        if "early market" in content or "market not ready" in content or "ahead of market" in content:
            risks.append({
                "description": "Market timing risk - market may not be ready",
                "severity": "medium"
            })

        # Economic sensitivity
        if "economic downturn" in content or "recession" in content or "economic sensitive" in content:
            risks.append({
                "description": "Business model sensitive to economic conditions",
                "severity": "medium"
            })

        return risks if risks else [{"description": "No significant market risks identified", "severity": "low"}]

    def identify_technical_risks(self, document: StartupDocument) -> List[Dict[str, str]]:
        """
        Identify technology-related risks

        Args:
            document: Startup document to analyze

        Returns:
            List of technical risks
        """
        content = document.content.raw_text.lower()
        risks = []

        # Scalability concerns
        if "scalability challenge" in content or "scaling issues" in content or "not scalable" in content:
            risks.append({
                "description": "Technical scalability limitations",
                "severity": "high"
            })

        # Security vulnerabilities
        if "security concern" in content or "data breach" in content or "vulnerable" in content:
            risks.append({
                "description": "Security vulnerabilities and data protection risks",
                "severity": "critical"
            })

        # Technical debt
        if "legacy code" in content or "technical debt" in content or "refactoring needed" in content:
            risks.append({
                "description": "Accumulated technical debt requiring refactoring",
                "severity": "medium"
            })

        # Vendor lock-in
        if "vendor lock" in content or "single vendor" in content or "platform dependency" in content:
            risks.append({
                "description": "Vendor lock-in and third-party dependency risks",
                "severity": "medium"
            })

        # Technology obsolescence
        if "outdated technology" in content or "legacy platform" in content:
            risks.append({
                "description": "Risk of technology stack becoming obsolete",
                "severity": "high"
            })

        return risks

    def identify_regulatory_risks(self, document: StartupDocument) -> List[Dict[str, str]]:
        """
        Identify regulatory and compliance risks

        Args:
            document: Startup document to analyze

        Returns:
            List of regulatory risks
        """
        content = document.content.raw_text.lower()
        risks = []

        # Data privacy risks
        if "gdpr" in content or "data privacy" in content or "personal data" in content or "ccpa" in content:
            risks.append({
                "description": "Data privacy compliance requirements (GDPR, CCPA)",
                "severity": "high"
            })

        # Industry regulations
        if "regulated industry" in content or "compliance required" in content or "regulatory approval" in content:
            risks.append({
                "description": "Industry-specific regulatory compliance requirements",
                "severity": "high"
            })

        # Licensing requirements
        if "license required" in content or "regulatory license" in content:
            risks.append({
                "description": "Licensing and regulatory approval requirements",
                "severity": "medium"
            })

        # IP risks
        if "patent infringement" in content or "ip risk" in content or "trademark" in content:
            risks.append({
                "description": "Intellectual property and patent infringement risks",
                "severity": "high"
            })

        return risks

    def assess_overall_risk_level(self, all_risks: Dict[str, List[Dict[str, str]]]) -> str:
        """
        Assess overall risk level based on all identified risks

        Args:
            all_risks: Dictionary of all risk categories

        Returns:
            Overall risk level (low/medium/high/critical)
        """
        # Count risks by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for risk_category in all_risks.values():
            for risk in risk_category:
                severity = risk.get("severity", "low").lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1

        # Determine overall risk level
        if severity_counts["critical"] > 0:
            return "critical"
        elif severity_counts["high"] >= 3:
            return "high"
        elif severity_counts["high"] >= 1 or severity_counts["medium"] >= 5:
            return "high"
        elif severity_counts["medium"] >= 2:
            return "medium"
        else:
            return "low"

    def generate_mitigation_strategies(self, all_risks: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[str]]:
        """
        Generate mitigation strategies for identified risks

        Args:
            all_risks: Dictionary of all identified risks

        Returns:
            Dictionary of mitigation strategies by category
        """
        strategies = {}

        # Business risk mitigations
        if all_risks.get("business_risks"):
            strategies["business"] = [
                "Diversify revenue streams to reduce concentration risk",
                "Implement customer success program to improve retention",
                "Develop multiple go-to-market channels",
                "Build strategic partnerships to de-risk customer acquisition"
            ]

        # Market risk mitigations
        if all_risks.get("market_risks"):
            strategies["market"] = [
                "Differentiate through unique value proposition",
                "Focus on underserved market segments",
                "Build defensible competitive moats",
                "Monitor market trends and adapt strategy accordingly"
            ]

        # Technical risk mitigations
        if all_risks.get("tech_risks"):
            strategies["technical"] = [
                "Invest in scalable architecture from the start",
                "Implement comprehensive security measures and audits",
                "Allocate time for technical debt reduction",
                "Diversify technology vendors to avoid lock-in",
                "Conduct regular security assessments"
            ]

        # Financial risk mitigations
        if all_risks.get("financial_risks"):
            strategies["financial"] = [
                "Extend runway through cost optimization",
                "Secure strategic investor commitments early",
                "Improve unit economics through operational efficiency",
                "Maintain financial discipline and cash flow monitoring"
            ]

        # Regulatory risk mitigations
        if all_risks.get("regulatory_risks"):
            strategies["regulatory"] = [
                "Engage compliance experts early in development",
                "Implement privacy-by-design principles",
                "Obtain necessary licenses and certifications proactively",
                "Stay updated on regulatory changes",
                "Build compliance into product roadmap"
            ]

        # Operational risk mitigations
        if all_risks.get("operational_risks"):
            strategies["operational"] = [
                "Document key processes and knowledge",
                "Build redundancy in critical roles",
                "Implement robust backup and disaster recovery",
                "Diversify vendor and supplier relationships"
            ]

        return strategies

    def analyze_combined_documents(self, pitch_deck_content: str, public_data_content: str) -> str:
        """
        Analyze startup using both pitch deck and public data together

        Args:
            pitch_deck_content: Content from pitch deck analysis
            public_data_content: Content from public data scraping

        Returns:
            Markdown formatted risk assessment
        """
        logger.info("Starting combined document risk analysis")

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

                logger.info(f"Generated analysis: {len(result)} characters")
            else:
                # Mock response for testing
                result = self._get_mock_combined_analysis()

            logger.info("Combined document risk analysis completed successfully")
            return result.strip()

        except Exception as e:
            error_msg = str(e).lower()
            if "token" in error_msg or "length" in error_msg or "limit" in error_msg:
                logger.error(f"Token limit exceeded in combined document analysis: {e}")
                raise AnalysisError(f"Token limit exceeded. Try reducing document size: {e}")
            else:
                logger.error(f"Error in combined document risk analysis: {e}")
                raise AnalysisError(f"Combined risk analysis failed: {e}")

    def _get_mock_combined_analysis(self) -> str:
        """
        Generate mock combined risk analysis for testing

        Returns:
            Mock markdown analysis
        """
        return """# Risk Assessment Report

## Executive Summary
Based on comprehensive analysis of both pitch deck and public data, this startup presents a **MEDIUM-HIGH** overall risk profile. While the business demonstrates strong technical foundations and market opportunity, significant risks exist in competitive positioning, regulatory compliance, and execution capabilities. Critical attention required for market timing and customer acquisition cost management.

## Business Risks

### Revenue Model Risks
**Risk:** Dependence on subscription revenue model in competitive market
**Severity:** Medium
**Details:** Heavy reliance on recurring revenue in a space where competitors offer freemium models could impact customer acquisition and retention.

### Customer Concentration
**Risk:** No indication of customer diversification strategy
**Severity:** Medium
**Details:** Early-stage concentration risk with limited customer base. Loss of key anchor customer could significantly impact revenue.

### Product-Market Fit
**Risk:** Unproven product-market fit in target SMB segment
**Severity:** High
**Details:** While technology is sound, actual market validation with paying customers is limited. SMB segment historically challenging for complex analytics tools.

### Execution Risk
**Risk:** Ambitious roadmap with limited resources
**Severity:** High
**Details:** Product roadmap appears aggressive relative to current team size and funding runway. Risk of feature bloat or delayed releases.

## Market Risks

### Intense Competition
**Risk:** Competing against well-funded incumbents (Tableau, Power BI, Looker)
**Severity:** High
**Details:** Market dominated by large players with significant resources and established customer bases. Differentiation through conversational AI may not be sufficient.

### Market Timing
**Risk:** SMB market adoption of advanced analytics tools uncertain
**Severity:** Medium
**Details:** Target market may not be ready to adopt AI-powered analytics. Educational burden significant.

### Economic Sensitivity
**Risk:** SMB spending highly sensitive to economic conditions
**Severity:** Medium
**Details:** Analytics tools often first to be cut in economic downturns. Subscription model vulnerable to churn.

### Market Size Concerns
**Risk:** Actual TAM for SMB AI analytics smaller than projected
**Severity:** Medium
**Details:** While total analytics market is large, segment willing to pay for AI features may be limited.

## Technical Risks

### Scalability Challenges
**Risk:** Current architecture may not scale to enterprise requirements
**Severity:** Medium
**Details:** Microservices architecture is solid but needs proven scaling for 100K+ users. Database sharding and multi-region support not yet implemented.

### API Dependency
**Risk:** Critical dependency on OpenAI API for core functionality
**Severity:** High
**Details:** Heavy reliance on third-party AI API creates:
- Cost unpredictability as usage scales
- Service availability risk
- Feature constraint by API limitations
- Potential pricing changes impacting margins

### Security & Data Protection
**Risk:** Handling sensitive business data requires robust security
**Severity:** Critical
**Details:** Any data breach would be catastrophic for B2B SaaS. Current security measures need third-party audit and penetration testing.

### Technical Debt
**Risk:** Legacy code from MVP phase requiring refactoring
**Severity:** Low
**Details:** Some technical debt accumulated during rapid development. Manageable with proper allocation of engineering resources.

## Financial Risks

### Burn Rate
**Risk:** High burn rate with 12-month runway
**Severity:** High
**Details:** Current burn rate ~$150K/month with limited revenue. Need to raise Series A within 6-9 months or achieve profitability.

### Unit Economics
**Risk:** CAC potentially exceeding LTV in competitive market
**Severity:** High
**Details:** Customer acquisition costs for SMB SaaS typically $500-1500. With average subscription $99/mo, payback period exceeds 12 months. Churn rate critical.

### Funding Environment
**Risk:** Challenging fundraising environment for early-stage AI startups
**Severity:** Medium
**Details:** Market has seen AI fatigue. Need strong traction metrics to raise Series A.

### Revenue Projections
**Risk:** Aggressive revenue projections may not materialize
**Severity:** Medium
**Details:** Projected growth from $0 to $5M ARR in 24 months requires significant market traction and execution excellence.

## Regulatory & Compliance Risks

### Data Privacy Compliance
**Risk:** GDPR, CCPA, and other data privacy regulations
**Severity:** High
**Details:** Processing customer business data across jurisdictions requires comprehensive compliance program. Non-compliance penalties severe. Current implementation unclear.

### Industry-Specific Regulations
**Risk:** Serving regulated industries (healthcare, finance) requires certifications
**Severity:** Medium
**Details:** To sell into healthcare or financial services, need HIPAA, SOC 2, ISO 27001 compliance. Significant time and cost investment.

### Data Residency Requirements
**Risk:** International customers may require data to stay in specific regions
**Severity:** Medium
**Details:** Multi-region deployment needed for global expansion. Current single-region AWS deployment limits market.

### AI Ethics & Transparency
**Risk:** Increasing regulations around AI decision-making and transparency
**Severity:** Low
**Details:** Emerging regulations around AI explainability and bias. May require model transparency features.

## Operational Risks

### Team Composition
**Risk:** Technical team stronger than go-to-market team
**Severity:** Medium
**Details:** Strong engineering talent but limited sales/marketing expertise. SMB sales execution challenging.

### Key Person Risk
**Risk:** Heavy dependence on founding team
**Severity:** High
**Details:** Loss of technical co-founder or CEO would significantly impact execution. Knowledge concentration risk.

### Vendor Dependencies
**Risk:** Reliance on multiple third-party services
**Severity:** Low
**Details:** Dependencies on AWS, OpenAI, Stripe, SendGrid. Manageable with proper vendor relationship management.

### Process Maturity
**Risk:** Limited operational processes for scaling
**Severity:** Medium
**Details:** Early-stage company with informal processes. Need to implement customer success, support, and operational frameworks before scaling.

## Strategic Risks

### Pivot Risk
**Risk:** May need to pivot target market or product positioning
**Severity:** Medium
**Details:** If SMB market proves challenging, pivot to enterprise could require significant product changes and sales model adjustment.

### Competitive Response
**Risk:** Incumbents could quickly replicate conversational AI features
**Severity:** High
**Details:** Large players have resources to add conversational interfaces. Differentiation window may be limited.

### Technology Shift
**Risk:** AI/LLM landscape evolving rapidly
**Severity:** Medium
**Details:** Rapid advancement in open-source LLMs could commoditize core technology. Need continuous innovation.

## Risk Prioritization Matrix

### Critical Priority (Immediate Attention)
1. **Security & Data Protection** - Conduct third-party security audit
2. **API Dependency** - Develop fallback AI models and reduce OpenAI reliance
3. **Cash Runway** - Accelerate fundraising or path to profitability

### High Priority (Next 3 Months)
1. **Customer Acquisition Economics** - Validate unit economics with real data
2. **Data Privacy Compliance** - Implement GDPR/CCPA compliance framework
3. **Competitive Positioning** - Strengthen differentiation beyond conversational UI
4. **Key Person Risk** - Document critical knowledge and cross-train team

### Medium Priority (6 Months)
1. **Market Validation** - Prove product-market fit in target segment
2. **Scalability** - Implement multi-region and database scaling
3. **Team Build-out** - Hire sales and marketing leadership

## Mitigation Strategies

### Business Risk Mitigations
- Diversify revenue streams (consulting, data services, API access)
- Implement robust customer success program to minimize churn
- Build case studies and social proof to reduce customer acquisition friction
- Consider freemium tier to accelerate adoption

### Market Risk Mitigations
- Focus on specific vertical with clear pain point (e.g., e-commerce analytics)
- Build community and content marketing to educate market
- Partner with complementary tools for distribution
- Develop competitive moats through proprietary data and models

### Technical Risk Mitigations
- Implement AI model fallbacks and reduce OpenAI dependency
- Conduct comprehensive security audit and penetration testing
- Allocate 20% sprint capacity to technical debt reduction
- Build multi-cloud capabilities to avoid vendor lock-in
- Obtain SOC 2 Type II certification

### Financial Risk Mitigations
- Optimize CAC through product-led growth strategies
- Extend runway through cost optimization and milestone-based hiring
- Secure committed investor interest before current round completion
- Implement usage-based pricing to improve unit economics

### Regulatory Risk Mitigations
- Engage data privacy counsel and implement compliance framework
- Build privacy-by-design into product architecture
- Obtain industry certifications (SOC 2, ISO 27001, HIPAA if needed)
- Implement data residency and regional deployment options

### Operational Risk Mitigations
- Document critical processes and create runbooks
- Implement knowledge sharing and cross-training programs
- Build advisory board to supplement team expertise
- Establish vendor backup options for critical dependencies

## Risk Monitoring & KPIs

### Key Risk Indicators to Track
**Financial Health:**
- Monthly burn rate and runway
- CAC and LTV trends
- Cash flow and revenue growth

**Customer Health:**
- Monthly churn rate
- Net revenue retention
- Customer satisfaction scores
- Support ticket volume and resolution time

**Technical Health:**
- System uptime and availability
- API response times and error rates
- Security incident frequency
- Technical debt ratio

**Market Position:**
- Win rate against competitors
- Sales cycle length
- Customer acquisition velocity
- Market share in target segments

## Overall Risk Assessment

**Risk Rating: MEDIUM-HIGH**

**Justification:**
This startup demonstrates strong technical capabilities and addresses a real market need, but faces significant execution and competitive risks. The combination of:
- High dependence on third-party AI infrastructure (High risk)
- Challenging unit economics in competitive SMB market (High risk)
- Critical security and compliance requirements (Critical risk)
- Limited runway requiring near-term fundraising (High risk)

...elevates the overall risk profile to MEDIUM-HIGH.

**Risk Trajectory:**
- With successful execution on key mitigation strategies, risk could reduce to MEDIUM within 6-9 months
- Failure to address critical risks (security, API dependency, cash runway) could elevate to HIGH-CRITICAL

## Red Flags

🚩 **Cash Runway Critical:** Only 12 months runway with limited revenue. Fundraising must start immediately.

🚩 **Unproven Unit Economics:** CAC and LTV assumptions not validated with real customer data.

🚩 **API Vendor Lock-in:** Critical business logic dependent on OpenAI API without fallback.

🚩 **Competitive Pressure:** Incumbents can replicate conversational AI features quickly.

🚩 **Security Audit Missing:** Handling sensitive business data without third-party security audit.

🚩 **Compliance Gap:** Data privacy compliance (GDPR/CCPA) implementation unclear.

## Risk Mitigation Recommendations

### Immediate Actions (30 Days)
1. **Conduct security audit** and address critical vulnerabilities
2. **Implement basic GDPR/CCPA compliance** framework
3. **Develop AI fallback strategy** to reduce OpenAI dependency
4. **Start fundraising outreach** for Series A
5. **Validate unit economics** with real customer cohort data

### Short-term (90 Days)
1. **Obtain SOC 2 Type I certification**
2. **Build competitive moats** through proprietary data and models
3. **Strengthen customer success program** to reduce churn
4. **Implement multi-region infrastructure** for scalability
5. **Hire go-to-market leadership** for sales and marketing

### Medium-term (6-12 Months)
1. **Achieve SOC 2 Type II certification**
2. **Prove product-market fit** with 100+ paying customers
3. **Reach cash flow positive** or close Series A
4. **Build strategic partnerships** for distribution
5. **Expand team** with key hires in sales, marketing, and customer success

## Information Gaps

**Critical Missing Information:**
- Actual customer acquisition costs and conversion metrics
- Churn rate and net revenue retention data
- Detailed unit economics with real cohort analysis
- Security audit results and compliance certifications
- Competitive win/loss analysis with specific competitor comparisons
- Detailed financial model with sensitivity analysis
- Team org chart and key person dependencies
- Vendor contracts and terms (especially OpenAI API costs at scale)

**Additional Information Needed:**
- Customer references and case studies
- Product roadmap with resource allocation
- Sales pipeline and conversion funnel metrics
- Technical architecture diagrams and scalability plans
- Disaster recovery and business continuity plans
- Intellectual property status (patents, trademarks)
- Advisory board composition and investor commitment levels"""


# Convenience function for risk analysis
def create_risk_agent(**kwargs) -> RiskAssessmentAgent:
    """
    Create a RiskAssessmentAgent with default configuration

    Args:
        **kwargs: Additional configuration parameters

    Returns:
        Configured RiskAssessmentAgent instance
    """
    return RiskAssessmentAgent(**kwargs)


if __name__ == "__main__":
    # Basic test of risk agent
    from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent
    from pathlib import Path
    from datetime import datetime

    # Create test document
    test_doc = StartupDocument(
        content=ParsedContent(
            sections=["Risks", "Challenges", "Competition"],
            raw_text="""
            The company faces intense competition from established players in the market.
            Regulatory compliance with GDPR and data privacy laws is a concern.
            High customer acquisition costs and unproven unit economics present financial risks.
            The technology relies heavily on third-party APIs which could change pricing.
            Market timing is uncertain as the SMB segment may not be ready for advanced analytics.
            """,
            word_count=60
        ),
        metadata=DocumentMetadata(
            file_path=Path("test_risks.md"),
            size=350,
            last_modified=datetime.now()
        ),
        document_type="risk_assessment"
    )

    try:
        # Test risk agent creation
        agent = create_risk_agent()
        print(f"✓ Created RiskAssessmentAgent: {agent.agent_name}")

        # Test specialized methods
        business_risks = agent.identify_business_risks(test_doc)
        print(f"✓ Business risks identified: {len(business_risks)} risks")

        market_risks = agent.identify_market_risks(test_doc)
        print(f"✓ Market risks identified: {len(market_risks)} risks")

        tech_risks = agent.identify_technical_risks(test_doc)
        print(f"✓ Technical risks identified: {len(tech_risks)} risks")

        regulatory_risks = agent.identify_regulatory_risks(test_doc)
        print(f"✓ Regulatory risks identified: {len(regulatory_risks)} risks")

        all_risks = {
            "business_risks": business_risks,
            "market_risks": market_risks,
            "tech_risks": tech_risks,
            "regulatory_risks": regulatory_risks
        }

        overall_risk = agent.assess_overall_risk_level(all_risks)
        print(f"✓ Overall risk level: {overall_risk}")

        mitigation_strategies = agent.generate_mitigation_strategies(all_risks)
        print(f"✓ Mitigation strategies generated: {len(mitigation_strategies)} categories")

        print("✓ RiskAssessmentAgent test completed successfully")

    except Exception as e:
        print(f"✗ RiskAssessmentAgent test failed: {e}")
        import traceback
        traceback.print_exc()
