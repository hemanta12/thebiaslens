# TODO: replace mock with real provider(s)
import re
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from data.mock_results import MOCK_ARTICLES

app = FastAPI()

# CORS configuration
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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
def search(q: Optional[str] = Query(None)):
    # Return empty result if query is missing or too short
    if not q or len(q) < 2:
        return {"items": [], "nextCursor": None}
    
    # Filter mock articles by substring check on title and source
    query_lower = q.lower()
    filtered_articles = [
        article for article in MOCK_ARTICLES
        if query_lower in article["title"].lower() or query_lower in article["source"].lower()
    ]
    
    return {"items": filtered_articles, "nextCursor": None}
