"""
Inc42 Startup Scraper Module

A robust Python module to scrape comprehensive startup information from inc42.com
including dynamic tab discovery and extraction of all available data sections.
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Inc42Scraper:
    """
    Main scraper class for extracting startup information from Inc42.com
    """
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize the scraper with configurable settings
        
        Args:
            delay: Delay between requests to respect rate limits
        """
        self.base_url = "https://inc42.com"
        self.delay = delay
        self.session = requests.Session()
        
        # Headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Ensure outputs directory exists
        os.makedirs('outputs', exist_ok=True)
    
    def get_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page with retry logic
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts
            
        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                time.sleep(self.delay)
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
                time.sleep(self.delay * 2)  # Longer delay before retry
        
        return None
    
    def discover_tabs(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """
        Dynamically discover all available tabs on the company page
        
        Args:
            soup: BeautifulSoup object of the main company page
            base_url: Base URL of the company page
            
        Returns:
            Dictionary mapping tab names to their URLs
        """
        tabs = {}
        
        # Look for tab navigation elements (updated for Inc42's React structure)
        tab_selectors = [
            '.cgjoFO button',  # Main tab buttons in React component
            '.MuiTabs-root button',  # Material UI tabs
            '.company-tabs a',
            '.nav-tabs a',
            '.tab-navigation a',
            '[data-tab-target]',
            '.company-nav a',
            'button[role="tab"]'  # ARIA role for tabs
        ]
        
        for selector in tab_selectors:
            tab_elements = soup.select(selector)
            if tab_elements:
                for tab in tab_elements:
                    tab_name = tab.get_text(strip=True)
                    
                    # For React buttons, construct URL based on tab name
                    if tab_name and 'button' in selector:
                        # Common tab names to URL mapping
                        tab_name_lower = tab_name.lower()
                        if tab_name_lower in ['overview', 'about']:
                            tab_url = base_url
                        elif tab_name_lower == 'financials':
                            tab_url = f"{base_url}/financials"
                        elif tab_name_lower == 'funding':
                            tab_url = f"{base_url}/funding"
                        elif tab_name_lower == 'investments':
                            tab_url = f"{base_url}/investments"
                        elif tab_name_lower == 'acquisitions':
                            tab_url = f"{base_url}/acquisitions"
                        elif tab_name_lower in ['latest news', 'news']:
                            tab_url = f"{base_url}/news"
                        else:
                            tab_url = f"{base_url}/{tab_name_lower.replace(' ', '-')}"
                        
                        tabs[tab_name] = tab_url
                    
                    # For regular anchor tags
                    elif tab_name:
                        tab_url = tab.get('href')
                        if tab_url and isinstance(tab_url, str):
                            # Convert relative URLs to absolute
                            if tab_url.startswith('/'):
                                tab_url = urljoin(self.base_url, tab_url)
                            tabs[tab_name] = tab_url
                
                if tabs:  # If we found tabs with this selector, use them
                    break
        
        # If no tabs discovered through selectors, create default tabs
        if not tabs:
            logger.info("No tabs discovered via selectors, creating default tab set")
            tabs = {
                'Overview': base_url,
                'Financials': f"{base_url}/financials",
                'Funding': f"{base_url}/funding",
                'Investments': f"{base_url}/investments",
                'Acquisitions': f"{base_url}/acquisitions",
                'Latest News': f"{base_url}/news"
            }
        
        logger.info(f"Discovered tabs: {list(tabs.keys())}")
        return tabs
    
    def extract_json_ld_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract structured data from JSON-LD scripts
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary containing structured data
        """
        json_ld_data = {}
        
        # Find all JSON-LD script tags
        json_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                
                # Handle different schema types
                if isinstance(data, dict):
                    schema_type = data.get('@type', '')
                    
                    if schema_type == 'Organization':
                        json_ld_data['organization'] = data
                    elif schema_type == 'FAQPage':
                        json_ld_data['faq'] = data
                    elif schema_type == 'Person':
                        json_ld_data['person'] = data
                    else:
                        json_ld_data['other'] = data
                        
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            schema_type = item.get('@type', '')
                            if schema_type not in json_ld_data:
                                json_ld_data[schema_type.lower()] = []
                            json_ld_data[schema_type.lower()].append(item)
                            
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Failed to parse JSON-LD: {e}")
                continue
        
        return json_ld_data

    def extract_faq_data(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract FAQ data from the page structure
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of FAQ items with questions and answers
        """
        faq_data = []
        
        # Look for FAQ sections in various formats
        faq_selectors = [
            '.faq-item',
            '.question-answer',
            '[data-faq]',
            '.accordion-item'
        ]
        
        for selector in faq_selectors:
            faq_items = soup.select(selector)
            for item in faq_items:
                question_elem = item.select_one('.question, .faq-question, h3, h4, h5')
                answer_elem = item.select_one('.answer, .faq-answer, p, .content')
                
                if question_elem and answer_elem:
                    faq_data.append({
                        'question': question_elem.get_text(strip=True),
                        'answer': answer_elem.get_text(strip=True)
                    })
        
        return faq_data

    def extract_basic_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract basic company information from the main page
        
        Args:
            soup: BeautifulSoup object of the company page
            
        Returns:
            Dictionary containing basic company information
        """
        info = {}
        
        # First, try to get data from JSON-LD structured data
        json_ld_data = self.extract_json_ld_data(soup)
        
        # Extract from Organization schema if available
        if 'organization' in json_ld_data:
            org_data = json_ld_data['organization']
            
            # Handle case where organization data might be a list
            if isinstance(org_data, list) and org_data:
                org_data = org_data[0]  # Take the first organization
            
            if isinstance(org_data, dict):
                info['company_name'] = org_data.get('name', '')
                info['description'] = org_data.get('description', '')
                info['founded_year'] = org_data.get('foundingDate', '')
                
                # Extract founders
                founders = org_data.get('founder', [])
                if founders:
                    if isinstance(founders, list):
                        founder_names = [f.get('name', '') if isinstance(f, dict) else str(f) for f in founders]
                        info['founders'] = ', '.join(founder_names)
                    elif isinstance(founders, dict):
                        info['founders'] = founders.get('name', '')
                    else:
                        info['founders'] = str(founders)
        
        # Company name (fallback to HTML parsing)
        if not info.get('company_name'):
            name_selectors = [
                '.cZZaIk',  # HeadingText component
                'h1.company-name',
                '.company-header h1',
                '.profile-header h1',
                'h1'
            ]
            
            for selector in name_selectors:
                name_elem = soup.select_one(selector)
                if name_elem:
                    info['company_name'] = name_elem.get_text(strip=True)
                    break
        
        # Company logo
        logo_selectors = [
            '.bVpssY img',  # CustomImageLayout component
            '.company-logo img',
            '.profile-image img',
            '.company-header img'
        ]
        
        for selector in logo_selectors:
            logo_elem = soup.select_one(selector)
            if logo_elem:
                logo_url = logo_elem.get('src')
                if logo_url and isinstance(logo_url, str):
                    info['logo_url'] = urljoin(self.base_url, logo_url) if logo_url.startswith('/') else logo_url
                break
        
        # Extract description (try to get full description)
        if not info.get('description'):
            content_areas = [
                '.hEQUO',  # SubContent component
                '.company-description',
                '.profile-content',
                '.company-details',
                '.overview-content'
            ]
            
            for selector in content_areas:
                content_elem = soup.select_one(selector)
                if content_elem:
                    description = content_elem.get_text(strip=True)
                    
                    # Try to extract fuller description from page text if truncated
                    if description.endswith('...View more'):
                        # Look for the full description in JSON-LD or meta tags
                        meta_desc = soup.find('meta', property='og:description')
                        if meta_desc:
                            full_desc = meta_desc.get('content', '')
                            if len(full_desc) > len(description.replace('...View more', '')):
                                description = full_desc
                    
                    info['description'] = description
                    break
        
        # Company type/status
        type_selectors = [
            '.GGWBb',  # CompanyTypeStyle
            '.company-type',
            '.business-type'
        ]
        
        for selector in type_selectors:
            type_elem = soup.select_one(selector)
            if type_elem:
                info['company_type'] = type_elem.get_text(strip=True)
                break
        
        # Extract social media links
        social_selectors = [
            '.bfYKob a',  # SocialMediaIconsLayout
            '.social-links a',
            '.company-social a'
        ]
        
        social_links = []
        for selector in social_selectors:
            social_elems = soup.select(selector)
            for elem in social_elems:
                href = elem.get('href')
                if href and href != '#':
                    social_links.append(href)
        
        if social_links:
            info['social_media'] = social_links
        
        # Extract funding information from JSON-LD if available
        if 'faq' in json_ld_data:
            faq_items = json_ld_data['faq'].get('mainEntity', [])
            for item in faq_items:
                question = item.get('name', '').lower()
                answer = item.get('acceptedAnswer', {}).get('text', '')
                
                if 'total funding' in question:
                    info['total_funding'] = answer
                elif 'funding rounds' in question:
                    info['funding_rounds'] = answer
                elif 'founders' in question and not info.get('founders'):
                    info['founders'] = answer
        
        # Extract additional structured data
        page_text = soup.get_text()
        
        # Look for key metrics in text
        funding_match = re.search(r'\$([0-9,.]+)\s*(million|billion)', page_text, re.IGNORECASE)
        if funding_match and not info.get('total_funding'):
            info['total_funding'] = f"${funding_match.group(1)} {funding_match.group(2)}"
        
        # Extract founding year if not found
        if not info.get('founded_year'):
            founding_patterns = [
                r'founded[:\s]+(\d{4})',
                r'established[:\s]+(\d{4})',
                r'started[:\s]+(\d{4})',
                r'inception[:\s]+(\d{4})'
            ]
            
            for pattern in founding_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    info['founded_year'] = match.group(1)
                    break
        
        return info
    
    def extract_tab_content(self, tab_name: str, tab_url: str) -> Dict[str, Any]:
        """
        Extract content from a specific tab
        
        Args:
            tab_name: Name of the tab
            tab_url: URL of the tab
            
        Returns:
            Dictionary containing tab content
        """
        soup = self.get_page(tab_url)
        if not soup:
            return {'error': f'Failed to fetch {tab_name} tab'}
        
        content = {'tab_name': tab_name, 'url': tab_url}
        
        # Extract JSON-LD structured data first
        json_ld_data = self.extract_json_ld_data(soup)
        data_sections = {}
        
        # Extract FAQ data if this is a funding or other data-rich tab
        if 'faq' in json_ld_data:
            faq_items = json_ld_data['faq'].get('mainEntity', [])
            faq_data = []
            
            for item in faq_items:
                question = item.get('name', '')
                answer_data = item.get('acceptedAnswer', {})
                answer = answer_data.get('text', '')
                
                if question and answer:
                    faq_data.append({
                        'question': question,
                        'answer': answer
                    })
            
            if faq_data:
                data_sections['faq_data'] = faq_data
        
        # Extract any organization data
        if 'organization' in json_ld_data:
            org_data = json_ld_data['organization']
            
            # Handle case where organization data might be a list
            if isinstance(org_data, list) and org_data:
                org_data = org_data[0]  # Take the first organization
            
            if org_data and isinstance(org_data, dict):
                data_sections['organization_data'] = org_data
        
        # Look for common data containers (updated for Inc42 structure)
        containers = [
            '.css-1qw96cp',  # Main content padding container
            '.hYlyBa',  # Primary card layout
            '.MuiDataGrid-root',  # Data grid components
            '.main-company-list',  # Company listing container
            '.tab-content',
            '.content-section',
            '.data-section',
            '.info-block',
            'main',
            '.container'
        ]
        
        for container_selector in containers:
            container = soup.select_one(container_selector)
            if container:
                # Extract tables (handle both regular tables and MUI DataGrids)
                tables = container.find_all('table')
                for i, table in enumerate(tables):
                    table_data = self.extract_table_data(table)
                    if table_data:
                        data_sections[f'table_{i+1}'] = table_data
                
                # Extract MUI DataGrid content
                datagrid_rows = container.select('.MuiDataGrid-row')
                if datagrid_rows:
                    grid_data = []
                    for row in datagrid_rows:
                        cells = row.select('.MuiDataGrid-cell')
                        if cells:
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            if any(row_data):  # Only add non-empty rows
                                grid_data.append(row_data)
                    
                    if grid_data:
                        data_sections['data_grid'] = grid_data
                
                # Extract lists
                lists = container.find_all(['ul', 'ol'])
                for i, list_elem in enumerate(lists):
                    list_data = [li.get_text(strip=True) for li in list_elem.find_all('li')]
                    if list_data:
                        data_sections[f'list_{i+1}'] = list_data
                
                # Extract key-value pairs
                kv_patterns = [
                    ('.key-value', '.key', '.value'),
                    ('.data-row', '.label', '.data'),
                    ('.info-item', '.label', '.info')
                ]
                
                for container_class, key_class, value_class in kv_patterns:
                    kv_containers = container.select(container_class)
                    for kv_container in kv_containers:
                        key_elem = kv_container.select_one(key_class)
                        value_elem = kv_container.select_one(value_class)
                        if key_elem and value_elem:
                            key = key_elem.get_text(strip=True)
                            value = value_elem.get_text(strip=True)
                            data_sections[key] = value
                
                # Extract key metrics and financial data
                text_content = container.get_text()
                
                # Look for funding amounts
                funding_patterns = [
                    r'\$([0-9,\.]+)\s*(billion|million|thousand)',
                    r'₹([0-9,\.]+)\s*(crore|lakh)',
                    r'([0-9,\.]+)\s*(rounds?|series|funding)',
                    r'total funding[:\s]*\$?([0-9,\.]+)',
                    r'valuation[:\s]*\$?([0-9,\.]+)'
                ]
                
                for pattern in funding_patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        data_sections['funding_metrics'] = matches
                        break
                
                # Extract dates
                date_patterns = [
                    r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
                    r'(\d{4})-(\d{2})-(\d{2})',
                    r'last funding[:\s]*([0-9\s\w,]+)',
                    r'founded[:\s]*([0-9\s\w,]+)'
                ]
                
                for pattern in date_patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        data_sections['dates'] = matches
                        break
                
                # Extract general text content
                if text_content and len(text_content) > 100 and 'raw_content' not in data_sections:
                    # Clean and truncate the content
                    clean_content = re.sub(r'\s+', ' ', text_content).strip()
                    data_sections['raw_content'] = clean_content[:1000] + '...' if len(clean_content) > 1000 else clean_content
                
                break
        
        content['data'] = data_sections
        return content
    
    def extract_table_data(self, table) -> List[Dict[str, str]]:
        """
        Extract data from HTML table
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            List of dictionaries representing table rows
        """
        data = []
        headers = []
        
        # Extract headers
        header_row = table.find('tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Extract data rows
        rows = table.find_all('tr')[1:] if headers else table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if cells:
                if headers and len(cells) == len(headers):
                    row_data = {headers[i]: cell.get_text(strip=True) for i, cell in enumerate(cells)}
                else:
                    row_data = {f'column_{i+1}': cell.get_text(strip=True) for i, cell in enumerate(cells)}
                
                if any(row_data.values()):  # Only add non-empty rows
                    data.append(row_data)
        
        return data
    
    def format_to_markdown(self, startup_data: Dict[str, Any]) -> str:
        """
        Format extracted data into a well-structured markdown document
        
        Args:
            startup_data: Dictionary containing all extracted startup data
            
        Returns:
            Formatted markdown string
        """
        md_content = []
        
        # Header
        company_name = startup_data.get('basic_info', {}).get('company_name', 'Unknown Company')
        md_content.append(f"# {company_name}")
        md_content.append("")
        
        # Extraction metadata
        md_content.append(f"*Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        md_content.append(f"*Source: Inc42.com*")
        md_content.append("")
        
        # Basic Information
        basic_info = startup_data.get('basic_info', {})
        if basic_info:
            md_content.append("## Basic Information")
            md_content.append("")
            
            # Order the fields logically
            field_order = ['description', 'founded_year', 'founders', 'company_type', 'total_funding', 'funding_rounds', 'logo_url', 'social_media']
            
            for field in field_order:
                if field in basic_info and basic_info[field]:
                    value = basic_info[field]
                    formatted_key = field.replace('_', ' ').title()
                    
                    # Format social media as a list
                    if field == 'social_media' and isinstance(value, list):
                        md_content.append(f"**{formatted_key}:**")
                        for link in value:
                            md_content.append(f"- {link}")
                    else:
                        md_content.append(f"**{formatted_key}:** {value}")
            
            # Add any remaining fields not in the ordered list
            for key, value in basic_info.items():
                if key not in field_order + ['company_name'] and value:
                    formatted_key = key.replace('_', ' ').title()
                    md_content.append(f"**{formatted_key}:** {value}")
            
            md_content.append("")
        
        # Tab content
        tabs_data = startup_data.get('tabs', {})
        for tab_name, tab_content in tabs_data.items():
            md_content.append(f"## {tab_name}")
            md_content.append("")
            
            if 'error' in tab_content:
                md_content.append(f"*Error: {tab_content['error']}*")
                md_content.append("")
                continue
            
            tab_data = tab_content.get('data', {})
            
            # Format tables
            table_count = 1
            for key, value in tab_data.items():
                if key.startswith('table_') and isinstance(value, list) and value:
                    md_content.append(f"### Table {table_count}")
                    md_content.append("")
                    
                    # Create markdown table
                    if isinstance(value[0], dict):
                        headers = list(value[0].keys())
                        md_content.append("| " + " | ".join(headers) + " |")
                        md_content.append("| " + " | ".join(["---"] * len(headers)) + " |")
                        
                        for row in value:
                            row_values = [str(row.get(header, '')) for header in headers]
                            md_content.append("| " + " | ".join(row_values) + " |")
                    
                    md_content.append("")
                    table_count += 1
            
            # Format lists
            list_count = 1
            for key, value in tab_data.items():
                if key.startswith('list_') and isinstance(value, list) and value:
                    md_content.append(f"### List {list_count}")
                    md_content.append("")
                    
                    for item in value:
                        md_content.append(f"- {item}")
                    
                    md_content.append("")
                    list_count += 1
            
            # Format FAQ data (most important structured data)
            if 'faq_data' in tab_data:
                md_content.append("### Frequently Asked Questions")
                md_content.append("")
                for faq in tab_data['faq_data']:
                    question = faq.get('question', '')
                    answer = faq.get('answer', '')
                    if question and answer:
                        md_content.append(f"**Q: {question}**")
                        md_content.append(f"A: {answer}")
                        md_content.append("")
            
            # Format organization data
            if 'organization_data' in tab_data:
                org_data = tab_data['organization_data']
                md_content.append("### Organization Details")
                md_content.append("")
                
                key_fields = ['name', 'description', 'foundingDate', 'founder', 'address', 'sameAs']
                for field in key_fields:
                    if field in org_data and org_data[field]:
                        value = org_data[field]
                        if isinstance(value, list):
                            if field == 'founder':
                                founder_names = [f.get('name', str(f)) if isinstance(f, dict) else str(f) for f in value]
                                value = ', '.join(founder_names)
                            else:
                                value = ', '.join(str(v) for v in value)
                        elif isinstance(value, dict):
                            if field == 'address':
                                value = f"{value.get('streetAddress', '')}, {value.get('addressLocality', '')}, {value.get('addressCountry', '')}"
                            else:
                                value = str(value)
                        
                        formatted_field = field.replace('Date', ' Date').replace('Same', 'Same ').title()
                        md_content.append(f"**{formatted_field}:** {value}")
                
                md_content.append("")
            
            # Format funding metrics and dates
            if 'funding_metrics' in tab_data:
                md_content.append("### Financial Metrics")
                md_content.append("")
                for metric in tab_data['funding_metrics']:
                    if isinstance(metric, tuple):
                        md_content.append(f"- {' '.join(str(x) for x in metric)}")
                    else:
                        md_content.append(f"- {metric}")
                md_content.append("")
            
            if 'dates' in tab_data:
                md_content.append("### Important Dates")
                md_content.append("")
                for date_info in tab_data['dates']:
                    if isinstance(date_info, tuple):
                        md_content.append(f"- {' '.join(str(x) for x in date_info)}")
                    else:
                        md_content.append(f"- {date_info}")
                md_content.append("")
            
            # Format data grid
            if 'data_grid' in tab_data and tab_data['data_grid']:
                md_content.append("### Data Grid")
                md_content.append("")
                
                grid_data = tab_data['data_grid']
                if grid_data and grid_data[0]:
                    # Create headers if we have data
                    max_cols = max(len(row) for row in grid_data) if grid_data else 0
                    headers = [f"Column {i+1}" for i in range(max_cols)]
                    
                    md_content.append("| " + " | ".join(headers) + " |")
                    md_content.append("| " + " | ".join(["---"] * len(headers)) + " |")
                    
                    for row in grid_data:
                        # Pad row to match header length
                        padded_row = row + [''] * (len(headers) - len(row))
                        md_content.append("| " + " | ".join(str(cell) for cell in padded_row) + " |")
                
                md_content.append("")
            
            # Format key-value data
            kv_data = {k: v for k, v in tab_data.items() 
                      if not k.startswith(('table_', 'list_', 'raw_content', 'funding_metrics', 'dates', 'data_grid', 'faq_data', 'organization_data')) and v}
            
            if kv_data:
                md_content.append("### Key Information")
                md_content.append("")
                
                for key, value in kv_data.items():
                    formatted_key = key.replace('_', ' ').title()
                    md_content.append(f"**{formatted_key}:** {value}")
                
                md_content.append("")
            
            # Add raw content if no structured data found
            if 'raw_content' in tab_data and not any(k in tab_data for k in ['table_1', 'list_1']) and not kv_data:
                md_content.append("### Content")
                md_content.append("")
                md_content.append(tab_data['raw_content'])
                md_content.append("")
        
        return "\n".join(md_content)
    
    def scrape_startup(self, startup_name: str) -> Dict[str, Any]:
        """
        Main method to scrape all available information for a startup
        
        Args:
            startup_name: Name of the startup to scrape
            
        Returns:
            Dictionary containing all extracted data
        """
        # Construct the company URL
        company_url = f"{self.base_url}/company/{startup_name.lower().replace(' ', '-')}"
        
        logger.info(f"Starting scrape for: {startup_name}")
        logger.info(f"URL: {company_url}")
        
        # Get the main company page
        main_soup = self.get_page(company_url)
        if not main_soup:
            return {'error': f'Could not access company page for {startup_name}'}
        
        startup_data = {}
        
        # Extract basic information from main page
        basic_info = self.extract_basic_info(main_soup)
        startup_data['basic_info'] = basic_info
        
        # Discover and extract from all tabs
        tabs = self.discover_tabs(main_soup, company_url)
        tabs_data = {}
        
        for tab_name, tab_url in tabs.items():
            logger.info(f"Extracting from tab: {tab_name}")
            tab_content = self.extract_tab_content(tab_name, tab_url)
            tabs_data[tab_name] = tab_content
        
        startup_data['tabs'] = tabs_data
        
        # Generate markdown output
        markdown_content = self.format_to_markdown(startup_data)
        
        # Save to file
        filename = f"{startup_name.lower().replace(' ', '_')}_profile.md"
        filepath = os.path.join('outputs', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Profile saved to: {filepath}")
        
        startup_data['output_file'] = filepath
        return startup_data


def scrape_inc42_startup(startup_name: str, delay: float = 1.0) -> Dict[str, Any]:
    """
    Convenience function to scrape a startup's information
    
    Args:
        startup_name: Name of the startup
        delay: Delay between requests
        
    Returns:
        Dictionary containing extracted data
    """
    scraper = Inc42Scraper(delay=delay)
    return scraper.scrape_startup(startup_name)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python inc42_scraper.py <startup_name>")
        print("Example: python inc42_scraper.py zomato")
        sys.exit(1)
    
    startup_name = sys.argv[1]
    result = scrape_inc42_startup(startup_name)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Successfully scraped data for {startup_name}")
        print(f"Output saved to: {result['output_file']}")