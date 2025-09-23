import React, { useState } from 'react';
import { Box, TextField, Button } from '@mui/material';

interface UrlFormProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
}

const UrlForm: React.FC<UrlFormProps> = ({ onSubmit, isLoading }) => {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSubmit(url.trim());
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}
    >
      <TextField
        fullWidth
        label="Article URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://example.com/article"
        helperText="Enter a news article URL to extract and analyze"
        variant="outlined"
      />
      <Button
        type="submit"
        variant="contained"
        disabled={!url.trim() || isLoading}
        sx={{ mt: 0, minWidth: 100, height: 56 }}
      >
        {isLoading ? 'Fetching...' : 'Fetch'}
      </Button>
    </Box>
  );
};

export default UrlForm;
