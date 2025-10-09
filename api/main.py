import logging
import re
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from urllib.parse import urlparse
from pydantic import BaseModel

from config import settings
from providers.newsapi import search_news
from data.mock_results import MOCK_ARTICLES
from schemas import ExtractResult, SummaryResult, AnalyzeResult, FactCheckResult, FactCheckRequest
from services.extract import extract_article
from services.summarize import summarize_lead3
from services.factcheck_service import find_best_factchecks
from utils.normalize import canonicalize_url, infer_source_from_url
from utils.analysis_id import make_analysis_id

class SummarizeRequest(BaseModel):
    text: str
    maxSentences: Optional[int] = 3
    maxChars: Optional[int] = 600

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# CORS setup for local and Vercel deployments
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://thebiaslens.vercel.app",
]
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
    if len(q.strip()) < 2:
        return {"items": [], "nextCursor": None}
    
    if pageSize is None:
        pageSize = settings.default_page_size
    
    # Use NewsAPI if key available, otherwise mock data
    if settings.news_api_key:
        return search_news(q, page=cursor, page_size=pageSize)
    else:
        query_lower = q.lower()
        filtered_articles = [
            article for article in MOCK_ARTICLES
            if query_lower in article["title"].lower() or query_lower in article["source"].lower()
        ]
        return {"items": filtered_articles, "nextCursor": None}


@app.get("/extract", response_model=ExtractResult)
async def extract(url: str = Query(..., description="URL of the article to extract")):
    # URL validation
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    canonical_url = canonicalize_url(url)
    headline, body, word_count, status, author, published_at, paywalled, canonical_from_meta = await extract_article(canonical_url)
    source = infer_source_from_url(canonical_url)
    
    return ExtractResult(
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
@app.post("/summarize", response_model=SummaryResult)
async def summarize(request: SummarizeRequest):
    text = request.text
    
    # Return whole text if very short
    if len(text.strip()) < 200:
        result = {
            "sentences": [text.strip()],
            "joined": text.strip(),
            "charCount": len(text.strip()),
            "wordCount": len(text.strip().split())
        }
        return SummaryResult(**result)
    
    summary = summarize_lead3(
        text=text,
        max_sentences=request.maxSentences,
        max_chars=request.maxChars
    )
    
    return SummaryResult(**summary)


@app.get("/analyze/url", response_model=AnalyzeResult)
async def analyze_url(url: str = Query(..., description="URL of the article to analyze")):
    # URL validation
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    canonical_url = canonicalize_url(url)
    
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
    # Require URL since IDs are one-way hashes
    if not url:
        raise HTTPException(status_code=400, detail="Missing url query parameter for analysis id lookup")

    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format")

    # Verify provided ID matches recomputed ID
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


@app.post("/factcheck", response_model=FactCheckResult)
async def factcheck(payload: FactCheckRequest):
    # Clamp maxAgeMonths to allowed values
    max_age_months = payload.maxAgeMonths or 18
    if max_age_months not in [6, 12, 18, 24, 9999]:
        max_age_months = min([6, 12, 18, 24, 9999], key=lambda x: abs(x - max_age_months))
    
    return await find_best_factchecks(
        headline=payload.headline,
        source_domain=payload.sourceDomain,
        summary=payload.summary,
        max_items=3,
        max_age_months=max_age_months
    )
