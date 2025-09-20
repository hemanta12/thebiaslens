import React, { useState } from 'react';
import { Box, TextField, Button, Chip, Typography, Container, Stack } from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';

const Search = () => {
  const [query, setQuery] = useState('');

  const exampleQueries = ['Climate change policies', 'Economic inequality', 'Healthcare reform'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      // Store query in local state - API call will be added later
      console.log('Search query:', query);
    }
  };

  const handleChipClick = (chipQuery: string) => {
    setQuery(chipQuery);
  };

  const EmptyState = () => (
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
      <SearchIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
      <Typography variant="h6" gutterBottom>
        Discover Unbiased Perspectives
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 400 }}>
        Search for news topics to explore different viewpoints and analyze potential bias across
        sources. Try one of the suggestions above to get started.
      </Typography>
    </Box>
  );

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

      {/* Empty State */}
      <EmptyState />
    </Container>
  );
};

export default Search;
