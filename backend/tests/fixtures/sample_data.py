"""
Sample data fixtures for testing the multi-agent startup analysis system
Task 2: Data Models and Schema Definition - Sample data fixtures
"""

from datetime import datetime
from typing import Dict, Any
from src.models.document_models import DocumentMetadata, ParsedContent, StartupDocument
from src.models.analysis_models import (
    BusinessAnalysis, FinancialAnalysis, MarketAnalysis,
    TechnologyAnalysis, RiskAnalysis
)
from src.models.output_models import (
    GapAnalysis, Question, QuestionCategory, InvestorQuestionnaire,
    Priority, QuestionType
)


class SampleDataFixtures:
    """Collection of sample data for testing"""

    @staticmethod
    def get_sample_metadata() -> DocumentMetadata:
        """Get sample document metadata"""
        return DocumentMetadata(
            file_path="/sample/data/pitch_deck.md",
            size=2048,
            last_modified=datetime(2024, 1, 15, 10, 30, 0),
            creation_time=datetime(2024, 1, 10, 9, 0, 0),
            file_extension=".md",
            encoding="utf-8"
        )

    @staticmethod
    def get_sample_content() -> ParsedContent:
        """Get sample parsed content"""
        return ParsedContent(
            sections={
                "Executive Summary": "TechStart is an AI-powered fintech platform that revolutionizes personal finance management for millennials and Gen Z users.",
                "Problem Statement": "Traditional banking and financial services are outdated, complex, and don't meet the needs of digital-native users.",
                "Solution": "Our AI-driven platform provides personalized financial insights, automated savings, and intelligent investment recommendations.",
                "Market Opportunity": "The global fintech market is valued at $127 billion and growing at 25% CAGR.",
                "Business Model": "Freemium subscription model with premium features and transaction-based revenue.",
                "Financial Projections": "Projecting $2M ARR by year 2, with 40% gross margins and path to profitability by year 3.",
                "Team": "Experienced team with backgrounds from Goldman Sachs, Google, and successful fintech startups.",
                "Funding Ask": "Seeking $3M Series A to accelerate user acquisition and product development."
            },
            raw_text="TechStart is an AI-powered fintech platform that revolutionizes personal finance management. Traditional banking services are outdated and complex. Our solution provides personalized insights and automated savings. The fintech market is growing rapidly at 25% CAGR. We use a freemium model with premium features. Projecting significant revenue growth. Our team has extensive experience. Seeking Series A funding.",
            word_count=58,
            paragraph_count=8,
            headers=["Executive Summary", "Problem Statement", "Solution", "Market Opportunity", "Business Model", "Financial Projections", "Team", "Funding Ask"],
            tables=[
                {
                    "title": "Financial Projections",
                    "data": [
                        {"Year": "1", "Revenue": "$500K", "Users": "10K"},
                        {"Year": "2", "Revenue": "$2M", "Users": "50K"},
                        {"Year": "3", "Revenue": "$8M", "Users": "200K"}
                    ]
                }
            ],
            links=["https://techstart.com", "https://market-research.com/fintech"]
        )

    @staticmethod
    def get_sample_document() -> StartupDocument:
        """Get sample startup document"""
        return StartupDocument(
            content=SampleDataFixtures.get_sample_content(),
            metadata=SampleDataFixtures.get_sample_metadata(),
            document_type="pitch_deck",
            title="TechStart - AI-Powered Fintech Platform",
            author="Sarah Johnson, CEO",
            version="2.1",
            tags=["fintech", "ai", "series-a", "b2c"],
            language="en",
            processed_at=datetime(2024, 1, 20, 14, 0, 0)
        )

    @staticmethod
    def get_sample_business_analysis() -> BusinessAnalysis:
        """Get sample business analysis"""
        return BusinessAnalysis(
            revenue_streams=[
                "Monthly subscription fees ($9.99/month premium)",
                "Transaction fees (0.5% on investments)",
                "Partner referral commissions",
                "Data insights API licensing"
            ],
            scalability="high",
            competitive_position="Strong differentiation through AI personalization and user experience focus",
            business_model="Freemium SaaS with transaction-based revenue streams",
            target_market=["Millennials (25-40)", "Gen Z (18-25)", "Tech-savvy professionals"],
            value_proposition="Simplified, AI-powered personal finance that adapts to individual spending patterns and goals",
            growth_strategy="Viral user acquisition through social features and referral programs",
            partnerships=["Regional banks", "Investment platforms", "Financial education platforms"],
            regulatory_considerations=["PCI DSS compliance", "Financial data privacy regulations", "Investment advisory licensing"]
        )

    @staticmethod
    def get_sample_financial_analysis() -> FinancialAnalysis:
        """Get sample financial analysis"""
        return FinancialAnalysis(
            projections={
                "revenue_y1": 500000,
                "revenue_y2": 2000000,
                "revenue_y3": 8000000,
                "users_y1": 10000,
                "users_y2": 50000,
                "users_y3": 200000,
                "expenses_y1": 800000,
                "expenses_y2": 1400000,
                "expenses_y3": 4800000
            },
            metrics={
                "gross_margin": 0.85,
                "cac": 45,
                "ltv": 360,
                "ltv_cac_ratio": 8.0,
                "monthly_churn": 0.05,
                "conversion_rate": 0.12
            },
            funding_requirements={
                "series_a": 3000000,
                "total_needed": 5000000,
                "use_of_funds_marketing": 40,
                "use_of_funds_product": 35,
                "use_of_funds_operations": 25
            },
            revenue_model="Freemium subscription with 12% conversion rate to premium tier",
            unit_economics={
                "arpu": 118,
                "monthly_premium_revenue": 9.99,
                "transaction_revenue_per_user": 2.50
            },
            burn_rate=85000,
            runway=18,
            profitability_timeline="Month 28 - break-even expected",
            financial_risks=[
                "Customer acquisition costs higher than projected",
                "Lower than expected conversion rates",
                "Regulatory compliance costs"
            ]
        )

    @staticmethod
    def get_sample_market_analysis() -> MarketAnalysis:
        """Get sample market analysis"""
        return MarketAnalysis(
            market_size={
                "tam": "$127B global fintech market",
                "sam": "$25B personal finance management",
                "som": "$2.5B addressable with current strategy"
            },
            competition=[
                {"name": "Mint", "strength": "Market leader, comprehensive features", "weakness": "Outdated UX, no AI"},
                {"name": "YNAB", "strength": "Strong budgeting focus", "weakness": "Complex for casual users"},
                {"name": "Personal Capital", "strength": "Investment tracking", "weakness": "Targets high net worth"},
                {"name": "Acorns", "strength": "Micro-investing", "weakness": "Limited financial management"}
            ],
            positioning="AI-first personal finance for digital natives with focus on simplicity and automation",
            market_trends=[
                "Increasing demand for automated financial management",
                "Growing adoption of AI in fintech",
                "Shift toward mobile-first financial services",
                "Rising financial literacy awareness among younger demographics"
            ],
            customer_segments=[
                {"segment": "Tech-savvy millennials", "size": "25M users", "characteristics": "High smartphone usage, early adopters"},
                {"segment": "Gen Z professionals", "size": "15M users", "characteristics": "Digital-first, value automation"},
                {"segment": "Young families", "size": "12M users", "characteristics": "Need budgeting help, goal-oriented"}
            ],
            go_to_market_strategy="Digital marketing through social media, influencer partnerships, and content marketing",
            geographic_focus=["United States", "Canada", "United Kingdom"],
            market_barriers=["Regulatory compliance", "Customer trust and security concerns", "Switching costs from existing solutions"],
            market_opportunities=["Open banking adoption", "Increased financial awareness post-pandemic", "Growing gig economy"]
        )

    @staticmethod
    def get_sample_technology_analysis() -> TechnologyAnalysis:
        """Get sample technology analysis"""
        return TechnologyAnalysis(
            tech_stack=[
                "React Native (mobile app)",
                "Node.js/Express (backend API)",
                "Python/TensorFlow (AI/ML)",
                "PostgreSQL (primary database)",
                "Redis (caching)",
                "AWS (cloud infrastructure)",
                "Docker/Kubernetes (containerization)"
            ],
            roadmap={
                "Q1": ["Enhanced AI recommendations", "Social features launch"],
                "Q2": ["Investment platform integration", "Advanced analytics dashboard"],
                "Q3": ["International expansion features", "Open banking integration"],
                "Q4": ["Business accounts", "Advanced AI financial coach"]
            },
            ip_assets=[
                {"type": "Patent application", "description": "AI-powered spending categorization algorithm", "status": "Pending"},
                {"type": "Trademark", "description": "TechStart brand and logo", "status": "Registered"},
                {"type": "Trade secret", "description": "User behavior prediction models", "status": "Active"}
            ],
            scalability_assessment="excellent",
            security_measures=[
                "End-to-end encryption for financial data",
                "Multi-factor authentication",
                "Regular security audits and penetration testing",
                "SOC 2 Type II compliance",
                "PCI DSS Level 1 certification"
            ],
            data_strategy="First-party data collection with user consent, anonymous analytics, and AI model training",
            infrastructure={
                "cloud_provider": "AWS",
                "deployment": "Microservices architecture with auto-scaling",
                "monitoring": "CloudWatch, DataDog",
                "ci_cd": "GitHub Actions with automated testing"
            },
            technical_debt="Minimal - well-architected system with regular refactoring",
            development_team={
                "size": 8,
                "backend_engineers": 3,
                "frontend_engineers": 2,
                "ai_engineers": 2,
                "devops_engineer": 1,
                "experience_level": "Senior (5+ years average)"
            }
        )

    @staticmethod
    def get_sample_risk_analysis() -> RiskAnalysis:
        """Get sample risk analysis"""
        return RiskAnalysis(
            business_risks=[
                {"description": "High customer acquisition costs may impact unit economics", "severity": "medium", "probability": "medium"},
                {"description": "Intense competition from established players", "severity": "high", "probability": "high"},
                {"description": "Economic downturn affecting discretionary spending", "severity": "high", "probability": "low"}
            ],
            market_risks=[
                {"description": "Regulatory changes in financial services", "severity": "high", "probability": "medium"},
                {"description": "Changes in consumer behavior toward financial apps", "severity": "medium", "probability": "low"},
                {"description": "Data privacy regulations limiting data usage", "severity": "medium", "probability": "medium"}
            ],
            tech_risks=[
                {"description": "AI model bias or accuracy issues", "severity": "high", "probability": "low"},
                {"description": "Security breach exposing user financial data", "severity": "critical", "probability": "low"},
                {"description": "Third-party API dependencies and reliability", "severity": "medium", "probability": "medium"}
            ],
            financial_risks=[
                {"description": "Burn rate higher than projections", "severity": "high", "probability": "medium"},
                {"description": "Lower than expected conversion rates", "severity": "medium", "probability": "medium"},
                {"description": "Difficulty raising follow-on funding", "severity": "high", "probability": "low"}
            ],
            regulatory_risks=[
                {"description": "Changes in financial advisory regulations", "severity": "medium", "probability": "medium"},
                {"description": "New data protection requirements", "severity": "medium", "probability": "high"},
                {"description": "Banking partnership compliance issues", "severity": "high", "probability": "low"}
            ],
            operational_risks=[
                {"description": "Key team member departure", "severity": "medium", "probability": "medium"},
                {"description": "Scaling customer support effectively", "severity": "medium", "probability": "high"},
                {"description": "Technical infrastructure scaling challenges", "severity": "medium", "probability": "low"}
            ],
            mitigation_strategies={
                "business": ["Diversified acquisition channels", "Strong product differentiation", "Flexible business model"],
                "market": ["Proactive regulatory monitoring", "Diverse geographic markets", "Privacy-first approach"],
                "technical": ["Rigorous testing and validation", "Multi-layered security", "Redundant systems"],
                "financial": ["Conservative cash management", "Multiple funding sources", "Regular financial monitoring"],
                "regulatory": ["Legal advisory team", "Compliance-first development", "Industry association participation"],
                "operational": ["Knowledge documentation", "Automated support systems", "Scalable architecture"]
            },
            overall_risk_level="medium"
        )

    @staticmethod
    def get_sample_gap_analysis() -> GapAnalysis:
        """Get sample gap analysis"""
        return GapAnalysis(
            critical_gaps=[
                {
                    "category": "financial",
                    "description": "Missing detailed cash flow projections beyond year 1",
                    "impact": "Investors cannot assess long-term sustainability and funding needs"
                },
                {
                    "category": "legal",
                    "description": "No mention of intellectual property strategy or existing IP",
                    "impact": "Unable to evaluate competitive moats and defensibility"
                }
            ],
            important_gaps=[
                {
                    "category": "market",
                    "description": "Limited competitive analysis depth - missing feature comparisons",
                    "impact": "Difficult to assess true competitive advantages"
                },
                {
                    "category": "operations",
                    "description": "Scaling plan lacks specific operational metrics and milestones",
                    "impact": "Concerns about execution capability at scale"
                },
                {
                    "category": "team",
                    "description": "Advisory board and key hires not mentioned",
                    "impact": "Missing insight into strategic guidance and talent acquisition plan"
                }
            ],
            minor_gaps=[
                {
                    "category": "product",
                    "description": "User feedback and validation data not included",
                    "impact": "Limited evidence of product-market fit validation"
                },
                {
                    "category": "partnerships",
                    "description": "Partnership agreements and timeline not detailed",
                    "impact": "Uncertainty about strategic relationship development"
                }
            ],
            analysis_date=datetime(2024, 1, 20, 15, 30, 0),
            document_coverage=78.5,
            overall_completeness="good",
            recommendations=[
                "Provide detailed 3-year cash flow projections with monthly granularity for year 1",
                "Include comprehensive IP strategy and existing patent/trademark portfolio",
                "Add detailed competitive feature matrix with key differentiators",
                "Define specific operational KPIs and scaling milestones",
                "List advisory board members and planned key hires with timelines",
                "Include customer validation data and user feedback metrics"
            ]
        )

    @staticmethod
    def get_sample_questions() -> Dict[str, Question]:
        """Get sample questions for different categories"""
        return {
            "business_model": Question(
                id="bus_001",
                text="Can you provide a detailed breakdown of your revenue streams and explain how each scales with user growth?",
                question_type=QuestionType.OPEN_ENDED,
                rationale="Understanding revenue scalability is crucial for assessing investment potential and long-term viability",
                expected_answer_guidance="Look for clear monetization strategy with multiple revenue streams and evidence of scalability",
                follow_up_questions=[
                    "What percentage of revenue comes from each stream currently?",
                    "Which revenue stream has the highest gross margin?",
                    "How do you plan to optimize pricing over time?"
                ],
                related_documents=["business_plan.pdf", "financial_projections.xlsx"]
            ),
            "market_validation": Question(
                id="mkt_001",
                text="What evidence do you have of product-market fit and how are you measuring user satisfaction?",
                question_type=QuestionType.OPEN_ENDED,
                rationale="Product-market fit validation reduces execution risk and indicates market demand",
                expected_answer_guidance="Strong metrics showing user engagement, retention, and satisfaction with quantitative data",
                follow_up_questions=[
                    "What is your current Net Promoter Score?",
                    "How has user retention changed over the past 6 months?",
                    "What do churned users tell you in exit interviews?"
                ]
            ),
            "financial_health": Question(
                id="fin_001",
                text="What is your current monthly burn rate and how many months of runway do you have?",
                question_type=QuestionType.NUMERIC,
                rationale="Understanding cash position and runway is essential for investment timing and risk assessment",
                expected_answer_guidance="Clear numbers with breakdown of major expense categories and realistic timeline",
                related_documents=["cash_flow_statement.xlsx", "budget_breakdown.pdf"]
            ),
            "competition": Question(
                id="cmp_001",
                text="How do you differentiate from direct competitors and what are your sustainable competitive advantages?",
                question_type=QuestionType.OPEN_ENDED,
                rationale="Competitive differentiation determines long-term market position and defensibility",
                expected_answer_guidance="Unique value propositions with barriers to replication by competitors",
                follow_up_questions=[
                    "Which competitor do you consider your biggest threat?",
                    "How would you respond if a competitor copied your key features?",
                    "What would it take for a new entrant to replicate your offering?"
                ]
            )
        }

    @staticmethod
    def get_sample_questionnaire() -> InvestorQuestionnaire:
        """Get sample investor questionnaire"""
        questions = SampleDataFixtures.get_sample_questions()

        business_category = QuestionCategory(
            category_name="Business Model & Strategy",
            questions=[questions["business_model"], questions["competition"]],
            priority=Priority.CRITICAL,
            description="Questions about core business model, strategy, and competitive positioning",
            estimated_time=20,
            category_weight=2.5
        )

        market_category = QuestionCategory(
            category_name="Market & Validation",
            questions=[questions["market_validation"]],
            priority=Priority.HIGH,
            description="Questions about market opportunity and product-market fit validation",
            estimated_time=15,
            category_weight=2.0
        )

        financial_category = QuestionCategory(
            category_name="Financial Position",
            questions=[questions["financial_health"]],
            priority=Priority.CRITICAL,
            description="Questions about current financial status and projections",
            estimated_time=10,
            category_weight=2.5
        )

        return InvestorQuestionnaire(
            categories=[business_category, market_category, financial_category],
            total_questions=4,
            metadata={
                "analysis_source": "techstart_pitch_deck",
                "startup_stage": "series_a",
                "industry": "fintech",
                "generated_by": "multi_agent_analyzer_v1"
            },
            version="1.0",
            target_audience="venture_capital",
            estimated_completion_time=45,
            instructions="Please provide detailed answers with specific metrics and examples where possible. This questionnaire is designed to help us understand your startup's investment readiness and potential."
        )

    @staticmethod
    def get_complete_sample_dataset() -> Dict[str, Any]:
        """Get complete sample dataset for comprehensive testing"""
        return {
            "document": SampleDataFixtures.get_sample_document(),
            "business_analysis": SampleDataFixtures.get_sample_business_analysis(),
            "financial_analysis": SampleDataFixtures.get_sample_financial_analysis(),
            "market_analysis": SampleDataFixtures.get_sample_market_analysis(),
            "technology_analysis": SampleDataFixtures.get_sample_technology_analysis(),
            "risk_analysis": SampleDataFixtures.get_sample_risk_analysis(),
            "gap_analysis": SampleDataFixtures.get_sample_gap_analysis(),
            "questionnaire": SampleDataFixtures.get_sample_questionnaire()
        }