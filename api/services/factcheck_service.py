import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from config import settings
from providers.factcheck_google import fetch_claims
from schemas import FactCheckItem, FactCheckResult
from .factcheck_query import build_queries
from .claims import claim_miner
from .textutil import text_util
from .factcheck_filters import passes_gates
from .factcheck_score import score_item

DEFAULT_MAX_AGE_MONTHS = 18
logger = logging.getLogger(__name__)

class FactCheckCache:
    def __init__(self):
        self._cache: Dict[str, Tuple[FactCheckResult, datetime]] = {}
    
    def get(self, key: str) -> Optional[FactCheckResult]:
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
        expired_keys = [k for k, (_, t) in self._cache.items() if now - t > timedelta(minutes=ttl_minutes)]
        for key in expired_keys:
            del self._cache[key]


_cache = FactCheckCache()


def _make_cache_key(headline: str, source_domain: Optional[str], max_age_months: int = DEFAULT_MAX_AGE_MONTHS) -> str:
    key_text = f"{headline}|{source_domain or ''}|{max_age_months}"
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


def _deduplicate_by_publisher(items: List[FactCheckItem]) -> List[FactCheckItem]:
    if not items:
        return items
    
    by_publisher: Dict[str, List[FactCheckItem]] = {}
    for item in items:
        publisher = item.source or "unknown"
        if publisher not in by_publisher:
            by_publisher[publisher] = []
        by_publisher[publisher].append(item)
    
    unique_items = []
    for publisher_items in by_publisher.values():
        best_item = max(publisher_items, key=lambda x: x.similarity or 0)
        unique_items.append(best_item)
    
    return unique_items


def _filter_by_recency(items: List[FactCheckItem], max_age_months: int = DEFAULT_MAX_AGE_MONTHS) -> List[FactCheckItem]:
    if max_age_months >= 9999:
        logger.info(f"No age limit (max_age_months={max_age_months})")
        return items
    
    cutoff_date = datetime.now() - timedelta(days=max_age_months * 30)
    logger.info(f"Recency filter: {max_age_months}m, cutoff={cutoff_date.date()}")
    
    filtered_items = []
    dropped_count = 0
    penalty_count = 0
    
    for item in items:
        if item.publishedAt is None:
            if item.similarity is not None:
                item.similarity = max(0.0, item.similarity - 0.05)
                penalty_count += 1
            filtered_items.append(item)
        else:
            item_date = item.publishedAt
            if item_date.tzinfo is not None:
                item_date = item_date.replace(tzinfo=None)
            
            if item_date >= cutoff_date:
                filtered_items.append(item)
            else:
                dropped_count += 1
    
    logger.info(f"Recency: {len(items)} → {len(filtered_items)} (dropped: {dropped_count})")
    return filtered_items


def _get_intelligent_recency_default(headline: str, max_age_months: int) -> int:
    if max_age_months != DEFAULT_MAX_AGE_MONTHS:
        return max_age_months
    
    headline_lower = headline.lower()
    time_sensitive = ['court', 'scotus', 'election', 'vote', 'covid', 'vaccine', 'stock', 'market']
    
    if any(term in headline_lower for term in time_sensitive):
        return 12
    return 18


async def find_best_factchecks(
    headline: str,
    source_domain: Optional[str] = None,
    summary: Optional[str] = None,
    max_items: int = 3,
    max_age_months: int = DEFAULT_MAX_AGE_MONTHS,
    language: str = "en"
) -> FactCheckResult:
    if not settings.fact_check_enabled or not settings.google_factcheck_api_key:
        return FactCheckResult(status="none", items=[])

    # Apply intelligent recency default
    effective_max_age = _get_intelligent_recency_default(headline, max_age_months)
    
    cache_key = _make_cache_key(headline, source_domain, effective_max_age)
    cached_result = _cache.get(cache_key)
    if cached_result:
        return cached_result

    _cache.clear_expired()
    
    queries = build_queries(headline, source_domain, summary)
    logger.info(f"Generated {len(queries)} queries for: '{headline[:80]}...'")
    
    collected_items: List[FactCheckItem] = []
    api_key = settings.google_factcheck_api_key
    
    core_claims = claim_miner.extract_core_claims(headline, summary, max_claims=3)
    primary_claim = core_claims[0] if core_claims else headline
    claim_type = claim_miner.classify_claim(primary_claim)
    claim_targets_dict = claim_miner.extract_targets(primary_claim, claim_type)
    
    all_targets = set()
    for target_set in claim_targets_dict.values():
        all_targets.update(target_set)
    
    logger.info(f"Claim type: {claim_type}, targets: {len(all_targets)}")

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
                page_size=5
            )
            logger.info(f"Query {i} returned {len(items)} items")
            scored_items = []
            for item in items:
                item.matchReason = reason
                query_text = query_info.get("q", "")
                
                score = score_item(
                    query=query_text,
                    claim_text=item.claim,
                    source_domain=source_domain,
                    published_at=item.publishedAt,
                    claim_type=claim_type,
                    targets=claim_targets_dict,
                    reason=reason
                )
                
                if score < 0:
                    logger.info(f"Gated out: '{item.claim[:60]}...'")
                    continue
                
                item.similarity = round(score, 3)
                scored_items.append(item)
            
            collected_items.extend(scored_items)
            collected_items = _deduplicate_items(collected_items)
            
            if len(collected_items) >= 3:
                avg_score = sum(item.similarity or 0 for item in collected_items) / len(collected_items)
                if avg_score >= 0.55:
                    logger.info(f"Early stop: {len(collected_items)} items, avg={avg_score:.3f}")
                    break
        except Exception as e:
            logger.error(f"Query {i} [{reason}] failed: {str(e)}")
            continue
    
    if not collected_items:
        logger.info("No items passed gates")
        result = FactCheckResult(status="none", items=[])
        _cache.set(cache_key, result)
        return result
    
    collected_items = _deduplicate_items(collected_items)
    collected_items = _deduplicate_by_publisher(collected_items)
    collected_items = _filter_by_recency(collected_items, effective_max_age)
    collected_items.sort(key=lambda x: -(x.similarity or 0))
    final_items = collected_items[:max_items]
    
    logger.info(f"Final: {len(final_items)} items from {len(collected_items)} total")
    for i, item in enumerate(final_items, 1):
        pct = (item.similarity or 0) * 100
        logger.info(f"{i}. {pct:.1f}% - [{item.matchReason}] '{item.claim[:60]}...'")
    
    if not final_items:
        result = FactCheckResult(status="none", items=[])
    else:
        result = FactCheckResult(status="found", items=final_items)
    
    _cache.set(cache_key, result)
    return result