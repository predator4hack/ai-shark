"""
Example: Business Analysis with Groq API Integration
Demonstrates how to use the AI-Shark system with Groq models for startup analysis
"""

import os
from datetime import datetime
from pathlib import Path

# Set Groq as the provider (before importing other modules)
os.environ['LLM_PROVIDER'] = 'groq'
os.environ['GROQ_MODEL'] = 'llama3-8b-8192'

from src.agents.business_agent import BusinessAnalysisAgent, create_business_agent
from src.utils.llm_setup import create_groq_llm, create_google_llm, create_mock_llm
from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent
from src.models.analysis_models import BusinessAnalysis

def create_sample_startup_document():
    """Create a sample startup document for analysis"""
    return StartupDocument(
        content=ParsedContent(
            sections={
                "Executive Summary": "AI-powered financial analytics platform for SMBs",
                "Problem Statement": "Small businesses lack access to sophisticated financial insights that larger companies enjoy",
                "Solution": "Our SaaS platform provides AI-driven financial analysis, cash flow forecasting, and business intelligence",
                "Business Model": "Tiered subscription model: Basic ($99/month), Professional ($299/month), Enterprise (custom pricing)",
                "Market Opportunity": "The SMB financial software market is valued at $12B annually with 15% YoY growth",
                "Traction": "150 paying customers, $450K ARR, 25% month-over-month growth",
                "Technology": "Cloud-native architecture built on Python, React, and PostgreSQL with proprietary ML algorithms",
                "Competition": "Compete with QuickBooks and Xero but differentiate through AI-powered insights and predictive analytics",
                "Team": "Founded by ex-Stripe and ex-Palantir engineers with deep fintech and ML expertise",
                "Funding": "Raising $5M Series A to accelerate product development and expand sales team"
            },
            raw_text="""
            Executive Summary: We are building an AI-powered financial analytics platform specifically designed for small and medium businesses (SMBs).

            Problem Statement: Small businesses lack access to the sophisticated financial insights and predictive analytics that larger companies enjoy. Most SMBs rely on basic accounting software that provides historical data but offers little forward-looking intelligence.

            Solution: Our SaaS platform provides AI-driven financial analysis, automated cash flow forecasting, and business intelligence dashboards. We make enterprise-grade financial analytics accessible and affordable for SMBs.

            Business Model: We operate on a tiered subscription model:
            - Basic Plan: $99/month for up to 1,000 transactions
            - Professional Plan: $299/month for up to 10,000 transactions with advanced analytics
            - Enterprise Plan: Custom pricing for unlimited transactions and white-label options

            We also charge transaction fees for premium AI features and offer API access for integration partners.

            Market Opportunity: The SMB financial software market is valued at $12B annually and growing at 15% YoY. Our addressable market includes 30 million SMBs in North America alone.

            Traction: We have 150 paying customers generating $450K in annual recurring revenue (ARR). We're experiencing 25% month-over-month growth with a 95% customer retention rate.

            Technology: Built on a cloud-native architecture using Python, React, and PostgreSQL. Our proprietary machine learning algorithms analyze transaction patterns to provide predictive insights. We've filed 2 patents for our financial forecasting technology.

            Competition: We compete with traditional players like QuickBooks and Xero but differentiate through our AI-powered insights, predictive analytics, and SMB-focused user experience.

            Team: Founded by experienced engineers from Stripe and Palantir with deep expertise in fintech and machine learning. Our team has previously built and scaled financial products serving millions of users.

            Funding: Currently raising a $5M Series A round to accelerate product development, expand our sales and marketing team, and pursue strategic partnerships with banks and accounting firms.
            """,
            word_count=298
        ),
        metadata=DocumentMetadata(
            file_path="fintech_startup_pitch.md",
            size=2500,
            last_modified=datetime.now(),
            file_extension=".md"
        ),
        document_type="pitch_deck"
    )

