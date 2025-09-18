import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class OutputManager:
    """Manages output directory structure and file saving"""
    
    @staticmethod
    def create_company_dir(company_name: str, base_dir: str = "outputs") -> str:
        """
        Create /outputs/<company-name>/ directory
        
        Args:
            company_name: Name of the company
            base_dir: Base directory for outputs
            
        Returns:
            Path to created company directory
        """
        sanitized_name = OutputManager.sanitize_company_name(company_name)
        company_dir = os.path.join(base_dir, sanitized_name)
        os.makedirs(company_dir, exist_ok=True)
        
        # Create subdirectory for additional documents
        additional_docs_dir = os.path.join(company_dir, "additional_docs")
        os.makedirs(additional_docs_dir, exist_ok=True)
        
        return company_dir
    
    @staticmethod
    def sanitize_company_name(name: str) -> str:
        """
        Sanitize company name for directory creation
        
        Args:
            name: Raw company name
            
        Returns:
            Sanitized company name suitable for directory name
        """
        if not name or not name.strip():
            return OutputManager.generate_fallback_name()
        
        # Remove special characters and replace spaces with underscores
        sanitized = re.sub(r'[^\w\s-]', '', name.strip())
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        
        # Remove leading/trailing underscores and convert to lowercase
        sanitized = sanitized.strip('_').lower()
        
        # If sanitization results in empty string, use fallback
        if not sanitized:
            return OutputManager.generate_fallback_name()
        
        return sanitized
    
    @staticmethod
    def generate_fallback_name() -> str:
        """
        Generate fallback name when company extraction fails
        
        Returns:
            Fallback directory name with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"unknown_company_{timestamp}"
    
    @staticmethod
    def save_file(content: str, filepath: str, mode: str = 'w') -> bool:
        """
        Save content to file with error handling
        
        Args:
            content: Content to save
            filepath: Path where to save the file
            mode: File mode (default: 'w')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, mode, encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving file {filepath}: {e}")
            return False
    
    @staticmethod
    def save_json(data: Dict[Any, Any], filepath: str) -> bool:
        """
        Save dictionary as JSON file
        
        Args:
            data: Dictionary to save
            filepath: Path where to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            return OutputManager.save_file(json_content, filepath)
        except Exception as e:
            print(f"Error saving JSON file {filepath}: {e}")
            return False
    
    @staticmethod
    def get_output_paths(company_dir: str, doc_type: str, filename: str = None) -> Dict[str, str]:
        """
        Get standard output file paths for different document types
        
        Args:
            company_dir: Company directory path
            doc_type: Type of document ('pitch_deck' or 'additional')
            filename: Original filename (for additional docs)
            
        Returns:
            Dictionary with paths for different output files
        """
        if doc_type == 'pitch_deck':
            return {
                'metadata': os.path.join(company_dir, 'metadata.json'),
                'markdown': os.path.join(company_dir, 'pitch_deck.md'),
                'toc': os.path.join(company_dir, 'table_of_contents.json')
            }
        elif doc_type == 'additional':
            if filename:
                base_name = Path(filename).stem
                return {
                    'markdown': os.path.join(company_dir, 'additional_docs', f'{base_name}.md')
                }
        
        return {}