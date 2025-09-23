# TheBiasLens API Server

FastAPI backend for news search, article extraction, and content analysis with configurable provider support.

## Features

### Core Endpoints

- **News Search**: `/search` endpoint with pagination support and provider abstraction
- **Article Extraction**: `GET /extract?url=` — fetch and extract full article text with trafilatura
- **Text Summarization**: `POST /summarize` — create lead-3 summaries from article text
- **Combined Analysis**: `GET /analyze/url` — extract, summarize, and perform bias analysis in a single request
- **Bias Analysis**: Schema support for Left/Neutral/Right political framing with confidence scores
- **Health Check**: `/health` — service status and version information

### Technical Features

- **Provider Abstraction**: Configurable news providers (NewsAPI implemented, extensible architecture)
- **Content Extraction**: Uses trafilatura for robust article text extraction from web pages
- **Intelligent Summarization**: Lead-3 algorithm for generating concise, meaningful summaries
- **Settings Management**: Pydantic-based configuration with environment variables
- **Mock Data Fallback**: Automatic fallback when API keys not configured for seamless development
- **CORS Support**: Ready for frontend integration with configurable origins
- **In-Memory Caching**: 60-second cache for improved performance (will migrate to Upstash TTL)
- **Error Handling**: Comprehensive error responses with detailed messages

## Installation

```bash
# Clone and navigate to API directory
cd api

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your NEWS_API_KEY and other configuration
```

## Configuration

Environment variables (`.env`):

```env
# News Provider Configuration
NEWS_PROVIDER=newsapi                    # News provider to use
NEWS_API_BASE_URL=https://newsapi.org/v2 # NewsAPI base URL
NEWS_API_KEY=                            # Your NewsAPI key (optional for development)

# Pagination Settings
DEFAULT_PAGE_SIZE=10                     # Default results per page
MAX_PAGE_SIZE=50                         # Maximum allowed results per page

# Extraction Settings
EXTRACTION_TIMEOUT=30                    # Timeout for article extraction in seconds
SUMMARY_MAX_SENTENCES=3                  # Default maximum sentences in summary
SUMMARY_MAX_CHARS=600                    # Default maximum characters in summary
```

## Run Commands

```bash
# Start with auto-reload for development
uvicorn main:app --reload

# Start with specific host/port
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

API will be available at `http://127.0.0.1:8000`

### Production Deploy

```bash
# Production server
uvicorn main:app --host 0.0.0.0 --port $PORT

# With workers for better performance
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4
```

## API Endpoints

### GET `/health`

Health check endpoint for monitoring and service discovery.

**Response:**

```json
{
  "status": "ok",
  "service": "thebiaslens-api",
  "version": "1.0.0",
  "timestamp": "2025-09-23T10:00:00Z"
}
```

### GET `/search`

Search for news articles with pagination support.

**Parameters:**

- `q` (required): Search query string
- `cursor` (optional): Page number for pagination (default: 1)
- `pageSize` (optional): Results per page (default: from settings, max: 50)

**Example Request:**

```
GET /search?q=climate%20change&pageSize=5&cursor=1
```

**Response:**

```json
{
  "items": [
    {
      "url": "https://example.com/article",
      "source": "Source Name",
      "publishedAt": "2025-09-22T10:00:00Z",
      "title": "Article Title",
      "extractStatus": "api"
    }
  ],
  "nextCursor": 2
}
```

### GET `/extract`

Extract article content from a URL using trafilatura.

**Parameters:**

- `url` (required): Article URL to extract content from

**Example Request:**

```
GET /extract?url=https://example.com/news-article
```

**Response:**

```json
{
  "url": "https://example.com/news-article",
  "headline": "Article Headline",
  "source": "Source Name",
  "publishedAt": "2025-09-22T10:00:00Z",
  "author": "Author Name",
  "body": "Full article text content...",
  "wordCount": 1250,
  "extractStatus": "extracted",
  "paywalled": false
}
```

**Extract Status Values:**

- `extracted`: Successfully extracted full content
- `missing`: URL could not be accessed or parsed
- `error`: Extraction failed due to technical issues

### POST `/summarize`

Generate a lead-3 summary from provided text.

**Request Body:**

```json
{
  "text": "Long article text to summarize...",
  "maxSentences": 3, // optional, default: 3
  "maxChars": 600 // optional, default: 600
}
```

**Response:**

```json
{
  "sentences": [
    "First key sentence from the article.",
    "Second important sentence.",
    "Third relevant sentence."
  ],
  "joined": "First key sentence from the article. Second important sentence. Third relevant sentence.",
  "charCount": 156,
  "wordCount": 28
}
```

