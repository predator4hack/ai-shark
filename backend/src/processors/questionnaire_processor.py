"""
Questionnaire Processor for AI-Shark Analysis Pipeline

This processor automatically generates founder questionnaires after analysis agents complete.
Integrates with the existing analysis pipeline workflow.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..agents.questionnaire_agent import QuestionnaireAgent, create_questionnaire_agent
from ..models.questionnaire_models import QuestionnaireConfig, QuestionnaireResult
from ..utils.llm_manager import LLMManager
from ..utils.output_manager import OutputManager


class QuestionnaireProcessor:
    """
    Processor that generates founder questionnaires from completed analysis reports
    """
    
    def __init__(self, llm_manager: Optional[LLMManager] = None, 
                 output_manager: Optional[OutputManager] = None):
        """
        Initialize the Questionnaire Processor
        
        Args:
            llm_manager: Optional LLM manager instance
            output_manager: Optional output manager instance
        """
        self.processor_name = "QuestionnaireProcessor"
        self.llm_manager = llm_manager or LLMManager()
        self.output_manager = output_manager or OutputManager()
        self.questionnaire_agent = create_questionnaire_agent(self.llm_manager)
        
    def should_run_questionnaire(self, company_dir: str) -> bool:
        """
        Check if questionnaire should be generated for a company
        
        Args:
            company_dir: Path to company directory
            
        Returns:
            True if questionnaire should be generated, False otherwise
        """
        company_path = Path(company_dir)
        analysis_dir = company_path / "analysis"
        
        # Check if analysis directory exists and has analysis files
        if not analysis_dir.exists():
            print(f"📁 No analysis directory found: {analysis_dir}")
            return False
        
        # Check for analysis files (excluding summary)
        analysis_files = [f for f in analysis_dir.glob("*.md") 
                         if f.name != "analysis_summary.md"]
        
        if not analysis_files:
            print(f"📁 No analysis reports found in: {analysis_dir}")
            return False
        
        # Check if questionnaire already exists
        questionnaire_file = company_path / "founders-checklist.md"
        if questionnaire_file.exists():
            print(f"📄 Questionnaire already exists: {questionnaire_file}")
            return False
        
        print(f"✅ Ready for questionnaire generation: {len(analysis_files)} reports available")
        return True
    
    def process_company_questionnaire(self, company_dir: str,
                                    config: Optional[QuestionnaireConfig] = None) -> QuestionnaireResult:
        """
        Process questionnaire generation for a single company

        Args:
            company_dir: Path to company directory
            config: Optional questionnaire configuration

        Returns:
            QuestionnaireResult with processing results
        """
        print(f"\n🎯 Processing Questionnaire for Company")
        print("=" * 50)

        company_path = Path(company_dir)
        company_name = company_path.name

        print(f"Company: {company_name}")
        print(f"Directory: {company_dir}")

        # Check if questionnaire already exists
        questionnaire_file = company_path / "founders-checklist.md"
        if questionnaire_file.exists():
            print(f"📄 Questionnaire already exists: {questionnaire_file}")

            # Return existing questionnaire info instead of treating as failure
            try:
                import os
                file_stats = os.stat(questionnaire_file)
                return QuestionnaireResult(
                    success=True,
                    markdown_file=str(questionnaire_file),
                    processing_time=0.0,
                    error_message=None,
                    metadata={
                        "company_name": company_name,
                        "already_existed": True,
                        "file_size": file_stats.st_size,
                        "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                    }
                )
            except Exception as e:
                print(f"⚠️ Error reading existing questionnaire: {e}")
                # Fall through to check if we should regenerate

        # Check if processing should proceed (analysis files exist, etc.)
        if not self.should_run_questionnaire(company_dir):
            return QuestionnaireResult(
                success=False,
                error_message="Questionnaire generation not needed or not ready",
                metadata={"company_name": company_name, "reason": "skip_generation"}
            )
        
        # Use default config if none provided
        if config is None:
            config = QuestionnaireConfig(
                company_dir=company_dir,
                use_real_llm=True,
                output_format="markdown"
            )
        
        try:
            # Process the questionnaire
            result = self.questionnaire_agent.process_company(company_dir, config)
            
            if result.success:
                # Update company metadata
                self._update_company_metadata(company_dir, result)
                
                print(f"🎉 Questionnaire processing completed for {company_name}")
            else:
                print(f"❌ Questionnaire processing failed for {company_name}: {result.error_message}")
            
            return result
            
        except Exception as e:
            error_msg = f"Questionnaire processing failed: {e}"
            print(f"❌ {error_msg}")
            
            return QuestionnaireResult(
                success=False,
                error_message=error_msg,
                metadata={"company_name": company_name, "error_type": type(e).__name__}
            )
    
    def process_multiple_companies(self, base_output_dir: str = "outputs") -> Dict[str, QuestionnaireResult]:
        """
        Process questionnaires for all companies in the output directory
        
        Args:
            base_output_dir: Base directory containing company folders
            
        Returns:
            Dictionary mapping company names to QuestionnaireResult
        """
        print(f"\n🚀 Batch Questionnaire Processing")
        print("=" * 60)
        print(f"Scanning directory: {base_output_dir}")
        
        results = {}
        base_path = Path(base_output_dir)
        
        if not base_path.exists():
            print(f"❌ Output directory not found: {base_output_dir}")
            return results
        
        # Find all company directories
        company_dirs = [d for d in base_path.iterdir() 
                       if d.is_dir() and not d.name.startswith('.')]
        
        if not company_dirs:
            print(f"📁 No company directories found in: {base_output_dir}")
            return results
        
        print(f"📊 Found {len(company_dirs)} company directories")
        
        # Process each company
        for i, company_dir in enumerate(company_dirs, 1):
            company_name = company_dir.name
            print(f"\n📈 Processing {i}/{len(company_dirs)}: {company_name}")
            print("-" * 40)
            
            try:
                result = self.process_company_questionnaire(str(company_dir))
                results[company_name] = result
                
                if result.success:
                    print(f"✅ {company_name}: Questionnaire generated")
                else:
                    print(f"⚠️ {company_name}: {result.error_message}")
                    
            except Exception as e:
                print(f"❌ {company_name}: Unexpected error - {e}")
                results[company_name] = QuestionnaireResult(
                    success=False,
                    error_message=f"Unexpected error: {e}",
                    metadata={"company_name": company_name}
                )
        
        # Display summary
        self._display_batch_summary(results)
        
        return results
    
    def _update_company_metadata(self, company_dir: str, result: QuestionnaireResult) -> None:
        """
        Update company metadata with questionnaire information
        
        Args:
            company_dir: Path to company directory
            result: QuestionnaireResult to record
        """
        try:
            company_path = Path(company_dir)
            metadata_file = company_path / "metadata.json"
            
            # Load existing metadata or create new
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            # Add questionnaire information
            metadata["questionnaire"] = {
                "generated": True,
                "generated_at": result.generated_at.isoformat(),
                "processing_time": result.processing_time,
                "markdown_file": result.markdown_file,
                "agent": "QuestionnaireAgent",
                "source_reports": result.metadata.get("report_types", []),
                "total_reports": result.metadata.get("total_reports", 0)
            }
            
            # Update general metadata
            metadata["last_updated"] = datetime.now().isoformat()
            metadata["processing_status"] = metadata.get("processing_status", {})
            metadata["processing_status"]["questionnaire_complete"] = True
            
            # Save updated metadata
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"📝 Updated metadata: {metadata_file}")
            
        except Exception as e:
            print(f"⚠️ Failed to update metadata: {e}")
    
    def _display_batch_summary(self, results: Dict[str, QuestionnaireResult]) -> None:
        """
        Display summary of batch processing results
        
        Args:
            results: Dictionary of processing results
        """
        successful = [r for r in results.values() if r.success]
        failed = [r for r in results.values() if not r.success]
        skipped = [r for r in failed if "skip_generation" in r.metadata.get("reason", "")]
        actual_failed = [r for r in failed if "skip_generation" not in r.metadata.get("reason", "")]
        
        print(f"\n📊 Batch Processing Summary")
        print("=" * 50)
        print(f"Total Companies: {len(results)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"⚠️ Skipped: {len(skipped)}")
        print(f"❌ Failed: {len(actual_failed)}")
        
        if successful:
            print(f"\n✅ Successfully Generated Questionnaires:")
            for company, result in results.items():
                if result.success:
                    print(f"   📄 {company}: {result.markdown_file}")
        
        if actual_failed:
            print(f"\n❌ Failed Generations:")
            for company, result in results.items():
                if not result.success and "skip_generation" not in result.metadata.get("reason", ""):
                    print(f"   ❌ {company}: {result.error_message}")
        
        if skipped:
            print(f"\n⚠️ Skipped (Already exists or not ready): {len(skipped)}")

    def _get_successful_agents(self, company_dir: str) -> List[str]:
        """
        Determine which agents completed successfully

        Args:
            company_dir: Path to company directory

        Returns:
            Sorted list of agent types that have analysis files
        """
        company_path = Path(company_dir)
        analysis_dir = company_path / "analysis"

        if not analysis_dir.exists():
            return []

        # Find all analysis files (exclude summary)
        analysis_files = [f for f in analysis_dir.glob("*_analysis.md")
                         if f.name != "analysis_summary.md"]

        # Extract agent types from filenames
        # business_analysis.md -> business
        agents = []
        for file_path in analysis_files:
            agent_type = file_path.stem.replace('_analysis', '')
            agents.append(agent_type)

        return sorted(agents)

    def _calculate_source_hashes(self, company_dir: str) -> Dict[str, str]:
        """
        Calculate SHA-256 hashes of source documents for cache validation

        Args:
            company_dir: Path to company directory

        Returns:
            Dictionary with content hashes
        """
        import hashlib

        company_path = Path(company_dir)
        hashes = {}

        pitch_deck_path = company_path / "pitch_deck.md"
        if pitch_deck_path.exists():
            content = pitch_deck_path.read_text(encoding='utf-8')
            hashes['pitch_deck_hash'] = hashlib.sha256(content.encode()).hexdigest()

        public_data_path = company_path / "public_data.md"
        if public_data_path.exists():
            content = public_data_path.read_text(encoding='utf-8')
            hashes['public_data_hash'] = hashlib.sha256(content.encode()).hexdigest()

        return hashes

    def run_post_analysis_questionnaire(self, company_dir: str) -> QuestionnaireResult:
        """
        Run questionnaire generation with intelligent caching

        Cache Logic:
        1. Check Firestore for existing questionnaire with same agents
        2. Validate source hashes match
        3. If valid → return cached (0s processing)
        4. If invalid/missing → generate fresh and save to Firestore

        Args:
            company_dir: Path to company directory

        Returns:
            QuestionnaireResult with processing results
        """
        from ..api.services.firestore_manager import firestore_db
        import json

        print(f"\n🎯 Post-Analysis Questionnaire Generation (with Caching)")
        print("=" * 60)

        company_path = Path(company_dir)
        company_name = company_path.name
        print(f"Company: {company_name}")

        # Determine successful agents
        successful_agents = self._get_successful_agents(company_dir)

        if not successful_agents:
            print("❌ No successful analyses found")
            return QuestionnaireResult(
                success=False,
                error_message="No successful analyses available"
            )

        print(f"✅ Found {len(successful_agents)} analyses: {', '.join(successful_agents)}")

        # ============= CACHING LOGIC =============

        if firestore_db.enabled:
            try:
                metadata_file = company_path / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)

                    website = metadata.get('website')
                    if website:
                        print(f"\n🔍 Checking Firestore cache...")

                        company = firestore_db.get_company_by_url(website)
                        if company:
                            company_id = company['company_id']
                            current_hashes = self._calculate_source_hashes(company_dir)

                            # Check cache validity
                            if firestore_db.check_questionnaire_valid(
                                company_id, successful_agents, current_hashes
                            ):
                                # CACHE HIT!
                                cached_q = firestore_db.get_questionnaire(company_id, successful_agents)

                                if cached_q:
                                    # Save to file
                                    questionnaire_file = company_path / "founders-checklist.md"
                                    questionnaire_file.write_text(cached_q['content'], encoding='utf-8')

                                    print(f"✅ Using cached questionnaire (0s)")
                                    print(f"📄 File: {questionnaire_file}")

                                    return QuestionnaireResult(
                                        success=True,
                                        questionnaire_content=cached_q['content'],
                                        markdown_file=str(questionnaire_file),
                                        processing_time=0.0,  # Instant
                                        metadata={
                                            "company_name": company_name,
                                            "cached": True,
                                            "agents_used": successful_agents,
                                            "cache_timestamp": cached_q.get('created_at')
                                        }
                                    )
                            else:
                                print(f"   ⚠️ Cache miss/invalid - generating fresh")
            except Exception as e:
                print(f"⚠️ Cache check failed: {e}")
                print("   Continuing with generation...")

        # ============= GENERATE FRESH =============

        print(f"\n🔄 Generating new questionnaire...")

        config = QuestionnaireConfig(
            company_dir=company_dir,
            use_real_llm=True,
            output_format="markdown",
            max_retries=3
        )

        result = self.process_company_questionnaire(company_dir, config)

        # Save to Firestore if successful
        if result.success and firestore_db.enabled:
            try:
                metadata_file = company_path / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)

                    website = metadata.get('website')
                    if website:
                        company = firestore_db.get_company_by_url(website)
                        if company:
                            company_id = company['company_id']
                            current_hashes = self._calculate_source_hashes(company_dir)

                            questionnaire_data = {
                                'content': result.questionnaire_content,
                                'processing_time': result.processing_time,
                                'source_hashes': current_hashes,
                                'metadata': {
                                    'report_types': successful_agents,
                                    'total_reports': len(successful_agents)
                                }
                            }

                            agents_hash = firestore_db.save_questionnaire(
                                company_id, successful_agents, questionnaire_data
                            )
                            print(f"   💾 Saved to Firestore (hash: {agents_hash})")
            except Exception as e:
                print(f"⚠️ Failed to save to Firestore: {e}")

        return result


def create_questionnaire_processor(llm_manager: Optional[LLMManager] = None,
                                 output_manager: Optional[OutputManager] = None) -> QuestionnaireProcessor:
    """
    Factory function to create a QuestionnaireProcessor instance
    
    Args:
        llm_manager: Optional LLM manager instance
        output_manager: Optional output manager instance
        
    Returns:
        Configured QuestionnaireProcessor instance
    """
    return QuestionnaireProcessor(llm_manager=llm_manager, output_manager=output_manager)


# CLI support for standalone usage
if __name__ == "__main__":
    import argparse
    
    def main():
        parser = argparse.ArgumentParser(description='Generate founder questionnaires from analysis reports')
        parser.add_argument('--company-dir', help='Specific company directory to process')
        parser.add_argument('--batch', action='store_true', help='Process all companies in outputs directory')
        parser.add_argument('--output-dir', default='outputs', help='Base output directory (default: outputs)')
        
        args = parser.parse_args()
        
        processor = create_questionnaire_processor()
        
        if args.company_dir:
            # Process single company
            result = processor.process_company_questionnaire(args.company_dir)
            
            if result.success:
                print(f"\n🎉 Success! Questionnaire saved to: {result.markdown_file}")
            else:
                print(f"\n❌ Failed: {result.error_message}")
                
        elif args.batch:
            # Process all companies
            results = processor.process_multiple_companies(args.output_dir)
            
            successful = sum(1 for r in results.values() if r.success)
            print(f"\n🎉 Batch processing complete: {successful}/{len(results)} successful")
            
        else:
            print("❌ Please specify either --company-dir or --batch")
            parser.print_help()
    
    main()