"""
Public Data Orchestrator

This module coordinates all public data extraction services using a plugin architecture.
It discovers available extractors and runs them in sequence to aggregate public data.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from .base_extractor import BaseExtractor

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PublicDataOrchestrator:
    """
    Coordinates all public data extraction services using plugin architecture
    
    This class discovers available extractors, runs them in sequence, and aggregates
    their results into a single public_data.md file.
    """
    
    def __init__(self):
        """Initialize the orchestrator and discover available extractors"""
        self.extractors = self._discover_extractors()
        logger.info(f"Discovered {len(self.extractors)} public data extractors")
    
    def _discover_extractors(self) -> List[BaseExtractor]:
        """
        Automatically discover and instantiate available extractors
        
        Returns:
            List of instantiated extractor objects
        """
        extractors = []
        
        try:
            # Import and instantiate all available extractors
            from .extractors import AVAILABLE_EXTRACTORS
            
            for extractor_class in AVAILABLE_EXTRACTORS:
                try:
                    extractor = extractor_class()
                    extractors.append(extractor)
                    logger.debug(f"Loaded extractor: {extractor.get_extractor_name()}")
                except Exception as e:
                    logger.error(f"Failed to instantiate extractor {extractor_class.__name__}: {e}")
                    
        except ImportError as e:
            logger.error(f"Failed to import extractors: {e}")
        
        return extractors
    
    def extract_all(self, company_name: str, company_dir: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all enabled extractors and aggregate results
        
        Args:
            company_name: Name of the company
            company_dir: Path to the company's output directory
            metadata: Company metadata from pitch deck processing
            
        Returns:
            Dictionary containing aggregated extraction results
        """
        logger.info(f"Starting public data extraction for {company_name}")
        
        results = {}
        public_data_content = self._create_header(company_name)
        extractors_run = 0
        
        # Ensure company directory exists
        Path(company_dir).mkdir(parents=True, exist_ok=True)
        
        for extractor in self.extractors:
            extractor_name = extractor.get_extractor_name()
            
            # Check if extractor should run
            if not extractor.is_enabled():
                logger.info(f"Skipping disabled extractor: {extractor_name}")
                results[extractor_name] = {
                    'status': 'skipped',
                    'reason': 'Extractor disabled in configuration'
                }
                continue
            
            if not extractor.should_extract(metadata):
                logger.info(f"Skipping extractor {extractor_name} - conditions not met")
                results[extractor_name] = {
                    'status': 'skipped',
                    'reason': 'Extractor conditions not met'
                }
                continue
            
            # Run the extractor
            try:
                extractor.log_extraction_start(company_name)
                
                website = self._normalize_website_url(metadata.get('website', ''))
                extraction_result = extractor.extract(company_name, website, metadata)
                
                # Validate and normalize the result
                extraction_result = extractor.validate_extraction_result(extraction_result)
                
                extractor.log_extraction_end(company_name, extraction_result['status'])
                
                if extraction_result['status'] == 'success':
                    # Append to public data markdown
                    section_title = extractor.get_section_title()
                    section_content = extraction_result.get('content', '')
                    
                    public_data_content += f"## {section_title}\n\n{section_content}\n\n"
                    extractors_run += 1
                    
                    logger.info(f"Successfully extracted data using {extractor_name}")
                else:
                    logger.warning(f"Extraction failed for {extractor_name}: {extraction_result.get('error', 'Unknown error')}")
                
                results[extractor_name] = extraction_result
                
            except Exception as e:
                logger.error(f"Error running extractor {extractor_name}: {e}")
                results[extractor_name] = {
                    'status': 'error',
                    'error': str(e),
                    'content': f'*Error running {extractor_name}: {str(e)}*'
                }
                extractor.log_extraction_end(company_name, 'error')
        
        # Save aggregated public data
        public_data_path = os.path.join(company_dir, 'public_data.md')
        
        try:
            with open(public_data_path, 'w', encoding='utf-8') as f:
                f.write(public_data_content)
            
            logger.info(f"Saved public data to: {public_data_path}")
            
        except Exception as e:
            logger.error(f"Failed to save public data file: {e}")
            return {
                'status': 'error',
                'error': f'Failed to save public data file: {str(e)}',
                'extractors_run': extractors_run,
                'total_extractors': len(self.extractors),
                'results': results
            }
        
        # Return aggregated results
        result = {
            'status': 'success',
            'extractors_run': extractors_run,
            'total_extractors': len(self.extractors),
            'results': results,
            'output_file': public_data_path
        }
        
        logger.info(f"Public data extraction completed for {company_name}. "
                   f"Successfully ran {extractors_run}/{len(self.extractors)} extractors")
        
        return result
    
    def _create_header(self, company_name: str) -> str:
        """
        Create the header for the public data markdown file
        
        Args:
            company_name: Name of the company
            
        Returns:
            Markdown header string
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"# Public Data Analysis for {company_name}\n\n*Last updated: {timestamp}*\n\n"
    
    def _normalize_website_url(self, website: str) -> str:
        """
        Normalize website URL for consistency
        
        Args:
            website: Raw website URL
            
        Returns:
            Normalized URL
        """
        if not website:
            return ''
        
        # Remove whitespace
        website = website.strip()
        
        # Add https:// if no protocol specified
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        
        # Remove trailing slash
        website = website.rstrip('/')
        
        return website
    
    def get_available_extractors(self) -> List[str]:
        """
        Get list of available extractor names
        
        Returns:
            List of extractor names
        """
        return [extractor.get_extractor_name() for extractor in self.extractors]
    
    def get_enabled_extractors(self) -> List[str]:
        """
        Get list of enabled extractor names
        
        Returns:
            List of enabled extractor names
        """
        return [extractor.get_extractor_name() for extractor in self.extractors if extractor.is_enabled()]