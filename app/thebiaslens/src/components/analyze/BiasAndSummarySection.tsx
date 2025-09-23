import React, { useState } from 'react';
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
import { BiasResult, SummaryResult } from '../../types/api';
import { BiasMeter } from './BiasMeter';
import { BiasLegend } from './BiasLegend';

interface BiasAndSummarySectionProps {
  bias: BiasResult | null;
  result: { body?: string; extractStatus: string };
  summaryResult?: SummaryResult;
  isSummarizing: boolean;
  summaryError: any;
  onRegenerate: () => void;
}

export const BiasAndSummarySection: React.FC<BiasAndSummarySectionProps> = ({
  bias,
  result,
  summaryResult,
  isSummarizing,
  summaryError,
  onRegenerate,
}) => {
  const [showLegend, setShowLegend] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopyText = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <>
      <Box>
        {/* Section Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
            Bias and Summary
          </Typography>
          <button
            onClick={() => setShowLegend(true)}
            className="text-gray-400 hover:text-gray-600 w-5 h-5 flex items-center justify-center rounded-full border border-gray-300 hover:border-gray-400 transition-colors"
            aria-label="Show bias analysis legend"
            title="Learn about bias analysis"
          >
            <span className="text-xs font-medium">?</span>
          </button>
        </Box>

        {/* Bias Meter */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" component="h3" sx={{ fontWeight: 600, mb: 1 }}>
            Bias
          </Typography>
          <BiasMeter bias={bias} />
        </Box>

        {/* Summary Section */}
        {result.body && result.extractStatus === 'extracted' && (
          <Box>
            {/* Show skeleton while summarizing */}
            {isSummarizing && (
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body1">Generating Summary</Typography>
                  <CircularProgress size={20} sx={{ ml: 2 }} />
                </Box>
                <Box
                  sx={{
                    height: 100,
                    bgcolor: 'grey.100',
                    borderRadius: 1,
                    border: '1px solid',
                    borderColor: 'grey.300',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <CircularProgress />
                </Box>
              </Box>
            )}

            {/* Show error if summarization failed */}
            {summaryError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                <Box>
                  Summary generation failed. Please try again.
                  <Button
                    size="small"
                    startIcon={<Refresh />}
                    onClick={onRegenerate}
                    sx={{ ml: 2 }}
                  >
                    Retry
                  </Button>
                </Box>
              </Alert>
            )}

            {/* Show summary if available */}
            {summaryResult && !isSummarizing && (
              <Box sx={{ mb: 2 }}>
                <Box
                  sx={{
                    p: 0,
                    borderRadius: 0,
                    border: 'none',
                  }}
                >
                  <List sx={{ p: 0 }}>
                    {summaryResult.sentences.map((sentence, index) => (
                      <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                        <ListItemText
                          primary={sentence}
                          primaryTypographyProps={{
                            variant: 'body1',
                            sx: { lineHeight: 1.6 },
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>

                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      mt: 1.5,
                      pt: 1.5,
                      borderTop: '1px solid',
                      borderColor: 'grey.200',
                    }}
                  >
                    <Typography variant="caption" color="text.secondary">
                      {summaryResult.sentences.length} sentences • {summaryResult.wordCount} words •{' '}
                      {summaryResult.charCount} characters
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        startIcon={<ContentCopy />}
                        onClick={() => handleCopyText(summaryResult.joined)}
                        variant="outlined"
                        color={copySuccess ? 'success' : 'primary'}
                      >
                        {copySuccess ? 'Copied!' : 'Copy'}
                      </Button>
                      <Button
                        size="small"
                        startIcon={<Refresh />}
                        onClick={onRegenerate}
                        variant="outlined"
                      >
                        Regenerate
                      </Button>
                    </Box>
                  </Box>
                </Box>
              </Box>
            )}
          </Box>
        )}
      </Box>

      {/* Legend modal */}
      <BiasLegend isOpen={showLegend} onClose={() => setShowLegend(false)} />
    </>
  );
};