def demonstrate_groq_analysis():
    """Demonstrate business analysis using Groq API"""
    print("🚀 AI-Shark Business Analysis with Groq Integration")
    print("=" * 60)

    # Create sample startup document
    startup_doc = create_sample_startup_document()
    print(f"📄 Analyzing: {startup_doc.metadata.file_path}")
    print(f"📊 Document Type: {startup_doc.document_type}")
    print(f"📝 Word Count: {startup_doc.content.word_count}")
    print(f"📋 Sections: {len(startup_doc.content.sections)}")

    # Method 1: Using mock LLM (for demonstration without API key)
    print("\n🤖 Method 1: Using Mock LLM (Demo Mode)")
    print("-" * 40)

    mock_response = """{
        "revenue_streams": [
            "Tiered subscription fees (Basic, Professional, Enterprise)",
            "Transaction fees for premium AI features",
            "API access fees for integration partners"
        ],
        "scalability": "high",
        "competitive_position": "Strong AI differentiation in SMB market vs traditional accounting software",
        "business_model": "SaaS with tiered subscription pricing and usage-based premium features",
        "value_proposition": "AI-powered financial insights and predictive analytics for SMBs",
        "target_market": [
            "Small and medium businesses (SMBs)",
            "Accounting firms serving SMBs",
            "Integration partners and banks"
        ],
        "growth_strategy": "Product development acceleration and sales team expansion via Series A funding",
        "partnerships": [
            "Banks and financial institutions",
            "Accounting firms",
            "Integration partners for API access"
        ],
        "regulatory_considerations": [
            "Financial data protection and privacy",
            "Banking regulations for financial analytics",
            "Data security compliance requirements"
        ]
    }"""

    try:
        # Create business agent with mock LLM
        mock_llm = create_mock_llm([mock_response])
        agent = BusinessAnalysisAgent(llm=mock_llm)

        print(f"Agent: {agent.agent_name}")
        print(f"LLM Type: Mock LLM (simulating Groq)")

        # Perform domain-specific analysis
        print("\n🔍 Domain-Specific Analysis:")
        revenue_streams = agent.analyze_revenue_streams(startup_doc)
        scalability = agent.assess_scalability(startup_doc)
        competitive_advantages = agent.identify_competitive_advantages(startup_doc)
        business_metrics = agent.extract_business_metrics(startup_doc)

        print(f"Revenue Streams: {revenue_streams}")
        print(f"Scalability Assessment: {scalability}")
        print(f"Competitive Advantages: {competitive_advantages}")
        print(f"Business Metrics: {list(business_metrics.keys())}")

        # Full structured analysis
        print("\n📈 Structured Business Analysis:")
        analysis_result = agent.analyze(startup_doc)

        if isinstance(analysis_result, BusinessAnalysis):
            print(f"✅ Analysis completed successfully")
            print(f"Revenue Streams: {len(analysis_result.revenue_streams)} identified")
            print(f"Target Markets: {len(analysis_result.target_market)} segments")
            print(f"Partnerships: {len(analysis_result.partnerships)} strategic relationships")

            # Generate business insights
            insights = agent.get_business_insights(analysis_result)
            print(f"\n💡 Business Insights:")
            print(f"Revenue Model Strength: {insights['revenue_model_assessment']['strength']}")
            print(f"Growth Potential: {insights['growth_potential']}")
            print(f"Competitive Strength: {insights['competitive_strength']}")
            print(f"Risk Factors: {len(insights['risk_factors'])} identified")

    except Exception as e:
        print(f"❌ Mock analysis failed: {e}")

    # Method 2: Real Groq API (if API key is available)
    print("\n🔥 Method 2: Real Groq API Integration")
    print("-" * 40)

    try:
        # Check if Groq API key is available
        groq_api_key = os.getenv('GROQ_API_KEY')
        if groq_api_key:
            print("✅ Groq API key found - creating real Groq LLM")

            # Create real Groq LLM
            groq_llm = create_groq_llm(
                model_name="llama3-8b-8192",
                temperature=0.1,
                max_tokens=4096
            )

            # Create business agent with real Groq LLM
            groq_agent = BusinessAnalysisAgent(llm=groq_llm)

            print(f"Agent: {groq_agent.agent_name}")
            print(f"LLM Provider: Groq")
            print(f"Model: llama3-8b-8192")

            # Note: In a real scenario, you would call groq_agent.analyze(startup_doc)
            print("🔮 Ready for real Groq API analysis")
            print("   (Uncomment the analysis call to run with real API)")

            # Uncomment the following lines to run real analysis:
            # real_analysis = groq_agent.analyze(startup_doc)
            # print(f"Real Groq Analysis: {type(real_analysis).__name__}")

        else:
            print("⚠️  Groq API key not found in environment")
            print("   Set GROQ_API_KEY environment variable to use real Groq API")

    except Exception as e:
        print(f"❌ Groq API integration error: {e}")

    # Method 3: Provider Comparison
    print("\n⚖️  Method 3: Provider Comparison")
    print("-" * 40)

    providers = {
        "google": {
            "create_func": create_google_llm,
            "model": "gemini-1.5-flash",
            "strengths": ["Multimodal capabilities", "Large context window", "Strong reasoning"]
        },
        "groq": {
            "create_func": create_groq_llm,
            "model": "llama3-8b-8192",
            "strengths": ["High-speed inference", "Cost-effective", "Open-source models"]
        }
    }

    for provider, config in providers.items():
        print(f"\n🔧 {provider.upper()} Configuration:")
        print(f"   Model: {config['model']}")
        print(f"   Strengths: {', '.join(config['strengths'])}")
        print(f"   Function: {config['create_func'].__name__}")

