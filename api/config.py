from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    news_provider: str = "newsapi"
    news_api_base_url: str = "https://newsapi.org/v2"
    news_api_key: Optional[str] = None
    default_page_size: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
settings = Settings()