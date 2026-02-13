"""
Technical Analysis Agent for Multi-Agent Startup Analysis System

Specialized agent for comprehensive technology stack and architecture evaluation.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel

from src.agents.base_agent import BaseStructuredAgent, AnalysisError
from src.models.document_models import StartupDocument
from src.models.analysis_models import TechnologyAnalysis
from src.utils.prompt_manager import PromptManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class TechnicalAnalysisAgent(BaseStructuredAgent):
    """
    Specialized agent for technical architecture and technology stack analysis

    Focuses on technology evaluation, IP assessment, architecture scalability,
    and technical feasibility for startup documents.
    """

    def __init__(self,
                 llm: Optional[BaseLanguageModel] = None,
                 temperature: float = 0.1,
                 **kwargs):
        """
        Initialize Technical Analysis Agent

        Args:
            llm: Language model instance
            temperature: Sampling temperature for technical analysis
            **kwargs: Additional parameters
        """
        super().__init__(
            agent_name="TechnicalAnalysisAgent",
            output_model=TechnologyAnalysis,
            llm=llm,
            temperature=temperature,
            **kwargs
        )

        # Initialize prompt manager
        self.prompt_manager = PromptManager()

        # Technical analysis frameworks
        self.tech_frameworks = {
            "architecture_patterns": [
                "microservices", "monolith", "serverless", "event-driven",
                "SOA", "cloud-native", "distributed", "peer-to-peer"
            ],
            "tech_stacks": [
                "MERN", "MEAN", "JAMstack", "LAMP", "Django", "Ruby on Rails",
                "Spring Boot", "ASP.NET", "FastAPI", "Next.js", "React Native"
            ],
            "cloud_platforms": [
                "AWS", "Azure", "Google Cloud", "DigitalOcean", "Heroku",
                "Vercel", "Netlify", "Cloudflare"
            ],
            "data_technologies": [
                "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Kafka",
                "Cassandra", "DynamoDB", "Firebase", "Supabase"
            ],
            "ai_ml_frameworks": [
                "TensorFlow", "PyTorch", "scikit-learn", "Keras", "Hugging Face",
                "OpenAI", "LangChain", "LlamaIndex"
            ]
        }

        logger.info("TechnicalAnalysisAgent initialized with tech frameworks")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for technical analysis

        Returns:
            Technical analysis system prompt
        """
        try:
            return self.prompt_manager.get_prompt_template("technical_analysis_system")
        except Exception as e:
            logger.warning(f"Could not load technical_analysis_system prompt: {e}")
            return """You are a senior technical architect specializing in startup technology evaluation.
                     Your expertise includes architecture assessment, technology stack evaluation,
                     scalability analysis, IP defensibility, and technical risk assessment. You excel
                     at identifying both technical strengths and potential architectural issues."""

    def get_analysis_prompt_template(self) -> PromptTemplate:
        """
        Get the main technical analysis prompt template

        Returns:
            Configured PromptTemplate for technical analysis
        """
        try:
            template_content = self.prompt_manager.get_prompt_template("technical_analysis_main")
            input_variables = [
                "document_content", "document_type", "word_count",
                "file_name", "sections"
            ]
        except Exception as e:
            logger.warning(f"Could not load technical_analysis_main prompt: {e}")
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
        Analyze the following startup document and provide a CONCISE technical analysis:

        DOCUMENT CONTENT:
        {document_content}

        DOCUMENT METADATA:
        - Type: {document_type}
        - Word Count: {word_count}
        - File Name: {file_name}
        - Sections: {sections}

        Provide your analysis in JSON format with these fields:

        {format_instructions}

        Focus ONLY on these 4 critical areas (be concise):
        1. TECH STACK & ARCHITECTURE: Technologies, frameworks, architecture pattern (2-3 sentences)
        2. SCALABILITY & SECURITY: Scalability assessment (high/medium/low), security measures, compliance (2-3 sentences)
        3. TOP 3 TECHNICAL RISKS: Critical technical risks only (3 sentences, one per risk)
        4. IP & INNOVATION: Proprietary technology, patents, unique technical moats (1-2 sentences)

        Keep analysis brief. Cite evidence. Note critical gaps only.
        """

    def _get_combined_markdown_template(self) -> str:
        """
        Get template for combined document analysis with markdown output

        Returns:
            Markdown template string for combined analysis
        """
        # Load from prompts.yaml for centralized management
        return self.prompt_manager.get_prompt_template("tech_analysis_combined")

    def analyze_tech_stack(self, document: StartupDocument) -> List[str]:
        """
        Identify technology stack components

        Args:
            document: Startup document to analyze

        Returns:
            List of identified technologies
        """
        content = document.content.raw_text.lower()
        identified_tech = []

        # Check for common technologies
        tech_keywords = {
            "frontend": ["react", "vue", "angular", "svelte", "next.js", "nuxt"],
            "backend": ["node.js", "python", "django", "flask", "fastapi", "ruby on rails", "spring boot", "express"],
            "database": ["postgresql", "mysql", "mongodb", "redis", "dynamodb", "cassandra", "elasticsearch"],
            "cloud": ["aws", "azure", "gcp", "google cloud", "cloudflare", "vercel", "heroku"],
            "ai_ml": ["tensorflow", "pytorch", "openai", "langchain", "hugging face", "scikit-learn"],
            "devops": ["docker", "kubernetes", "jenkins", "github actions", "ci/cd", "terraform"]
        }

        for category, keywords in tech_keywords.items():
            found = [tech for tech in keywords if tech in content]
            if found:
                identified_tech.extend([f"{category}: {tech}" for tech in found])

        logger.debug(f"Identified technologies: {identified_tech}")
        return identified_tech

    def assess_technical_scalability(self, document: StartupDocument) -> str:
        """
        Assess technical scalability based on document content

        Args:
            document: Startup document to analyze

        Returns:
            Scalability assessment (high/medium/low)
        """
        content = document.content.raw_text.lower()
        scalability_score = 0

        # Positive scalability indicators
        positive_indicators = [
            "microservices", "cloud-native", "serverless", "kubernetes",
            "auto-scaling", "load balancing", "distributed", "horizontal scaling",
            "cache", "cdn", "api-first", "containerized"
        ]

        # Negative scalability indicators
        negative_indicators = [
            "monolithic", "single server", "on-premise only", "tightly coupled",
            "no caching", "manual scaling", "legacy"
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

    def identify_technical_risks(self, document: StartupDocument) -> List[str]:
        """
        Identify technical risks and challenges

        Args:
            document: Startup document to analyze

        Returns:
            List of identified technical risks
        """
        content = document.content.raw_text.lower()
        risks = []

        risk_indicators = {
            "legacy_technology": ["legacy", "outdated", "deprecated", "end-of-life"],
            "vendor_lock": ["vendor lock-in", "proprietary platform", "single vendor"],
            "security_concerns": ["security vulnerabilities", "no encryption", "weak authentication"],
            "technical_debt": ["technical debt", "refactoring needed", "legacy code"],
            "scalability_limits": ["scalability issues", "performance bottleneck", "single point of failure"],
            "dependency_risk": ["third-party dependency", "external API dependency"]
        }

        for risk_type, indicators in risk_indicators.items():
            if any(indicator in content for indicator in indicators):
                risks.append(risk_type.replace("_", " ").title())

        return risks

    def evaluate_ip_innovation(self, document: StartupDocument) -> Dict[str, Any]:
        """
        Evaluate intellectual property and technical innovation

        Args:
            document: Startup document to analyze

        Returns:
            Dictionary of IP and innovation metrics
        """
        content = document.content.raw_text.lower()
        ip_metrics = {}

        # Check for patents
        if "patent" in content or "intellectual property" in content or "ip protection" in content:
            ip_metrics["has_patents"] = True

        # Check for proprietary technology
        proprietary_indicators = ["proprietary", "unique algorithm", "custom-built", "in-house developed"]
        if any(indicator in content for indicator in proprietary_indicators):
            ip_metrics["proprietary_tech"] = True

        # Check for AI/ML innovation
        ai_indicators = ["machine learning", "artificial intelligence", "deep learning", "neural network", "ai model"]
        if any(indicator in content for indicator in ai_indicators):
            ip_metrics["ai_innovation"] = True

        # Check for open source contributions
        if "open source" in content or "github" in content:
            ip_metrics["open_source"] = True

        return ip_metrics

    def analyze_combined_documents(self, pitch_deck_content: str, public_data_content: str) -> str:
        """
        Analyze startup using both pitch deck and public data together

        Args:
            pitch_deck_content: Content from pitch deck analysis
            public_data_content: Content from public data scraping

        Returns:
            Markdown formatted technical analysis
        """
        logger.info("Starting combined document technical analysis")

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

            logger.info("Combined document technical analysis completed successfully")
            return result.strip()

        except Exception as e:
            error_msg = str(e).lower()
            if "token" in error_msg or "length" in error_msg or "limit" in error_msg:
                logger.error(f"Token limit exceeded in combined document analysis: {e}")
                raise AnalysisError(f"Token limit exceeded. Try reducing document size: {e}")
            else:
                logger.error(f"Error in combined document technical analysis: {e}")
                raise AnalysisError(f"Combined technical analysis failed: {e}")

    def _get_mock_combined_analysis(self) -> str:
        """
        Generate mock combined technical analysis for testing

        Returns:
            Mock markdown analysis
        """
        return """# Technical Analysis Report

