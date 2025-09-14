"""
AI-Shark Demo: End-to-End Startup Analysis Pipeline

This demo script demonstrates the complete AI-Shark analysis pipeline:
1. Loads documents from results directory (analysis_results.md, public_data.md)
2. Processes them using the document loader
3. Runs business analysis using the BusinessAnalysisAgent
4. Generates comprehensive analysis reports in the outputs directory

Usage:
    python demo_analysis_pipeline.py

Output:
    - outputs/sia_business_analysis.md
    - outputs/ziniosa_business_analysis.md
    - outputs/combined_analysis_report.md
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import AI-Shark components
from src.utils.document_loader import DirectoryLoader, MarkdownParser
from src.agents.business_agent import BusinessAnalysisAgent, create_business_agent
from src.utils.llm_setup import get_llm, create_mock_llm, llm_setup
from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent
from src.models.analysis_models import BusinessAnalysis
from config.settings import settings

class AnalysisPipelineDemo:
    """
    Comprehensive demo of the AI-Shark analysis pipeline
    """

    def __init__(self, use_real_llm: bool = False):
        """
        Initialize the demo pipeline

        Args:
            use_real_llm: Whether to use real LLM API or mock for demo
        """
        self.use_real_llm = use_real_llm
        self.results_dir = Path("results")
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(exist_ok=True)

        # Initialize components
        self.document_loader = DirectoryLoader()
        self.markdown_parser = MarkdownParser()

        # Initialize business agent
        if use_real_llm:
            self.business_agent = create_business_agent()
            print(f"🤖 Using real LLM: {llm_setup.get_model_info()}")
        else:
            # Create mock LLM with realistic business analysis responses
            mock_responses = self._get_mock_responses()
            mock_llm = create_mock_llm(mock_responses)
            self.business_agent = BusinessAnalysisAgent(llm=mock_llm)
            print("🤖 Using Mock LLM for demonstration")

        print(f"📁 Results directory: {self.results_dir}")
        print(f"📁 Outputs directory: {self.outputs_dir}")

    def _get_mock_responses(self) -> List[str]:
        """Generate realistic mock responses for business analysis"""

        # Mock response for Sia (Data Analytics AI)
        sia_response = """{
            "revenue_streams": [
                "SaaS subscription tiers",
                "Platform-as-a-Service (PaaS) licensing",
                "Enterprise custom integration services",
                "Data processing and analytics consulting"
            ],
            "scalability": "high",
            "competitive_position": "Strong differentiation through conversational AI interface and agentic data analytics automation",
            "business_model": "SaaS/PaaS hybrid with tiered pricing for data analytics platform",
            "value_proposition": "Democratizes data analytics through conversational AI, making complex data insights accessible to non-technical users",
            "target_market": [
                "Small and medium businesses needing data insights",
                "Non-technical users requiring data analysis",
                "Enterprises seeking automated data processing"
            ],
            "growth_strategy": "Focus on user-friendly conversational interface and automation to capture underserved SMB market",
            "partnerships": [
                "Data visualization tool integrations",
                "Cloud storage providers",
                "Business intelligence platforms"
            ],
            "regulatory_considerations": [
                "Data privacy and GDPR compliance",
                "Industry-specific data regulations",
                "AI ethics and algorithmic transparency"
            ]
        }"""

        # Mock response for Ziniosa (Luxury Fashion Platform)
        ziniosa_response = """{
            "revenue_streams": [
                "Commission on marketplace transactions",
                "Authentication and verification service fees",
                "Premium seller listing fees",
                "EMI and financing service partnerships"
            ],
            "scalability": "medium",
            "competitive_position": "First-mover advantage in Indian pre-loved luxury market with strong authentication guarantee",
            "business_model": "Two-sided marketplace for pre-loved luxury fashion with authentication services",
            "value_proposition": "Access to authenticated luxury goods at 60% discount with convenience and trust",
            "target_market": [
                "Luxury fashion enthusiasts seeking affordable options",
                "Environmentally conscious consumers",
                "Sellers of pre-owned luxury items"
            ],
            "growth_strategy": "Geographic expansion across India and brand partnerships with luxury designers",
            "partnerships": [
                "Luxury brand authentication partnerships",
                "Logistics and shipping providers",
                "Payment and EMI service providers"
            ],
            "regulatory_considerations": [
                "Consumer protection laws",
                "E-commerce regulations in India",
                "Import/export regulations for luxury goods"
            ]
        }"""

        return [sia_response, ziniosa_response]

    def load_documents(self) -> List[StartupDocument]:
        """
        Load and process documents from the results directory

        Returns:
            List of processed StartupDocument objects
        """
        print("\n📄 Loading Documents")
        print("=" * 50)

        documents = []

        # Define document files and their metadata
        document_files = [
            {
                "path": self.results_dir / "analysis_results.md",
                "name": "Startup Pitch Deck Analysis",
                "type": "pitch_deck",
                "description": "Analysis results from pitch deck processing"
            },
            {
                "path": self.results_dir / "public_data.md",
                "name": "Startup Public Data Analysis",
                "type": "market_analysis",
                "description": "Scraped public information about the startup"
            }
        ]

        for doc_info in document_files:
            try:
                if doc_info["path"].exists():
                    print(f"📖 Loading: {doc_info['name']}")

                    # Read document content
                    with open(doc_info["path"], 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Parse with markdown parser
                    parsed_content = self.markdown_parser.parse_content(content, str(doc_info["path"]))
                    # print(f"   🧾 Parsed content: {parsed_content}")

                    # Create document metadata
                    file_stat = doc_info["path"].stat()
                    metadata = DocumentMetadata(
                        file_path=str(doc_info["path"]),
                        size=file_stat.st_size,
                        last_modified=datetime.fromtimestamp(file_stat.st_mtime),
                        file_extension=".md"
                    )

                    # Create startup document
                    startup_doc = StartupDocument(
                        content=parsed_content,
                        metadata=metadata,
                        document_type=doc_info["type"],
                        title=doc_info["name"],
                        tags=["startup", "analysis", "demo"]
                    )

                    documents.append(startup_doc)

                    print(f"   ✅ Loaded: {len(parsed_content.raw_text)} characters")
                    print(f"   📊 Sections: {len(parsed_content.sections)}")
                    print(f"   📝 Word count: {parsed_content.word_count}")

                else:
                    print(f"   ❌ File not found: {doc_info['path']}")

            except Exception as e:
                print(f"   ❌ Error loading {doc_info['name']}: {e}")

        print(f"\n✅ Successfully loaded {len(documents)} documents")
        return documents

    def analyze_documents_combined(self, documents: List[StartupDocument]) -> Dict[str, Any]:
        """
        Run combined business analysis on pitch deck and public data together

        Args:
            documents: List of StartupDocument objects (pitch deck and public data)

        Returns:
            Combined analysis result
        """
        print("\n🧠 Combined Business Analysis")
        print("=" * 50)

        # Separate pitch deck and public data documents
        pitch_deck_doc = None
        public_data_doc = None

        for doc in documents:
            if doc.document_type == "pitch_deck":
                pitch_deck_doc = doc
            elif doc.document_type == "market_analysis":
                public_data_doc = doc

        if not pitch_deck_doc or not public_data_doc:
            raise ValueError("Both pitch deck and public data documents are required")

        try:
            print(f"\n📈 Analyzing Combined Documents")
            print("-" * 40)
            print(f"   📄 Pitch Deck: {pitch_deck_doc.title}")
            print(f"   🌐 Public Data: {public_data_doc.title}")

            start_time = datetime.now()

            # Extract content from both documents
            pitch_deck_content = pitch_deck_doc.content.raw_text
            public_data_content = public_data_doc.content.raw_text

            print(f"   📊 Pitch deck content: {len(pitch_deck_content)} characters")
            print(f"   📊 Public data content: {len(public_data_content)} characters")

            # Perform combined analysis using the new method
            print("🏗️ Running combined business analysis...")
            markdown_analysis = self.business_agent.analyze_combined_documents(
                pitch_deck_content=pitch_deck_content,
                public_data_content=public_data_content
            )

            processing_time = datetime.now() - start_time

            print(f"   ✅ Combined analysis completed in {processing_time.total_seconds():.2f}s")
            print(f"   📝 Generated markdown report: {len(markdown_analysis)} characters")

            # Compile results
            result = {
                "pitch_deck_document": pitch_deck_doc,
                "public_data_document": public_data_doc,
                "markdown_analysis": markdown_analysis,
                "processing_time": processing_time.total_seconds(),
                "analysis_type": "combined_markdown"
            }

            return result

        except Exception as e:
            print(f"   ❌ Combined analysis failed: {e}")
            import traceback
            traceback.print_exc()
            raise


    def generate_combined_markdown_report(self, analysis_result: Dict[str, Any]) -> None:
        """
        Generate report for combined markdown analysis

        Args:
            analysis_result: Combined analysis result containing markdown analysis
        """
        print("\n📝 Generating Combined Markdown Report")
        print("=" * 50)

        # Extract information
        pitch_deck_doc = analysis_result["pitch_deck_document"]
        public_data_doc = analysis_result["public_data_document"]
        markdown_analysis = analysis_result["markdown_analysis"]
        processing_time = analysis_result["processing_time"]

        # Create report header
        report_header = f"""# Combined Startup Business Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Engine:** AI-Shark Multi-Agent System (Combined Document Analysis)
