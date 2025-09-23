import React from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { Refresh, ContentCopy } from '@mui/icons-material';
import { SummaryResult } from '../../types/api';

interface SummarySectionProps {
  result: { body?: string; extractStatus: string };
  summaryResult?: SummaryResult;
  isSummarizing: boolean;
  summaryError: any;
  onRegenerate: () => void;
}

const SummarySection: React.FC<SummarySectionProps> = ({
  result,
  summaryResult,
  isSummarizing,
  summaryError,
  onRegenerate,
}) => {
  if (!result.body || result.extractStatus !== 'extracted') {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      {/* Show skeleton while summarizing */}
      {isSummarizing && (
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
              Generating Summary
            </Typography>
            <CircularProgress size={20} sx={{ ml: 2 }} />
          </Box>
          <Box
            sx={{
              height: 100,
              bgcolor: 'grey.100',
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'grey.200',
            }}
          />
        </Box>
      )}

      {/* Show error if summarization failed */}
      {summaryError && !isSummarizing && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to generate summary. Please try again.
        </Alert>
      )}

      {/* Show summary card if available */}
      {summaryResult && !isSummarizing && !summaryError && (
        <Box sx={{ mb: 3 }}>
          <Box
            sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}
          >
            <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
              Summary
            </Typography>
            <Box>
              <Button
                size="small"
                startIcon={<Refresh fontSize="small" />}
                onClick={onRegenerate}
                disabled={isSummarizing}
                sx={{ fontSize: '0.75rem', mr: 1 }}
              >
                Regenerate (lead-3)
              </Button>
              <Button
                size="small"
                startIcon={<ContentCopy fontSize="small" />}
                onClick={() => {
                  navigator.clipboard.writeText(summaryResult.joined);
                }}
                sx={{ minWidth: 'auto' }}
              >
                Copy
              </Button>
            </Box>
          </Box>

          <Box
            sx={{
              backgroundColor: 'grey.50',
              p: 2,
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'grey.100',
            }}
          >
            {summaryResult.sentences.length > 1 ? (
              <List disablePadding dense>
                {summaryResult.sentences.map((sentence, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={sentence}
                      primaryTypographyProps={{
                        variant: 'body1',
                        sx: { lineHeight: 1.6, color: 'text.primary' },
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body1" sx={{ lineHeight: 1.8, color: 'text.primary' }}>
                {summaryResult.joined}
              </Typography>
            )}
          </Box>

          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            {summaryResult.wordCount} words · {summaryResult.charCount} characters · Lead-3 summary
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SummarySection;
