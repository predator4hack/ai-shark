"""
Pytest configuration and fixtures for the VC Document Analyzer tests.
"""

import pytest


def pytest_addoption(parser):
    """Add command line option for integration tests."""
    parser.addoption(
        "--integration", 
        action="store_true", 
        default=False, 
        help="run integration tests"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --integration flag is provided."""
    if config.getoption("--integration"):
        return
    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)