import httpx
import trafilatura
from typing import Tuple, Optional, Dict, Any
import time
from datetime import datetime
from html import unescape
import re
import json

from utils.normalize import canonicalize_url
from urllib.parse import urljoin

# In-memory cache for 60 seconds
_cache: Dict[str, Dict[str, Any]] = {}
_cache_ttl = 60  # seconds


def _is_cache_valid(timestamp: float) -> bool:
    """Check if cache entry is still valid (within TTL)."""
    return time.time() - timestamp < _cache_ttl


def _get_from_cache(canonical_url: str) -> Optional[Tuple[Optional[str], Optional[str], int, str, Optional[str], Optional[str], bool, Optional[str]]]:
    """Get extraction result from cache if valid."""
    if canonical_url in _cache:
        entry = _cache[canonical_url]
        if _is_cache_valid(entry['timestamp']):
            return (
                entry['headline'],
                entry['body'],
                entry['word_count'],
                entry['status'],
                entry.get('author'),
                entry.get('published_at'),
                entry.get('paywalled', False),
                entry.get('canonical_from_meta'),
            )
        else:
            # Remove expired entry
            del _cache[canonical_url]
    return None


def _set_cache(
    canonical_url: str,
    headline: Optional[str],
    body: Optional[str],
    word_count: int,
    status: str,
    author: Optional[str],
    published_at: Optional[str],
    paywalled: bool,
    canonical_from_meta: Optional[str],
) -> None:
    """Store extraction result in cache."""
    _cache[canonical_url] = {
        'headline': headline,
        'body': body,
        'word_count': word_count,
        'status': status,
        'timestamp': time.time(),
        'author': author,
        'published_at': published_at,
        'paywalled': paywalled,
        'canonical_from_meta': canonical_from_meta,
    }