**Processing Time:** {processing_time:.2f} seconds
**Analysis Type:** {analysis_result['analysis_type']}

## Source Documents

### 📄 Pitch Deck Analysis
- **Title:** {pitch_deck_doc.title}
- **Document Type:** {pitch_deck_doc.document_type}
- **Content Length:** {len(pitch_deck_doc.content.raw_text):,} characters
- **Sections:** {len(pitch_deck_doc.content.sections)}
- **File Size:** {pitch_deck_doc.metadata.size:,} bytes

### 🌐 Public Data Analysis
- **Title:** {public_data_doc.title}
- **Document Type:** {public_data_doc.document_type}
- **Content Length:** {len(public_data_doc.content.raw_text):,} characters
- **Sections:** {len(public_data_doc.content.sections)}
- **File Size:** {public_data_doc.metadata.size:,} bytes

---

"""

        # Combine header with LLM-generated analysis
        full_report = report_header + markdown_analysis

        # Create output file
        report_file = self.outputs_dir / "combined_business_analysis.md"

        # Write report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(full_report)

        print(f"📄 Generated combined analysis report: {report_file}")
        print(f"📊 Report size: {len(full_report):,} characters")

        # Also create a summary file with key insights
        self._generate_markdown_summary(analysis_result)

        print(f"\n✅ Combined markdown reports generated in {self.outputs_dir}")

    def _generate_markdown_summary(self, analysis_result: Dict[str, Any]) -> None:
        """Generate a summary of the combined markdown analysis"""

        summary_content = f"""# Startup Analysis Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Type:** Combined Document Analysis (Pitch Deck + Public Data)
