import React, { useState } from 'react';
import { Box, Chip, Typography, Container, Stack, Alert } from '@mui/material';
import { useSearchPaged } from '../hooks/useSearchPaged';
import EmptyState from '../components/EmptyState';
import ResultSkeleton from '../components/ResultSkeleton';
import ResultList from '../components/ResultList';
import SearchBar from '../components/SearchBar';

const Search = () => {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');

  const { items, isLoading, error } = useSearchPaged(submittedQuery);

  const exampleQueries = ['Climate change policies', 'Economic inequality', 'Healthcare reform'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setSubmittedQuery(query.trim());
    }
  };

  const handleChipClick = (chipQuery: string) => {
    setQuery(chipQuery);
    setSubmittedQuery(chipQuery);
  };
  const renderContent = () => {
    if (!submittedQuery) {
      return <EmptyState />;
    }

    if (isLoading && (!items || items.length === 0)) {
      return <ResultSkeleton />;
    }

    if (error) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          Couldn't fetch results. Try again.
        </Alert>
      );
    }

    if (items && items.length > 0) {
      return <ResultList results={items} isLoading={isLoading} />;
    }

    // Show "no results" message when search returns empty results
    if (items && items.length === 0) {
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            mt: 4,
            px: 2,
          }}
        >
          <Typography variant="h6" gutterBottom>
            No results found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 400 }}>
            We couldn't find any articles matching "{submittedQuery}". Try a different search term
            or check for typos.
          </Typography>
        </Box>
      );
    }

    return <EmptyState />;
  };

  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      {/* Search Form */}
      <Box sx={{ mb: 3 }}>
        <Stack spacing={2}>
          <SearchBar value={query} onChange={setQuery} onSubmit={handleSubmit} />

          {/* Example Chips */}
          <Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Try these topics:
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {exampleQueries.map((chipQuery) => (
                <Chip
                  key={chipQuery}
                  label={chipQuery}
                  onClick={() => handleChipClick(chipQuery)}
                  variant="outlined"
                  clickable
                />
              ))}
            </Stack>
          </Box>
        </Stack>
      </Box>

      {/* Content */}
      {renderContent()}
    </Container>
  );
};

export default Search;