## Executive Summary
Based on the technical evaluation of both the pitch deck and public data, this startup demonstrates a solid modern technology stack with cloud-native architecture. The technical foundation leverages AI/ML capabilities with a scalable microservices approach, though some areas require further technical maturity and security hardening.

## Technology Stack & Tools
**Frontend Technologies:** React.js, TypeScript, Tailwind CSS, Next.js for SSR
**Backend Technologies:** Python FastAPI, Node.js microservices, GraphQL API layer
**AI/ML Stack:** TensorFlow, LangChain, OpenAI GPT-4 integration, custom models
**Database Systems:** PostgreSQL (primary), Redis (caching), MongoDB (document store)
**Development Tools:** VSCode, GitHub, Docker, Postman, Figma for design

## Architecture & Design
**Architecture Pattern:** Microservices architecture with API gateway
**Design Approach:** Event-driven architecture with asynchronous processing
**Scalability Design:** Horizontal scaling supported through containerization
**Service Communication:** REST APIs with GraphQL for complex queries, message queues for async tasks
**Modularity:** Well-separated concerns with clear service boundaries

## Infrastructure & Deployment
**Cloud Platform:** AWS (primary hosting and services)
**Containerization:** Docker containers with Docker Compose for local development
**Orchestration:** Kubernetes for production deployment and auto-scaling
**CI/CD:** GitHub Actions for automated testing and deployment
**Monitoring:** CloudWatch, Prometheus, Grafana for metrics and alerts
**CDN:** CloudFlare for content delivery and DDoS protection

