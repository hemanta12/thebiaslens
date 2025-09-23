import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import AnalyzePage from './AnalyzePage';
import { Container, Box, Typography, TextField, Button, Alert } from '@mui/material';

// A thin wrapper route that reads :id and optional ?url=
// - If url is missing, prompt user to paste the URL
// - If present, we just render the AnalyzePage which already reads ?url=
const AnalyzePageById: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const urlParam = searchParams.get('url') || '';

  const [inputUrl, setInputUrl] = useState(urlParam);
  const [touched, setTouched] = useState(false);

  useEffect(() => {
    // Keep local input in sync with query param
    if (urlParam && urlParam !== inputUrl) {
      setInputUrl(urlParam);
    }
  }, [urlParam, inputUrl]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    const v = inputUrl.trim();
    if (v.length < 8) return;
    // set ?url= and let AnalyzePage consume it
    setSearchParams((prev) => {
      const sp = new URLSearchParams(prev);
      sp.set('url', v);
      return sp;
    });
  };

  // If we have url, render AnalyzePage (it reads ?url= itself)
  if (urlParam) {
    return <AnalyzePage />;
  }

  // Missing url -> prompt user
  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
          Provide the article URL
        </Typography>
        <Typography variant="body2" color="text.secondary">
          The analysis id "{id}" requires the original URL to proceed.
        </Typography>
      </Box>

      {touched && inputUrl.trim().length < 8 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Please paste a valid article URL.
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="https://example.com/news-article"
          value={inputUrl}
          onChange={(e) => setInputUrl(e.target.value)}
        />
        <Button type="submit" variant="contained" size="small">
          Analyze
        </Button>
      </Box>

      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Note: For now, the id cannot be reversed without the URL.
        </Typography>
      </Box>
    </Container>
  );
};

export default AnalyzePageById;
