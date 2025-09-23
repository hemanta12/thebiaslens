# TODO: Upstash Redis cache later for 48h TTL once analysis exists.

# News API integration with configurable providers
import re
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from urllib.parse import urlparse
from pydantic import BaseModel

# Request models
class SummarizeRequest(BaseModel):
    text: str
    maxSentences: Optional[int] = 3
    maxChars: Optional[int] = 600

# Load settings at module import
from config import settings
from providers.newsapi import search_news
from data.mock_results import MOCK_ARTICLES
from schemas import ExtractResult, SummaryResult, AnalyzeResult
from services.extract import extract_article
from services.summarize import summarize_lead3
from utils.normalize import canonicalize_url, infer_source_from_url
from utils.analysis_id import make_analysis_id

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
        # Fallback to mock data 
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
    headline, body, word_count, status, author, published_at, paywalled, canonical_from_meta = await extract_article(canonical_url)
    
    # Infer source from URL
    source = infer_source_from_url(canonical_url)
    
    # Build and return ExtractResult
    result = ExtractResult(
        url=canonical_url,
        canonicalUrl=canonical_from_meta or canonical_url,
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


@app.post("/summarize", response_model=SummaryResult)
async def summarize(request: SummarizeRequest):
    """
    Summarize provided text with simple lead-3 algorithm.
    
    Args:
        request: SummarizeRequest with text and optional max parameters
        
    Returns:
        SummaryResult with sentences, joined text, and counts
    """
    text = request.text
    
    # Short text handling - just return the whole text as one sentence if very short
    if len(text.strip()) < 200:
        result = {
            "sentences": [text.strip()],
            "joined": text.strip(),
            "charCount": len(text.strip()),
            "wordCount": len(text.strip().split())
        }
        return SummaryResult(**result)
    
    # Standard case - run summarize_lead3
    summary = summarize_lead3(
        text=text,
        max_sentences=request.maxSentences,
        max_chars=request.maxChars
    )
    
    return SummaryResult(**summary)


@app.get("/analyze/url", response_model=AnalyzeResult)
async def analyze_url(url: str = Query(..., description="URL of the article to analyze")):
    """
    Extract and summarize article content from a given URL.
    
    Args:
        url: The URL of the article to extract and summarize (required)
        
    Returns:
        AnalyzeResult with extraction and optional summary
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
    
    # Extract article content (reusing the extraction logic)
    headline, body, word_count, status, author, published_at, paywalled, canonical_from_meta = await extract_article(canonical_url)
    
    # Infer source from URL
    source = infer_source_from_url(canonical_url)
    
    # Build ExtractResult
    extract_result = ExtractResult(
        url=canonical_url,
        canonicalUrl=canonical_from_meta or canonical_url,
        headline=headline,
        source=source,
        publishedAt=published_at,
        author=author,
        body=body,
        wordCount=word_count,
        extractStatus=status,
        paywalled=paywalled,
    )
    
    # Create summary if body is available
    summary_result = None
    if body:
        summary_data = summarize_lead3(body)
        summary_result = SummaryResult(**summary_data)
    
    # Compute analysis id and canonical
    analysis_id = make_analysis_id(canonical_url)
    canonical_final = extract_result.canonicalUrl or canonical_url

    # Return combined result
    return AnalyzeResult(
        id=analysis_id,
        canonicalUrl=canonical_final,
        extract=extract_result,
        summary=summary_result,
        bias=None
    )


@app.get("/analyze/id/{analysis_id}", response_model=AnalyzeResult)
async def analyze_by_id(analysis_id: str, url: Optional[str] = Query(None, description="Original URL to analyze if id cannot be reversed")):
    """
    Analyze by deterministic id. Since ids are one-way hashes, require `?url=` as fallback.

    If `url` is not provided, return 400.
    """
    if not url:
        raise HTTPException(status_code=400, detail="Missing url query parameter for analysis id lookup")

    # Validate and canonicalize
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format")

    # Best-effort check: ensure provided id matches recomputed id
    canonical_url = canonicalize_url(url)
    recomputed_id = make_analysis_id(canonical_url)
    if recomputed_id != analysis_id:
        raise HTTPException(status_code=400, detail="Provided url does not match analysis id")

    # Proceed with the same analysis flow as /analyze/url
    headline, body, word_count, status, author, published_at, paywalled, canonical_from_meta = await extract_article(canonical_url)
    source = infer_source_from_url(canonical_url)
    extract_result = ExtractResult(
        url=canonical_url,
        canonicalUrl=canonical_from_meta or canonical_url,
        headline=headline,
        source=source,
        publishedAt=published_at,
        author=author,
        body=body,
        wordCount=word_count,
        extractStatus=status,
        paywalled=paywalled,
    )
    summary_result = None
    if body:
        summary_data = summarize_lead3(body)
        summary_result = SummaryResult(**summary_data)
    canonical_final = extract_result.canonicalUrl or canonical_url
    return AnalyzeResult(
        id=analysis_id,
        canonicalUrl=canonical_final,
        extract=extract_result,
        summary=summary_result,
        bias=None,
    )
