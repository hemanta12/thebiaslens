import asyncio
import aiohttp
import re
from datetime import datetime
from typing import List, Optional
from urllib.parse import quote_plus

from schemas import FactCheckItem
from config import settings


# Normalize verdict labels from various fact-checking organizations
VERDICT_MAP = {
    "true": "True",
    "mostly true": "Mostly True",
    "half true": "Mixed/Needs Context",
    "mixture": "Mixed/Needs Context",
    "missing context": "Mixed/Needs Context",
    "misleading": "Misleading",
    "false": "False",
    "mostly false": "False",
    "unverified": "Unverified/Unsupported",
    "unsupported": "Unverified/Unsupported",
    "opinion": "Opinion/Analysis",
    "analysis": "Opinion/Analysis",
    "satire": "Satire/Parody",
    "parody": "Satire/Parody",
}


def normalize_verdict(text: Optional[str]) -> Optional[str]:
    if not text:
        return "Unverified/Unsupported"
    
    # Lowercase and strip punctuation before lookup
    normalized = re.sub(r'[^\w\s]', '', text.lower().strip())
    return VERDICT_MAP.get(normalized, "Unverified/Unsupported")


def parse_published_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse publication date from ISO string if available."""
    if not date_str:
        return None
    
    try:
        # Handle ISO format dates
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Handle date-only format
            return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


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
                    
                    # Extract and parse publication date from claimDate or reviewDate
                    published_at = None
                    date_str = claim.get("claimDate") or review.get("datePublished")
                    if date_str:
                        published_at = parse_published_date(date_str)
                    
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