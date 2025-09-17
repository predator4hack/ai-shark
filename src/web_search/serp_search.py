import requests
from typing import Dict, List

class SerpAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search.json"
    
    def search_person_info(self, company_name: str, person_name: str, role: str) -> Dict:
        queries = [
            f'{person_name} {company_name} {role} biography',
            f'{person_name} education background career',
            f'{person_name} notable achievements interviews',
        ]
        
        all_results = []
        for query in queries:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key,
                "num": 10,
                "gl": "us",
                "hl": "en"
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            all_results.extend(data.get('organic_results', []))
        
        return {"source": "serpapi", "results": all_results}