import React, { useState } from 'react';
import { Box, TextField, Button, IconButton, InputAdornment } from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';

interface UrlFormProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
  value?: string;
}

const UrlForm: React.FC<UrlFormProps> = ({ onSubmit, isLoading, value = '' }) => {
  const [url, setUrl] = useState(value);

  // Update internal state when value prop changes
  React.useEffect(() => {
    setUrl(value);
  }, [value]);

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
        InputProps={{
          endAdornment: url ? (
            <InputAdornment position="end">
              <IconButton aria-label="Clear URL" onClick={() => setUrl('')} size="small" edge="end">
                <ClearIcon fontSize="small" />
              </IconButton>
            </InputAdornment>
          ) : null,
        }}
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
