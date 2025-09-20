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
import inspect
import importlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

# Import AI-Shark components
from ..utils.document_loader import DirectoryLoader, MarkdownParser
from ..agents.base_agent import BaseAnalysisAgent
from ..agents import *  # Import all agents
from ..utils.llm_setup import get_llm, create_mock_llm, llm_setup
from ..models.document_models import StartupDocument, DocumentMetadata, ParsedContent
from ..models.analysis_models import BusinessAnalysis, MarketAnalysis
from config.settings import settings

class AnalysisPipeline:
    """
    AI-Shark analysis pipeline for processing startup documents with multiple agents
    """

    def __init__(self, company_dir: str, use_real_llm: bool = True):
        """
        Initialize the analysis pipeline

        Args:
            company_dir: Path to the company's output directory (e.g., "outputs/company-name")
            use_real_llm: Whether to use real LLM API (defaults to True for production)
        """
        self.use_real_llm = use_real_llm
        self.company_dir = Path(company_dir)
        self.analysis_dir = self.company_dir / "analysis"
        self.analysis_dir.mkdir(exist_ok=True)

        # Initialize components
        self.document_loader = DirectoryLoader()
        self.markdown_parser = MarkdownParser()
        
        # Discover and initialize all available agents
        self.available_agents = self.discover_available_agents()
        self.agents = self._initialize_agents()
        
        print(f"🤖 LLM Mode: {'Real API' if use_real_llm else 'Mock/Demo'}")
        if use_real_llm:
            print(f"🤖 Using real LLM: {llm_setup.get_model_info()}")
        else:
            print("🤖 Using Mock LLM for demonstration")
        
        print(f"📊 Discovered {len(self.agents)} analysis agents: {list(self.agents.keys())}")
        print(f"📁 Company directory: {self.company_dir}")
        print(f"📁 Analysis output directory: {self.analysis_dir}")

    def discover_available_agents(self) -> Dict[str, Callable]:
        """
        Dynamically discover all available analysis agents
        
        Returns:
            Dictionary mapping agent names to their factory functions
        """
        agent_registry = {}
        
        # Import the agents module to get access to all agent classes and factories
        import src.agents as agents_module
        
        # Look for factory functions (create_*_agent pattern)
        for name in dir(agents_module):
            if name.startswith('create_') and name.endswith('_agent'):
                factory_func = getattr(agents_module, name)
                if callable(factory_func):
                    # Extract agent type from function name (e.g., create_business_agent -> business)
                    agent_type = name.replace('create_', '').replace('_agent', '')
                    agent_registry[agent_type] = factory_func
                    print(f"🔍 Discovered agent: {agent_type} -> {name}")
        
        return agent_registry
    
    def _initialize_agents(self) -> Dict[str, BaseAnalysisAgent]:
        """
        Initialize all discovered agents
        
        Returns:
            Dictionary mapping agent names to initialized agent instances
        """
        agents = {}
        
        for agent_name, factory_func in self.available_agents.items():
            try:
                if self.use_real_llm:
                    agent = factory_func()
                else:
                    # Create mock LLM with realistic responses for this agent
                    mock_responses = self._get_mock_responses(agent_name)
                    mock_llm = create_mock_llm(mock_responses)
                    # Try to create agent with mock LLM (need to inspect the agent class)
                    agent_class_name = f"{agent_name.title()}AnalysisAgent"
                    if hasattr(globals(), agent_class_name):
                        agent_class = globals()[agent_class_name]
                        agent = agent_class(llm=mock_llm)
                    else:
                        # Fallback to factory function (may not work with mock)
                        agent = factory_func()
                
                agents[agent_name] = agent
                print(f"✅ Initialized {agent_name} agent: {agent.agent_name}")
                
            except Exception as e:
                print(f"❌ Failed to initialize {agent_name} agent: {e}")
                continue
        
        return agents

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
        Load documents for analysis from company directory

        Returns:
            List of loaded StartupDocument objects
        """
        print("\n📄 Loading Documents")
        print("=" * 50)

        documents = []

        # Define document files and their metadata in the company directory
        document_files = [
            {
                "path": self.company_dir / "pitch_deck.md",
                "name": "Startup Pitch Deck Analysis",
                "type": "pitch_deck",
                "description": "Analysis results from pitch deck processing"
            },
            {
                "path": self.company_dir / "public_data.md",
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

    def load_additional_documents(self) -> Optional[str]:
        """
        Load and concatenate all additional documents from the additional_docs directory
        
        Returns:
            Concatenated content of all additional documents, or None if no additional docs
        """
        additional_docs_dir = self.company_dir / "additional_docs"
        
        if not additional_docs_dir.exists():
            print("📄 No additional documents directory found")
            return None
        
        additional_files = list(additional_docs_dir.glob("*.md"))
        if not additional_files:
            print("📄 No additional documents found")
            return None
        
        print(f"\n📄 Loading {len(additional_files)} Additional Documents")
        print("=" * 50)
        
        concatenated_content = []
        concatenated_content.append("# Additional Documents Analysis\n")
        concatenated_content.append(f"This section contains analysis of {len(additional_files)} additional documents.\n\n")
        
        for file_path in additional_files:
            try:
                print(f"📖 Loading: {file_path.name}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Add document header and content
                concatenated_content.append(f"## Document: {file_path.stem}\n")
                concatenated_content.append(content)
                concatenated_content.append("\n\n---\n\n")
                
                print(f"   ✅ Loaded: {len(content):,} characters")
                
            except Exception as e:
                print(f"   ❌ Error loading {file_path.name}: {e}")
                continue
        
        result = "\n".join(concatenated_content)
        print(f"\n✅ Successfully concatenated {len(additional_files)} additional documents")
        print(f"📊 Total additional content: {len(result):,} characters")
        
        return result

    def run_all_agents_analysis(self) -> Dict[str, Any]:
        """
        Run analysis using all discovered agents with pitch deck, public data, and additional docs
        
        Returns:
            Dictionary with results from each agent, keyed by agent name
        """
        print("\n🧠 Multi-Agent Analysis Pipeline")
        print("=" * 60)
        
        # Load all documents
        documents = self.load_documents()
        additional_content = self.load_additional_documents()
        
        # Extract document contents
        pitch_deck_content = ""
        public_data_content = ""
        
        for doc in documents:
            if doc.document_type == "pitch_deck":
                pitch_deck_content = doc.content.raw_text
                print(f"📄 Pitch deck loaded: {len(pitch_deck_content)} characters")
            elif doc.document_type == "market_analysis":
                public_data_content = doc.content.raw_text
                print(f"🌐 Public data loaded: {len(public_data_content)} characters")
        
        # Handle missing public data (pass empty string as per requirements)
        if not public_data_content:
            public_data_content = ""
            print("⚠️ No public data found, using empty content")
        
        # Handle additional documents
        if not additional_content:
            additional_content = ""
            print("📄 No additional documents found")
        else:
            print(f"📄 Additional docs loaded: {len(additional_content)} characters")
        
        # Check minimum requirements
        if not pitch_deck_content:
            raise ValueError("Pitch deck content is required for analysis")
        
        all_results = {}
        
        # Run analysis with each agent
        for agent_name, agent in self.agents.items():
            try:
                print(f"\n🤖 Running {agent_name} analysis...")
                print("-" * 40)
                print(f"   Agent: {agent.agent_name}")
                
                start_time = datetime.now()
                
                # Combine public data and additional content for analysis
                combined_public_content = public_data_content
                if additional_content:
                    combined_public_content += "\n\n" + additional_content
                
                # Run combined analysis
                markdown_analysis = agent.analyze_combined_documents(
                    pitch_deck_content=pitch_deck_content,
                    public_data_content=combined_public_content
                )
                
                processing_time = datetime.now() - start_time
                
                # Store results
                all_results[agent_name] = {
                    "agent_name": agent.agent_name,
                    "markdown_analysis": markdown_analysis,
                    "processing_time": processing_time.total_seconds(),
                    "analysis_type": f"{agent_name}_analysis"
                }
                
                print(f"   ✅ {agent_name} analysis completed in {processing_time.total_seconds():.2f}s")
                print(f"   📝 Generated report: {len(markdown_analysis)} characters")
                
            except Exception as e:
                print(f"   ❌ {agent_name} analysis failed: {e}")
                all_results[agent_name] = {
                    "agent_name": agent.agent_name,
                    "error": str(e),
                    "status": "failed"
                }
                continue
        
        successful_analyses = [r for r in all_results.values() if "error" not in r]
        failed_analyses = [r for r in all_results.values() if "error" in r]
        
        print(f"\n📊 Multi-Agent Analysis Summary")
        print("=" * 40)
        print(f"✅ Successful: {len(successful_analyses)} agents")
        print(f"❌ Failed: {len(failed_analyses)} agents")
        
        return all_results

    def generate_agent_specific_reports(self, all_results: Dict[str, Any]) -> None:
        """
        Generate separate markdown reports for each agent
        
        Args:
            all_results: Dictionary with results from each agent
        """
        print("\n📝 Generating Agent-Specific Reports")
        print("=" * 50)
        
        successful_reports = 0
        
        for agent_name, result in all_results.items():
            if "error" in result:
                print(f"❌ Skipping {agent_name} - analysis failed")
                continue
            
            try:
                # Create report header
                report_header = f"""# {agent_name.title()} Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Engine:** AI-Shark Multi-Agent System
