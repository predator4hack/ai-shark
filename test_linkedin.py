import os
import time
import functools
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from ddgs.ddgs import DDGS
from typing import Dict

from src.web_search.brave_search import BraveSearchClient
from src.web_search.tavily_search import TavilySearchClient
from src.web_search.serp_search import SerpAPIClient

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
try:
    api_key = os.environ["GEMINI_API_KEY"]
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    genai.configure(api_key=api_key)
except (KeyError, ValueError) as e:
    print(f"Error: {e}")
    print("Please make sure you have a .env file with your GEMINI_API_KEY.")
    exit(1)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# --- Retry Decorator ---
def retry_with_backoff(retries=3, backoff_factor=4.0):
    """A decorator for retrying a function with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e: # In a real app, you'd catch more specific API errors
                    print(f"Call to {func.__name__} attempt {attempt + 1}/{retries} failed: {e}")
                    if attempt < retries - 1:
                        sleep_time = backoff_factor ** attempt
                        print(f"Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                    else:
                        print(f"Max retries reached for {func.__name__}.")
                        raise
            # This part should not be reached if the loop completes
            # but as a fallback, we raise an error.
            raise RuntimeError(f"Function {func.__name__} failed after {retries} retries")
        return wrapper
    return decorator


class FounderResearchAgent:
    """
    An autonomous agent that researches a founder by searching the web,
    fetching content, and synthesizing a leadership profile.
    """

    def __init__(self):
        print(f"Initializing model: {GEMINI_MODEL}")
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.search_tool = DDGS()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    @retry_with_backoff(retries=3, backoff_factor=1.0)
    def _search_for_sources(self, query: str, max_results: int = 3):
        """Performs a web search with retries and returns a list of URLs."""
        print(f'Searching for: "{query}"...')
        results = self.search_tool.text(query, max_results=max_results)
        if not results:
            # Raise an exception to trigger the retry decorator if search returns nothing
            raise ValueError("Search returned no results.")
        return [r['href'] for r in results]

    def _fetch_content(self, url: str):
        """Fetches and cleans the text content from a given URL."""
        print(f"Fetching content from: {url}...")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            return " ".join(soup.stripped_strings)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    @retry_with_backoff(retries=3, backoff_factor=2.0)
    def _synthesize_report(self, founder_name: str, company_name: str, content: str):
        """Generates the final report using the Gemini API with exponential backoff."""
        print("Synthesizing information with the Gemini API...")
        prompt = f"""
        Based on the provided web content, generate a comprehensive leadership profile for {founder_name} of {company_name}.

        Structure the output in Markdown format.

        ## Section 1: Factual Summary
        - **Role:**
        - **Company:**
        - **Career History:** (Previous roles, companies)
        - **Education:**
        - **Key Achievements:** (e.g., funding rounds, product launches, awards)

        ## Section 2: Leadership Capability Analysis
        Based on the factual summary, provide an analysis of the founder's capability to lead their startup. For each dimension below, provide a brief, evidence-based summary using only the information from the text.

        - **Domain Expertise:** How does their background align with their company's industry?
        - **Entrepreneurial Experience:** Is there evidence of past startup experience or entrepreneurial ventures?
        - **Vision & Strategy:** Based on quotes or company mission statements, how clearly do they articulate their vision?
        - **Execution & Results:** Does the text mention concrete results, such as securing funding, successful product launches, or significant partnerships?
        """
        full_prompt = f"{prompt}\n\n--- Aggregated Web Content ---\n{content}"
        response = self.model.generate_content(full_prompt)
        return response.text

    def research_founder(self, founder_name: str, company_name: str):
        """Orchestrates the research process: search, fetch, and synthesize."""
        print(f"--- Starting Research for {founder_name} ---")
        queries = [
            f'"{founder_name}" "{company_name}"',
            f'"{founder_name}" "{company_name}" about',
            f'"{founder_name}" "{company_name}" background',
            f'"{founder_name}" linkedin',
        ]

        all_urls = []
        for query in queries:
            try:
                all_urls.extend(self._search_for_sources(query))
            except Exception as e:
                print(f"Could not complete search for query '{query}' after all retries.")
        
        unique_urls = list(set(all_urls))
        print(f"\nFound {len(unique_urls)} unique URLs to analyze.")

        if not unique_urls:
            return "Could not find any relevant sources online."

        aggregated_content = ""
        for url in unique_urls:
            content = self._fetch_content(url)
            if content:
                aggregated_content += f"\n\n--- Content from {url} ---\n{content}"

        if not aggregated_content:
            return "Could not fetch content from any of the discovered URLs."
        
        try:
            return self._synthesize_report(founder_name, company_name, aggregated_content)
        except Exception as e:
            return f"Synthesis failed after all retries: {e}"


# --- API Connection Test Functions ---
def test_brave_connection(api_key: str, company: str, person: str, role: str) -> Dict:
    print(f"\n--- Testing Brave Search API ---")
    if not api_key:
        print("Brave API Key not provided. Skipping test.")
        return {"source": "brave", "results": [], "error": "API Key missing"}
    try:
        client = BraveSearchClient(api_key)
        results = client.search_person_info(company, person, role)
        if results.get("results"):
            print(f"Brave Search: SUCCESS! Found {len(results['results'])} results.")
        else:
            print("Brave Search: No results found.")
        return results
    except Exception as e:
        print(f"Brave Search: ERROR - {e}")
        return {"source": "brave", "results": [], "error": str(e)}

def test_tavily_connection(api_key: str, company: str, person: str, role: str) -> Dict:
    print(f"\n--- Testing Tavily Search API ---")
    if not api_key:
        print("Tavily API Key not provided. Skipping test.")
        return {"source": "tavily", "results": [], "error": "API Key missing"}
    try:
        client = TavilySearchClient(api_key)
        results = client.search_person_info(company, person, role)
        if results.get("results"):
            print(f"Tavily Search: SUCCESS! Found {len(results['results'])} results.")
        else:
            print("Tavily Search: No results found.")
        return results
    except Exception as e:
        print(f"Tavily Search: ERROR - {e}")
        return {"source": "tavily", "results": [], "error": str(e)}

def test_serp_connection(api_key: str, company: str, person: str, role: str) -> Dict:
    print(f"\n--- Testing SerpAPI ---")
    if not api_key:
        print("SerpAPI Key not provided. Skipping test.")
        return {"source": "serpapi", "results": [], "error": "API Key missing"}
    try:
        client = SerpAPIClient(api_key)
        results = client.search_person_info(company, person, role)
        if results.get("results"):
            print(f"SerpAPI: SUCCESS! Found {len(results['results'])} results.")
        else:
            print("SerpAPI: No results found.")
        return results
    except Exception as e:
        print(f"SerpAPI: ERROR - {e}")
        return {"source": "serpapi", "results": [], "error": str(e)}


# --- Main Execution ---
if __name__ == "__main__":
    # --- Agent Research Example ---
    # agent = FounderResearchAgent()
    # report = agent.research_founder(
    #     founder_name="Divya Krishna R",
    #     company_name="Sia Analytics"
    # )
    # print("\n--- Generated Report ---")
    # with open("results/founder_details.md", "w") as f:
    #     f.write(report)
    # print(report)

    # --- API Connection Test Functions ---
    print("\n--- Running API Connection Tests ---")
    test_brave_connection(
        api_key=os.getenv("BRAVE_API_KEY"),
        company="Microsoft",
        person="Satya Nadella",
        role="CEO"
    )
    test_tavily_connection(
        api_key=os.getenv("TAVILY_API_KEY"),
        company="Microsoft",
        person="Satya Nadella",
        role="CEO"
    )
    test_serp_connection(
        api_key=os.getenv("SERP_API_KEY"),
        company="Microsoft",
        person="Satya Nadella",
        role="CEO"
    )