**Processing Time:** {analysis_result['processing_time']:.2f} seconds

## Quick Facts

- **Pitch Deck Analyzed:** {analysis_result['pitch_deck_document'].title}
- **Public Data Analyzed:** {analysis_result['public_data_document'].title}
- **Total Content Processed:** {len(analysis_result['pitch_deck_document'].content.raw_text) + len(analysis_result['public_data_document'].content.raw_text):,} characters
- **Analysis Method:** LLM-powered markdown analysis with sector-specific insights

## Key Features of This Analysis

✅ **Combined Document Processing:** Both pitch deck and public data analyzed together
✅ **Sector-Specific Analysis:** Industry-focused insights and trends
✅ **Markdown Output:** Human-readable format instead of rigid JSON structure
✅ **LLM-Generated Insights:** Business recommendations generated by AI expertise
✅ **Information Gap Identification:** Highlights missing data for more thorough analysis

## Output Files

- `combined_business_analysis.md` - Full comprehensive analysis report
- `analysis_summary.md` - This summary file

For the complete analysis, please refer to the main report file.
"""

        summary_file = self.outputs_dir / "analysis_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        print(f"📄 Generated analysis summary: {summary_file}")

    def run_pipeline(self) -> None:
        """
        Run the combined analysis pipeline (pitch deck + public data)
        """
        print("🚀 AI-Shark Analysis Pipeline Demo")
        print("=" * 60)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"LLM Provider: {llm_setup.get_model_info().get('provider', 'unknown')}")
        print(f"Use Real LLM: {self.use_real_llm}")
        print(f"Analysis Type: Combined Document Analysis (Pitch Deck + Public Data)")

        try:
            # Step 1: Load documents
            documents = self.load_documents()
            if not documents:
                print("❌ No documents loaded. Pipeline cannot continue.")
                return

            if len(documents) < 2:
                print("❌ Combined analysis requires both pitch deck and public data documents.")
                return

            # Step 2: Perform combined analysis
            combined_result = self.analyze_documents_combined(documents)

            # Step 3: Generate combined markdown reports
            self.generate_combined_markdown_report(combined_result)

            # Step 4: Display summary
            self._display_combined_pipeline_summary(combined_result)

            print(f"\n🎉 Pipeline completed successfully!")
            print(f"📁 Check outputs directory: {self.outputs_dir}")

        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()

    def _display_combined_pipeline_summary(self, result: Dict[str, Any]) -> None:
        """Display summary of the combined pipeline results"""

        print("\n📊 Combined Pipeline Summary")
        print("=" * 50)

        print(f"\n📈 Combined Analysis Completed")
        print("-" * 30)
        print(f"   📄 Pitch Deck: {result['pitch_deck_document'].title}")
        print(f"   🌐 Public Data: {result['public_data_document'].title}")
        print(f"   ⏱️ Processing Time: {result['processing_time']:.2f}s")
        print(f"   📝 Analysis Length: {len(result['markdown_analysis']):,} characters")
        print(f"   🔄 Analysis Type: {result['analysis_type']}")

        # Show key features
        print(f"\n✨ Analysis Features:")
        print("   ✅ Combined document processing")
        print("   ✅ Sector-specific insights")
        print("   ✅ Markdown output format")
        print("   ✅ LLM-generated business insights")
        print("   ✅ Information gap identification")

        print(f"\n📁 Generated Files:")
        print("   📄 combined_business_analysis.md - Full analysis report")
        print("   📄 analysis_summary.md - Quick summary")


def main():

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Engine:** AI-Shark Multi-Agent System
**Processing Time:** {result['processing_time']:.2f} seconds

## Executive Summary

{doc.title} analysis completed using AI-Shark's business analysis agent. This report provides comprehensive insights into the business model, market opportunity, competitive position, and growth potential.

## Document Information

- **Document Type:** {doc.document_type.title()}
- **File Size:** {doc.metadata.size:,} bytes
- **Word Count:** {doc.content.word_count:,}
- **Sections:** {len(doc.content.sections)}
- **Last Modified:** {doc.metadata.last_modified.strftime('%Y-%m-%d %H:%M:%S')}

## Business Analysis Results

### Revenue Model Analysis
"""

        # Add revenue streams
        if isinstance(analysis, BusinessAnalysis):
            report += f"""
**Identified Revenue Streams:**
"""
            for i, stream in enumerate(analysis.revenue_streams, 1):
                report += f"{i}. {stream}\n"

            report += f"""
**Business Model:** {analysis.business_model}

**Scalability Assessment:** {analysis.scalability.title()}

**Value Proposition:** {analysis.value_proposition}

### Market Analysis

**Target Markets:**
"""
            for i, market in enumerate(analysis.target_market, 1):
                report += f"{i}. {market}\n"

            report += f"""
**Competitive Position:** {analysis.competitive_position}

### Strategic Partnerships
"""
            if analysis.partnerships:
                for i, partnership in enumerate(analysis.partnerships, 1):
                    report += f"{i}. {partnership}\n"
            else:
                report += "No strategic partnerships identified.\n"

            report += """
### Regulatory Considerations
"""
            if analysis.regulatory_considerations:
                for i, consideration in enumerate(analysis.regulatory_considerations, 1):
                    report += f"{i}. {consideration}\n"
            else:
                report += "No specific regulatory considerations identified.\n"

        # Add domain analysis
        report += f"""
## Domain-Specific Analysis

### Revenue Stream Detection
**Method:** Pattern-based identification using business frameworks
**Results:** {len(domain['revenue_streams'])} revenue streams detected
- {', '.join(domain['revenue_streams']) if domain['revenue_streams'] else 'None detected'}

### Scalability Assessment
**Assessment:** {domain['scalability'].title()}
**Method:** Multi-factor analysis of business model indicators

### Competitive Advantages
**Identified:** {len(domain['competitive_advantages'])} competitive advantages
- {', '.join(domain['competitive_advantages']) if domain['competitive_advantages'] else 'None detected'}

### Business Metrics Extraction
**Extracted Metrics:** {len(domain['business_metrics'])} metrics found
"""

        if domain['business_metrics']:
            for metric_type, values in domain['business_metrics'].items():
                report += f"- **{metric_type.replace('_', ' ').title()}:** {values}\n"

        # Add business insights
        report += f"""
## Business Insights

### Revenue Model Assessment
- **Strength:** {insights['revenue_model_assessment']['strength']}
- **Recurring Revenue:** {'Yes' if insights['revenue_model_assessment']['recurring_revenue'] else 'No'}
- **Diversity Score:** {insights['revenue_model_assessment']['diversity_score']:.2f}/1.0

### Growth Potential
**Assessment:** {insights['growth_potential']}

### Competitive Strength
**Assessment:** {insights['competitive_strength']}

### Risk Factors
"""
        if insights['risk_factors']:
            for i, risk in enumerate(insights['risk_factors'], 1):
                report += f"{i}. {risk}\n"
        else:
            report += "No significant risk factors identified.\n"

        # Add performance statistics
        report += f"""
## Analysis Performance

- **Agent:** {stats['agent_name']}
- **Total Analyses Performed:** {stats['total_analyses']}
- **Average Processing Time:** {stats['average_processing_time']:.2f} seconds
- **Success Rate:** {stats['success_rate']*100:.1f}%
- **Error Count:** {stats['error_count']}

## Methodology

This analysis was performed using the AI-Shark Multi-Agent Startup Analysis System, which includes:

1. **Document Processing:** Advanced markdown parsing and content extraction
2. **Business Analysis Agent:** Specialized agent for business model evaluation
3. **Domain Expertise:** Built-in frameworks for revenue models, scalability, and competitive analysis
4. **Structured Output:** Pydantic-based data models for consistent analysis results
5. **Performance Tracking:** Comprehensive metrics and quality assurance

## Recommendations

Based on this analysis, key areas for further investigation include:
"""

        # Generate recommendations based on analysis
        if isinstance(analysis, BusinessAnalysis):
            if analysis.scalability == "high":
                report += "- Develop scalability roadmap to capitalize on high growth potential\n"
            if len(analysis.revenue_streams) == 1:
                report += "- Consider diversifying revenue streams to reduce dependency risk\n"
            if not analysis.partnerships:
                report += "- Explore strategic partnerships to accelerate growth\n"
            if insights['competitive_strength'] == "Weak":
                report += "- Strengthen competitive positioning through differentiation\n"

        report += f"""
---
*Report generated by AI-Shark Multi-Agent Startup Analysis System*
*For questions or additional analysis, contact the development team*
"""

        return report

    def _generate_combined_report(self, analysis_results: List[Dict[str, Any]]) -> str:
        """Generate combined analysis report for all startups"""

        report = f"""# Combined Startup Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Engine:** AI-Shark Multi-Agent System
**Documents Analyzed:** {len(analysis_results)}

## Executive Summary

This report presents a comparative analysis of {len(analysis_results)} startup companies processed through the AI-Shark Multi-Agent Startup Analysis System. Each company was evaluated using standardized business analysis frameworks to provide consistent and comparable insights.

## Startup Comparison

| Metric | """ + " | ".join([result["document"].title for result in analysis_results]) + """ |
|--------|""" + "|".join(["--------" for _ in analysis_results]) + """|
"""

        # Add comparison rows
        comparison_metrics = [
            ("Document Type", lambda r: r["document"].document_type.title()),
            ("Word Count", lambda r: f"{r['document'].content.word_count:,}"),
            ("Processing Time", lambda r: f"{r['processing_time']:.2f}s"),
            ("Revenue Streams", lambda r: len(r['business_analysis'].revenue_streams) if isinstance(r['business_analysis'], BusinessAnalysis) else 0),
            ("Scalability", lambda r: r['business_analysis'].scalability.title() if isinstance(r['business_analysis'], BusinessAnalysis) else "Unknown"),
            ("Target Markets", lambda r: len(r['business_analysis'].target_market) if isinstance(r['business_analysis'], BusinessAnalysis) else 0),
            ("Growth Potential", lambda r: r['business_insights']['growth_potential']),
            ("Risk Factors", lambda r: len(r['business_insights']['risk_factors']))
        ]

        for metric_name, metric_func in comparison_metrics:
            row = f"| {metric_name} |"
            for result in analysis_results:
                try:
                    value = metric_func(result)
                    row += f" {value} |"
                except:
                    row += " N/A |"
            report += row + "\n"

        # Add detailed analysis for each startup
        for i, result in enumerate(analysis_results, 1):
            doc = result["document"]
            analysis = result["business_analysis"]
            insights = result["business_insights"]

            report += f"""
## {i}. {doc.title}

### Business Model Overview
"""
            if isinstance(analysis, BusinessAnalysis):
                report += f"""
- **Business Model:** {analysis.business_model}
- **Value Proposition:** {analysis.value_proposition}
- **Scalability:** {analysis.scalability.title()}
- **Revenue Streams:** {len(analysis.revenue_streams)} identified

### Key Insights
- **Revenue Model Strength:** {insights['revenue_model_assessment']['strength']}
- **Growth Potential:** {insights['growth_potential']}
- **Competitive Strength:** {insights['competitive_strength']}
- **Primary Risk Factors:** {len(insights['risk_factors'])} identified
"""

        # Add comparative insights
        report += """
## Comparative Analysis

### Revenue Model Comparison
"""

        for result in analysis_results:
            if isinstance(result["business_analysis"], BusinessAnalysis):
                analysis = result["business_analysis"]
                insights = result["business_insights"]
                report += f"""
**{result["document"].title}:**
- Revenue Streams: {', '.join(analysis.revenue_streams[:3])}{'...' if len(analysis.revenue_streams) > 3 else ''}
- Model Strength: {insights['revenue_model_assessment']['strength']}
- Recurring Revenue: {'Yes' if insights['revenue_model_assessment']['recurring_revenue'] else 'No'}
"""

        report += """
### Growth Potential Analysis
"""

        growth_categories = {}
        for result in analysis_results:
            growth = result["business_insights"]["growth_potential"]
            if growth not in growth_categories:
                growth_categories[growth] = []
            growth_categories[growth].append(result["document"].title)

        for growth_level, companies in growth_categories.items():
            report += f"**{growth_level} Growth Potential:** {', '.join(companies)}\n"

        report += """
## System Performance Summary

"""

        total_processing_time = sum(r["processing_time"] for r in analysis_results)
        avg_processing_time = total_processing_time / len(analysis_results)

        report += f"""
- **Total Processing Time:** {total_processing_time:.2f} seconds
- **Average Processing Time:** {avg_processing_time:.2f} seconds per document
- **Success Rate:** 100% (all documents processed successfully)
- **Analysis Engine:** AI-Shark Business Analysis Agent

## Methodology Notes

All analyses were performed using consistent frameworks and methodologies:

1. **Document Processing:** Standardized markdown parsing and content extraction
2. **Business Analysis:** Uniform application of business evaluation frameworks
3. **Risk Assessment:** Systematic identification of business, market, and operational risks
4. **Insight Generation:** Automated generation of actionable business insights
5. **Performance Tracking:** Comprehensive metrics for quality assurance

---
*Report generated by AI-Shark Multi-Agent Startup Analysis System*
"""

        return report

    def _generate_summary_report(self, analysis_results: List[Dict[str, Any]]) -> None:
        """Generate executive summary report"""

        summary_file = self.outputs_dir / "executive_summary.md"

        total_docs = len(analysis_results)
        total_time = sum(r["processing_time"] for r in analysis_results)
        avg_time = total_time / total_docs if total_docs > 0 else 0

        # Collect statistics
        revenue_streams_total = 0
        scalability_distribution = {}
        growth_distribution = {}

        for result in analysis_results:
            if isinstance(result["business_analysis"], BusinessAnalysis):
                analysis = result["business_analysis"]
                insights = result["business_insights"]

                revenue_streams_total += len(analysis.revenue_streams)

                scalability = analysis.scalability
                scalability_distribution[scalability] = scalability_distribution.get(scalability, 0) + 1

                growth = insights["growth_potential"]
                growth_distribution[growth] = growth_distribution.get(growth, 0) + 1

        summary = f"""# AI-Shark Analysis Pipeline - Executive Summary

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Pipeline Version:** AI-Shark Multi-Agent System v1.0

## Analysis Overview

- **Documents Processed:** {total_docs}
- **Total Processing Time:** {total_time:.2f} seconds
- **Average Time per Document:** {avg_time:.2f} seconds
- **Success Rate:** 100%

## Key Findings

### Revenue Model Analysis
- **Total Revenue Streams Identified:** {revenue_streams_total}
- **Average per Company:** {revenue_streams_total/total_docs:.1f}

### Scalability Distribution
"""

        for scalability, count in scalability_distribution.items():
            percentage = (count / total_docs) * 100
            summary += f"- **{scalability.title()}:** {count} companies ({percentage:.1f}%)\n"

        summary += """
### Growth Potential Distribution
"""

        for growth, count in growth_distribution.items():
            percentage = (count / total_docs) * 100
            summary += f"- **{growth}:** {count} companies ({percentage:.1f}%)\n"

        summary += f"""
## System Performance

The AI-Shark Multi-Agent System successfully processed all {total_docs} startup documents with:

- **Zero Failures:** 100% success rate in document processing
- **Consistent Analysis:** Standardized frameworks applied to all companies
- **Comprehensive Coverage:** Business model, scalability, competitive analysis, and risk assessment
- **Actionable Insights:** Generated specific recommendations for each startup

## Technology Stack Validation

✅ **Document Loading:** Successfully processed markdown documents from results directory
✅ **Business Analysis Agent:** Performed comprehensive business model evaluation
✅ **Domain Expertise:** Applied specialized frameworks for revenue and scalability analysis
✅ **Structured Output:** Generated consistent Pydantic-based analysis results
✅ **Report Generation:** Created detailed markdown reports in outputs directory

## Next Steps

1. **Review Individual Reports:** Detailed analysis available for each startup
2. **Comparative Analysis:** Use combined report for cross-company insights
3. **Deep Dive Analysis:** Consider running additional specialized agents (Financial, Market, Technology)
4. **Pipeline Optimization:** Monitor performance metrics for continuous improvement

---
*Generated by AI-Shark Multi-Agent Startup Analysis System*
"""

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)

        print(f"📄 Generated: {summary_file}")

    def run_pipeline(self) -> None:
        """
        Run the combined analysis pipeline (pitch deck + public data)
        """
        print("🚀 AI-Shark Analysis Pipeline Demo")
        print("=" * 60)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"LLM Provider: {llm_setup.get_model_info().get('provider', 'unknown')}")
        print(f"Use Real LLM: {self.use_real_llm}")
        print(f"Analysis Type: Combined Document Analysis (Pitch Deck + Public Data)")

        try:
            # Step 1: Load documents
            documents = self.load_documents()
            if not documents:
                print("❌ No documents loaded. Pipeline cannot continue.")
                return

            if len(documents) < 2:
                print("❌ Combined analysis requires both pitch deck and public data documents.")
                return

            # Step 2: Perform combined analysis
            combined_result = self.analyze_documents_combined(documents)

            # Step 3: Generate combined markdown reports
            self.generate_combined_markdown_report(combined_result)

            # Step 4: Display summary
            self._display_combined_pipeline_summary(combined_result)

            print(f"\n🎉 Pipeline completed successfully!")
            print(f"📁 Check outputs directory: {self.outputs_dir}")

        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()

    def _display_combined_pipeline_summary(self, result: Dict[str, Any]) -> None:
        """Display summary of the combined pipeline results"""

        print("\n📊 Combined Pipeline Summary")
        print("=" * 50)

        print(f"\n📈 Combined Analysis Completed")
        print("-" * 30)
        print(f"   📄 Pitch Deck: {result['pitch_deck_document'].title}")
        print(f"   🌐 Public Data: {result['public_data_document'].title}")
        print(f"   ⏱️ Processing Time: {result['processing_time']:.2f}s")
        print(f"   📝 Analysis Length: {len(result['markdown_analysis']):,} characters")
        print(f"   🔄 Analysis Type: {result['analysis_type']}")

        # Show key features
        print(f"\n✨ Analysis Features:")
        print("   ✅ Combined document processing")
        print("   ✅ Sector-specific insights")
        print("   ✅ Markdown output format")
        print("   ✅ LLM-generated business insights")
        print("   ✅ Information gap identification")

        print(f"\n📁 Generated Files:")
        print("   📄 combined_business_analysis.md - Full analysis report")
        print("   📄 analysis_summary.md - Quick summary")

    def run_complete_pipeline(self) -> None:
        """
        Run the complete analysis pipeline (legacy method)
        """
        print("🚀 AI-Shark Analysis Pipeline Demo")
        print("=" * 60)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"LLM Provider: {llm_setup.get_model_info().get('provider', 'unknown')}")
        print(f"Use Real LLM: {self.use_real_llm}")

        try:
            # Step 1: Load documents
            documents = self.load_documents()
            if not documents:
                print("❌ No documents loaded. Pipeline cannot continue.")
                return

            # Step 2: Analyze documents
            analysis_results = self.analyze_documents(documents)
            if not analysis_results:
                print("❌ No analysis results. Pipeline cannot continue.")
                return

            # Step 3: Generate reports
            self.generate_reports(analysis_results)

            # Step 4: Display summary
            self._display_pipeline_summary(analysis_results)

            print(f"\n🎉 Pipeline completed successfully!")
            print(f"📁 Check outputs directory: {self.outputs_dir}")

        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()

    def _display_pipeline_summary(self, analysis_results: List[Dict[str, Any]]) -> None:
        """Display a summary of the pipeline results"""

        print("\n📊 Pipeline Summary")
        print("=" * 50)

        for result in analysis_results:
            doc = result["document"]
            analysis = result["business_analysis"]
            insights = result["business_insights"]

            print(f"\n📈 {doc.title}")
            print("-" * 30)

            if isinstance(analysis, BusinessAnalysis):
                print(f"Revenue Streams: {len(analysis.revenue_streams)}")
                print(f"Scalability: {analysis.scalability.title()}")
                print(f"Growth Potential: {insights['growth_potential']}")
                print(f"Processing Time: {result['processing_time']:.2f}s")

        total_time = sum(r["processing_time"] for r in analysis_results)
        print(f"\n⏱️  Total Processing Time: {total_time:.2f} seconds")
        print(f"📄 Reports Generated: {len(analysis_results) + 2}")  # Individual + combined + summary


