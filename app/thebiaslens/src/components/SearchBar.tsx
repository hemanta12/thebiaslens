import React from 'react';
import { Box, TextField, Button } from '@mui/material';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

const SearchBar = ({ value, onChange, onSubmit }: SearchBarProps) => {
  return (
    <Box component="form" onSubmit={onSubmit}>
      <TextField
        fullWidth
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search for news topics..."
        variant="outlined"
        InputProps={{
          endAdornment: (
            <Button type="submit" variant="contained" sx={{ ml: 1 }} disabled={!value.trim()}>
              Search
            </Button>
          ),
        }}
      />
    </Box>
  );
};

export default SearchBar;
