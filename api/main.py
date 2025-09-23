# TODO: Upstash Redis cache later for 48h TTL once analysis exists.

# News API integration with configurable providers
import re
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from urllib.parse import urlparse

# Load settings at module import
from config import settings
from providers.newsapi import search_news
from data.mock_results import MOCK_ARTICLES
from schemas import ExtractResult
from services.extract import extract_article
from utils.normalize import canonicalize_url, infer_source_from_url

app = FastAPI()

# CORS configuration
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
     "https://thebiaslens.vercel.app",
]

# Add regex pattern for Vercel preview URLs
allowed_origin_regex = r"https://.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "api",
        "version": "0.0.1"
    }

@app.get("/search")
def search(
    q: str,
    cursor: int = Query(1, ge=1),
    pageSize: int = Query(default=None)
):
    """
    Search for news articles using the configured provider or mock data.
    
    Args:
        q: Search query (required)
        cursor: Page number (1-based, default: 1)
        pageSize: Number of articles per page (default: from settings)
    """
    # Return empty result if query is too short
    if len(q.strip()) < 2:
        return {"items": [], "nextCursor": None}
    
    # Use default page size from settings if not provided
    if pageSize is None:
        pageSize = settings.default_page_size
    
    # If NEWS_API_KEY is present, use NewsAPI
    if settings.news_api_key:
        # TODO: add provider switch if we add GNews later
        return search_news(q, page=cursor, page_size=pageSize)
    else:
        # Fallback to mock data (unchanged from original implementation)
        query_lower = q.lower()
        filtered_articles = [
            article for article in MOCK_ARTICLES
            if query_lower in article["title"].lower() or query_lower in article["source"].lower()
        ]
        
        return {"items": filtered_articles, "nextCursor": None}


@app.get("/extract", response_model=ExtractResult)
async def extract(url: str = Query(..., description="URL of the article to extract")):
    """
    Extract article content from a given URL.
    
    Args:
        url: The URL of the article to extract (required)
        
    Returns:
        ExtractResult with article content and metadata
    """
    # Basic URL validation
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Canonicalize URL
    canonical_url = canonicalize_url(url)
    
    # Extract article content
    headline, body, word_count, status, author, published_at, paywalled = await extract_article(canonical_url)
    
    # Infer source from URL
    source = infer_source_from_url(canonical_url)
    
    # Build and return ExtractResult
    result = ExtractResult(
        url=canonical_url,
        headline=headline,
        source=source,
        publishedAt=published_at,
        author=author,
        # Pydantic model may not have author; we include only if present in schema
        body=body,
        wordCount=word_count,
        extractStatus=status,
        paywalled=paywalled,
    )
    
    return result
