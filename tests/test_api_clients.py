import os
import pytest
from src.web_search.brave_search import BraveSearchClient
from src.web_search.tavily_search import TavilySearchClient
from src.web_search.serp_search import SerpAPIClient

# --- Fixtures for API Keys ---
@pytest.fixture(scope="module")
def brave_api_key():
    key = os.getenv("BRAVE_API_KEY")
    if not key:
        pytest.skip("BRAVE_API_KEY not set for integration tests")
    return key

@pytest.fixture(scope="module")
def tavily_api_key():
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        pytest.skip("TAVILY_API_KEY not set for integration tests")
    return key

@pytest.fixture(scope="module")
def serp_api_key():
    key = os.getenv("SERP_API_KEY")
    if not key:
        pytest.skip("SERP_API_KEY not set for integration tests")
    return key

# --- Test Cases for Brave Search Client ---
@pytest.mark.integration
class TestBraveSearchClient:
    def test_search_person_info(self, brave_api_key):
        client = BraveSearchClient(brave_api_key)
        # Use a well-known public figure for reliable results
        results = client.search_person_info(
            company_name="Microsoft",
            person_name="Satya Nadella",
            role="CEO"
        )
        assert "source" in results
        assert results["source"] == "brave"
        assert "results" in results
        assert isinstance(results["results"], list)
        assert len(results["results"]) > 0, "Brave search returned no results"
        # Optionally, check for expected fields in a result
        assert all("title" in r or "description" in r for r in results["results"])

# --- Test Cases for Tavily Search Client ---
@pytest.mark.integration
class TestTavilySearchClient:
    def test_search_person_info(self, tavily_api_key):
        client = TavilySearchClient(tavily_api_key)
        results = client.search_person_info(
            company_name="Microsoft",
            person_name="Satya Nadella",
            role="CEO"
        )
        assert "source" in results
        assert results["source"] == "tavily"
        assert "results" in results
        assert isinstance(results["results"], list)
        assert len(results["results"]) > 0, "Tavily search returned no results"
        assert all("title" in r or "content" in r for r in results["results"])

# --- Test Cases for SerpAPI Client ---
@pytest.mark.integration
class TestSerpAPIClient:
    def test_search_person_info(self, serp_api_key):
        client = SerpAPIClient(serp_api_key)
        results = client.search_person_info(
            company_name="Microsoft",
            person_name="Satya Nadella",
            role="CEO"
        )
        assert "source" in results
        assert results["source"] == "serpapi"
        assert "results" in results
        assert isinstance(results["results"], list)
        assert len(results["results"]) > 0, "SerpAPI search returned no results"
        assert all("title" in r or "snippet" in r for r in results["results"])