def main():
    """Main entry point for the demo"""

    print("AI-Shark Demo: End-to-End Startup Analysis Pipeline")
    print("=" * 60)

    # Check if we should use real LLM (default to mock for automated runs)
    import sys
    if sys.stdin.isatty():
        use_real_llm = input("Use real LLM API? (y/N): ").lower().startswith('y')
    else:
        # Non-interactive mode - use mock LLM
        use_real_llm = False
        print("Running in non-interactive mode - using Mock LLM")

    if use_real_llm:
        # Check if API keys are configured
        provider = os.getenv('LLM_PROVIDER', 'google').lower()
        if provider == 'google' and not os.getenv('GOOGLE_API_KEY'):
            print("❌ Google API key not found. Set GOOGLE_API_KEY environment variable.")
            use_real_llm = False
        elif provider == 'groq' and not os.getenv('GROQ_API_KEY'):
            print("❌ Groq API key not found. Set GROQ_API_KEY environment variable.")
            use_real_llm = False

    if not use_real_llm:
        print("Using Mock LLM for demonstration (no API key required)")

    # Create and run pipeline
    pipeline = AnalysisPipelineDemo(use_real_llm=use_real_llm)

    # Ask user which pipeline to run
    if sys.stdin.isatty():
        pipeline_choice = input("\nChoose pipeline type:\n1. Combined Analysis (NEW - Pitch Deck + Public Data)\n2. Legacy Individual Analysis\nChoice (1/2): ").strip()
        use_combined = pipeline_choice == "1" or pipeline_choice.lower().startswith("c")
    else:
        # Non-interactive mode - use combined pipeline
        use_combined = True
        print("Running Combined Analysis Pipeline (default for non-interactive mode)")

    if use_combined:
        pipeline.run_combined_pipeline()
    else:
        pipeline.run_complete_pipeline()


if __name__ == "__main__":
    main()