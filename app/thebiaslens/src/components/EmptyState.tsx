import React from 'react';
import { Box, Typography } from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';

const EmptyState = () => {
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
};

export default EmptyState;
