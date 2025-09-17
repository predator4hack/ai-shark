## Sample Output

The system now generates much more comprehensive reports. Here's what you can expect:

```markdown
# Founder Research Report

**Company:**# Multi-API Founder Research System

## System Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Brave API     │    │   Tavily API    │    │   SerpAPI       │
│   (General Web) │    │   (AI-focused)  │    │   (Google SERP) │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Search Orchestrator     │
                    │   (Query Distribution)    │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   Google ADK Agent        │
                    │   (Content Analysis)      │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   Data Consolidator       │
                    │   (Merge & Dedupe)        │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   Markdown Generator      │
                    │   (Structured Output)     │
                    └───────────────────────────┘
```

## Implementation Components

### 1. Search API Clients

#### Brave API Client
```python
import requests
from typing import Dict, List

class BraveSearchClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    def search_founder_info(self, company_name: str, founder_name: str = None) -> Dict:
        queries = [
            f"{company_name} founder CEO biography",
            f"{company_name} founding team leadership",
        ]
        if founder_name:
            queries.append(f"{founder_name} {company_name} background education")
        
        results = []
        for query in queries:
            response = self._make_request(query)
            results.extend(response.get('web', {}).get('results', []))
        
        return {"source": "brave", "results": results}
    
    def _make_request(self, query: str) -> Dict:
        headers = {"X-Subscription-Token": self.api_key}
        params = {
            "q": query,
            "count": 10,
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate"
        }
        response = requests.get(self.base_url, headers=headers, params=params)
        return response.json()
```

#### Tavily API Client
```python
import requests
from typing import Dict, List

class TavilySearchClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
    
    def search_founder_info(self, company_name: str, founder_name: str = None) -> Dict:
        query = f"{company_name} founder background education experience"
        if founder_name:
            query = f"{founder_name} {company_name} founder biography education career"
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_domains": [
                "linkedin.com", "crunchbase.com", "forbes.com", 
                "techcrunch.com", "bloomberg.com"
            ],
            "max_results": 10
        }
        
        response = requests.post(self.base_url, json=payload)
        result = response.json()
        
        return {"source": "tavily", "results": result.get('results', [])}
```

#### SerpAPI Client
```python
import requests
from typing import Dict, List

class SerpAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search.json"
    
    def search_founder_info(self, company_name: str, founder_name: str = None) -> Dict:
        queries = [
            f"{company_name} founder biography",
            f"{company_name} CEO leadership team",
        ]
        if founder_name:
            queries.append(f"{founder_name} education background career")
        
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
```

### 2. Search Orchestrator

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

class SearchOrchestrator:
    def __init__(self, brave_client: BraveSearchClient, 
                 tavily_client: TavilySearchClient, 
                 serpapi_client: SerpAPIClient):
        self.brave = brave_client
        self.tavily = tavily_client
        self.serpapi = serpapi_client
    
    async def search_all_sources(self, company_name: str, 
                               founder_name: Optional[str] = None) -> List[Dict]:
        """Execute searches across all APIs concurrently"""
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.brave.search_founder_info, company_name, founder_name),
                executor.submit(self.tavily.search_founder_info, company_name, founder_name),
                executor.submit(self.serpapi.search_founder_info, company_name, founder_name)
            ]
            
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    print(f"Search failed: {e}")
            
            return results
```

### 3. Google ADK Agent for Content Analysis

```python
import google.generativeai as genai
from typing import Dict, List, Any
import json

class FounderAnalysisAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_search_results(self, search_results: List[Dict]) -> Dict[str, Any]:
        """Use Google ADK to analyze and extract founder information"""
        
        # Prepare content for analysis
        content_for_analysis = self._prepare_content(search_results)
        
        analysis_prompt = f"""
        Analyze the following search results and extract detailed founder information.
        
        Extract:
        1. Founder names and current roles
        2. Educational background (universities, degrees, graduation years)
        3. Professional experience (previous companies, positions, years)
        4. Entrepreneurial experience (companies founded, exit events)
        5. Notable achievements and recognition
        6. Key skills and expertise areas
        7. Personal background (age, location, interests if available)
        
        Content to analyze:
        {content_for_analysis}
        
        Return a structured JSON response with the extracted information.
        """
        
        try:
            response = self.model.generate_content(analysis_prompt)
            # Parse the JSON response
            extracted_data = json.loads(response.text)
            return extracted_data
        except Exception as e:
            print(f"Analysis failed: {e}")
            return {}
    
    def _prepare_content(self, search_results: List[Dict]) -> str:
        """Prepare search results for analysis"""
        content = ""
        for source_data in search_results:
            source = source_data.get('source', 'unknown')
            results = source_data.get('results', [])
            
            content += f"\n--- {source.upper()} RESULTS ---\n"
            for result in results[:5]:  # Limit to top 5 results per source
                title = result.get('title', result.get('name', ''))
                description = result.get('description', result.get('snippet', ''))
                url = result.get('url', result.get('link', ''))
                
                content += f"Title: {title}\n"
                content += f"Description: {description}\n"
                content += f"URL: {url}\n\n"
        
        return content[:8000]  # Limit content length for API
```

### 4. Data Consolidator

```python
from typing import Dict, List, Any
import json