**Agent:** {result['agent_name']}
**Processing Time:** {result['processing_time']:.2f} seconds
**Analysis Type:** {result['analysis_type']}

## Company Analysis

"""
                
                # Combine header with LLM-generated analysis
                full_report = report_header + result['markdown_analysis']
                
                # Create output file
                report_file = self.analysis_dir / f"{agent_name}_analysis.md"
                
                # Write report
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(full_report)
                
                print(f"📄 Generated {agent_name} report: {report_file}")
                print(f"   📊 Report size: {len(full_report):,} characters")
                successful_reports += 1
                
            except Exception as e:
                print(f"❌ Failed to generate {agent_name} report: {e}")
                continue
        
        # Generate summary report
        self._generate_analysis_summary(all_results)
        
        print(f"\n✅ Generated {successful_reports} agent-specific reports in {self.analysis_dir}")

    def _generate_analysis_summary(self, all_results: Dict[str, Any]) -> None:
        """Generate a summary of all agent analyses"""
        
        successful_analyses = {k: v for k, v in all_results.items() if "error" not in v}
        failed_analyses = {k: v for k, v in all_results.items() if "error" in v}
        
        summary_content = f"""# Multi-Agent Analysis Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis System:** AI-Shark Multi-Agent Pipeline
**Company Directory:** {self.company_dir}

