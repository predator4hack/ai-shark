"""
Base extractor class for public data extraction.

This module defines the abstract base class that all public data extractors must inherit from.
It provides a plugin-style architecture for extensible data extraction.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """
    Abstract base class for all public data extractors using plugin-style architecture
    
    This class defines the interface that all extractors must implement to be compatible
    with the PublicDataOrchestrator.
    """
    
    @abstractmethod
    def extract(self, company_name: str, website: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract public data for the company
        
        Args:
            company_name: Name of the company
            website: Company website URL
            metadata: Company metadata from pitch deck processing
            
        Returns:
            Dictionary containing extraction results with the following structure:
            {
                'status': 'success' | 'error' | 'skipped',
                'content': str,  # Markdown content to append to public_data.md
                'error': str,    # Error message if status is 'error'
                'reason': str,   # Reason if status is 'skipped'
                **kwargs         # Additional extractor-specific data
            }
        """
        pass
    
    @abstractmethod
    def get_extractor_name(self) -> str:
        """
        Return the unique name of this extractor
        
        Returns:
            String identifier for this extractor (e.g., 'products_services')
        """
        pass
    
    @abstractmethod
    def get_section_title(self) -> str:
        """
        Return the markdown section title for this extractor
        
        Returns:
            String title to use in the markdown output (e.g., 'Products and Services Analysis')
        """
        pass
    
    def should_extract(self, metadata: Dict[str, Any]) -> bool:
        """
        Determine if this extractor should run for the given company
        
        Args:
            metadata: Company metadata from pitch deck processing
            
        Returns:
            True if this extractor should run, False otherwise
        """
        return True
    
    def is_enabled(self) -> bool:
        """
        Check if this extractor is enabled in configuration
        
        Returns:
            True if enabled, False otherwise
        """
        # Import here to avoid circular imports
        try:
            from config.settings import settings
            enabled_extractors = getattr(settings, 'PUBLIC_DATA_EXTRACTORS', ['products_services'])
            return self.get_extractor_name() in enabled_extractors
        except ImportError:
            logger.warning("Could not import settings, defaulting to enabled")
            return True
    
    def validate_extraction_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the extraction result
        
        Args:
            result: Raw extraction result from the extract method
            
        Returns:
            Validated and normalized result dictionary
        """
        if not isinstance(result, dict):
            return {
                'status': 'error',
                'error': f"Invalid result type: {type(result)}",
                'content': '*Extraction failed due to invalid result format*'
            }
        
        # Ensure required fields exist
        if 'status' not in result:
            result['status'] = 'error'
            result['error'] = 'Missing status field in extraction result'
        
        if 'content' not in result:
            result['content'] = '*No content extracted*'
        
        # Validate status values
        valid_statuses = ['success', 'error', 'skipped']
        if result['status'] not in valid_statuses:
            logger.warning(f"Invalid status '{result['status']}', setting to 'error'")
            result['status'] = 'error'
            result['error'] = f"Invalid status value: {result['status']}"
        
        return result
    
    def log_extraction_start(self, company_name: str) -> None:
        """Log the start of extraction for this extractor"""
        logger.info(f"Starting {self.get_extractor_name()} extraction for {company_name}")
    
    def log_extraction_end(self, company_name: str, status: str) -> None:
        """Log the end of extraction for this extractor"""
        if status == 'success':
            logger.info(f"Successfully completed {self.get_extractor_name()} extraction for {company_name}")
        elif status == 'skipped':
            logger.info(f"Skipped {self.get_extractor_name()} extraction for {company_name}")
        else:
            logger.warning(f"Failed {self.get_extractor_name()} extraction for {company_name}")