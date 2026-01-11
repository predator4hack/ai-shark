"""
Secret management for Cloud Run mounted secrets with env var fallback.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables early to ensure they're available
# This is needed because this module may be imported before settings.py calls load_dotenv()
load_dotenv()


def get_secret(name: str, default: str = "") -> str:
    """
    Get a secret value with Cloud Run mounted secret support.

    Priority:
    1. Mounted secret file (Cloud Run): /secrets/{name}
    2. Environment variable: {NAME} (uppercase)
    3. Default value

    Args:
        name: Secret name (e.g., "google-api-key")
        default: Default value if not found

    Returns:
        Secret value
    """
    # Try mounted secret first (Cloud Run pattern)
    secret_path = Path(f"/secrets/{name}")
    if secret_path.exists():
        return secret_path.read_text().strip()

    # Fallback to environment variable (convert to uppercase, replace - with _)
    env_name = name.upper().replace("-", "_")
    return os.getenv(env_name, default)


def get_google_api_key() -> str:
    """Get Google API key from mounted secret or env var."""
    return get_secret("google-api-key")


def get_groq_api_key() -> str:
    """Get Groq API key from mounted secret or env var."""
    return get_secret("groq-api-key")
