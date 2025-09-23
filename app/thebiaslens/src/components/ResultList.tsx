import React from 'react';
import { Typography, Button, Box, IconButton, Card, CardContent, Chip } from '@mui/material';
import { Analytics, OpenInNew } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ArticleStub } from '../types/api';

interface ResultListProps {
  results: ArticleStub[];
  isLoading?: boolean;
}

interface ResultItemProps {
  item: ArticleStub;
}

const ResultItem: React.FC<ResultItemProps> = ({ item }) => {
  const navigate = useNavigate();

  const handleAnalyze = () => {
    navigate(`/analyze?url=${encodeURIComponent(item.url)}`);
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box
          sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}
        >
          <Typography variant="h6" sx={{ flex: 1, mr: 2 }}>
            {item.title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexShrink: 0 }}>
            <IconButton
              size="small"
              onClick={() => window.open(item.url, '_blank')}
              title="Open article"
            >
              <OpenInNew />
            </IconButton>
            <Button
              variant="outlined"
              size="small"
              startIcon={<Analytics />}
              onClick={handleAnalyze}
            >
              Analyze
            </Button>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {item.url}
        </Typography>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {item.publishedAt && new Date(item.publishedAt).toLocaleDateString()}
            </Typography>
            {/* Bias pill - pending until classification is implemented */}
            <Chip
              label="Bias: pending"
              size="small"
              variant="outlined"
              sx={{
                fontSize: '0.6rem',
                height: 20,
                color: 'text.secondary',
                borderColor: 'grey.300',
                backgroundColor: 'grey.50',
              }}
            />
          </Box>
          <Typography variant="caption" color="text.secondary">
            {item.source}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

const ResultList: React.FC<ResultListProps> = ({ results, isLoading }) => {
  if (isLoading) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography>Loading results...</Typography>
      </Box>
    );
  }

  if (!results || results.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography color="text.secondary">
          No articles found. Try a different search term.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Search Results ({results.length})
      </Typography>
      {results.map((item, index) => (
        <ResultItem key={item.url || index} item={item} />
      ))}
    </Box>
  );
};

export default ResultList;
