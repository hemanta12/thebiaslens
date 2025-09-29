import os
from pydantic_settings import BaseSettings
from typing import Optional


def bool_env(key: str, default: bool = False) -> bool:
    """Convert environment variable to boolean."""
    value = os.getenv(key, "").lower()
    return value in ("true", "1", "yes", "on") if value else default


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    news_provider: str = "newsapi"
    news_api_base_url: str = "https://newsapi.org/v2"
    news_api_key: Optional[str] = None
    default_page_size: int = 10
    
    # Fact-check settings
    fact_check_enabled: bool = bool_env("FACT_CHECK_ENABLED", default=True)
    google_factcheck_api_key: Optional[str] = os.getenv("GOOGLE_FACTCHECK_API_KEY")
    fact_check_cache_ttl_min: int = int(os.getenv("FACT_CHECK_CACHE_TTL_MIN", "360"))
    factcheck_api_base: str = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
settings = Settings()