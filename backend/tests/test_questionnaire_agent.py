#!/usr/bin/env python3
"""
Test script for the new Questionnaire Agent implementation

This script demonstrates the questionnaire generation functionality.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.processors.questionnaire_processor import create_questionnaire_processor
from src.models.questionnaire_models import QuestionnaireConfig


def test_questionnaire_generation():
    """Test questionnaire generation for available companies"""
    
    print("🧪 Testing Questionnaire Agent Implementation")
    print("=" * 60)
    
    # Check available companies
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("❌ No outputs directory found")
        return
    
    # Find companies with analysis directories
    companies_with_analysis = []
    for company_dir in outputs_dir.iterdir():
        if company_dir.is_dir() and not company_dir.name.startswith('.'):
            analysis_dir = company_dir / "analysis"
            if analysis_dir.exists():
                analysis_files = [f for f in analysis_dir.glob("*.md") 
                                if f.name != "analysis_summary.md"]
                if analysis_files:
                    companies_with_analysis.append({
                        "name": company_dir.name,
                        "path": str(company_dir),
                        "analysis_files": len(analysis_files)
                    })
    
    if not companies_with_analysis:
        print("❌ No companies found with analysis reports")
        print("   Run the analysis pipeline first to generate reports")
        return
    
    print(f"📊 Found {len(companies_with_analysis)} companies with analysis reports:")
    for company in companies_with_analysis:
        print(f"   - {company['name']}: {company['analysis_files']} analysis files")
    
    # Test questionnaire generation
    processor = create_questionnaire_processor()
    
    print(f"\n🤖 Testing Questionnaire Generation")
    print("-" * 50)
    
    results = {}
    
    for company in companies_with_analysis:
        company_name = company["name"]
        company_path = company["path"]
        
        print(f"\n📋 Generating questionnaire for: {company_name}")
        print(f"   Company directory: {company_path}")
        
        try:
            # Configure for testing
            config = QuestionnaireConfig(
                company_dir=company_path,
                use_real_llm=True,  # Set to False for mock testing
                output_format="both",  # Generate both markdown and DOCX
                max_retries=2
            )
            
            # Generate questionnaire
            result = processor.process_company_questionnaire(company_path, config)
            results[company_name] = result
            
            if result.success:
                print(f"   ✅ Success: {result.markdown_file}")
                if result.docx_file:
                    print(f"   ✅ DOCX: {result.docx_file}")
            else:
                print(f"   ❌ Failed: {result.error_message}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[company_name] = None
    
    # Display summary
    print(f"\n📊 Test Results Summary")
    print("=" * 50)
    
    successful = [name for name, result in results.items() 
                 if result and result.success]
    failed = [name for name, result in results.items() 
             if not result or not result.success]
    
    print(f"✅ Successful: {len(successful)}")
    for name in successful:
        result = results[name]
        print(f"   - {name}: {result.processing_time:.2f}s")
    
    print(f"❌ Failed: {len(failed)}")
    for name in failed:
        result = results[name]
        if result:
            print(f"   - {name}: {result.error_message}")
        else:
            print(f"   - {name}: Exception occurred")
    
    if successful:
        print(f"\n🎉 Questionnaire generation test completed!")
        print(f"Check the company directories for 'founders-checklist.md' files")
    else:
        print(f"\n⚠️ No questionnaires were generated successfully")
        print(f"Check LLM configuration and API keys")


def test_batch_processing():
    """Test batch processing of all companies"""
    
    print("\n🚀 Testing Batch Processing")
    print("=" * 50)
    
    processor = create_questionnaire_processor()
    results = processor.process_multiple_companies("outputs")
    
    print(f"\n📈 Batch processing results:")
    print(f"   Total companies processed: {len(results)}")
    
    successful = sum(1 for r in results.values() if r.success)
    print(f"   Successful generations: {successful}")
    
    if successful > 0:
        print(f"\n✅ Batch processing successful!")
    else:
        print(f"\n⚠️ No questionnaires generated in batch mode")


def main():
    """Main test function"""
    
    print("AI-Shark Questionnaire Agent Test Suite")
    print("=" * 60)
    
    # Test individual questionnaire generation
    test_questionnaire_generation()
    
    # Test batch processing
    test_batch_processing()
    
    print(f"\n🏁 Test Suite Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()