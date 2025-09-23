from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class ArticleStub(BaseModel):
    """Basic article information for search results."""
    url: str
    source: str
    publishedAt: Optional[datetime] = None
    title: str
    extractStatus: Literal['extracted', 'missing', 'error']


class ExtractResult(BaseModel):
    """Full article extraction result with content."""
    url: str
    headline: Optional[str] = None
    source: str
    publishedAt: Optional[datetime] = None
    author: Optional[str] = None
    body: Optional[str] = None
    wordCount: int
    extractStatus: Literal['extracted', 'missing', 'error']
    paywalled: Optional[bool] = None