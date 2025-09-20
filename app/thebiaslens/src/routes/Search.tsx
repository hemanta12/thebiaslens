import React, { useState } from 'react';
import { Box, TextField, Button, Chip, Typography, Container, Stack, Alert } from '@mui/material';
import { useSearch } from '../hooks/useSearch';
import EmptyState from '../components/EmptyState';
import ResultSkeleton from '../components/ResultSkeleton';
import ResultList from '../components/ResultList';

const Search = () => {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');

  const { data, isLoading, error } = useSearch(submittedQuery);

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

    if (isLoading) {
      return <ResultSkeleton />;
    }

    if (error) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          Couldn't fetch results. Try again.
        </Alert>
      );
    }

    if (data?.items && data.items.length > 0) {
      return <ResultList items={data.items} />;
    }

    // Show "no results" message when search returns empty results
    if (data?.items && data.items.length === 0) {
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
      <Box component="form" onSubmit={handleSubmit} sx={{ mb: 3 }}>
        <Stack spacing={2}>
          <TextField
            fullWidth
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for news topics..."
            variant="outlined"
            InputProps={{
              endAdornment: (
                <Button type="submit" variant="contained" sx={{ ml: 1 }} disabled={!query.trim()}>
                  Search
                </Button>
              ),
            }}
          />

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
