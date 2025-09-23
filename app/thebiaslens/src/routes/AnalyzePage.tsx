import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, Alert } from '@mui/material';
import { useSearchParams } from 'react-router-dom';
import { useExtract } from '../hooks/useExtract';
import { useSummarize } from '../hooks/useSummarize';
import UrlForm from '../components/analyze/UrlForm';
import ResultSkeleton from '../components/ResultSkeleton';
import InputTypeSelector from '../components/analyze/InputTypeSelector';
import ExtractResultCard from '../components/analyze/ExtractResultCard';
import { formatDate, getPreviewText } from '../utils/textUtils';

const AnalyzePage = () => {
  const [searchParams] = useSearchParams();
  const [inputType, setInputType] = useState<'url' | 'text' | 'pdf'>('url');
  const [currentUrl, setCurrentUrl] = useState('');
  const [showFullText, setShowFullText] = useState(false);
  const [summaryEnabled, setSummaryEnabled] = useState(false);

  // Check for URL parameter on component mount
  useEffect(() => {
    const urlParam = searchParams.get('url');
    if (urlParam) {
      setCurrentUrl(urlParam);
      setSummaryEnabled(true);
    }
  }, [searchParams]);

  const { data: extractResult, isLoading, error } = useExtract(currentUrl);
  const {
    data: summaryResult,
    isLoading: isSummarizing,
    error: summaryError,
    refetch: refetchSummary,
  } = useSummarize(extractResult?.body || '', summaryEnabled && !!extractResult?.body);

  const handleInputTypeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newInputType: 'url' | 'text' | 'pdf',
  ) => {
    if (newInputType && newInputType === 'url') {
      setInputType(newInputType);
    }
  };

  const handleUrlSubmit = (url: string) => {
    setCurrentUrl(url);
    setShowFullText(false);
    setSummaryEnabled(true);
  };

  const handleToggleText = () => {
    setShowFullText(!showFullText);
  };

  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      {/* Enhanced Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600, mb: 1 }}>
          Analyze Content
        </Typography>

        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ fontSize: '1.1rem', lineHeight: 1.6 }}
        >
          Extract and analyze news articles for bias detection and summarization.
        </Typography>
      </Box>

      <InputTypeSelector inputType={inputType} onInputTypeChange={handleInputTypeChange} />

      {/* URL input form */}
      {inputType === 'url' && (
        <UrlForm onSubmit={handleUrlSubmit} isLoading={isLoading} value={currentUrl} />
      )}

      {/* Results area */}
      <Box sx={{ mt: 3 }}>
        {isLoading && <ResultSkeleton />}

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Failed to extract content. Please check the URL and try again.
          </Alert>
        )}

        {extractResult && !isLoading && !error && (
          <ExtractResultCard
            result={extractResult}
            summaryResult={summaryResult}
            isSummarizing={isSummarizing}
            summaryError={summaryError}
            showFullText={showFullText}
            onToggleText={handleToggleText}
            onRegenerate={refetchSummary}
            formatDate={formatDate}
            getPreviewText={getPreviewText}
          />
        )}
      </Box>
    </Container>
  );
};

export default AnalyzePage;
