from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Storage Settings
    use_gcs: bool = False
    gcs_bucket_name: str = "ai-shark-outputs"
    output_dir: str = "outputs"

    # LLM Settings (inherited from existing config)
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # File Upload Limits
    max_file_size_mb: int = 100

    # Job Management
    job_cleanup_hours: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
