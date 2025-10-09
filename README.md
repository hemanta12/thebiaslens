# TheBiasLens

A web service that analyzes news content for political framing, generates article summaries, and provides content extraction capabilities with bias detection potential.

## Overview

TheBiasLens consists of two main components:

- **API Server**: FastAPI backend with article extraction, summarization, and configurable news providers
- **Web App**: React + TypeScript frontend with responsive UI, search functionality, and analysis tools

## Features

### Current Features ✅

- **News Search**: Search articles from multiple news providers (currently NewsAPI)
- **Article Extraction**: Extract full article content from URLs using trafilatura
- **Text Summarization**: Generate lead-3 summaries from extracted content
- **Bias Analysis UI**: Visual political bias meter with Left/Neutral/Right labels
- **Combined Analysis**: Single-endpoint analysis combining extraction, summarization, and bias detection
- **Responsive Design**: Mobile-first UI with Material-UI components
- **Search to Analysis Flow**: Click "Analyze" buttons in search results to automatically extract and summarize articles
- **Real-time Updates**: Live search results with loading states and error handling
- **Unified Analysis UI**: Integrated card layout combining metadata, bias analysis, and summary
- **Copy Functionality**: One-click copy for summaries with visual feedback
- **Shareable Analysis Links**: Deterministic analysis ids enable clean links like `/analyze/:id?url=...`
- **Open/Copy/Share Actions**: Open canonical article, copy app link with feedback, or share via Web Share API
- **Canonical URL Detection**: Extracts and reports canonical URL per page metadata
- **Sources & Citations**: Primary source plus up to 5 referenced links deduped by host
- **UX Polishing**: Clear (X) button on URL input, subtle skeletons for actions/sources, footer disclaimer
- **Share Image**: Download analysis as 1200x630 PNG for clean social media sharing without server OG tags
- **Advanced Fact-Check System**: Type-aware claim mining with policy, statistics, causal, and factoid classification
- **Intelligent Query Planning**: Multi-pass search strategy with deduplication and semantic expansion
- **Professional Scoring Engine**: Multi-algorithm similarity scoring with type bonuses and distractor penalties
- **Publisher Deduplication**: Quality control with highest-scoring results per source
- **Recency Controls**: Configurable date filtering with intelligent defaults (12-18 months)
- **Comprehensive UI**: Dynamic verdict chips, relation levels, and source attribution with clickable links

### Planned Features 🚧

- **Bias ML Model**: Implementation of the political framing detection algorithm
- **User Preferences**: Saved searches and bookmarks
- **Historical Analysis**: Track bias trends over time

## Quick Start

1. **Start the API server**:

   ```bash
   cd api
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Start the web app**:

   ```bash
   cd app/thebiaslens
   npm install
   npm start
   ```

3. **Configure environment**:
   - Set `NEWS_API_KEY` in `api/.env` for live news data
   - Without API key, uses mock data for development

## Usage Flow

1. **Search for News**: Use the search interface to find articles on topics of interest
2. **Analyze Articles**: Click "Analyze" buttons in search results to extract and summarize content
3. **Review Results**: View extracted article metadata, content, and AI-generated summaries
4. **Navigate Seamlessly**: Switch between search and analysis with automatic URL parameter handling
5. **Share Results**: Use Copy/Share actions to share a stable link to the analysis

### Direct Link Formats

- Analyze by URL query:
  - `/analyze?url=<article-url>`
- Analyze by deterministic id (clean route):
  - `/analyze/<id>?url=<article-url>`

Note: `id` is derived from the canonicalized URL (sha256→base32) and cannot be reversed; the `url` query is required to run the analysis.

## Project Structure

```
thebiaslens/
├── api/                    # FastAPI backend
│   ├── main.py            # API routes and app
│   ├── config.py          # Configuration management
│   ├── providers/         # News provider implementations
│   └── data/              # Mock data for development
├── app/thebiaslens/       # React frontend
│   ├── src/components/    # Reusable UI components
│   ├── src/hooks/         # Custom React hooks
│   ├── src/routes/        # Page components
│   └── src/api/           # API client utilities
└── sprints/               # Development documentation
```

## Development Status

✅ **Completed Features**:

- News search API with provider abstraction
- Article extraction with trafilatura integration
- Lead-3 text summarization
- Combined analysis endpoint
- Bias schema and UI implementation
- Unified analysis card with integrated components
- Responsive web interface with search and analysis
- Navigation flow from search results to analysis page
- URL parameter handling for direct analysis links
- Copy feedback and improved user interactions
- Mock data fallback for development
- Share/Copy actions for analysis links
- Sources & Citations section on Analyze page
- Deterministic analysis ids and canonical URL detection
- Share Image feature with HTML2Canvas rendering for social media sharing
- Advanced fact-check architecture with type-aware claim mining and classification
- Intelligent query planning with semantic expansion and deduplication logic
- Multi-algorithm scoring engine with type bonuses and quality penalties
- Publisher deduplication and recency filtering for enhanced quality control
- Professional fact-check UI with verdict chips, relation levels, and source attribution
- Comprehensive testing infrastructure for backend quality assurance

🚧 **In Progress**:

- Bias detection ML model integration
- Enhanced UI/UX improvements

🔮 **Future Plans**:

- Multi-provider bias analysis
- User authentication and preferences
- Historical analysis and trending
- Browser extension for real-time analysis

## Disclaimer

Bias and fact-check estimations are AI-generated and may not be fully accurate. This is for informational purposes only.
