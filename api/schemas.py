from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum


class BiasLabel(str, Enum):
    """Political bias labels."""
    LEFT = "Left"
    NEUTRAL = "Neutral"
    RIGHT = "Right"


class BiasResult(BaseModel):
    """Bias analysis result."""
    label: BiasLabel
    confidence: float  # [0..1]
    score: float  # [-1..1] where -1 left, 0 neutral, +1 right
    calibrationVersion: str = "v1"


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


class SummaryResult(BaseModel):
    """Summary of article text."""
    sentences: List[str]
    joined: str
    charCount: int
    wordCount: int


class AnalyzeResult(BaseModel):
    """Combined extraction and summary result."""
    extract: ExtractResult
    summary: Optional[SummaryResult] = None
    bias: Optional[BiasResult] = None