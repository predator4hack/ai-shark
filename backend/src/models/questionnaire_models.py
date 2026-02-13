"""
Questionnaire Data Models

This module defines data structures and models for the questionnaire generation system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


def create_analysis_report_collection_from_dict(
    reports_dict: Dict[str, str], 
    company_name: Optional[str] = None,
    company_dir: str = ""
) -> "AnalysisReportCollection":
    """
    Create AnalysisReportCollection from a dictionary of reports (analysis_loader output)
    
    Args:
        reports_dict: Dictionary with report types as keys and content as values
        company_name: Optional company name
        company_dir: Path to company directory
        
    Returns:
        AnalysisReportCollection instance
    """
    reports = {}
    
    for report_type, content in reports_dict.items():
        if content and content.strip():
            report = AnalysisReport(
                report_type=report_type,
                content=content,
                file_path=None  # analysis_loader doesn't provide file paths
            )
            reports[report_type] = report
    
    return AnalysisReportCollection(
        reports=reports,
        company_name=company_name,
        company_dir=company_dir
    )


@dataclass
class QuestionnaireConfig:
    """Configuration for questionnaire generation"""
    
    company_dir: str
    use_real_llm: bool = True
    prompt_version: str = ""
    prompt_key: str = "questionaire_agent_v4"
    max_retries: int = 3
    output_format: str = "markdown"  # "markdown", "docx", "both"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.company_dir:
            raise ValueError("company_dir cannot be empty")
        
        if not Path(self.company_dir).exists():
            raise ValueError(f"Company directory does not exist: {self.company_dir}")
        
        if self.max_retries < 1:
            raise ValueError("max_retries must be at least 1")
        
        if self.output_format not in ["markdown", "docx", "both"]:
            raise ValueError("output_format must be 'markdown', 'docx', or 'both'")


@dataclass
class AnalysisReport:
    """Structure for individual analysis reports"""
    
    report_type: str
    content: str
    file_path: Optional[str] = None
    character_count: int = field(init=False)
    word_count: int = field(init=False)
    loaded_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate derived fields after initialization"""
        self.character_count = len(self.content)
        self.word_count = len(self.content.split())
    
    @property
    def is_valid(self) -> bool:
        """Check if the report contains valid content"""
        return (
            bool(self.content.strip()) and
            self.character_count >= 50 and
            self.word_count >= 10
        )
    
    @property
    def summary(self) -> str:
        """Get a brief summary of the report"""
        return f"{self.report_type}: {self.character_count:,} chars, {self.word_count:,} words"


