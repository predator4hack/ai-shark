import google.generativeai as genai
from typing import Dict, List, Any, Optional
import json
import os
from dotenv import load_dotenv
import re
import time # Added for retry_with_backoff
import functools # Added for retry_with_backoff

load_dotenv()

# --- Retry Decorator (Copied from test_linkedin.py) ---
def retry_with_backoff(retries=3, backoff_factor=2.0):
    """A decorator for retrying a function with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Call to {func.__name__} attempt {attempt + 1}/{retries} failed: {e}")
                    if attempt < retries - 1:
                        sleep_time = backoff_factor ** attempt
                        print(f"Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                    else:
                        print(f"Max retries reached for {func.__name__}.")
                        raise # Re-raise the exception after the last attempt
            raise RuntimeError(f"Function {func.__name__} failed after {retries} retries")
        return wrapper
    return decorator


class FounderAnalysisAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))

    def _extract_json_from_response(self, text: str) -> Optional[str]:
        """Extracts a JSON object from a string, even with markdown fences."""
        match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1)
        match = re.search(r"{\s*\".*\"\s*:.*}", text, re.DOTALL)
        if match:
            return match.group(0)
        return None

    @retry_with_backoff(retries=3, backoff_factor=2.0) # Applied decorator here
    def analyze_search_results(self, search_results: List[Dict], person_name: str, role: str) -> Dict[str, Any]:
        """Use Google ADK to analyze and extract information about a person."""
        print(f"--- FounderAnalysisAgent: Received search_results ---")
        print(search_results) # Log received search_results

        content_for_analysis = self._prepare_content(search_results)

        print(f"--- FounderAnalysisAgent: Prepared content_for_analysis (length: {len(content_for_analysis)}) ---")
        print(content_for_analysis[:500] + "..." if len(content_for_analysis) > 500 else content_for_analysis) # Log prepared content

        if not content_for_analysis.strip():
            print("No content available for analysis after preparation.")
            return {}

        analysis_prompt = f"""        Analyze the following search results and extract detailed information about {person_name}, the {role}.
        Your response MUST be a single, valid JSON object and nothing else. 
        Do not include any explanatory text or markdown formatting like ```json.

        The JSON object should have the following keys, with the values being lists of strings:
        "person_and_roles", "education", "professional_experience", "entrepreneurial_experience", 
        "achievements", "skills", "personal_background".

        Content to analyze:
        ---
        {content_for_analysis}
        ---
        """

        try:
            response = self.model.generate_content(analysis_prompt)

            print(f"--- FounderAnalysisAgent: Raw model response ---")
            print(response.text) # Log raw model response

            json_str = self._extract_json_from_response(response.text)
            if not json_str:
                raise ValueError("No valid JSON object found in the model's response.")

            extracted_data = json.loads(json_str)
            print(f"--- FounderAnalysisAgent: Extracted JSON data ---")
            print(extracted_data) # Log extracted JSON
            return extracted_data
        except (json.JSONDecodeError, ValueError, Exception) as e:
            print(f"Analysis failed: {e}")
            return {}

    def _prepare_content(self, search_results: List[Dict]) -> str:
        """Prepare search results for analysis"""
        content = ""
        for source_data in search_results:
            source = source_data.get('source', 'unknown')
            results = source_data.get('results', [])

            content += f"\n--- {source.upper()} RESULTS ---\n"
            for result in results[:5]:
                title = result.get('title', result.get('name', ''))
                description = result.get('description', result.get('snippet', ''))
                url = result.get('url', result.get('link', ''))

                content += f"Title: {title}\n"
                content += f"Description: {description}\n"
                content += f"URL: {url}\n\n"

        return content[:15000]