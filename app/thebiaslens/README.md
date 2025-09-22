# TheBiasLens — Web App

React + TypeScript frontend for news search and bias analysis with responsive Material-UI design.

## Features

- **Search Interface**: Real-time news search with example queries
- **Paginated Results**: "Load more" functionality for browsing large result sets
- **Responsive Design**: Mobile-first UI optimized for all screen sizes
- **Loading States**: Skeleton screens and loading indicators
- **Error Handling**: User-friendly error messages and fallbacks
- **Material-UI**: Modern, accessible component library

## Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for components and theming
- **React Query** for data fetching and caching
- **React Router** for client-side routing
- **Tailwind CSS** for utility styling

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── BottomNav.tsx   # Bottom navigation bar
│   ├── Header.tsx      # App header
│   ├── Layout.tsx      # Main layout wrapper
│   ├── ResultList.tsx  # Article results with pagination
│   ├── SearchBar.tsx   # Search input component
│   └── ...
├── hooks/              # Custom React hooks
│   ├── useSearch.ts    # Single-page search hook
│   ├── useSearchPaged.ts # Paginated search hook
│   └── useTheme.ts     # Theme management
├── routes/             # Page components
│   ├── Search.tsx      # Main search page
│   ├── Analyze.tsx     # Analysis page (placeholder)
│   ├── Recents.tsx     # Recent searches (placeholder)
│   ├── Settings.tsx    # App settings (placeholder)
│   └── Details.tsx     # Article details (placeholder)
├── api/                # API client
│   └── client.ts       # HTTP client utilities
├── types/              # TypeScript type definitions
│   └── api.ts          # API response types
└── styles/             # Global styles and theme
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
```

## Environment Variables

Create `.env.local` for local development:

```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
```

## Available Routes

- `/` - Home/Search page
- `/analyze` - Bias analysis (coming soon)
- `/recents` - Recent searches (coming soon)
- `/settings` - User preferences (coming soon)
- `/details/:id` - Article details (coming soon)

## Features in Development

✅ **Completed**:

- Search interface with real-time results
- Paginated article browsing
- Responsive design and navigation
- Error handling and loading states
- API integration with fallbacks

🚧 **Planned**:

- Bias analysis visualization
- Article content extraction
- User preferences and history
- Fact-check integration
- Saved searches and bookmarks

## Development Notes

- **API Integration**: Automatically falls back to mock data when API is unavailable
- **Responsive**: Mobile-first design with breakpoint-aware components
- **Accessibility**: ARIA labels and keyboard navigation support
- **Performance**: React Query caching and optimized re-renders
- **Type Safety**: Full TypeScript coverage with strict mode
