import React from 'react';
import { Box, ToggleButtonGroup, ToggleButton } from '@mui/material';
import { Article, TextSnippet, PictureAsPdf } from '@mui/icons-material';

interface InputTypeSelectorProps {
  inputType: 'url' | 'text' | 'pdf';
  onInputTypeChange: (
    _event: React.MouseEvent<HTMLElement>,
    newInputType: 'url' | 'text' | 'pdf',
  ) => void;
}

const InputTypeSelector: React.FC<InputTypeSelectorProps> = ({ inputType, onInputTypeChange }) => {
  return (
    <Box sx={{ mb: 3 }}>
      <ToggleButtonGroup
        value={inputType}
        exclusive
        onChange={onInputTypeChange}
        aria-label="input type"
      >
        <ToggleButton value="url" aria-label="url input">
          <Article sx={{ mr: 1 }} />
          URL
        </ToggleButton>
        <ToggleButton value="text" disabled aria-label="text input">
          <TextSnippet sx={{ mr: 1 }} />
          Text
        </ToggleButton>
        <ToggleButton value="pdf" disabled aria-label="pdf input">
          <PictureAsPdf sx={{ mr: 1 }} />
          PDF
        </ToggleButton>
      </ToggleButtonGroup>
    </Box>
  );
};

export default InputTypeSelector;
