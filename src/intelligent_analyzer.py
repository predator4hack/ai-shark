"""
Intelligent Analyzer Module

A comprehensive Python module that analyzes prompts using Gemini LLM with advanced web scraping
and Google search integration capabilities.
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent
import google.generativeai as genai
from googlesearch import search
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


@dataclass
class SearchResult:
    """Data class for search results"""
    title: str
    url: str
    snippet: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResult:
    """Data class for analysis results"""
    query: str
    gemini_response: str
    search_results: List[SearchResult]
    web_content: List[Dict[str, Any]]
    confidence_score: float
    timestamp: str
    metadata: Dict[str, Any]


class IntelligentAnalyzer:
    """
    Comprehensive analyzer that uses Gemini LLM with web scraping and Google search
    to provide in-depth analysis of user prompts.
    """
    
    def __init__(self, 
                 gemini_api_key: Optional[str] = None,
                 max_search_results: int = 10,
                 timeout: int = 30,
                 enable_javascript: bool = True,
                 log_level: int = logging.INFO):
        """
        Initialize the Intelligent Analyzer
        
        Args:
            gemini_api_key: Google Gemini API key (if not provided, will use env var)
            max_search_results: Maximum number of search results to process
            timeout: Request timeout in seconds
            enable_javascript: Whether to enable JavaScript rendering
            log_level: Logging level
        """
        # Setup logging
        self._setup_logging(log_level)
        
        # Initialize Gemini
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass it directly.")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Configuration
        self.max_search_results = max_search_results
        self.timeout = timeout
        self.enable_javascript = enable_javascript
        
        # Setup components
        self.user_agent = UserAgent()
        self.session = requests.Session()
        self._setup_session()
        
        # Selenium driver (lazy initialization)
        self._driver = None
        
        self.logger.info("IntelligentAnalyzer initialized successfully")
    
    def _setup_logging(self, log_level: int):
        """Setup logging configuration"""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('intelligent_analyzer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_session(self):
        """Setup requests session with headers and retry strategy"""
        self.session.headers.update({
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Add retry strategy
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_selenium_driver(self) -> webdriver.Chrome:
        """Get Selenium WebDriver instance (lazy initialization)"""
        if self._driver is None:
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument(f'--user-agent={self.user_agent.random}')
                chrome_options.add_argument('--window-size=1920,1080')
                
                self._driver = webdriver.Chrome(options=chrome_options)
                self.logger.info("Selenium WebDriver initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Selenium WebDriver: {e}")
                raise
        
        return self._driver
    
    def google_search(self, query: str, num_results: int = None) -> List[SearchResult]:
        """
        Perform Google search and return results
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        if num_results is None:
            num_results = self.max_search_results
        
        try:
            self.logger.info(f"Performing Google search for: {query}")
            search_results = []
            
            # Use googlesearch-python library
            urls = search(query, num_results=num_results, stop=num_results, pause=2)
            
            for i, url in enumerate(urls):
                try:
                    # Get basic info from the URL
                    result = SearchResult(
                        title=f"Search Result {i+1}",
                        url=url,
                        snippet="",
                        metadata={"rank": i+1}
                    )
                    search_results.append(result)
                    
                    if len(search_results) >= num_results:
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Error processing search result {url}: {e}")
                    continue
            
            self.logger.info(f"Found {len(search_results)} search results")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Google search failed: {e}")
            return []
    
    def scrape_url_basic(self, url: str) -> Dict[str, Any]:
        """
        Basic web scraping using requests and BeautifulSoup
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        try:
            self.logger.debug(f"Basic scraping: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract content
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text_content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract meta information
            meta_description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                meta_description = meta_desc.get('content', '')
            
            # Extract links
            links = [link.get('href') for link in soup.find_all('a', href=True)]
            
            return {
                'url': url,
                'title': title_text,
                'content': text_content[:5000],  # Limit content length
                'meta_description': meta_description,
                'links_count': len(links),
                'content_length': len(text_content),
                'scraping_method': 'basic',
                'status_code': response.status_code
            }
            
        except Exception as e:
            self.logger.error(f"Basic scraping failed for {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'scraping_method': 'basic'
            }
    
    def scrape_url_selenium(self, url: str) -> Dict[str, Any]:
        """
        Advanced web scraping using Selenium for JavaScript-heavy sites
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        try:
            self.logger.debug(f"Selenium scraping: {url}")
            
            driver = self._get_selenium_driver()
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Extract content
            title = driver.title
            page_source = driver.page_source
            
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text_content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract additional JavaScript-loaded content
            try:
                # Try to find common dynamic content containers
                dynamic_elements = driver.find_elements(By.CSS_SELECTOR, 
                                                      "[data-react], [ng-app], [v-app], .dynamic-content")
                dynamic_content = []
                for element in dynamic_elements[:5]:  # Limit to first 5
                    dynamic_content.append(element.text)
            except:
                dynamic_content = []
            
            return {
                'url': url,
                'title': title,
                'content': text_content[:5000],
                'dynamic_content': dynamic_content,
                'content_length': len(text_content),
                'scraping_method': 'selenium',
                'page_load_time': 'measured'
            }
            
        except TimeoutException:
            self.logger.error(f"Timeout while loading {url}")
            return {'url': url, 'error': 'Timeout', 'scraping_method': 'selenium'}
        except Exception as e:
            self.logger.error(f"Selenium scraping failed for {url}: {e}")
            return {'url': url, 'error': str(e), 'scraping_method': 'selenium'}
    
    def scrape_urls_parallel(self, urls: List[str], use_selenium: bool = False) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs in parallel
        
        Args:
            urls: List of URLs to scrape
            use_selenium: Whether to use Selenium for scraping
            
        Returns:
            List of scraped content dictionaries
        """
        self.logger.info(f"Scraping {len(urls)} URLs in parallel (selenium={use_selenium})")
        
        results = []
        scrape_func = self.scrape_url_selenium if use_selenium else self.scrape_url_basic
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(scrape_func, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error scraping {url}: {e}")
                    results.append({'url': url, 'error': str(e)})
        
        return results
    
    def analyze_with_gemini(self, prompt: str, context_data: List[Dict[str, Any]] = None) -> str:
        """
        Analyze prompt using Gemini LLM with optional context data
        
        Args:
            prompt: User prompt to analyze
            context_data: Additional context from web scraping
            
        Returns:
            Gemini's analysis response
        """
        try:
            self.logger.info("Analyzing with Gemini LLM")
            
            # Prepare the enhanced prompt
            enhanced_prompt = f"""
            Please analyze the following prompt and provide a comprehensive response:
            
            USER PROMPT: {prompt}
            
            """
            
            if context_data:
                enhanced_prompt += "\nADDITIONAL CONTEXT FROM WEB SOURCES:\n"
                for i, data in enumerate(context_data[:5], 1):  # Limit to 5 sources
                    if 'content' in data and data['content']:
                        enhanced_prompt += f"\nSource {i} ({data.get('url', 'Unknown')}):\n"
                        enhanced_prompt += f"Title: {data.get('title', 'N/A')}\n"
                        enhanced_prompt += f"Content: {data['content'][:1000]}...\n"
                        enhanced_prompt += "---\n"
            
            enhanced_prompt += """
            
            Please provide a detailed analysis that:
            1. Directly addresses the user's prompt
            2. Incorporates relevant information from the web sources
            3. Provides actionable insights or recommendations
            4. Highlights any important considerations or limitations
            5. Cites sources when appropriate
            
            Response:
            """
            
            # Generate response
            response = self.model.generate_content(enhanced_prompt)
            
            self.logger.info("Gemini analysis completed")
            return response.text
            
        except Exception as e:
            self.logger.error(f"Gemini analysis failed: {e}")
            return f"Error during analysis: {str(e)}"
    
    def analyze_prompt(self, 
                      prompt: str, 
                      enable_search: bool = True,
                      enable_scraping: bool = True,
                      use_selenium: bool = None) -> AnalysisResult:
        """
        Main method to analyze a prompt using all available tools
        
        Args:
            prompt: User prompt to analyze
            enable_search: Whether to perform Google search
            enable_scraping: Whether to scrape web content
            use_selenium: Whether to use Selenium (auto-detect if None)
            
        Returns:
            AnalysisResult object with comprehensive analysis
        """
        start_time = time.time()
        self.logger.info(f"Starting comprehensive analysis for prompt: {prompt[:100]}...")
        
        search_results = []
        web_content = []
        
        try:
            # Step 1: Perform Google search if enabled
            if enable_search:
                search_results = self.google_search(prompt)
                
                # Step 2: Scrape web content if enabled
                if enable_scraping and search_results:
                    urls_to_scrape = [result.url for result in search_results[:5]]
                    
                    # Auto-detect whether to use Selenium
                    if use_selenium is None:
                        # Use Selenium for common SPA/dynamic sites
                        dynamic_domains = ['react', 'angular', 'vue', 'spa', 'app', 'dashboard']
                        use_selenium = any(domain in url.lower() for url in urls_to_scrape 
                                         for domain in dynamic_domains)
                    
                    web_content = self.scrape_urls_parallel(urls_to_scrape, use_selenium)
                    
                    # Update search results with scraped content
                    for i, content in enumerate(web_content):
                        if i < len(search_results) and 'content' in content:
                            search_results[i].content = content.get('content', '')
                            search_results[i].title = content.get('title', search_results[i].title)
            
            # Step 3: Analyze with Gemini
            gemini_response = self.analyze_with_gemini(prompt, web_content)
            
            # Calculate confidence score based on available data
            confidence_score = self._calculate_confidence_score(
                search_results, web_content, gemini_response
            )
            
            # Create result
            result = AnalysisResult(
                query=prompt,
                gemini_response=gemini_response,
                search_results=search_results,
                web_content=web_content,
                confidence_score=confidence_score,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                metadata={
                    'processing_time': time.time() - start_time,
                    'search_enabled': enable_search,
                    'scraping_enabled': enable_scraping,
                    'selenium_used': use_selenium,
                    'sources_found': len(search_results),
                    'content_scraped': len([c for c in web_content if 'content' in c])
                }
            )
            
            self.logger.info(f"Analysis completed in {result.metadata['processing_time']:.2f} seconds")
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            # Return partial result even if there's an error
            return AnalysisResult(
                query=prompt,
                gemini_response=f"Analysis partially failed: {str(e)}",
                search_results=search_results,
                web_content=web_content,
                confidence_score=0.0,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                metadata={
                    'processing_time': time.time() - start_time,
                    'error': str(e)
                }
            )
    
    def _calculate_confidence_score(self, 
                                  search_results: List[SearchResult], 
                                  web_content: List[Dict[str, Any]], 
                                  gemini_response: str) -> float:
        """Calculate confidence score based on available data"""
        score = 0.0
        
        # Base score from Gemini response
        if gemini_response and len(gemini_response) > 100:
            score += 0.3
        
        # Score from search results
        if search_results:
            score += min(len(search_results) * 0.1, 0.3)
        
        # Score from scraped content
        content_with_data = [c for c in web_content if 'content' in c and len(c['content']) > 100]
        if content_with_data:
            score += min(len(content_with_data) * 0.1, 0.4)
        
        return min(score, 1.0)
    
    def export_result(self, result: AnalysisResult, format_type: str = 'json') -> str:
        """
        Export analysis result in specified format
        
        Args:
            result: AnalysisResult to export
            format_type: Export format ('json', 'markdown', 'txt')
            
        Returns:
            Formatted string
        """
        if format_type.lower() == 'json':
            return json.dumps({
                'query': result.query,
                'gemini_response': result.gemini_response,
                'search_results': [
                    {
                        'title': sr.title,
                        'url': sr.url,
                        'snippet': sr.snippet,
                        'content_preview': sr.content[:200] if sr.content else None
                    } for sr in result.search_results
                ],
                'confidence_score': result.confidence_score,
                'timestamp': result.timestamp,
                'metadata': result.metadata
            }, indent=2)
        
        elif format_type.lower() == 'markdown':
            md = f"# Analysis Report\n\n"
            md += f"**Query:** {result.query}\n\n"
            md += f"**Timestamp:** {result.timestamp}\n"
            md += f"**Confidence Score:** {result.confidence_score:.2f}\n\n"
            md += f"## Gemini Analysis\n\n{result.gemini_response}\n\n"
            
            if result.search_results:
                md += f"## Sources\n\n"
                for i, sr in enumerate(result.search_results, 1):
                    md += f"{i}. [{sr.title}]({sr.url})\n"
            
            return md
        
        else:  # txt
            txt = f"ANALYSIS REPORT\n{'='*50}\n\n"
            txt += f"Query: {result.query}\n"
            txt += f"Timestamp: {result.timestamp}\n"
            txt += f"Confidence: {result.confidence_score:.2f}\n\n"
            txt += f"ANALYSIS:\n{'-'*30}\n{result.gemini_response}\n\n"
            
            if result.search_results:
                txt += f"SOURCES:\n{'-'*30}\n"
                for i, sr in enumerate(result.search_results, 1):
                    txt += f"{i}. {sr.title}\n   {sr.url}\n\n"
            
            return txt
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self._driver:
                self._driver.quit()
                self.logger.info("Selenium WebDriver closed")
            
            if hasattr(self, 'session'):
                self.session.close()
                self.logger.info("Requests session closed")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    analyzer = IntelligentAnalyzer()
    
    try:
        # Test analysis
        result = analyzer.analyze_prompt(
            "What are the latest developments in artificial intelligence for 2024?",
            enable_search=True,
            enable_scraping=True
        )
        
        print("Analysis completed!")
        print(f"Confidence Score: {result.confidence_score}")
        print(f"Sources found: {len(result.search_results)}")
        print(f"Response preview: {result.gemini_response[:200]}...")
        
        # Export result
        json_export = analyzer.export_result(result, 'json')
        print("\nJSON export sample:")
        print(json_export[:500] + "..." if len(json_export) > 500 else json_export)
        
    finally:
        analyzer.cleanup()