## Security & Data Protection
**Authentication:** OAuth 2.0, JWT tokens, multi-factor authentication support
**Data Encryption:** TLS 1.3 for transit, AES-256 for data at rest
**Access Control:** Role-based access control (RBAC) implementation
**Security Practices:** Regular security audits, dependency scanning, OWASP compliance
**Data Privacy:** GDPR and CCPA compliant data handling procedures
**Backup & Recovery:** Automated daily backups with point-in-time recovery

## Scalability Assessment
**Overall Scalability:** High - Architecture designed for horizontal scaling
**Performance Considerations:** Caching strategies implemented, database query optimization needed
**Bottleneck Analysis:** Current bottleneck at API rate limiting, requires implementation of better queue management
**Load Handling:** Can handle 10,000+ concurrent users with current infrastructure
**Future Scaling:** Architecture supports expansion to multi-region deployment

## IP & Technical Innovation
**Proprietary Technology:** Custom AI models trained on industry-specific data
**Patents:** Patent pending for conversational AI query optimization algorithm
**Technical Moats:** Proprietary data preprocessing pipeline, unique ML model architecture
**Innovation Level:** Moderate to high - combines existing technologies in novel ways
**Open Source Contributions:** Several internal tools released as open source projects

## Development Practices
**Methodology:** Agile/Scrum with 2-week sprints
**Code Quality:** Code reviews required, 80%+ test coverage target, linting enforced
**Testing:** Unit tests, integration tests, end-to-end testing with Cypress
**Documentation:** API documentation with Swagger/OpenAPI, technical wiki maintained
**Version Control:** Git with feature branching and pull request workflows
**Quality Assurance:** Automated testing in CI pipeline, staging environment for pre-production testing

## Data Architecture
**Database Design:** Normalized relational schema with document store for unstructured data
**Data Pipeline:** ETL processes using Apache Airflow for data orchestration
**Analytics Infrastructure:** Data warehouse using Amazon Redshift for analytics
**Data Governance:** Data lineage tracking, PII detection and masking
**Performance:** Indexed queries, partitioned tables for large datasets

## AI/ML Implementation
**ML Models:** Custom NLP models, fine-tuned GPT-4 for domain-specific tasks
**Training Infrastructure:** GPU-enabled instances for model training (AWS EC2 P3)
**Model Deployment:** MLOps pipeline with versioning and A/B testing capabilities
**Inference:** Real-time prediction API with sub-second latency
**Continuous Learning:** Feedback loop for model improvement based on user interactions

## Technical Risks & Challenges
**Architecture Risks:**
- Microservices complexity may increase operational overhead
- Inter-service communication latency needs monitoring

**Technology Choices:**
- Heavy reliance on OpenAI API creates vendor dependency risk
- Need for fallback solutions if third-party AI services face outages

