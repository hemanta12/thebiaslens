# TheBiasLens — Web App

React + TypeScript frontend for news search and content analysis with responsive Material-UI design.

## Features

### Core Functionality

- **Search Interface**: Real-time news search with example queries and autocomplete
- **Article Analysis**: Extract and summarize articles with a single click from search results
- **Content Extraction**: Full article text extraction with metadata display
- **Text Summarization**: AI-powered lead-3 summaries with copy-to-clipboard functionality
- **Responsive Design**: Mobile-first UI optimized for all screen sizes
- **Navigation Flow**: Seamless transition from search results to detailed analysis

### User Experience

- **Loading States**: Skeleton screens and loading indicators for better perceived performance
- **Error Handling**: User-friendly error messages and fallbacks
- **URL Parameter Support**: Direct links to analysis pages with pre-filled URLs
- **Progressive Enhancement**: Works with or without JavaScript enabled
- **Accessibility**: ARIA labels, keyboard navigation, and screen reader support

## Tech Stack

- **React 18** with TypeScript for type safety and modern React patterns
- **Material-UI (MUI)** for components, theming, and responsive design
- **React Query** for data fetching, caching, and synchronization
- **React Router** for client-side routing and URL parameter handling
- **Tailwind CSS** for utility styling and rapid development

## Project Structure

```
src/
├── components/              # Reusable UI components
│   ├── BottomNav.tsx       # Bottom navigation bar
│   ├── Header.tsx          # App header with branding
│   ├── Layout.tsx          # Main layout wrapper
│   ├── ResultList.tsx      # Article results with analyze buttons
│   ├── SearchBar.tsx       # Search input component
│   └── analyze/            # Analysis-specific components
│       ├── UrlForm.tsx     # URL input form for analysis
│       ├── ExtractResultCard.tsx  # Article content display
│       ├── ArticleMetadata.tsx    # Article title, source, metadata
│       ├── SummarySection.tsx     # Summary display and controls
│       └── ArticleTextSection.tsx # Full text toggle and display
├── hooks/                  # Custom React hooks
│   ├── useSearch.ts        # Single-page search hook
│   ├── useSearchPaged.ts   # Paginated search hook
│   ├── useExtract.ts       # Article extraction hook
│   ├── useSummarize.ts     # Text summarization hook
│   └── useTheme.ts         # Theme management
├── routes/                 # Page components
│   ├── Search.tsx          # Main search page
│   ├── AnalyzePage.tsx     # Article analysis and extraction
│   ├── Recents.tsx         # Recent searches (placeholder)
│   ├── Settings.tsx        # App settings (placeholder)
│   └── Details.tsx         # Article details (placeholder)
├── api/                    # API client
│   └── client.ts           # HTTP client utilities
├── types/                  # TypeScript type definitions
│   └── api.ts              # API response types
├── utils/                  # Utility functions
│   └── textUtils.ts        # Text formatting and processing
└── styles/                 # Global styles and theme
```

## Installation & Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Type checking
npm run type-check
```

## Environment Variables

Create `.env.local` for local development:

```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
```

## Available Routes

- `/` - Home/Search page with news article search
- `/analyze` - Article analysis page with extraction and summarization
  - Supports `?url=` parameter for direct analysis
- `/recents` - Recent searches (coming soon)
- `/settings` - User preferences (coming soon)
- `/details/:id` - Article details (coming soon)

## Key User Flows

### Search to Analysis Flow

1. User searches for articles on the main page
2. Results display with "Analyze" buttons for each article
3. Clicking "Analyze" navigates to `/analyze?url=<article-url>`
4. Analysis page automatically extracts and summarizes the article
5. User can view metadata, summary, and full text

### Direct Analysis Flow

1. User visits `/analyze` page directly
2. Enters article URL manually
3. System extracts content and generates summary
4. Results display with copy functionality

## Features in Development

✅ **Completed**:

- Search interface with real-time results
- Article content extraction from URLs
- AI-powered text summarization
- Responsive design and navigation
- Error handling and loading states
- API integration with fallbacks
- URL parameter handling for direct analysis
- Copy-to-clipboard functionality

🚧 **Planned**:

- Bias analysis visualization
- Fact-check integration
- User preferences and history
- Saved searches and bookmarks
- Advanced filtering and sorting
- Social sharing capabilities

## Development Notes

- **API Integration**: Automatically falls back to mock data when API is unavailable
- **Responsive**: Mobile-first design with breakpoint-aware components
- **Accessibility**: Full ARIA support and keyboard navigation
- **Performance**: React Query caching, code splitting, and optimized re-renders
- **Type Safety**: Full TypeScript coverage with strict mode enabled
- **Error Boundaries**: Graceful error handling with user-friendly messages
