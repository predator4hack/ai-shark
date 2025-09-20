"""
Questionnaire Agent for AI-Shark

This agent processes all analysis reports from various agents and generates 
comprehensive questionnaire documents for founders to clarify investment gaps.
"""

import os
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..utils.llm_manager import LLMManager
from ..utils.prompt_manager import PromptManager
from ..utils.analysis_loader import load_analysis_reports, extract_company_name
from ..models.questionnaire_models import (
    QuestionnaireConfig, 
    AnalysisReportCollection,
    QuestionnaireResult,
    validate_questionnaire_content,
    create_analysis_report_collection_from_dict
)
from ..utils.docx_converter import convert_founders_checklist_to_docx, is_docx_conversion_available


class QuestionnaireAgent:
    """
    Agent responsible for generating founder questionnaires from analysis reports
    """
    
    def __init__(self, llm_manager: Optional[LLMManager] = None):
        """
        Initialize the Questionnaire Agent
        
        Args:
            llm_manager: Optional LLM manager instance. If None, creates a new one.
        """
        self.agent_name = "QuestionnaireAgent"
        self.llm_manager = llm_manager or LLMManager()
        self.prompt_manager = PromptManager()
        
    def load_analysis_reports(self, company_dir: str) -> AnalysisReportCollection:
        """
        Load all analysis reports from company's analysis directory using analysis_loader
        
        Args:
            company_dir: Path to the company directory (e.g., "outputs/company-name")
            
        Returns:
            AnalysisReportCollection with all loaded reports
            
        Raises:
            FileNotFoundError: If analysis directory doesn't exist
            ValueError: If no valid reports found
        """
        try:
            # Use analysis_loader as the single source of truth
            reports_dict = load_analysis_reports(company_dir)
            
            # Extract company name from directory
            company_name = extract_company_name(company_dir)
            
            # Convert to rich data model
            collection = create_analysis_report_collection_from_dict(
                reports_dict=reports_dict,
                company_name=company_name,
                company_dir=company_dir
            )
            
            print(f"\n✅ {collection.summary}")
            return collection
            
        except Exception as e:
            # Re-raise with consistent error types for backwards compatibility
            if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                raise FileNotFoundError(str(e))
            else:
                raise ValueError(str(e))
    
    def generate_questionnaire(self, report_collection: AnalysisReportCollection, 
                             config: QuestionnaireConfig) -> QuestionnaireResult:
        """
        Generate founder questionnaire from analysis reports
        
        Args:
            report_collection: Collection of analysis reports
            config: Configuration for questionnaire generation
            
        Returns:
            QuestionnaireResult with generation results
        """
        print(f"\n🤖 Generating Founder Questionnaire")
        print("=" * 50)
        print(f"Company: {report_collection.company_name}")
        print(f"Reports: {', '.join(report_collection.report_types)}")
        print(f"LLM Info: {self.llm_manager.get_model_info()}")
        
        start_time = datetime.now()
        
        try:
            # Prepare prompt parameters based on available reports
            prompt_params = {
                "company_name": report_collection.company_name,
                "total_reports": len(report_collection.valid_reports),
                "report_types": ', '.join(report_collection.report_types)
            }
            
            # Add individual report contents based on what's available
            for report_type, report in report_collection.valid_reports.items():
                if "business" in report_type.lower():
                    prompt_params["business_analysis"] = report.content
                elif "market" in report_type.lower():
                    prompt_params["market_analysis"] = report.content
                else:
                    # For other report types, use generic parameter names
                    param_name = report_type.replace("_", " ").replace("-", " ").strip()
                    prompt_params[f"{report_type}_analysis"] = report.content
            
            # Debug output
            print(f"🔍 Available reports: {list(report_collection.valid_reports.keys())}")
            print(f"🔍 Prompt parameters being passed: {list(prompt_params.keys())}")
            
            # Ensure we have parameters for the template (even if empty)
            expected_params = ["business_analysis", "market_analysis", "financial_analysis", 
                             "competitive_analysis", "technology_analysis"]
            
            for param in expected_params:
                if param not in prompt_params:
                    prompt_params[param] = ""  # Empty string for missing reports
            
            prompt = self.prompt_manager.format_prompt(
                config.prompt_key,
                version=config.prompt_version,
                **prompt_params
            )
            
            print(f"📝 Prompt size: {len(prompt):,} characters")
            print(f"🔄 Starting generation with {config.max_retries} max retries...")
            
            # Generate questionnaire with retry logic
            questionnaire_content = self._generate_with_retry(prompt, config.max_retries)
            
            if not questionnaire_content:
                raise Exception("Failed to generate questionnaire content")
            
            # Validate content
            if not validate_questionnaire_content(questionnaire_content):
                print("⚠️ Generated content failed validation, but proceeding...")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ Generation successful in {processing_time:.2f}s")
            print(f"📊 Content length: {len(questionnaire_content):,} characters")
            
            return QuestionnaireResult(
                success=True,
                questionnaire_content=questionnaire_content,
                processing_time=processing_time,
                metadata={
                    "company_name": report_collection.company_name,
                    "report_types": report_collection.report_types,
                    "total_reports": report_collection.total_reports,
                    "total_content_chars": report_collection.total_characters,
                    "llm_info": self.llm_manager.get_model_info()
                }
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Questionnaire generation failed: {e}"
            print(f"❌ {error_msg}")
            
            return QuestionnaireResult(
                success=False,
                error_message=error_msg,
                processing_time=processing_time,
                metadata={
                    "company_name": report_collection.company_name,
                    "report_types": report_collection.report_types if report_collection else [],
                    "error_type": type(e).__name__
                }
            )
    
    def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Generate questionnaire content with retry logic
        
        Args:
            prompt: The formatted prompt for LLM
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated questionnaire content or None if all retries fail
        """
        for attempt in range(max_retries):
            try:
                print(f"🔄 Generation attempt {attempt + 1}/{max_retries}")
                
                response = self.llm_manager.invoke_with_retry(prompt)
                
                if response and response.strip():
                    print(f"✅ Generation successful on attempt {attempt + 1}")
                    return response
                else:
                    print(f"⚠️ Empty response on attempt {attempt + 1}")
                    
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    sleep_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"⏱️ Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    print("❌ All retry attempts exhausted")
                    
        return None
    
    def save_questionnaire(self, result: QuestionnaireResult, 
                          output_dir: str, filename: str = "founders-checklist.md",
                          export_docx: bool = False) -> QuestionnaireResult:
        """
        Save questionnaire to markdown file and optionally convert to DOCX
        
        Args:
            result: QuestionnaireResult containing the generated content
            output_dir: Directory to save the file
            filename: Output filename (default: "founders-checklist.md")
            export_docx: Whether to also create a DOCX version
            
        Returns:
            Updated QuestionnaireResult with file paths
        """
        if not result.success or not result.questionnaire_content:
            print("❌ Cannot save - no valid questionnaire content")
            return result
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create full markdown content with metadata
        company_name = result.metadata.get("company_name", "Unknown")
        
        full_content = f"""# Founder Investment Questionnaire - {company_name}

**Generated:** {result.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Engine:** AI-Shark Questionnaire Agent
**Processing Time:** {result.processing_time:.2f} seconds
**Source Reports:** {', '.join(result.metadata.get('report_types', []))}

---

{result.questionnaire_content}

---

*This questionnaire was generated by AI-Shark's multi-agent analysis system based on comprehensive business and market analysis reports.*
"""
        
        markdown_file = output_path / filename
        
        try:
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            print(f"📄 Questionnaire saved: {markdown_file}")
            print(f"📊 File size: {len(full_content):,} characters")
            
            # Update result with file path
            result.markdown_file = str(markdown_file)
            
            # Generate DOCX version if requested
            if export_docx:
                try:
                    if is_docx_conversion_available():
                        docx_file = convert_founders_checklist_to_docx(str(markdown_file))
                        result.docx_file = docx_file
                        print(f"📄 DOCX version saved: {docx_file}")
                    else:
                        print("⚠️ DOCX conversion not available - install python-docx package")
                except Exception as e:
                    print(f"⚠️ DOCX conversion failed: {e}")
            
        except Exception as e:
            print(f"❌ Failed to save questionnaire: {e}")
            result.error_message = f"Save failed: {e}"
            result.success = False
        
        return result
    
    def process_company(self, company_dir: str, config: Optional[QuestionnaireConfig] = None) -> QuestionnaireResult:
        """
        Complete end-to-end processing for a company
        
        Args:
            company_dir: Path to company directory containing analysis reports
            config: Optional configuration. If None, uses defaults.
            
        Returns:
            QuestionnaireResult with complete processing results
        """
        # Use default config if none provided
        if config is None:
            config = QuestionnaireConfig(company_dir=company_dir)
        
        print(f"🚀 Processing Company Questionnaire")
        print("=" * 60)
        print(f"Company Directory: {company_dir}")
        print(f"Agent: {self.agent_name}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Step 1: Load analysis reports
            print(f"\n📊 Step 1: Loading Analysis Reports")
            report_collection = self.load_analysis_reports(company_dir)
            
            # Step 2: Generate questionnaire
            print(f"\n🤖 Step 2: Generating Questionnaire")
            result = self.generate_questionnaire(report_collection, config)
            
            if not result.success:
                return result
            
            # Step 3: Save questionnaire
            print(f"\n💾 Step 3: Saving Questionnaire")
            export_docx = config.output_format in ["docx", "both"]
            result = self.save_questionnaire(result, company_dir, export_docx=export_docx)
            
            # Display summary
            if result.success:
                print(f"\n🎉 Questionnaire Processing Complete!")
                print(f"📁 Output file: {result.markdown_file}")
                print(f"⏱️ Total processing time: {result.processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            error_msg = f"Company processing failed: {e}"
            print(f"❌ {error_msg}")
            
            return QuestionnaireResult(
                success=False,
                error_message=error_msg,
                metadata={"company_dir": company_dir, "error_type": type(e).__name__}
            )


def create_questionnaire_agent(llm_manager: Optional[LLMManager] = None) -> QuestionnaireAgent:
    """
    Factory function to create a QuestionnaireAgent instance
    
    Args:
        llm_manager: Optional LLM manager instance
        
    Returns:
        Configured QuestionnaireAgent instance
    """
    return QuestionnaireAgent(llm_manager=llm_manager)