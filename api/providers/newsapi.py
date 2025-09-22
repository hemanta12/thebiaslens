"""
NewsAPI provider for fetching news articles.
"""
import requests
from typing import Dict, List, Optional
from fastapi import HTTPException

from config import settings


def search_news(q: str, page: int, page_size: int) -> Dict:
    """
    Search for news articles using NewsAPI.
    
    Args:
        q: Search query
        page: Page number (1-based)
        page_size: Number of articles per page
        
    Returns:
        Dictionary containing articles and pagination info
        
    Raises:
        HTTPException: If the provider is down or returns an error
    """
    if not settings.news_api_key:
        raise HTTPException(
            status_code=500, 
            detail="NEWS_API_KEY not configured"
        )
    
    # Prepare request parameters
    params = {
        "q": q,
        "page": page,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": settings.news_api_key
    }
    
    try:
        # Make request to NewsAPI
        response = requests.get(
            f"{settings.news_api_base_url}/everything",
            params=params,
            timeout=10
        )
        
        # Handle HTTP errors
        if response.status_code != 200:
            if response.status_code >= 500:
                raise HTTPException(
                    status_code=502,
                    detail="News provider is currently unavailable"
                )
            else:
                # For client errors (4xx), return empty results
                return {"items": [], "nextCursor": None}
                
        data = response.json()
        
        # Handle API-level errors
        if data.get("status") != "ok":
            if data.get("code") in ["rateLimited", "maximumResultsReached"]:
                return {"items": [], "nextCursor": None}
            else:
                raise HTTPException(
                    status_code=502,
                    detail="News provider returned an error"
                )
        
        # Extract articles
        articles = data.get("articles", [])
        total_results = data.get("totalResults", 0)
        
        # Map articles to our format
        items = []
        for article in articles:
            items.append({
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name") or "Unknown",
                "publishedAt": article.get("publishedAt", ""),
                "title": article.get("title") or ""
            })
        
        # Determine if there are more pages
        # NewsAPI uses 1-based pagination
        current_page_items = len(items)
        has_more = (page * page_size) < total_results and current_page_items == page_size
        next_cursor = page + 1 if has_more else None
        
        return {
            "items": items,
            "nextCursor": next_cursor
        }
        
    except requests.exceptions.RequestException:
        # Network or connection errors
        raise HTTPException(
            status_code=502,
            detail="News provider is currently unavailable"
        )
    except Exception:
        # Any other unexpected errors
        return {"items": [], "nextCursor": None}