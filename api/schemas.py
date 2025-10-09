from pydantic import BaseModel, AnyUrl
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum


class BiasLabel(str, Enum):
    LEFT = "Left"
    NEUTRAL = "Neutral"
    RIGHT = "Right"


class BiasResult(BaseModel):
    label: BiasLabel
    confidence: float  # [0..1]
    score: float  # [-1..1] where -1 left, 0 neutral, +1 right
    calibrationVersion: str = "v1"


class ArticleStub(BaseModel):
    url: str
    source: str
    publishedAt: Optional[datetime] = None
    title: str
    extractStatus: Literal['extracted', 'missing', 'error']


class ExtractResult(BaseModel):
    url: str
    canonicalUrl: Optional[str] = None
    headline: Optional[str] = None
    source: str
    publishedAt: Optional[datetime] = None
    author: Optional[str] = None
    body: Optional[str] = None
    wordCount: int
    extractStatus: Literal['extracted', 'missing', 'error']
    paywalled: Optional[bool] = None


class SummaryResult(BaseModel):
    sentences: List[str]
    joined: str
    charCount: int
    wordCount: int


class FactCheckRequest(BaseModel):
    headline: str
    sourceDomain: Optional[str] = None
    summary: Optional[str] = None
    maxAgeMonths: Optional[int] = None


class FactCheckItem(BaseModel):
    claim: str
    verdict: Optional[str] = None
    snippet: Optional[str] = None
    source: Optional[str] = None  # publisher
    url: Optional[AnyUrl] = None
    publishedAt: Optional[datetime] = None
    matchReason: Optional[str] = None
    similarity: Optional[float] = None  # 0..1 from scoring


class FactCheckResult(BaseModel):
    status: Literal["found", "none"]
    items: List[FactCheckItem] = []


class AnalyzeResult(BaseModel):
    id: str
    canonicalUrl: str
    extract: ExtractResult
    summary: Optional[SummaryResult] = None
    bias: Optional[BiasResult] = None