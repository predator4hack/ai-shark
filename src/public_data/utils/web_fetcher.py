"""
Web Content Utilities

This module provides utilities for web content analysis and URL handling
for public data extraction.
"""

import logging
import requests
from typing import Optional
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class WebContentAnalyzer:
    """
    Utilities for web content analysis using Gemini URL context
    
    This class provides helper functions for URL validation, normalization,
    and basic accessibility checking before using Gemini URL context.
    """
    
    @staticmethod
    def is_website_accessible(url: str, timeout: int = 10) -> bool:
        """
        Quick check if website is accessible
        
        Args:
            url: Website URL to check
            timeout: Request timeout in seconds
            
        Returns:
            True if website responds successfully, False otherwise
        """
        if not url:
            return False
        
        try:
            # Normalize URL first
            normalized_url = WebContentAnalyzer.normalize_url(url)
            
            # Send a HEAD request to check accessibility
            response = requests.head(
                normalized_url, 
                timeout=timeout, 
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; StartupAnalyzer/1.0)'
                }
            )
            
            # Consider 2xx and 3xx status codes as accessible
            is_accessible = response.status_code < 400
            
            if is_accessible:
                logger.debug(f"Website {normalized_url} is accessible (status: {response.status_code})")
            else:
                logger.warning(f"Website {normalized_url} returned status {response.status_code}")
            
            return is_accessible
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Cannot access website {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking website accessibility for {url}: {e}")
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize URL format for Gemini URL context
        
        Args:
            url: Raw website URL
            
        Returns:
            Normalized URL string
        """
        if not url:
            return ''
        
        # Remove whitespace
        url = url.strip()
        
        if not url:
            return ''
        
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash for consistency
        url = url.rstrip('/')
        
        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                logger.warning(f"Invalid URL format: {url}")
                return ''
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return ''
        
        return url
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """
        Extract domain from URL
        
        Args:
            url: Website URL
            
        Returns:
            Domain name or None if extraction fails
        """
        try:
            normalized_url = WebContentAnalyzer.normalize_url(url)
            if not normalized_url:
                return None
            
            parsed = urlparse(normalized_url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix for consistency
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
            
        except Exception as e:
            logger.error(f"Error extracting domain from {url}: {e}")
            return None
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if URL has valid format
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL format is valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        try:
            normalized_url = WebContentAnalyzer.normalize_url(url)
            if not normalized_url:
                return False
            
            parsed = urlparse(normalized_url)
            
            # Check if URL has required components
            has_scheme = parsed.scheme in ('http', 'https')
            has_netloc = bool(parsed.netloc)
            
            return has_scheme and has_netloc
            
        except Exception:
            return False
    
    @staticmethod
    def get_website_info(url: str) -> dict:
        """
        Get basic information about a website
        
        Args:
            url: Website URL
            
        Returns:
            Dictionary with website information
        """
        info = {
            'original_url': url,
            'normalized_url': '',
            'domain': '',
            'is_valid': False,
            'is_accessible': False,
            'status_code': None,
            'final_url': '',
        }
        
        try:
            # Normalize URL
            normalized_url = WebContentAnalyzer.normalize_url(url)
            info['normalized_url'] = normalized_url
            info['is_valid'] = bool(normalized_url)
            
            if not normalized_url:
                return info
            
            # Extract domain
            domain = WebContentAnalyzer.extract_domain(normalized_url)
            info['domain'] = domain or ''
            
            # Check accessibility with more detailed response
            try:
                response = requests.head(
                    normalized_url,
                    timeout=10,
                    allow_redirects=True,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; StartupAnalyzer/1.0)'
                    }
                )
                
                info['is_accessible'] = response.status_code < 400
                info['status_code'] = response.status_code
                info['final_url'] = response.url
                
            except requests.exceptions.RequestException as e:
                logger.debug(f"Accessibility check failed for {normalized_url}: {e}")
                info['is_accessible'] = False
                
        except Exception as e:
            logger.error(f"Error getting website info for {url}: {e}")
        
        return info