import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from src.web_search.brave_search import BraveSearchClient
from src.web_search.tavily_search import TavilySearchClient
from src.web_search.serp_search import SerpAPIClient


class SearchOrchestrator:
    def __init__(self, brave_client: BraveSearchClient, 
                 tavily_client: TavilySearchClient, 
                 serpapi_client: SerpAPIClient):
        self.brave = brave_client
        self.tavily = tavily_client
        self.serpapi = serpapi_client
    
    async def search_all_sources(self, company_name: str, 
                               person_name: str, role: str) -> List[Dict]:
        """Execute searches across all APIs concurrently"""
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.brave.search_person_info, company_name, person_name, role),
                executor.submit(self.tavily.search_person_info, company_name, person_name, role),
                executor.submit(self.serpapi.search_person_info, company_name, person_name, role)
            ]
            
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    print(f"--- Search Result from {result.get('source', 'unknown').upper()} ---")
                    print(result) # Log the raw result
                    results.append(result)
                except Exception as e:
                    print(f"Search failed: {e}")
            
            print(f"--- Consolidated Search Results (Orchestrator) ---")
            print(results) # Log the consolidated results before returning
            return results