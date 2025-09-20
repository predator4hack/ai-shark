"""
Q&A Document Processor

Handles processing of direct Q&A documents for founder simulation
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from .additional_doc_processor import AdditionalDocProcessor
from ..models.founder_simulation_models import SimulationResult, QAEntry
from ..utils.founder_simulation_utils import (
    validate_company_directory_structure,
    parse_qa_document_content,
    load_founders_checklist,
    format_simulation_output
)
from ..utils.output_manager import OutputManager


class QADocProcessor:
    """
    Processor for handling direct Q&A document uploads
    """
    
    def __init__(self):
        """Initialize the Q&A document processor"""
        self.processor_name = "QADocProcessor"
        self.additional_doc_processor = AdditionalDocProcessor()
        self.supported_extensions = ['.pdf', '.doc', '.docx', '.txt']
    
    def validate_company_directory(self, company_dir: str) -> Dict[str, Any]:
        """
        Validate that the company directory meets prerequisites
        
        Args:
            company_dir: Path to company directory
            
        Returns:
            Validation result dictionary
        """
        validation = validate_company_directory_structure(company_dir)
        
        result = {
            'valid': False,
            'errors': [],
            'warnings': []
        }
        
        if not validation['company_dir_exists']:
            result['errors'].append(f"Company directory does not exist: {company_dir}")
            return result
        
        if not validation['founders_checklist_exists']:
            result['errors'].append("founders-checklist.md not found. Please complete analysis pipeline first.")
            return result
        
        result['valid'] = True
        return result
    
    def process_qa_document(self, uploaded_file: Any, company_dir: str) -> SimulationResult:
        """
        Process Q&A document and create ans-founders-checklist.md
        
        Args:
            uploaded_file: Uploaded file object from Streamlit
            company_dir: Path to company directory
            
        Returns:
            SimulationResult with processing status
        """
        start_time = time.time()
        
        print(f"\n📝 Processing Q&A document: {uploaded_file.name}")
        print(f"Company Directory: {company_dir}")
        
        # Validate prerequisites
        validation = self.validate_company_directory(company_dir)
        if not validation['valid']:
            return SimulationResult(
                success=False,
                error_message=f"Validation failed: {'; '.join(validation['errors'])}",
                processing_time=time.time() - start_time,
                metadata={'validation_errors': validation['errors']}
            )
        
        try:
            # Extract text content from uploaded document
            temp_file = self._save_temp_file(uploaded_file)
            
            try:
                text_content = self.additional_doc_processor._extract_text(temp_file)
                
                if not text_content or not text_content.strip():
                    return SimulationResult(
                        success=False,
                        error_message="Could not extract text content from the Q&A document",
                        processing_time=time.time() - start_time
                    )
                
                # Parse Q&A pairs from document
                qa_pairs = self.extract_qa_pairs(text_content)
                
                if not qa_pairs:
                    return SimulationResult(
                        success=False,
                        error_message="Could not extract Q&A pairs from the document. Please check the format.",
                        processing_time=time.time() - start_time,
                        metadata={'extracted_content_length': len(text_content)}
                    )
                
                print(f"📋 Extracted {len(qa_pairs)} Q&A pairs")
                
                # Load founders checklist for mapping
                checklist_path = Path(company_dir) / "founders-checklist.md"
                checklist_questions = load_founders_checklist(str(checklist_path))
                
                # Map Q&A to founders checklist format
                mapped_responses = self.map_to_founders_checklist(qa_pairs, checklist_questions)
                
                # Save results
                output_path = Path(company_dir) / "ans-founders-checklist.md"
                success = self.save_qa_responses(mapped_responses, str(output_path), uploaded_file.name)
                
                processing_time = time.time() - start_time
                
                if success:
                    print(f"✅ Q&A document processed successfully!")
                    print(f"📄 Output saved to: {output_path}")
                    
                    return SimulationResult(
                        success=True,
                        output_file=str(output_path),
                        processing_time=processing_time,
                        metadata={
                            'processing_type': 'direct_qa',
                            'source_document': uploaded_file.name,
                            'qa_pairs_extracted': len(qa_pairs),
                            'responses_generated': len(mapped_responses),
                            'checklist_questions': len(checklist_questions)
                        }
                    )
                else:
                    return SimulationResult(
                        success=False,
                        error_message="Failed to save Q&A responses",
                        processing_time=processing_time
                    )
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            return SimulationResult(
                success=False,
                error_message=f"Error processing Q&A document: {e}",
                processing_time=time.time() - start_time
            )
    
    def extract_qa_pairs(self, text_content: str) -> List[Tuple[str, str]]:
        """
        Extract Q&A pairs from document text content
        
        Args:
            text_content: Raw text content from document
            
        Returns:
            List of (question, answer) tuples
        """
        print("🔍 Extracting Q&A pairs from document...")
        
        qa_pairs = parse_qa_document_content(text_content)
        
        if qa_pairs:
            print(f"✅ Found {len(qa_pairs)} Q&A pairs using pattern matching")
        else:
            print("⚠️ No Q&A pairs found using standard patterns")
            # Try alternative extraction methods
            qa_pairs = self._extract_qa_alternative_methods(text_content)
        
        return qa_pairs
    
    def _extract_qa_alternative_methods(self, content: str) -> List[Tuple[str, str]]:
        """
        Alternative methods for extracting Q&A pairs when standard patterns fail
        
        Args:
            content: Document content
            
        Returns:
            List of (question, answer) tuples
        """
        qa_pairs = []
        
        # Method 1: Look for paragraph-based Q&A
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        current_question = None
        for para in paragraphs:
            if '?' in para and len(para) < 200:  # Likely a question
                if current_question:
                    # Previous question without answer, skip it
                    pass
                current_question = para
            elif current_question and len(para) > 50:  # Likely an answer
                qa_pairs.append((current_question, para))
                current_question = None
        
        if qa_pairs:
            print(f"✅ Found {len(qa_pairs)} Q&A pairs using paragraph method")
            return qa_pairs
        
        # Method 2: Manual prompting approach (could be enhanced with LLM)
        print("📝 Could not automatically extract Q&A pairs. Document may need manual review.")
        
        return qa_pairs
    
    def map_to_founders_checklist(self, qa_pairs: List[Tuple[str, str]], 
                                 checklist_questions: List[str]) -> List[QAEntry]:
        """
        Map extracted Q&A pairs to founders checklist format
        
        Args:
            qa_pairs: List of (question, answer) tuples from document
            checklist_questions: List of questions from founders checklist
            
        Returns:
            List of QAEntry objects
        """
        print("🔗 Mapping Q&A pairs to founders checklist format...")
        
        mapped_responses = []
        
        # Simple mapping strategy: use extracted Q&A as-is, then fill any missing from checklist
        for question, answer in qa_pairs:
            qa_entry = QAEntry(
                question=question,
                answer=answer,
                confidence=1.0,  # High confidence for direct Q&A
                source_documents=["Direct Q&A Document"]
            )
            mapped_responses.append(qa_entry)
        
        # Add any checklist questions that weren't covered
        covered_topics = set()
        for qa in mapped_responses:
            # Simple keyword matching to avoid duplicates
            covered_topics.update(qa.question.lower().split())
        
        for checklist_q in checklist_questions:
            # Check if this question is already covered
            checklist_keywords = set(checklist_q.lower().split())
            overlap = len(covered_topics.intersection(checklist_keywords))
            
            if overlap < 2:  # Low overlap, likely not covered
                qa_entry = QAEntry(
                    question=checklist_q,
                    answer="*No response provided in uploaded Q&A document*",
                    confidence=0.0,
                    source_documents=[]
                )
                mapped_responses.append(qa_entry)
        
        print(f"📊 Generated {len(mapped_responses)} total responses")
        return mapped_responses
    
    def save_qa_responses(self, qa_entries: List[QAEntry], output_path: str, source_filename: str) -> bool:
        """
        Save Q&A responses to ans-founders-checklist.md
        
        Args:
            qa_entries: List of QA entries
            output_path: Path to output file
            source_filename: Name of source document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = {
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'simulation_type': 'Direct Q&A Upload',
                'source_documents': [source_filename],
                'source_doc_count': 1
            }
            
            markdown_content = format_simulation_output(qa_entries, metadata)
            
            return OutputManager.save_file(markdown_content, output_path)
            
        except Exception as e:
            print(f"Error saving Q&A responses: {e}")
            return False
    
    def _save_temp_file(self, uploaded_file: Any) -> str:
        """
        Save uploaded file to temporary location
        
        Args:
            uploaded_file: Uploaded file object from Streamlit
            
        Returns:
            Path to temporary file
        """
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name