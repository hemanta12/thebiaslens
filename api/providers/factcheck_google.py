"""Google Fact Check Tools API integration."""

import asyncio
import aiohttp
from typing import List, Optional
from urllib.parse import quote_plus

from schemas import FactCheckItem
from config import settings


# Normalize verdict labels from various fact-checking organizations
NORMALIZED_VERDICT_MAP = {
    "true": "True",
    "mostly true": "True", 
    "false": "False",
    "mostly false": "False",
    "mixture": "Mixed",
    "half true": "Mixed",
    "unverified": "Unverified",
    "unknown": "Unknown"
}


def normalize_verdict(text: Optional[str]) -> Optional[str]:
    """Normalize verdict text to standard labels."""
    if not text:
        return None
    
    normalized = text.lower().strip()
    return NORMALIZED_VERDICT_MAP.get(normalized, text.title())


async def fetch_claims(
    query: str,
    *,
    api_key: str,
    language: str = "en",
    page_size: int = 5,
    timeout_s: int = 4
) -> List[FactCheckItem]:
    """
    Fetch fact-check claims from Google Fact Check Tools API.
    
    Args:
        query: Search query for claims
        api_key: Google API key
        language: Language code (default: "en")
        page_size: Maximum number of results (default: 5)
        timeout_s: Request timeout in seconds (default: 4)
    
    Returns:
        List of FactCheckItem objects, empty on error
    """
    if not query.strip() or not api_key:
        return []
    
    url = settings.factcheck_api_base
    params = {
        "query": query,
        "languageCode": language,
        "pageSize": min(page_size, 10),  # API limit
        "key": api_key
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_s)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                claims = data.get("claims", [])
                
                items = []
                for claim in claims:
                    claim_text = claim.get("text", "").strip()
                    if not claim_text:
                        continue
                    
                    # Get the best review (prefer first one)
                    reviews = claim.get("claimReview", [])
                    if not reviews:
                        continue
                    
                    review = reviews[0]  # Take first/best review
                    
                    # Extract review details
                    verdict = normalize_verdict(review.get("textualRating"))
                    snippet = review.get("textualRating", "").strip() or None
                    publisher = review.get("publisher", {})
                    source = publisher.get("name", "").strip() or None
                    review_url = review.get("url", "").strip() or None
                    
                    # Extract publication date from claimDate or reviewDate
                    published_at = None
                    if claim.get("claimDate"):
                        published_at = claim.get("claimDate")
                    elif review.get("datePublished"):
                        published_at = review.get("datePublished")
                    
                    items.append(FactCheckItem(
                        claim=claim_text,
                        verdict=verdict,
                        snippet=snippet,
                        source=source,
                        url=review_url,
                        publishedAt=published_at
                    ))
                
                return items
                
    except asyncio.TimeoutError:
        return []
    except Exception:
        # Log error in production, return empty for now
        return []