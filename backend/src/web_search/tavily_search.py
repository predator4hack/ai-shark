import requests
from typing import Dict, List

class TavilySearchClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
    
    def search_person_info(self, company_name: str, person_name: str, role: str) -> Dict:
        query = f'{person_name} {company_name} {role} biography education career'
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_domains": [
                "linkedin.com", "crunchbase.com", "forbes.com", 
                "techcrunch.com", "bloomberg.com", "wikipedia.org"
            ],
            "max_results": 10
        }
        
        response = requests.post(self.base_url, json=payload)
        result = response.json()
        
        return {"source": "tavily", "results": result.get('results', [])}