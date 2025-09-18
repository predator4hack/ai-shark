from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pathlib import Path

class BaseProcessor(ABC):
    """Abstract base class for document processors"""
    
    @abstractmethod
    def process(self, file_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Process document and return metadata
        
        Args:
            file_path: Path to the file to process
            output_dir: Directory to save processed outputs
            
        Returns:
            Dictionary containing processing results and metadata
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Return list of supported file extensions
        
        Returns:
            List of supported file extensions (e.g., ['.pdf', '.ppt'])
        """
        pass
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if file type is supported by this processor
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file type is supported, False otherwise
        """
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.get_supported_extensions()