### GET `/analyze/url`

Combined extraction and summarization in a single request for optimal user experience.

**Parameters:**

- `url` (required): Article URL to analyze

**Example Request:**

```
GET /analyze/url?url=https://example.com/news-article
```

**Response:**

```json
{
  "id": "abc123defg",
  "canonicalUrl": "https://example.com/news-article",
  "extract": {
    "url": "https://example.com/news-article?utm_source=twitter",
    "canonicalUrl": "https://example.com/news-article",
    "headline": "Article Headline",
    "source": "Source Name",
    "body": "Full article text...",
    "wordCount": 1250,
    "extractStatus": "extracted"
  },
  "summary": {
    "sentences": ["Key sentence 1.", "Key sentence 2.", "Key sentence 3."],
    "joined": "Key sentence 1. Key sentence 2. Key sentence 3.",
    "charCount": 156,
    "wordCount": 28
  },
  "bias": {
    "label": "Neutral",
    "confidence": 0.82,
    "score": 0.05,
    "calibrationVersion": "v1"
  }
}
```

Fields:

- `id`: Stable 10-char slug derived from the canonical URL (sha256 → base32)
- `canonicalUrl`: Canonical URL detected from the page (`<link rel=canonical>`, `og:url`, JSON-LD),
  falling back to normalized input URL when not present

### GET `/analyze/id/{id}`

Helper endpoint to address an analysis by deterministic id. Since ids are one-way hashes, provide the `url` query for verification and analysis.

**Parameters:**

- `id` (path): Deterministic slug produced from the canonical URL
- `url` (query, required): Original URL; must canonicalize to the same id

**Example Request:**

```
GET /analyze/id/abc123defg?url=https://example.com/news-article
```

Returns the same response shape as `/analyze/url`.

Notes:

- If the `url` canonicalizes to an id different from the path parameter, the API responds with `400`.
- This provides a stable route for the frontend without a database.

## Architecture

```
api/
├── main.py              # FastAPI app, routes, and middleware
├── config.py            # Pydantic settings and environment management
├── providers/           # News provider implementations
│   ├── __init__.py     # Provider interface and factory
│   └── newsapi.py      # NewsAPI provider implementation
├── data/               # Mock data for development
│   └── mock_results.py # Sample articles and responses
├── requirements.txt    # Python dependencies
└── .env.example       # Environment variable template
```

## Development Features

### Provider System

- **Extensible Architecture**: Easy to add new news providers (Reddit, RSS, etc.)
- **Interface Abstraction**: Common interface for all news sources
- **Configuration Driven**: Switch providers via environment variables

### Mock Data Mode

- **Seamless Development**: Automatically uses mock data when API keys not configured
- **Realistic Testing**: Mock responses mirror real API structures
- **No External Dependencies**: Full functionality without third-party API keys

### Error Handling

- **Graceful Degradation**: Continues operation even when external services fail
- **Detailed Responses**: Clear error messages for debugging
- **Timeout Management**: Prevents hanging requests with configurable timeouts

## Development Workflow

1. **Setup**: Copy `.env.example` to `.env` and configure as needed
2. **Development**: Run with `--reload` flag for automatic code reloading
3. **Testing**: Use mock mode by omitting API keys
4. **Production**: Configure all environment variables and use production ASGI server

## Current Features and Future Enhancements

✅ **Implemented Features**:

- **Bias Analysis Schema**: Complete Pydantic models for bias detection results
- **Combined Analysis Endpoint**: Ready for ML model integration
- **Score Standardization**: Normalized -1 to 1 scoring system

🚧 **Planned Features**:

- **Bias ML Model**: Political framing analysis model implementation
- **Fact-Checking**: Integration with fact-checking services
- **Advanced Caching**: Redis/Upstash for distributed caching
- **Rate Limiting**: Request throttling and quotas
- **Authentication**: API key management for different usage tiers
- **Webhooks**: Real-time notifications for analysis completion

## Bias Analysis

### Bias Labels and Scoring

- **Three Labels Only**: "Left", "Neutral", "Right" (implemented as enum)
- **Score Range**: -1 to 1 (where -1 = left, 0 = neutral, +1 = right)
- **Confidence Level**: 0 to 1 score indicating certainty of classification
- **Calibration Versioning**: Support for model version tracking
- **Suggested Thresholds**:
  - Left: score <= -0.2
  - Neutral: -0.2 < score < 0.2
  - Right: score >= 0.2
