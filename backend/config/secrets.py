"""
Secret management for Cloud Run with JSON bundle support and env var fallback.

Priority:
1. JSON secrets bundle: /secrets/secrets.json (Cloud Run mounted volume)
2. Environment variable (local development)
"""

import json
import os
from pathlib import Path
from functools import lru_cache
from typing import Dict

from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# Path for Cloud Run mounted JSON secrets
SECRETS_BUNDLE_PATH = Path("/secrets/secrets.json")


@lru_cache(maxsize=1)
def _load_secrets_bundle() -> Dict[str, str]:
    """Load and cache the JSON secrets bundle."""
    if SECRETS_BUNDLE_PATH.exists():
        try:
            content = SECRETS_BUNDLE_PATH.read_text().strip()
            if content:
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def get_secret(name: str, default: str = "") -> str:
    """
    Get a secret value.

    Priority:
    1. JSON secrets bundle: /secrets/secrets.json
    2. Environment variable
    3. Default value

    Args:
        name: Secret name (e.g., "GOOGLE_API_KEY")
        default: Default value if not found

    Returns:
        Secret value
    """
    # 1. JSON secrets bundle (Cloud Run)
    secrets_bundle = _load_secrets_bundle()
    if name in secrets_bundle:
        return secrets_bundle[name]

    # 2. Environment variable fallback (local development)
    return os.getenv(name, default)


def get_google_api_key() -> str:
    """Get Google API key."""
    return get_secret("GOOGLE_API_KEY")


def get_groq_api_key() -> str:
    """Get Groq API key."""
    return get_secret("GROQ_API_KEY")


def clear_secrets_cache() -> None:
    """Clear the cached secrets bundle."""
    _load_secrets_bundle.cache_clear()
