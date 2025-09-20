"""
Reference Document Processor

Handles processing of reference documents for founder simulation
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from .additional_doc_processor import AdditionalDocProcessor
from ..models.founder_simulation_models import SimulationResult, ProcessingStatus
from ..utils.founder_simulation_utils import (
    validate_company_directory_structure,
    create_ref_data_directory,
    sanitize_filename
)
from ..utils.output_manager import OutputManager


class RefDocProcessor:
    """
    Processor for handling reference documents upload and storage
    """
    
    def __init__(self):
        """Initialize the reference document processor"""
        self.processor_name = "RefDocProcessor"
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
        
        if not validation['analysis_complete']:
            result['warnings'].append("Analysis directory not found. Some functionality may be limited.")
        
        result['valid'] = True
        return result
    
    def process_reference_documents(self, uploaded_files: List[Any], company_dir: str) -> SimulationResult:
        """
        Process multiple reference documents and store in ref-data directory
        
        Args:
            uploaded_files: List of uploaded file objects from Streamlit
            company_dir: Path to company directory
            
        Returns:
            SimulationResult with processing status
        """
        start_time = time.time()
        
        print(f"\n🔄 Processing {len(uploaded_files)} reference documents")
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
        
        # Create ref-data directory
        try:
            ref_data_dir = create_ref_data_directory(company_dir)
            print(f"📁 Using ref-data directory: {ref_data_dir}")
        except Exception as e:
            return SimulationResult(
                success=False,
                error_message=f"Failed to create ref-data directory: {e}",
                processing_time=time.time() - start_time
            )
        
        # Process each document
        results = []
        successful_files = []
        failed_files = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            print(f"\n📄 Processing {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
            
            try:
                result = self.extract_and_save_to_ref_data(uploaded_file, ref_data_dir)
                results.append(result)
                
                if result['status'] == 'success':
                    successful_files.append(result['output_file'])
                    print(f"✅ Successfully processed: {uploaded_file.name}")
                else:
                    failed_files.append({
                        'filename': uploaded_file.name,
                        'error': result.get('error', 'Unknown error')
                    })
                    print(f"❌ Failed to process: {uploaded_file.name} - {result.get('error')}")
                    
            except Exception as e:
                error_msg = f"Unexpected error processing {uploaded_file.name}: {e}"
                print(f"❌ {error_msg}")
                failed_files.append({
                    'filename': uploaded_file.name,
                    'error': str(e)
                })
        
        # Prepare final result
        processing_time = time.time() - start_time
        success = len(successful_files) > 0
        
        metadata = {
            'ref_data_dir': ref_data_dir,
            'total_files': len(uploaded_files),
            'successful_files': len(successful_files),
            'failed_files': len(failed_files),
            'successful_file_paths': successful_files,
            'failed_file_details': failed_files,
            'processing_type': 'reference_documents'
        }
        
        if success:
            print(f"\n🎉 Reference document processing completed!")
            print(f"✅ Successful: {len(successful_files)}")
            print(f"❌ Failed: {len(failed_files)}")
            print(f"📁 Documents saved to: {ref_data_dir}")
        else:
            print(f"\n❌ All reference documents failed to process")
        
        return SimulationResult(
            success=success,
            output_file=ref_data_dir if success else None,
            processing_time=processing_time,
            error_message=f"Failed to process {len(failed_files)} files" if failed_files and not success else None,
            metadata=metadata
        )
    
    def extract_and_save_to_ref_data(self, uploaded_file: Any, ref_data_dir: str) -> Dict[str, Any]:
        """
        Extract content from uploaded file and save to ref-data directory
        
        Args:
            uploaded_file: Uploaded file object from Streamlit
            ref_data_dir: Path to ref-data directory
            
        Returns:
            Processing result dictionary
        """
        try:
            # Save uploaded file temporarily
            temp_file = self._save_temp_file(uploaded_file)
            
            try:
                # Extract text content using existing processor
                text_content = self.additional_doc_processor._extract_text(temp_file)
                
                if not text_content or not text_content.strip():
                    return {
                        'status': 'error',
                        'filename': uploaded_file.name,
                        'error': 'Could not extract text content from the document'
                    }
                
                # Generate output filename
                sanitized_name = sanitize_filename(uploaded_file.name)
                
                # Check if document is founder checklist related and rename accordingly
                sanitized_name_lower = sanitized_name.lower()
                if any(keyword in sanitized_name_lower for keyword in ['founder', 'checklist', "founders_checklist"]):
                    sanitized_name = 'ref-founders-checklist'
                
                output_filename = f"{sanitized_name}.md"
                output_path = Path(ref_data_dir) / output_filename
                
                # Convert to markdown format
                markdown_content = self._convert_to_reference_markdown(
                    text_content, 
                    uploaded_file.name,
                    sanitized_name
                )
                
                # Save to ref-data directory
                success = OutputManager.save_file(markdown_content, str(output_path))
                
                if success:
                    return {
                        'status': 'success',
                        'filename': uploaded_file.name,
                        'output_file': str(output_path),
                        'content_length': len(text_content),
                        'word_count': len(text_content.split())
                    }
                else:
                    return {
                        'status': 'error',
                        'filename': uploaded_file.name,
                        'error': 'Failed to save processed content'
                    }
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            return {
                'status': 'error',
                'filename': uploaded_file.name,
                'error': str(e)
            }
    
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
    
    def _convert_to_reference_markdown(self, content: str, original_filename: str, sanitized_name: str) -> str:
        """
        Convert extracted content to markdown format for reference documents
        
        Args:
            content: Extracted text content
            original_filename: Original filename
            sanitized_name: Sanitized filename
            
        Returns:
            Formatted markdown content
        """
        lines = []
        
        # Header
        doc_title = sanitized_name.replace('_', ' ').title()
        lines.append(f"# {doc_title}")
        lines.append("")
        
        # Metadata
        lines.append("## Document Information")
        lines.append("")
        lines.append(f"**Original Filename:** {original_filename}")
        lines.append(f"**Document Type:** Reference Document")
        lines.append(f"**Processing Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Word Count:** {len(content.split())}")
        lines.append("")
        
        # Content
        lines.append("## Content")
        lines.append("")
        
        # Clean and format content
        content_lines = content.split('\n')
        for line in content_lines:
            line = line.strip()
            if line:
                lines.append(line)
            else:
                lines.append("")
        
        return "\n".join(lines)
    
    def get_ref_data_files(self, company_dir: str) -> List[Dict[str, Any]]:
        """
        Get list of reference data files in company directory
        
        Args:
            company_dir: Path to company directory
            
        Returns:
            List of file information dictionaries
        """
        ref_data_dir = Path(company_dir) / "ref-data"
        files = []
        
        if not ref_data_dir.exists():
            return files
        
        for md_file in ref_data_dir.glob("*.md"):
            try:
                stat = md_file.stat()
                files.append({
                    'filename': md_file.name,
                    'filepath': str(md_file),
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
            except Exception as e:
                print(f"Error getting file info for {md_file}: {e}")
        
        return sorted(files, key=lambda x: x['modified'], reverse=True)