## Analysis Overview

- **Total Agents Executed:** {len(all_results)}
- **Successful Analyses:** {len(successful_analyses)}
- **Failed Analyses:** {len(failed_analyses)}
- **Total Processing Time:** {sum(r.get('processing_time', 0) for r in successful_analyses.values()):.2f} seconds

## Agent Results

### ✅ Successful Analyses

"""
        
        for agent_name, result in successful_analyses.items():
            summary_content += f"""#### {agent_name.title()} Analysis
- **Agent:** {result['agent_name']}
- **Processing Time:** {result['processing_time']:.2f} seconds
- **Report Length:** {len(result['markdown_analysis']):,} characters
- **Output File:** `{agent_name}_analysis.md`

"""
        
        if failed_analyses:
            summary_content += f"""
### ❌ Failed Analyses

"""
            for agent_name, result in failed_analyses.items():
                summary_content += f"""#### {agent_name.title()} Analysis
- **Agent:** {result.get('agent_name', 'Unknown')}
- **Error:** {result.get('error', 'Unknown error')}

"""
        
        summary_content += f"""
## Analysis Files Generated

"""
        for agent_name in successful_analyses.keys():
            summary_content += f"- `{agent_name}_analysis.md` - {agent_name.title()} analysis report\n"
        
        summary_content += f"""
## Next Steps

The individual agent analysis reports are available in the analysis directory. Each report contains:
- Comprehensive analysis from the specific agent's perspective
- Sector-specific insights and recommendations
- Business intelligence generated using advanced AI models