async def fetch_html(url: str) -> Optional[str]:
    """
    Fetch HTML content from URL using httpx with 10s timeout.
    
    Args:
        url: The URL to fetch
        
    Returns:
        HTML content string or None if fetch fails
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                # Use a modern desktop Chrome UA to avoid simplistic bot blocks and legacy-fallback pages
                'User-Agent': (
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/124.0.0.0 Safari/537.36'
                )
            }
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            return response.text
    except Exception:
        return None


def extract_text(html: str, url: str) -> Tuple[Optional[str], Optional[str], int]:
    """
    Extract text content from HTML using trafilatura.
    
    Args:
        html: HTML content string
        url: Original URL for context
        
    Returns:
        Tuple of (headline, body, word_count)
    """
    try:
        # Extract main content without metadata header for a cleaner preview
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            url=url,
            with_metadata=False,
            output_format='txt'
        )
        
        if not extracted:
            return None, None, 0
        
        # Try to extract headline separately using multiple approaches
        headline = None
        try:
            # Method 1: Try trafilatura metadata extraction (more robust, not fast)
            metadata = trafilatura.extract_metadata(html, url=url, fast=False)
            if metadata and metadata.title:
                headline = unescape(metadata.title.strip())
        except Exception:
            pass
        
        # Method 1.5: Check OpenGraph/Twitter meta titles
        if not headline:
            m_meta = re.search(
                r"<meta[^>]+(?:property|name)=[\'\"](?:og:title|twitter:title)[\'\"][^>]*content=[\'\"](.*?)[\'\"][^>]*>",
                html, re.IGNORECASE | re.DOTALL
            )
            if m_meta:
                meta_title = unescape(m_meta.group(1).strip())
                if meta_title:
                    headline = meta_title

        # Method 2: If no headline from metadata, try simple HTML parsing
        if not headline:
            try:
                # Try to find title in basic HTML tags
                # Look for h1 tags
                h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
                if h1_match:
                    potential_title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
                    if potential_title and len(potential_title) > 10:  # Reasonable title length
                        headline = unescape(potential_title)
                
                # If no h1, try title tag
                if not headline:
                    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
                    if title_match:
                        potential_title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                        if potential_title:
                            # Heuristic: many sites append sitename after a dash
                            # Prefer the part before the separator if it's long enough
                            for sep in [' - ', ' | ']:
                                if sep in potential_title and len(potential_title.split(sep)[0]) >= 15:
                                    potential_title = potential_title.split(sep)[0].strip()
                                    break
                            # Filter out obviously wrong titles like nav dumps
                            if len(potential_title) <= 180:
                                headline = unescape(potential_title)
                        
            except Exception:
                pass
        
        # Clean up the extracted text
        body = extracted.strip()
        word_count = len(body.split()) if body else 0
        
        return headline, body, word_count
        
    except Exception:
        return None, None, 0


def _normalize_author(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    v = unescape(str(val)).strip()
    if not v:
        return None
    # If it's a URL to a profile, try to convert the slug to title case
    if v.startswith('http'):  
        try:
            from urllib.parse import urlparse
            path = urlparse(v).path.strip('/')
            slug = path.split('/')[-1]
            if slug and len(slug) < 100:
                name = slug.replace('-', ' ').strip()
                return ' '.join(w.capitalize() for w in name.split())
        except Exception:
            pass
        return None  
    # Drop emails to just the local-part
    if '@' in v and ' ' not in v:
        v = v.split('@')[0].replace('.', ' ')
    # Collapse whitespace and title-case if it looks like a name
    v2 = ' '.join(v.split())
    if len(v2) <= 80:
        return v2
    return None


def _is_likely_paywalled(html: str, body: Optional[str], wc: int) -> bool:
    if body and wc >= 150:
        return False
    hay = (html or '').lower()
    clues = [
        'subscribe to continue', 'subscribe now', 'for subscribers', 'this content is for subscribers',
        'paywall', 'metered', 'sign in to read', 'sign in to continue', 'remaining free articles',
        'you have reached your limit', 'become a subscriber', 'support our journalism'
    ]
    return any(c in hay for c in clues)


async def extract_article(url: str) -> Tuple[Optional[str], Optional[str], int, str, Optional[str], Optional[str], bool, Optional[str]]:
    """
    Extract article content with caching.
    
    Args:
        url: The URL to extract content from
        
    Returns:
        Tuple of (headline, body, word_count, status)
        Status is one of: 'extracted', 'missing', 'error'
    """
    # Canonicalize URL for consistent caching
    canonical_url = canonicalize_url(url)
    
    # Check cache first
    cached_result = _get_from_cache(canonical_url)
    if cached_result:
        return cached_result
    
    # Fetch HTML
    html = await fetch_html(canonical_url)
    if html is None:
        result = (None, None, 0, 'error', None, None, False, None)
        _set_cache(canonical_url, *result)
        return result
    
    # Extract text content
    headline, body, word_count = extract_text(html, canonical_url)

    # Extract metadata for author and date if available
    author: Optional[str] = None
    published_at: Optional[str] = None
    try:
        md = trafilatura.extract_metadata(html, url=canonical_url, fast=False)
        if md is not None:
            if getattr(md, 'author', None):
                # md.author can be list or str; normalize to a comma-separated string
                a = md.author
                if isinstance(a, (list, tuple)):
                    norm = [x for x in (_normalize_author(x) for x in a) if x]
                    author = ", ".join(norm) if norm else None
                else:
                    author = _normalize_author(a)
            # Trafilatura date is typically ISO string 'YYYY-MM-DD'
            if getattr(md, 'date', None):
                published_at = str(md.date).strip()
    except Exception:
        pass

    # Fallback: try common meta tags for author and date
    try:
        def _find_meta_content(names: Tuple[str, ...]) -> Optional[str]:
           
            pattern = r"<meta[^>]+(?:name|property)=[\'\"](?:" + "|".join(map(re.escape, names)) + r")[\'\"][^>]*content=[\'\"](.*?)[\'\"][^>]*>"
            m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            return unescape(m.group(1).strip()) if m else None

        if author is None:
            raw_author = _find_meta_content((
                'author', 'article:author', 'byl', 'byline', 'by', 'dcterms.creator', 'dc.creator', 'parsely-author',
            ))
            author = _normalize_author(raw_author)

        if published_at is None:
            published_at = _find_meta_content((
                'article:published_time', 'og:pubdate', 'pubdate', 'date', 'dc.date', 'dc.date.issued', 'dcterms.date',
                'datePublished', 'article:modified_time', 'og:updated_time', 'parsely-pub-date',
            ))
    except Exception:
        pass

    # Fallback: parse JSON-LD blocks for author and date
    try:
        if author is None or published_at is None:
            for script_match in re.finditer(r'<script[^>]+type=[\'\"]application/ld\+json[\'\"][^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL):
                block = script_match.group(1).strip()
                try:
                    data = json.loads(block)
                except Exception:
                    continue

                def _get_first(items):
                    if isinstance(items, list):
                        return items[0] if items else None
                    return items

                # Some pages wrap in a list
                candidates = data if isinstance(data, list) else [data]
                for node in candidates:
                    if not isinstance(node, dict):
                        continue
                    # Use NewsArticle or generic creative work fields
                    if author is None and 'author' in node:
                        a = node['author']
                        a = _get_first(a)
                        if isinstance(a, dict) and 'name' in a:
                            author = str(a['name']).strip()
                        elif isinstance(a, str):
                            author = a.strip()
                    if published_at is None:
                        if 'datePublished' in node:
                            published_at = str(node['datePublished']).strip()
                        elif 'dateCreated' in node:
                            published_at = str(node['dateCreated']).strip()
                    # If both found, break
                    if author is not None and published_at is not None:
                        break
                if author is not None and published_at is not None:
                    break
    except Exception:
        pass

    # Fallback: <time> tags
    try:
        if published_at is None:
            # <time datetime="..."> or <time content="...">
            t = re.search(r'<time[^>]+(?:datetime|content)=[\'\"](.*?)[\'\"][^>]*>', html, re.IGNORECASE)
            if t:
                published_at = t.group(1).strip()
    except Exception:
        pass
    
    # Determine status based on extraction results
    paywalled = _is_likely_paywalled(html, body, word_count)

    # Try to detect canonical URL from metadata if available
    canonical_from_meta: Optional[str] = None
    try:
        # <link rel="canonical" href="...">
        m_link = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\'](.*?)["\']', html, re.IGNORECASE)
        if m_link:
            href = m_link.group(1).strip()
            if href:
                canonical_from_meta = canonicalize_url(urljoin(canonical_url, href))
        # <meta property="og:url" content="...">
        if not canonical_from_meta:
            m_og = re.search(r'<meta[^>]+property=["\']og:url["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
            if m_og:
                href = m_og.group(1).strip()
                if href:
                    canonical_from_meta = canonicalize_url(urljoin(canonical_url, href))
        # JSON-LD mainEntityOfPage / url
        if not canonical_from_meta:
            for script_match in re.finditer(r'<script[^>]+type=[\'\"]application/ld\+json[\'\"][^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL):
                block = script_match.group(1).strip()
                try:
                    data = json.loads(block)
                except Exception:
                    continue
                nodes = data if isinstance(data, list) else [data]
                for node in nodes:
                    if isinstance(node, dict):
                        for key in ('mainEntityOfPage', 'url'):
                            val = node.get(key)
                            if isinstance(val, str) and val:
                                canonical_from_meta = canonicalize_url(urljoin(canonical_url, val))
                                break
                        if canonical_from_meta:
                            break
                if canonical_from_meta:
                    break
    except Exception:
        pass
    if body and word_count > 100 and not paywalled:
        status = 'extracted'
    elif body:
        status = 'missing'  # Content too short
    else:
        status = 'missing'  # No content extracted
    
    result = (headline, body, word_count, status, author, published_at, paywalled, canonical_from_meta)
    _set_cache(canonical_url, *result)
    return result