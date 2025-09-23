# TheBiasLens API Server

FastAPI backend for news search and analysis with configurable provider support.

## Features

- **News Search**: `/search` endpoint with pagination support
- **Article Extraction**: `GET /extract?url=` — fetch + extract article text with trafilatura; returns normalized shape
- **Text Summarization**: `POST /summarize` — create lead-3 summaries from article text
- **Combined Analysis**: `GET /analyze/url` — extract and summarize in a single request
- **Provider Abstraction**: Configurable news providers (NewsAPI implemented)
- **Settings Management**: Pydantic-based configuration with environment variables
- **Mock Data Fallback**: Automatic fallback when API keys not configured
- **CORS Support**: Ready for frontend integration
- **Caching**: In-memory 60s cache; will switch to Upstash TTL later

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your NEWS_API_KEY
```

## Configuration

Environment variables (`.env`):

```env
NEWS_PROVIDER=newsapi                    # News provider to use
NEWS_API_BASE_URL=https://newsapi.org/v2 # NewsAPI base URL
NEWS_API_KEY=                            # Your NewsAPI key (optional)
DEFAULT_PAGE_SIZE=10                     # Default results per page
```

## Run Commands

### Local Development

```bash
uvicorn main:app --reload
```

API will be available at `http://127.0.0.1:8000`

### Production Deploy

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## API Endpoints

### GET `/health`

Health check endpoint

```json
{
  "status": "ok",
  "service": "api",
  "version": "0.0.1"
}
```

### GET `/search`

Search for news articles

**Parameters:**

- `q` (required): Search query string
- `cursor` (optional): Page number for pagination (default: 1)
- `pageSize` (optional): Results per page (default: from settings)

**Response:**

```json
{
  "items": [
    {
      "url": "https://example.com/article",
      "source": "Source Name",
      "publishedAt": "2025-09-22T10:00:00Z",
      "title": "Article Title"
    }
  ],
  "nextCursor": 2
}
```

### GET `/extract`

Extract article content by URL.

```
GET /extract?url=<article-url>
```

Returns normalized shape with fields like `url`, `headline`, `source`, `publishedAt`, `author`, `body`, `wordCount`, `extractStatus`, and `paywalled`.

### POST `/summarize`

Summarize provided text using a lead-3 algorithm.

```
POST /summarize
Content-Type: application/json

{
  "text": "Article text to summarize",
  "maxSentences": 3,  // optional, default: 3
  "maxChars": 600     // optional, default: 600
}
```

Returns `SummaryResult` with extracted sentences, joined text, and character/word counts.

### GET `/analyze/url`

Combined extraction and summarization in a single request.

```
GET /analyze/url?url=<article-url>
```

Returns `AnalyzeResult` containing both the extraction result and a summary (if content was successfully extracted).

## Architecture

```
api/
├── main.py              # FastAPI app and routes
├── config.py            # Pydantic settings
├── providers/           # News provider implementations
│   ├── __init__.py
│   └── newsapi.py       # NewsAPI provider
├── data/                # Mock data for development
└── requirements.txt     # Python dependencies
```

## Development

- **Mock Mode**: When `NEWS_API_KEY` is not set, uses mock data
- **Provider System**: Easy to add new news providers
- **Type Safety**: Full typing with Pydantic models
- **Error Handling**: Graceful fallbacks and error responses