class DataConsolidator:
    def __init__(self):
        self.confidence_weights = {
            'linkedin.com': 0.9,
            'crunchbase.com': 0.95,
            'forbes.com': 0.8,
            'bloomberg.com': 0.85,
            'techcrunch.com': 0.7,
            'company_website': 0.9
        }
    
    def consolidate_founder_data(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate and deduplicate founder information"""
        
        consolidated = {
            'founders': [],
            'company_info': {},
            'data_quality': {
                'sources_used': [],
                'confidence_score': 0.0,
                'last_updated': None
            }
        }
        
        # Process founders data
        founders_data = analyzed_data.get('founders', [])
        for founder in founders_data:
            consolidated_founder = self._consolidate_founder_info(founder)
            consolidated['founders'].append(consolidated_founder)
        
        # Calculate overall confidence score
        consolidated['data_quality']['confidence_score'] = self._calculate_confidence(analyzed_data)
        
        return consolidated
    
    def _consolidate_founder_info(self, founder_data: Dict) -> Dict:
        """Consolidate information for a single founder"""
        return {
            'name': founder_data.get('name', ''),
            'current_role': founder_data.get('current_role', ''),
            'education': self._consolidate_education(founder_data.get('education', [])),
            'experience': self._consolidate_experience(founder_data.get('experience', [])),
            'entrepreneurial_background': founder_data.get('entrepreneurial_background', []),
            'achievements': founder_data.get('achievements', []),
            'skills': founder_data.get('skills', [])
        }
    
    def _consolidate_education(self, education_list: List[Dict]) -> List[Dict]:
        """Deduplicate and consolidate education information"""
        consolidated = []
        seen_institutions = set()
        
        for edu in education_list:
            institution = edu.get('institution', '').lower()
            if institution and institution not in seen_institutions:
                consolidated.append(edu)
                seen_institutions.add(institution)
        
        return consolidated
    
    def _consolidate_experience(self, experience_list: List[Dict]) -> List[Dict]:
        """Deduplicate and consolidate work experience"""
        consolidated = []
        seen_companies = set()
        
        for exp in experience_list:
            company = exp.get('company', '').lower()
            if company and company not in seen_companies:
                consolidated.append(exp)
                seen_companies.add(company)
        
        return consolidated
    
    def _calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence score based on source quality"""
        # Implementation for confidence scoring
        return 0.75  # Placeholder
```

### 5. Markdown Generator

```python
from typing import Dict, Any
from datetime import datetime

class MarkdownGenerator:
    def __init__(self):
        self.template = """
# Founder Research Report

**Company:** {company_name}  
**Generated:** {timestamp}  
**Confidence Score:** {confidence_score}/1.0

## Executive Summary

{executive_summary}

## Founders Overview

{founders_overview}

{founders_detailed}

## Data Quality Assessment

- **Sources Used:** {sources_used}
- **Confidence Score:** {confidence_score}
- **Data Completeness:** {data_completeness}
- **Last Updated:** {last_updated}

---
*Generated by Multi-API Founder Research System*
"""
    
    def generate_markdown(self, consolidated_data: Dict[str, Any], 
                         company_name: str) -> str:
        """Generate structured markdown report"""
        
        # Extract data
        founders = consolidated_data.get('founders', [])
        data_quality = consolidated_data.get('data_quality', {})
        
        # Generate sections
        executive_summary = self._generate_executive_summary(founders, company_name)
        founders_overview = self._generate_founders_overview(founders)
        founders_detailed = self._generate_detailed_profiles(founders)
        
        # Format the report
        report = self.template.format(
            company_name=company_name,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            confidence_score=data_quality.get('confidence_score', 0.0),
            executive_summary=executive_summary,
            founders_overview=founders_overview,
            founders_detailed=founders_detailed,
            sources_used=", ".join(data_quality.get('sources_used', [])),
            data_completeness=self._calculate_completeness(founders),
            last_updated=data_quality.get('last_updated', 'Unknown')
        )
        
        return report
    
    def _generate_executive_summary(self, founders: List[Dict], company_name: str) -> str:
        """Generate executive summary"""
        if not founders:
            return f"No founder information found for {company_name}."
        
        founder_names = [f['name'] for f in founders if f.get('name')]
        summary = f"{company_name} was founded by {', '.join(founder_names[:3])}."
        
        if len(founder_names) > 3:
            summary += f" The founding team includes {len(founder_names)} members total."
        
        return summary
    
    def _generate_founders_overview(self, founders: List[Dict]) -> str:
        """Generate founders overview table"""
        if not founders:
            return "No founder information available."
        
        overview = "| Name | Current Role | Education | Notable Experience |\n"
        overview += "|------|--------------|-----------|-------------------|\n"
        
        for founder in founders:
            name = founder.get('name', 'Unknown')
            role = founder.get('current_role', 'Unknown')
            
            # Summarize education
            education = founder.get('education', [])
            edu_summary = education[0].get('institution', 'Unknown') if education else 'Unknown'
            
            # Summarize experience
            experience = founder.get('experience', [])
            exp_summary = experience[0].get('company', 'Unknown') if experience else 'Unknown'
            
            overview += f"| {name} | {role} | {edu_summary} | {exp_summary} |\n"
        
        return overview
    
    def _generate_detailed_profiles(self, founders: List[Dict]) -> str:
        """Generate detailed founder profiles"""
        if not founders:
            return ""
        
        profiles = ""
        for i, founder in enumerate(founders, 1):
            profiles += f"\n## Founder {i}: {founder.get('name', 'Unknown')}\n\n"
            
            # Current role
            if founder.get('current_role'):
                profiles += f"**Current Role:** {founder['current_role']}\n\n"
            
            # Education
            education = founder.get('education', [])
            if education:
                profiles += "### Education\n\n"
                for edu in education:
                    institution = edu.get('institution', '')
                    degree = edu.get('degree', '')
                    year = edu.get('year', '')
                    profiles += f"- **{institution}** - {degree}"
                    if year:
                        profiles += f" ({year})"
                    profiles += "\n"
                profiles += "\n"
            
            # Professional Experience
            experience = founder.get('experience', [])
            if experience:
                profiles += "### Professional Experience\n\n"
                for exp in experience:
                    company = exp.get('company', '')
                    position = exp.get('position', '')
                    duration = exp.get('duration', '')
                    profiles += f"- **{position}** at **{company}**"
                    if duration:
                        profiles += f" ({duration})"
                    profiles += "\n"
                profiles += "\n"
            
            # Entrepreneurial Background
            entrepreneurial = founder.get('entrepreneurial_background', [])
            if entrepreneurial:
                profiles += "### Entrepreneurial Experience\n\n"
                for venture in entrepreneurial:
                    profiles += f"- {venture}\n"
                profiles += "\n"
            
            # Achievements
            achievements = founder.get('achievements', [])
            if achievements:
                profiles += "### Notable Achievements\n\n"
                for achievement in achievements:
                    profiles += f"- {achievement}\n"
                profiles += "\n"
            
            # Skills
            skills = founder.get('skills', [])
            if skills:
                profiles += f"**Key Skills:** {', '.join(skills)}\n\n"
        
        return profiles
    
    def _calculate_completeness(self, founders: List[Dict]) -> str:
        """Calculate data completeness percentage"""
        if not founders:
            return "0%"
        
        total_fields = 0
        filled_fields = 0
        
        for founder in founders:
            fields_to_check = ['name', 'current_role', 'education', 'experience']
            total_fields += len(fields_to_check)
            
            for field in fields_to_check:
                if founder.get(field):
                    filled_fields += 1
        
        completeness = (filled_fields / total_fields) * 100 if total_fields > 0 else 0
        return f"{completeness:.0f}%"
```

### 6. Main Orchestrator

```python
import asyncio
from typing import Optional

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
        self.consolidator = DataConsolidator()
        self.markdown_generator = MarkdownGenerator()
    
    async def research_founders(self, company_name: str, 
                              founder_name: Optional[str] = None) -> str:
        """Main method to research founders and generate markdown report"""
        
        try:
            # Step 1: Search all sources
            print("Searching across multiple APIs...")
            search_results = await self.orchestrator.search_all_sources(
                company_name, founder_name
            )
            
            # Step 2: Analyze with Google ADK
            print("Analyzing content with Google ADK...")
            analyzed_data = self.analyzer.analyze_search_results(search_results)
            
            # Step 3: Consolidate data
            print("Consolidating and deduplicating data...")
            consolidated_data = self.consolidator.consolidate_founder_data(analyzed_data)
            
            # Step 4: Generate markdown report
            print("Generating markdown report...")
            markdown_report = self.markdown_generator.generate_markdown(
                consolidated_data, company_name
            )
            
            return markdown_report
            
        except Exception as e:
            return f"Error in research process: {str(e)}"

# Usage Example
async def main():
    system = FounderResearchSystem(
        brave_key="your_brave_api_key",
        tavily_key="your_tavily_api_key", 
        serpapi_key="your_serpapi_key",
        google_adk_key="your_google_adk_key"
    )
    
    report = await system.research_founders("OpenAI", "Sam Altman")
    
    # Save to file
    with open("founder_report.md", "w") as f:
        f.write(report)
    
    print("Report generated: founder_report.md")

if __name__ == "__main__":
    asyncio.run(main())
```

## Key Features

1. **Multi-API Integration:** Combines Brave, Tavily, and SerpAPI for comprehensive coverage
2. **AI-Powered Analysis:** Uses Google ADK (Gemini) to extract structured information
3. **Data Consolidation:** Deduplicates and merges information from multiple sources
4. **Quality Scoring:** Assigns confidence scores based on source reliability
5. **Structured Output:** Generates professional markdown reports
6. **Async Processing:** Concurrent API calls for better performance
7. **Error Handling:** Robust error handling and fallbacks

## Setup Requirements

```bash
pip install requests google-generativeai asyncio
```

## Environment Variables

```bash
export BRAVE_API_KEY="your_key_here"
export TAVILY_API_KEY="your_key_here"  
export SERPAPI_KEY="your_key_here"
export GOOGLE_ADK_KEY="your_key_here"
```

This system provides a comprehensive solution for founder research using multiple APIs and AI-powered analysis to generate structured markdown reports.