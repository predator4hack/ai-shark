"""
Analysis Loader Utility

This module provides functionality to load and validate analysis reports
from the /outputs/<company-name>/analysis/ directory for questionnaire generation.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class AnalysisLoadError(Exception):
    """Custom exception for analysis loading errors"""
    pass


def load_analysis_reports(company_dir: str) -> Dict[str, str]:
    """
    Load all analysis reports from the company's analysis directory.
    
    Args:
        company_dir: Path to the company directory (e.g., "/outputs/company-name")
        
    Returns:
        Dictionary with report types as keys and content as values
        
    Raises:
        AnalysisLoadError: If no valid reports are found or directory doesn't exist
    """
    company_path = Path(company_dir)
    analysis_dir = company_path / "analysis"
    
    # Validate company directory exists
    if not company_path.exists():
        raise AnalysisLoadError(f"Company directory '{company_dir}' does not exist")
    
    # Validate analysis directory exists
    if not analysis_dir.exists():
        raise AnalysisLoadError(f"Analysis directory '{analysis_dir}' does not exist")
    
    # Find all markdown files in analysis directory
    analysis_files = list(analysis_dir.glob("*.md"))
    
    if not analysis_files:
        raise AnalysisLoadError(f"No analysis reports found in '{analysis_dir}'")
    
    print(f"📄 Found {len(analysis_files)} analysis files in {analysis_dir}")
    
    reports = {}
    
    for file_path in analysis_files:
        try:
            # Extract report type from filename (e.g., "business_analysis.md" -> "business_analysis")
            report_type = file_path.stem
            
            # Skip non-analysis files
            if report_type in ["analysis_summary", "README"]:
                print(f"   ⏭️ Skipping {file_path.name} (summary/readme file)")
                continue
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                print(f"   ⚠️ Warning: {file_path.name} is empty, skipping")
                continue
            
            reports[report_type] = content
            print(f"   ✅ Loaded {report_type}: {len(content):,} characters")
            
        except Exception as e:
            print(f"   ❌ Error loading {file_path.name}: {e}")
            continue
    
    if not reports:
        raise AnalysisLoadError(f"No valid analysis reports found in '{analysis_dir}'")
    
    print(f"📊 Successfully loaded {len(reports)} analysis reports")
    return reports


def validate_reports(reports: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validate that the loaded reports contain meaningful content.
    
    Args:
        reports: Dictionary of report type -> content
        
    Returns:
        Tuple of (is_valid: bool, issues: List[str])
    """
    issues = []
    
    if not reports:
        issues.append("No reports provided")
        return False, issues
    
    for report_type, content in reports.items():
        # Check minimum content length
        if len(content.strip()) < 100:
            issues.append(f"Report '{report_type}' is too short ({len(content)} chars)")
        
        # Check for basic structure markers
        if not any(marker in content.lower() for marker in ['#', '##', '**', 'analysis', 'report']):
            issues.append(f"Report '{report_type}' appears to lack proper structure")
        
        # Check for error indicators
        if any(error_word in content.lower() for error_word in ['error', 'failed', 'exception', 'traceback']):
            issues.append(f"Report '{report_type}' may contain error messages")
    
    is_valid = len(issues) == 0
    return is_valid, issues


def format_reports_for_llm(reports: Dict[str, str]) -> str:
    """
    Format the analysis reports for LLM consumption.
    
    Args:
        reports: Dictionary of report type -> content
        
    Returns:
        Formatted string ready for LLM prompt
    """
    formatted_sections = []
    
    # Add header
    formatted_sections.append("# ANALYSIS REPORTS SUMMARY")
    formatted_sections.append(f"\nTotal Reports: {len(reports)}")
    formatted_sections.append(f"Report Types: {', '.join(reports.keys())}\n")
    formatted_sections.append("=" * 80)
    
    # Add each report as a distinct section
    for report_type, content in reports.items():
        # Clean report type name for display
        display_name = report_type.replace('_', ' ').title()
        
        formatted_sections.append(f"\n## {display_name}")
        formatted_sections.append(f"Report Type: {report_type}")
        formatted_sections.append(f"Content Length: {len(content):,} characters")
        formatted_sections.append("-" * 40)
        formatted_sections.append(content)
        formatted_sections.append("\n" + "=" * 80)
    
    return "\n".join(formatted_sections)


def extract_company_name(company_dir: str) -> Optional[str]:
    """
    Extract company name from the directory path.
    
    Args:
        company_dir: Path to the company directory
        
    Returns:
        Company name or None if extraction fails
    """
    try:
        company_path = Path(company_dir)
        company_name = company_path.name
        
        # Clean company name (remove special characters, convert to title case)
        clean_name = re.sub(r'[^\w\s-]', '', company_name)
        clean_name = re.sub(r'[-_]', ' ', clean_name)
        clean_name = clean_name.strip().title()
        
        if clean_name and len(clean_name) > 1:
            return clean_name
    except Exception:
        pass
    
    return None


def get_report_metadata(reports: Dict[str, str]) -> Dict[str, any]:
    """
    Generate metadata about the loaded reports.
    
    Args:
        reports: Dictionary of report type -> content
        
    Returns:
        Dictionary with metadata information
    """
    total_chars = sum(len(content) for content in reports.values())
    total_words = sum(len(content.split()) for content in reports.values())
    
    metadata = {
        "total_reports": len(reports),
        "report_types": list(reports.keys()),
        "total_characters": total_chars,
        "total_words": total_words,
        "average_report_length": total_chars // len(reports) if reports else 0,
        "loaded_at": datetime.now().isoformat()
    }
    
    return metadata


if __name__ == "__main__":
    """Test the analysis loader with sample data"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python analysis_loader.py <company_dir>")
        sys.exit(1)
    
    company_dir = sys.argv[1]
    
    try:
        print(f"Testing analysis loader with: {company_dir}")
        reports = load_analysis_reports(company_dir)
        
        print("\n📊 Validation Results:")
        is_valid, issues = validate_reports(reports)
        if is_valid:
            print("✅ All reports are valid")
        else:
            print("❌ Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        
        print("\n📈 Metadata:")
        metadata = get_report_metadata(reports)
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        
        print("\n📝 Formatted for LLM (first 500 chars):")
        formatted = format_reports_for_llm(reports)
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        
    except AnalysisLoadError as e:
        print(f"❌ Analysis loading failed: {e}")
        sys.exit(1)