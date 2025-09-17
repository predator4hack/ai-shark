import asyncio
import os 
from typing import Optional
from src.web_search.brave_search import BraveSearchClient
from src.web_search.tavily_search import TavilySearchClient
from src.web_search.serp_search import SerpAPIClient
from src.web_search.founder_analysis_agent import FounderAnalysisAgent
from src.web_search.data_consolidator import DataConsolidator
from src.web_search.markdown_generator import MarkdownGenerator
from src.web_search.search_orchestrator import SearchOrchestrator


class FounderResearchSystem:
    def __init__(self, brave_key: str, tavily_key: str, 
                 serpapi_key: str, google_adk_key: str):
        # Initialize all components
        self.brave_client = BraveSearchClient(brave_key)
        self.tavily_client = TavilySearchClient(tavily_key)
        self.serpapi_client = SerpAPIClient(serpapi_key)
        
        self.orchestrator = SearchOrchestrator(
            self.brave_client, self.tavily_client, self.serpapi_client
        )
        self.analyzer = FounderAnalysisAgent(google_adk_key)
        # self.consolidator = DataConsolidator() # Removed
        self.markdown_generator = MarkdownGenerator()
    
    async def research_person(self, company_name: str, 
                            person_name: str, role: str) -> str:
        """Main method to research a person and generate a markdown report"""
        
        try:
            # Step 1: Search all sources
            print(f"Searching for {person_name} ({role} of {company_name})...")
            search_results = await self.orchestrator.search_all_sources(
                company_name, person_name, role
            )
            
            # Step 2: Analyze with Google ADK
            print("Analyzing content with Google ADK...")
            analyzed_data = self.analyzer.analyze_search_results(search_results, person_name, role)
            
            # Step 3: Consolidate data (Removed)
            # consolidated_data = self.consolidator.consolidate_person_data(analyzed_data)
            
            # Step 4: Generate markdown report
            print("Generating markdown report...")
            markdown_report = self.markdown_generator.generate_markdown(
                analyzed_data, company_name, person_name, role # Pass analyzed_data directly
            )
            
            return markdown_report
            
        except Exception as e:
            return f"Error in research process: {str(e)}"

# Usage Example
async def main():
    system = FounderResearchSystem(
        brave_key=os.getenv("BRAVE_API_KEY"),
        tavily_key=os.getenv("TAVILY_API_KEY"), 
        serpapi_key=os.getenv("SERP_API_KEY"),
        google_adk_key=os.getenv("GOOGLE_API_KEY")
    )
    
    report = await system.research_person(
        company_name="Ziniosa", 
        person_name="Ashri Jaiswal", 
        role="CEO"
    )
    
    # Save to file
    with open("results/founder_report.md", "w") as f:
        f.write(report)
    
    print("Report generated: founder_report.md")

if __name__ == "__main__":
    asyncio.run(main())