For complete insights, please review all successful analysis reports.
"""
        
        summary_file = self.analysis_dir / "analysis_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"📄 Generated analysis summary: {summary_file}")

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

    def run_pipeline(self) -> Dict[str, Any]:
        """
        Run the multi-agent analysis pipeline
        
        Returns:
            Dictionary with results from all agents
        """
        print("🚀 AI-Shark Multi-Agent Analysis Pipeline")
        print("=" * 60)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.use_real_llm:
            print(f"LLM Provider: {llm_setup.get_model_info().get('provider', 'unknown')}")
        print(f"Use Real LLM: {self.use_real_llm}")
        print(f"Analysis Type: Multi-Agent Analysis (All Available Agents)")
        print(f"Company Directory: {self.company_dir}")

        try:
            # Step 1: Run multi-agent analysis
            all_results = self.run_all_agents_analysis()
            
            if not all_results:
                print("❌ No analysis results generated. Pipeline cannot continue.")
                return {}

            # Step 2: Generate agent-specific reports
            self.generate_agent_specific_reports(all_results)

            # Step 3: Generate questionnaire if analysis successful
            questionnaire_result = self._run_questionnaire_generation(all_results)

            # Step 4: Display summary
            self._display_multi_agent_pipeline_summary(all_results, questionnaire_result)

            print(f"\n🎉 Multi-Agent Pipeline completed successfully!")
            print(f"📁 Check analysis directory: {self.analysis_dir}")
            if questionnaire_result and questionnaire_result.success:
                print(f"📄 Founder questionnaire: {questionnaire_result.markdown_file}")
            
            return all_results

        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _run_questionnaire_generation(self, all_results: Dict[str, Any]):
        """
        Generate questionnaire after successful analysis completion
        
        Args:
            all_results: Results from all analysis agents
            
        Returns:
            QuestionnaireResult or None if generation fails/skipped
        """
        # Check if we have successful analysis results
        successful_analyses = {k: v for k, v in all_results.items() if "error" not in v}
        
        if not successful_analyses:
            print("⚠️ No successful analyses - skipping questionnaire generation")
            return None
        
        try:
            # Import questionnaire processor (lazy import to avoid circular dependencies)
            from .questionnaire_processor import create_questionnaire_processor
            
            print(f"\n📋 Generating Founder Questionnaire")
            print("=" * 50)
            print(f"Based on {len(successful_analyses)} successful analysis reports")
            
            # Create questionnaire processor
            questionnaire_processor = create_questionnaire_processor()
            
            # Generate questionnaire for this company
            questionnaire_result = questionnaire_processor.run_post_analysis_questionnaire(
                str(self.company_dir)
            )
            
            if questionnaire_result.success:
                print(f"✅ Questionnaire generated successfully!")
                print(f"📄 File: {questionnaire_result.markdown_file}")
                print(f"⏱️ Processing time: {questionnaire_result.processing_time:.2f}s")
            else:
                print(f"❌ Questionnaire generation failed: {questionnaire_result.error_message}")
            
            return questionnaire_result
            
        except Exception as e:
            print(f"❌ Questionnaire generation error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _display_multi_agent_pipeline_summary(self, all_results: Dict[str, Any], questionnaire_result=None) -> None:
        """Display summary of the multi-agent pipeline results"""

        successful_analyses = {k: v for k, v in all_results.items() if "error" not in v}
        failed_analyses = {k: v for k, v in all_results.items() if "error" in v}

        print("\n📊 Multi-Agent Pipeline Summary")
        print("=" * 50)

        print(f"\n📈 Multi-Agent Analysis Completed")
        print("-" * 40)
        print(f"   🤖 Total Agents: {len(all_results)}")
        print(f"   ✅ Successful: {len(successful_analyses)}")
        print(f"   ❌ Failed: {len(failed_analyses)}")
        print(f"   ⏱️ Total Processing Time: {sum(r.get('processing_time', 0) for r in successful_analyses.values()):.2f}s")

        if successful_analyses:
            print(f"\n✨ Successful Agent Analyses:")
            for agent_name, result in successful_analyses.items():
                print(f"   ✅ {agent_name.title()}: {result['agent_name']}")
                print(f"      ⏱️ {result['processing_time']:.2f}s, 📝 {len(result['markdown_analysis']):,} chars")

        if failed_analyses:
            print(f"\n❌ Failed Agent Analyses:")
            for agent_name, result in failed_analyses.items():
                print(f"   ❌ {agent_name.title()}: {result.get('error', 'Unknown error')}")

        print(f"\n📁 Generated Files:")
        for agent_name in successful_analyses.keys():
            print(f"   📄 {agent_name}_analysis.md - {agent_name.title()} analysis report")
        print("   📄 analysis_summary.md - Multi-agent summary")
        
        # Add questionnaire information if available
        if questionnaire_result:
            if questionnaire_result.success:
                print(f"   📋 founders-checklist.md - Investment questionnaire for founders")
            else:
                print(f"   ⚠️ Questionnaire generation failed: {questionnaire_result.error_message}")


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
    pipeline = AnalysisPipeline(use_real_llm=use_real_llm, agent_type=agent_type)
    pipeline.run_pipeline()


if __name__ == "__main__":
    main()