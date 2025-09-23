# TheBiasLens

A web service that analyzes news content for political framing (Left/Center/Right), generates a short summary, and surfaces fact-check snippets with citations.

## Overview

TheBiasLens consists of two main components:

- **API Server**: FastAPI backend with configurable news providers and search functionality
- **Web App**: React + TypeScript frontend with responsive UI and paginated search

## Features

- **News Search**: Search articles from multiple news providers (currently NewsAPI)
- **Paginated Results**: Load more functionality for browsing large result sets
- **Responsive Design**: Mobile-first UI with Material-UI components
- **Provider Abstraction**: Configurable backend supporting multiple news APIs
- **Real-time Updates**: Live search results with loading states

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

## Project Structure

```
thebiaslens/
├── api/           # FastAPI backend
├── app/           # React frontend
└── sprints/       # Development documentation
```

## Development Status

✅ **Completed Features**:

- News search API with provider abstraction
- Paginated search results
- Responsive web interface
- Mock data fallback for development

🚧 **Planned Features**:

- Bias analysis (Left/Center/Right framing)
- Article summaries
- Fact-check integration
- User preferences and history