def demonstrate_configuration_options():
    """Show different configuration options"""
    print("\n⚙️  Configuration Options")
    print("=" * 60)

    configurations = [
        {
            "name": "Google AI (Default)",
            "env_vars": {
                "LLM_PROVIDER": "google",
                "GOOGLE_API_KEY": "your_google_api_key",
                "GEMINI_MODEL": "gemini-1.5-flash"
            }
        },
        {
            "name": "Groq (High-Speed)",
            "env_vars": {
                "LLM_PROVIDER": "groq",
                "GROQ_API_KEY": "your_groq_api_key",
                "GROQ_MODEL": "llama3-8b-8192"
            }
        },
        {
            "name": "Groq (Large Model)",
            "env_vars": {
                "LLM_PROVIDER": "groq",
                "GROQ_API_KEY": "your_groq_api_key",
                "GROQ_MODEL": "llama3-70b-8192"
            }
        }
    ]

    for config in configurations:
        print(f"\n📋 {config['name']}:")
        for var, value in config['env_vars'].items():
            print(f"   export {var}={value}")

def main():
    """Run the complete Groq integration demonstration"""
    try:
        demonstrate_groq_analysis()
        demonstrate_configuration_options()

        print("\n" + "=" * 60)
        print("🎉 Groq Integration Demonstration Complete!")
        print("\n📚 Key Features Demonstrated:")
        print("   ✅ Multi-provider LLM support (Google AI + Groq)")
        print("   ✅ Business analysis with domain expertise")
        print("   ✅ Structured output using Pydantic models")
        print("   ✅ Comprehensive business insights generation")
        print("   ✅ Flexible configuration management")
        print("   ✅ Provider-agnostic agent architecture")

        print("\n🚀 Next Steps:")
        print("   1. Set up your Groq API key: export GROQ_API_KEY=your_key")
        print("   2. Switch to Groq: export LLM_PROVIDER=groq")
        print("   3. Choose your model: export GROQ_MODEL=llama3-8b-8192")
        print("   4. Run real analysis with: agent.analyze(document)")

    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()