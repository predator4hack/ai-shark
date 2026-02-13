"""
Pytest configuration and shared fixtures for AI-Shark tests
"""
import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test fixtures directory"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_pdf_path(test_data_dir):
    """Return path to sample PDF file"""
    pdf_path = test_data_dir / "sample_deck.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Sample PDF not found at {pdf_path}")
    return pdf_path


@pytest.fixture(scope="module")
def api_client():
    """Create FastAPI test client"""
    # Import here to avoid circular dependencies
    from src.api.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_env(tmp_path, monkeypatch):
    """Setup test environment variables"""
    # Use temporary directory for outputs during testing
    monkeypatch.setenv("USE_GCS", "false")
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "outputs"))
    monkeypatch.setenv("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", "test-api-key"))
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Create outputs directory
    (tmp_path / "outputs").mkdir(exist_ok=True)

    return tmp_path