@dataclass
class AnalysisReportCollection:
    """Collection of analysis reports with metadata"""
    
    reports: Dict[str, AnalysisReport]
    company_name: Optional[str] = None
    company_dir: str = ""
    loaded_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_reports(self) -> int:
        """Total number of reports"""
        return len(self.reports)
    
    @property
    def valid_reports(self) -> Dict[str, AnalysisReport]:
        """Get only valid reports"""
        return {k: v for k, v in self.reports.items() if v.is_valid}
    
    @property
    def total_characters(self) -> int:
        """Total character count across all reports"""
        return sum(report.character_count for report in self.reports.values())
    
    @property
    def total_words(self) -> int:
        """Total word count across all reports"""
        return sum(report.word_count for report in self.reports.values())
    
    @property
    def report_types(self) -> List[str]:
        """List of report types"""
        return list(self.reports.keys())
    
    @property
    def summary(self) -> str:
        """Get a summary of the collection"""
        valid_count = len(self.valid_reports)
        return (
            f"Analysis Collection: {valid_count}/{self.total_reports} valid reports, "
            f"{self.total_characters:,} chars, {self.total_words:,} words"
        )
    
    def get_formatted_content(self) -> str:
        """Get formatted content for LLM processing (legacy method - kept for compatibility)"""
        sections = []
        
        # Header
        sections.append("# ANALYSIS REPORTS FOR QUESTIONNAIRE GENERATION")
        sections.append(f"\nCompany: {self.company_name or 'Unknown'}")
        sections.append(f"Total Reports: {len(self.valid_reports)}")
        sections.append(f"Report Types: {', '.join(self.valid_reports.keys())}")
        sections.append(f"Generated: {self.loaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("\n" + "=" * 80)
        
        # Individual reports
        for report_type, report in self.valid_reports.items():
            display_name = report_type.replace('_', ' ').title()
            
            sections.append(f"\n## {display_name}")
            sections.append(f"Report Type: {report.report_type}")
            sections.append(f"Content Length: {report.character_count:,} characters")
            sections.append(f"Word Count: {report.word_count:,} words")
            sections.append("-" * 60)
            sections.append(report.content)
            sections.append("\n" + "=" * 80)
        
        return "\n".join(sections)
    
    def get_concatenated_reports(self) -> str:
        """
        Get concatenated reports formatted for questionnaire prompt
        
        Returns:
            Concatenated string with H1 headers and equals separators
        """
        sections = []
        
        # Process reports in the order they were loaded
        for report_type, report in self.valid_reports.items():
            # Convert report type to H1 header format
            display_name = report_type.replace('_', ' ').upper()
            
            sections.append(f"# {display_name} REPORT")
            sections.append(report.content)
            sections.append("=" * 80)
        
        return "\n".join(sections)


@dataclass
class QuestionnaireResult:
    """Result structure for questionnaire generation"""
    
    success: bool
    questionnaire_content: Optional[str] = None
    markdown_file: Optional[str] = None
    docx_file: Optional[str] = None
    processing_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def output_files(self) -> List[str]:
        """Get list of generated output files"""
        files = []
        if self.markdown_file:
            files.append(self.markdown_file)
        if self.docx_file:
            files.append(self.docx_file)
        return files
    
    @property
    def has_outputs(self) -> bool:
        """Check if any output files were generated"""
        return bool(self.output_files)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization"""
        return {
            "success": self.success,
            "questionnaire_content": self.questionnaire_content,
            "markdown_file": self.markdown_file,
            "docx_file": self.docx_file,
            "processing_time": self.processing_time,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "generated_at": self.generated_at.isoformat(),
            "output_files": self.output_files,
            "has_outputs": self.has_outputs
        }


@dataclass
class QuestionnaireStats:
    """Statistics about questionnaire generation"""
    
    total_attempts: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    average_processing_time: float = 0.0
    total_questionnaires_generated: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_attempts == 0:
            return 0.0
        return (self.successful_generations / self.total_attempts) * 100
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage"""
        return 100.0 - self.success_rate
    
    def record_attempt(self, result: QuestionnaireResult):
        """Record a questionnaire generation attempt"""
        self.total_attempts += 1
        
        if result.success:
            self.successful_generations += 1
            self.total_questionnaires_generated += 1
            
            # Update average processing time
            if self.successful_generations == 1:
                self.average_processing_time = result.processing_time
            else:
                self.average_processing_time = (
                    (self.average_processing_time * (self.successful_generations - 1) + 
                     result.processing_time) / self.successful_generations
                )
        else:
            self.failed_generations += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary"""
        return {
            "total_attempts": self.total_attempts,
            "successful_generations": self.successful_generations,
            "failed_generations": self.failed_generations,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "average_processing_time": self.average_processing_time,
            "total_questionnaires_generated": self.total_questionnaires_generated
        }


# Validation functions
def validate_questionnaire_content(content: str) -> bool:
    """
    Validate that questionnaire content appears to be properly generated.
    
    Args:
        content: The questionnaire content to validate
        
    Returns:
        True if content appears valid, False otherwise
    """
    if not content or not content.strip():
        return False
    
    # Check minimum length
    if len(content.strip()) < 200:
        return False
    
    # Check for question indicators
    question_indicators = ['?', 'What', 'How', 'Why', 'When', 'Where', 'Who', 'Which']
    has_questions = any(indicator in content for indicator in question_indicators)
    
    # Check for structure indicators
    structure_indicators = ['#', '##', '###', '-', '*', '1.', '2.']
    has_structure = any(indicator in content for indicator in structure_indicators)
    
    return has_questions and has_structure


def create_questionnaire_config(**kwargs) -> QuestionnaireConfig:
    """
    Factory function to create QuestionnaireConfig with validation.
    
    Args:
        **kwargs: Configuration parameters
        
    Returns:
        Validated QuestionnaireConfig instance
    """
    return QuestionnaireConfig(**kwargs)


# Constants
DEFAULT_PROMPT_VERSION = "v4"
DEFAULT_PROMPT_KEY = "questionaire_agent_v4"
DEFAULT_MAX_RETRIES = 3
MINIMUM_CONTENT_LENGTH = 200
MINIMUM_REPORT_LENGTH = 50