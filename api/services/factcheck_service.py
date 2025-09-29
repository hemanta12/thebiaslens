"""Fact-check service with multi-pass search strategy and similarity scoring."""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from config import settings
from providers.factcheck_google import fetch_claims
from schemas import FactCheckItem, FactCheckResult
from .factcheck_query import build_queries
from .similarity import similarity_calculator

logger = logging.getLogger(__name__)
class FactCheckCache:
    def __init__(self):
        self._cache: Dict[str, Tuple[FactCheckResult, datetime]] = {}
    
    def get(self, key: str) -> Optional[FactCheckResult]:
        """Get cached result if not expired."""
        if key not in self._cache:
            return None
        
        result, timestamp = self._cache[key]
        ttl_minutes = settings.fact_check_cache_ttl_min
        if datetime.now() - timestamp > timedelta(minutes=ttl_minutes):
            del self._cache[key]
            return None
        
        return result
    
    def set(self, key: str, result: FactCheckResult) -> None:
        self._cache[key] = (result, datetime.now())
    
    def clear_expired(self) -> None:
        now = datetime.now()
        ttl_minutes = settings.fact_check_cache_ttl_min
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp > timedelta(minutes=ttl_minutes)
        ]
        for key in expired_keys:
            del self._cache[key]


_cache = FactCheckCache()


def _make_cache_key(headline: str, source_domain: Optional[str]) -> str:
    key_text = f"{headline}|{source_domain or ''}"
    return hashlib.sha1(key_text.encode()).hexdigest()


def _deduplicate_items(items: List[FactCheckItem]) -> List[FactCheckItem]:
    seen = set()
    unique_items = []
    
    for item in items:
        key = (item.claim.lower().strip(), str(item.url) if item.url else "")
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    
    return unique_items


async def find_best_factchecks(
    headline: str,
    source_domain: Optional[str] = None,
    summary: Optional[str] = None,
    max_items: int = 3,
    language: str = "en"
) -> FactCheckResult:
    """
    Find fact-checks using multi-pass search strategy.
    
    Searches with different query strategies and returns up to max_items unique results.
    Uses in-memory LRU cache with configurable TTL.
    
    Args:
        headline: Article headline to fact-check
        source_domain: Optional source domain for additional context
        max_items: Maximum number of items to return (default: 3)
        language: Language code (default: "en")
    
    Returns:
        FactCheckResult with found items or empty result
    """
    if not settings.fact_check_enabled or not settings.google_factcheck_api_key:
        return FactCheckResult(status="none", items=[])
    
    cache_key = _make_cache_key(headline, source_domain)
    cached_result = _cache.get(cache_key)
    if cached_result:
        return cached_result
    
    _cache.clear_expired()
    
    queries = build_queries(headline, source_domain, summary)
    
    logger.info(f"Generated {len(queries)} fact-check queries for headline: '{headline[:100]}...'")
    for i, query_info in enumerate(queries, 1):
        logger.info(f"Query {i}: [{query_info.get('reason', 'unknown')}] '{query_info.get('q', '')}'")
    
    collected_items: List[FactCheckItem] = []
    api_key = settings.google_factcheck_api_key
    for i, query_info in enumerate(queries, 1):
        query = query_info.get("q", "")
        reason = query_info.get("reason", "unknown")
        
        if not query.strip():
            logger.warning(f"Skipping empty query {i}")
            continue
        
        logger.info(f"Executing query {i}/{len(queries)}: [{reason}] '{query}'")
        
        try:
            items = await fetch_claims(
                query=query,
                api_key=api_key,
                language=language,
                page_size=5  # Get a few more to allow for deduplication
            )
            
            logger.info(f"Query {i} returned {len(items)} items")
            
            for item in items:
                item.matchReason = reason
                
                similarity_data = similarity_calculator.calculate_similarity(
                    headline=headline,
                    summary=summary or "",
                    claim=item.claim
                )
                
                item.similarityPercentage = similarity_data["overall_score"]
                
            collected_items.extend(items)
            collected_items = _deduplicate_items(collected_items)
            
            if len(collected_items) >= max_items:
                logger.info(f"Early stopping: collected {len(collected_items)} items after {i} queries")
                break
                
        except Exception as e:
            logger.error(f"Query {i} [{reason}] failed: {str(e)}")
            continue
    
    collected_items.sort(key=lambda x: x.similarityPercentage or 0, reverse=True)
    final_items = collected_items[:max_items]
    
    logger.info(f"Fact-check search completed: {len(final_items)} final items from {len(collected_items)} total collected")
    for i, item in enumerate(final_items, 1):
        logger.info(f"Result {i}: {item.similarityPercentage:.1f}% similarity - '{item.claim[:100]}...'")
    
    result = FactCheckResult(
        status="found" if final_items else "none",
        items=final_items
    )
    
    _cache.set(cache_key, result)
    
    return result