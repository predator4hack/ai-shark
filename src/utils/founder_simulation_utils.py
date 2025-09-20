"""
Founder Simulation Utilities

Helper functions for the founder simulation agent
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from ..models.founder_simulation_models import ReferenceDocument, QAEntry


def validate_founders_checklist_exists(company_dir: str) -> bool:
    """
    Check if founders-checklist.md exists in the company directory
    
    Args:
        company_dir: Path to company directory
        
    Returns:
        True if founders-checklist.md exists, False otherwise
    """
    company_path = Path(company_dir)
    checklist_file = company_path / "founders-checklist.md"
    return checklist_file.exists()


def create_ref_data_directory(company_dir: str) -> str:
    """
    Create ref-data directory in company directory if it doesn't exist
    
    Args:
        company_dir: Path to company directory
        
    Returns:
        Path to ref-data directory
    """
    company_path = Path(company_dir)
    ref_data_dir = company_path / "ref-data"
    ref_data_dir.mkdir(exist_ok=True)
    return str(ref_data_dir)


def load_all_markdown_files(directory: str) -> List[ReferenceDocument]:
    """
    Load all markdown files from a directory
    
    Args:
        directory: Path to directory containing markdown files
        
    Returns:
        List of ReferenceDocument objects
    """
    dir_path = Path(directory)
    reference_docs = []
    
    if not dir_path.exists():
        return reference_docs
    
    for md_file in dir_path.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ref_doc = ReferenceDocument(
                filename=md_file.name,
                filepath=str(md_file),
                content=content
            )
            reference_docs.append(ref_doc)
            
        except Exception as e:
            print(f"Error loading {md_file}: {e}")
    
    return reference_docs


def load_founders_checklist(checklist_path: str) -> List[str]:
    """
    Load and parse founders checklist questions
    
    Args:
        checklist_path: Path to founders-checklist.md file
        
    Returns:
        List of questions extracted from the checklist
    """
    try:
        with open(checklist_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract questions using regex patterns
        # Look for numbered questions, bullet points, or markdown headers
        question_patterns = [
            r'^\d+\.\s+(.+?)(?=\n\d+\.|\n#|\n\n|$)',  # Numbered questions
            r'^\*\s+(.+?)(?=\n\*|\n#|\n\n|$)',        # Bullet point questions
            r'^-\s+(.+?)(?=\n-|\n#|\n\n|$)',          # Dash bullet questions
            r'^#{1,6}\s+(.+?)(?=\n#|\n\n|$)',         # Header questions
        ]
        
        questions = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check each pattern
            for pattern in question_patterns:
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    question = match.group(1).strip()
                    if question and len(question) > 10:  # Filter out very short matches
                        questions.append(question)
                    break
        
        # If no patterns match, try to extract meaningful lines as questions
        if not questions:
            for line in lines:
                line = line.strip()
                if line and len(line) > 20 and '?' in line:
                    questions.append(line)
        
        return questions
        
    except Exception as e:
        print(f"Error loading founders checklist: {e}")
        return []


def format_simulation_output(qa_entries: List[QAEntry], metadata: Dict[str, Any]) -> str:
    """
    Format simulation results into markdown output
    
    Args:
        qa_entries: List of QA entries
        metadata: Processing metadata
        
    Returns:
        Formatted markdown content
    """
    lines = []
    
    # Header
    lines.append("# Founder Investment Questionnaire Responses")
    lines.append("")
    lines.append("*AI-Generated responses based on reference documents*")
    lines.append("")
    
    # Metadata section
    lines.append("## Document Information")
    lines.append("")
    lines.append(f"**Generated:** {metadata.get('generated_at', 'Unknown')}")
    lines.append(f"**Processing Type:** {metadata.get('simulation_type', 'Unknown')}")
    lines.append(f"**Source Documents:** {metadata.get('source_doc_count', 0)}")
    lines.append(f"**Total Questions:** {len(qa_entries)}")
    lines.append("")
    
    if metadata.get('source_documents'):
        lines.append("**Reference Documents Used:**")
        for doc in metadata['source_documents']:
            lines.append(f"- {doc}")
        lines.append("")
    
    # Questions and Answers
    lines.append("## Questionnaire Responses")
    lines.append("")
    
    for i, qa in enumerate(qa_entries, 1):
        lines.append(f"### {i}. {qa.question}")
        lines.append("")
        lines.append(qa.answer)
        lines.append("")
        
        # Add confidence indicator if available
        if qa.confidence < 1.0:
            confidence_pct = int(qa.confidence * 100)
            lines.append(f"*Confidence: {confidence_pct}%*")
            lines.append("")
        
        # Add source documents if available
        if qa.source_documents:
            lines.append(f"*Based on: {', '.join(qa.source_documents)}*")
            lines.append("")
    
    return "\n".join(lines)


def calculate_simulation_confidence(responses: List[QAEntry]) -> float:
    """
    Calculate overall confidence score for simulation results
    
    Args:
        responses: List of QA entries
        
    Returns:
        Average confidence score (0.0 to 1.0)
    """
    if not responses:
        return 0.0
    
    total_confidence = sum(qa.confidence for qa in responses)
    return total_confidence / len(responses)


def parse_qa_document_content(content: str) -> List[Tuple[str, str]]:
    """
    Parse Q&A pairs from document content
    
    Args:
        content: Raw text content from Q&A document
        
    Returns:
        List of (question, answer) tuples
    """
    qa_pairs = []
    
    # Common Q&A patterns
    patterns = [
        r'(?:Q\d*[:.]\s*)(.*?)\s*(?:A\d*[:.]\s*)(.*?)(?=Q\d*[:]|\n\n|$)',
        r'(?:Question\d*[:.]\s*)(.*?)\s*(?:Answer\d*[:.]\s*)(.*?)(?=Question\d*[:]|\n\n|$)',
        r'(?:^\d+\.\s*)(.*?)\s*\n\s*(.*?)(?=^\d+\.|\n\n|$)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if matches:
            for question, answer in matches:
                question = question.strip()
                answer = answer.strip()
                if question and answer and len(question) > 10 and len(answer) > 10:
                    qa_pairs.append((question, answer))
            break
    
    # If no patterns match, try alternative approaches
    if not qa_pairs:
        # Look for alternating question/answer blocks
        lines = content.split('\n')
        current_question = None
        current_answer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_question and current_answer:
                    answer_text = ' '.join(current_answer).strip()
                    if len(answer_text) > 10:
                        qa_pairs.append((current_question, answer_text))
                    current_question = None
                    current_answer = []
                continue
            
            # Check if this looks like a question
            if '?' in line or line.lower().startswith(('what', 'how', 'why', 'when', 'where', 'who')):
                if current_question and current_answer:
                    answer_text = ' '.join(current_answer).strip()
                    if len(answer_text) > 10:
                        qa_pairs.append((current_question, answer_text))
                current_question = line
                current_answer = []
            else:
                if current_question:
                    current_answer.append(line)
        
        # Handle last pair
        if current_question and current_answer:
            answer_text = ' '.join(current_answer).strip()
            if len(answer_text) > 10:
                qa_pairs.append((current_question, answer_text))
    
    return qa_pairs


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove file extension and sanitize
    name = Path(filename).stem
    # Replace spaces and special characters with underscores
    name = re.sub(r'[^\w\-_.]', '_', name)
    # Remove multiple consecutive underscores
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    
    return name if name else "document"


def validate_company_directory_structure(company_dir: str) -> Dict[str, bool]:
    """
    Validate the company directory structure and prerequisites
    
    Args:
        company_dir: Path to company directory
        
    Returns:
        Dictionary with validation results
    """
    company_path = Path(company_dir)
    
    validation = {
        'company_dir_exists': company_path.exists(),
        'founders_checklist_exists': False,
        'analysis_complete': False,
        'ref_data_dir_exists': False,
    }
    
    if validation['company_dir_exists']:
        validation['founders_checklist_exists'] = (company_path / "founders-checklist.md").exists()
        validation['analysis_complete'] = (company_path / "analysis").exists()
        validation['ref_data_dir_exists'] = (company_path / "ref-data").exists()
    
    return validation