**Technical Debt:**
- Some legacy code from MVP phase requires refactoring
- Database schema optimization needed for improved query performance

**Dependencies:**
- Critical dependency on AWS services - multi-cloud strategy recommended
- Multiple third-party APIs create integration maintenance burden

## Integration & APIs
**API Design:** RESTful API with OpenAPI specification, GraphQL for complex queries
**Third-Party Integrations:** Stripe, SendGrid, Twilio, Google Analytics, Segment
**Extensibility:** Plugin architecture supports custom integrations
**Developer Platform:** Public API with SDK libraries (Python, JavaScript, Ruby)
**Webhook Support:** Event-driven webhooks for real-time notifications

## Performance & Reliability
**Performance Metrics:** 99.9% uptime target, <200ms average API response time
**Optimization:** CDN usage, database query optimization, lazy loading, code splitting
**Monitoring:** Real-time monitoring with alerts for anomalies and errors
**SLAs:** Service level agreements defined for enterprise customers
**Disaster Recovery:** Multi-AZ deployment, automated failover, 4-hour RTO target

## Technical Recommendations
1. **Multi-Cloud Strategy:** Implement cloud-agnostic design to reduce vendor lock-in risk
2. **Security Hardening:** Conduct third-party security audit and penetration testing
3. **Performance Optimization:** Implement advanced caching strategies and database sharding
4. **Observability:** Enhanced monitoring with distributed tracing (e.g., Jaeger, OpenTelemetry)
5. **AI/ML Resilience:** Develop fallback models to reduce dependency on OpenAI API
6. **Technical Debt:** Allocate 20% of sprint capacity to address technical debt
7. **Documentation:** Improve architectural documentation and runbooks for operations
8. **Testing:** Increase integration test coverage, implement chaos engineering for resilience

## Information Gaps
**Infrastructure Details:**
- Exact server specifications and resource allocation
- Cost breakdown of cloud infrastructure
- Detailed disaster recovery procedures and RTO/RPO targets

**Development Metrics:**
- Team size and technical expertise distribution
- Development velocity and sprint metrics
- Bug tracking and resolution time metrics

**Security Details:**
- Complete security compliance certifications (SOC 2, ISO 27001, etc.)
- Incident response procedures and history
- Third-party security audit results

**Performance Data:**
- Production performance metrics and benchmarks
- Load testing results and capacity limits
- Historical uptime and incident reports"""


# Convenience function for technical analysis
def create_tech_agent(**kwargs) -> TechnicalAnalysisAgent:
    """
    Create a TechnicalAnalysisAgent with default configuration

    Args:
        **kwargs: Additional configuration parameters

    Returns:
        Configured TechnicalAnalysisAgent instance
    """
    return TechnicalAnalysisAgent(**kwargs)


if __name__ == "__main__":
    # Basic test of technical agent
    from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent
    from pathlib import Path
    from datetime import datetime

    # Create test document
    test_doc = StartupDocument(
        content=ParsedContent(
            sections=["Technology", "Architecture", "Stack"],
            raw_text="""
            Our platform is built on a modern microservices architecture using Python and FastAPI.
            We leverage cloud-native technologies including Docker and Kubernetes for deployment.
            The tech stack includes React for the frontend, PostgreSQL for the database,
            and Redis for caching. We use AWS for our cloud infrastructure with auto-scaling capabilities.
            Our AI/ML models are built with TensorFlow and deployed using our custom MLOps pipeline.
            """,
            word_count=65
        ),
        metadata=DocumentMetadata(
            file_path=Path("test_tech.md"),
            size=400,
            last_modified=datetime.now()
        ),
        document_type="technical_overview"
    )

    try:
        # Test technical agent creation
        agent = create_tech_agent()
        print(f"✓ Created TechnicalAnalysisAgent: {agent.agent_name}")

        # Test specialized methods
        tech_stack = agent.analyze_tech_stack(test_doc)
        print(f"✓ Technology stack identified: {tech_stack}")

        scalability = agent.assess_technical_scalability(test_doc)
        print(f"✓ Technical scalability assessment: {scalability}")

        risks = agent.identify_technical_risks(test_doc)
        print(f"✓ Technical risks: {risks}")

        ip_metrics = agent.evaluate_ip_innovation(test_doc)
        print(f"✓ IP & Innovation metrics: {ip_metrics}")

        print("✓ TechnicalAnalysisAgent test completed successfully")

    except Exception as e:
        print(f"✗ TechnicalAnalysisAgent test failed: {e}")
        import traceback
        traceback.print_exc()
