"""
AI-Shark Demo: End-to-End Startup Analysis Pipeline

This demo script demonstrates the complete AI-Shark analysis pipeline:
1. Loads documents from results directory (analysis_results.md, public_data.md)
2. Processes them using the document loader
3. Runs analysis using either BusinessAnalysisAgent or MarketAnalysisAgent
4. Generates comprehensive analysis reports in the outputs directory

Usage:
    python demo_analysis_pipeline.py

Features:
- Interactive agent selection (Business or Market Analysis)
- Support for both real LLM and mock responses
- Combined document analysis (pitch deck + public data)
- Markdown report generation with sector-specific insights

Output:
    - outputs/combined_business_analysis.md (for business agent)
    - outputs/combined_market_analysis.md (for market agent)
    - outputs/analysis_summary.md
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import AI-Shark components
from src.utils.document_loader import DirectoryLoader, MarkdownParser
from src.agents.business_agent import BusinessAnalysisAgent, create_business_agent
from src.agents.market_agent import MarketAnalysisAgent, create_market_agent
from src.utils.llm_setup import get_llm, create_mock_llm, llm_setup
from src.models.document_models import StartupDocument, DocumentMetadata, ParsedContent
from src.models.analysis_models import BusinessAnalysis, MarketAnalysis
from config.settings import settings

class AnalysisPipelineDemo:
    """
    Comprehensive demo of the AI-Shark analysis pipeline
    """

    def __init__(self, use_real_llm: bool = False, agent_type: str = "business"):
        """
        Initialize the demo pipeline

        Args:
            use_real_llm: Whether to use real LLM API or mock for demo
            agent_type: Type of agent to use ("business" or "market")
        """
        self.use_real_llm = use_real_llm
        self.agent_type = agent_type
        self.results_dir = Path("results")
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(exist_ok=True)

        # Initialize components
        self.document_loader = DirectoryLoader()
        self.markdown_parser = MarkdownParser()

        # Initialize agents based on type
        if use_real_llm:
            if agent_type == "business":
                self.analysis_agent = create_business_agent()
            else:  # market
                self.analysis_agent = create_market_agent()
            print(f"🤖 Using real LLM: {llm_setup.get_model_info()}")
        else:
            # Create mock LLM with realistic responses
            mock_responses = self._get_mock_responses(agent_type)
            mock_llm = create_mock_llm(mock_responses)
            if agent_type == "business":
                self.analysis_agent = BusinessAnalysisAgent(llm=mock_llm)
            else:  # market
                self.analysis_agent = MarketAnalysisAgent(llm=mock_llm)
            print("🤖 Using Mock LLM for demonstration")

        print(f"📊 Analysis Agent: {self.analysis_agent.agent_name}")
        print(f"📁 Results directory: {self.results_dir}")
        print(f"📁 Outputs directory: {self.outputs_dir}")

    def _get_mock_responses(self, agent_type: str) -> List[str]:
        """Get mock responses for testing"""
        if agent_type == "business":
            return [
                json.dumps({
                    "revenue_streams": ["SaaS subscription", "Enterprise licensing"],
                    "scalability": "high",
                    "competitive_position": "Strong market position with proprietary technology",
                    "business_model": "B2B SaaS with freemium tier",
                    "value_proposition": "AI-powered analytics for business intelligence",
                    "target_market": ["SMBs", "Enterprise customers"],
                    "growth_strategy": "Product-led growth with strategic partnerships",
                    "partnerships": ["Technology integrations", "Channel partners"],
                    "regulatory_considerations": ["Data privacy", "Industry compliance"]
                })
            ]
        else:  # market
            return [
                json.dumps({
                    "market_size": {"tam": "50B", "sam": "5B", "som": "500M"},
                    "competition": [
                        {"name": "Tableau", "strength": "Market leader in visualization"},
                        {"name": "Power BI", "strength": "Microsoft ecosystem integration"},
                        {"name": "Looker", "strength": "Google cloud integration"}
                    ],
                    "positioning": "Conversational AI analytics for SMB market",
                    "market_trends": ["AI adoption", "Self-service analytics", "SMB digitization"],
                    "customer_segments": [
                        {"segment": "SMBs", "size": "10-500 employees"},
                        {"segment": "Non-technical users", "description": "Business managers"}
                    ],
                    "go_to_market_strategy": "Product-led growth with freemium model",
                    "geographic_focus": ["North America", "Europe"],
                    "market_barriers": ["Brand recognition", "Customer acquisition"],
                    "market_opportunities": ["Underserved SMB segment", "Conversational interfaces"]
                })
            ]

    def load_documents(self) -> List[StartupDocument]:
        """
        Load documents for analysis

        Returns:
            List of loaded StartupDocument objects
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
                    print(f"   ✅ Loaded: {len(content):,} characters")
                    print(f"   📊 Sections: {len(parsed_content.sections)}")
                    print(f"   📝 Word count: {parsed_content.word_count:,}")

                else:
                    print(f"   ⚠️ File not found: {doc_info['path']}")

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
            print(f"🏗️ Running combined {self.agent_type} analysis...")
            markdown_analysis = self.analysis_agent.analyze_combined_documents(
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
        analysis_type_title = "Business" if self.agent_type == "business" else "Market & Competition"
        report_header = f"""# Combined Startup {analysis_type_title} Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Engine:** AI-Shark Multi-Agent System (Combined Document Analysis)
**Analysis Agent:** {self.analysis_agent.agent_name}
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

        # Extract company name for filename
        company_name = self._extract_company_name(pitch_deck_doc, public_data_doc)

        # Create output file
        if company_name:
            report_file = self.outputs_dir / f"{company_name}-{self.agent_type}-analysis.md"
        else:
            report_file = self.outputs_dir / f"combined_{self.agent_type}_analysis.md"

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

        analysis_type_title = "Business" if self.agent_type == "business" else "Market & Competition"
        summary_content = f"""# Startup {analysis_type_title} Analysis Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Type:** Combined Document Analysis (Pitch Deck + Public Data)
**Analysis Agent:** {self.analysis_agent.agent_name}
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

- `combined_{self.agent_type}_analysis.md` - Full comprehensive analysis report
- `analysis_summary.md` - This summary file

For the complete analysis, please refer to the main report file.
"""

        summary_file = self.outputs_dir / "analysis_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        print(f"📄 Generated analysis summary: {summary_file}")

    def _extract_company_name(self, pitch_deck_doc: StartupDocument, public_data_doc: StartupDocument) -> Optional[str]:
        """
        Extract company name from documents for filename

        Args:
            pitch_deck_doc: Pitch deck document
            public_data_doc: Public data document

        Returns:
            Extracted company name or None
        """
        import re

        # Try to extract from pitch deck first
        pitch_content = pitch_deck_doc.content.raw_text

        # Look for patterns like "Sia:", "Company: Sia", etc.
        patterns = [
            r'##?\s*([A-Z][a-zA-Z\s&.-]+?):\s*[A-Z]',  # "## Sia: Agentic AI..."
            r'Company:\s*([A-Z][a-zA-Z\s&.-]+?)(?:\n|$)',  # "Company: Sia"
            r'\*\*([A-Z][a-zA-Z\s&.-]+?)\*\*\s*is',  # "**Sia** is"
            r'^([A-Z][a-zA-Z\s&.-]+?)\s+is\s+an?',  # "Sia is an"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, pitch_content, re.MULTILINE)
            if matches:
                company_name = matches[0].strip()
                # Clean up the name
                company_name = re.sub(r'[^\w\s-]', '', company_name)  # Remove special chars
                company_name = re.sub(r'\s+', '-', company_name.strip())  # Replace spaces with hyphens
                if len(company_name) > 2 and len(company_name) < 30:  # Reasonable length
                    return company_name.lower()

        return None

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
        print(f"Agent Type: {self.agent_type.title()} Analysis")

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
        print(f"   📄 combined_{self.agent_type}_analysis.md - Full analysis report")
        print("   📄 analysis_summary.md - Quick summary")


def main():
    """Main entry point for the pipeline demo"""
    print("AI-Shark Demo: End-to-End Startup Analysis Pipeline")
    print("=" * 60)

    # Determine agent type
    import sys
    if sys.stdin.isatty():
        print("\nSelect Analysis Agent:")
        print("1. Business Analysis Agent - Revenue, scalability, competitive positioning")
        print("2. Market Analysis Agent - Market size, competition, positioning")
        agent_choice = input("Choose agent (1/2) [1]: ").strip() or "1"
        agent_type = "business" if agent_choice == "1" else "market"

        use_real_llm = input("Use real LLM API? (y/N): ").lower().startswith('y')
    else:
        # Non-interactive mode - use defaults
        agent_type = "business"
        use_real_llm = False
        print("Running in non-interactive mode - using Business Agent and Mock LLM")

    print(f"\n🔧 Configuration:")
    print(f"   📊 Agent Type: {agent_type.title()} Analysis")
    print(f"   🤖 LLM Mode: {'Real API' if use_real_llm else 'Mock/Demo'}")

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
    pipeline = AnalysisPipelineDemo(use_real_llm=use_real_llm, agent_type=agent_type)
    pipeline.run_pipeline()


if __name__ == "__main__":
    main()