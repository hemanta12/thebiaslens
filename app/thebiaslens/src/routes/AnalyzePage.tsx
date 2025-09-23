import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, Alert, Card, CardContent } from '@mui/material';
import { useSearchParams } from 'react-router-dom';
import { useAnalyze } from '../hooks/useAnalyze';
import UrlForm from '../components/analyze/UrlForm';
import InputTypeSelector from '../components/analyze/InputTypeSelector';
import ArticleTextCard from '../components/analyze/ArticleTextCard';
import { BiasAndSummarySection } from '../components/analyze/BiasAndSummarySection';
import ArticleMetadata from '../components/analyze/ArticleMetadata';
import { formatDate, getPreviewText } from '../utils/textUtils';

const AnalyzePage = () => {
  const [searchParams] = useSearchParams();
  const [inputType, setInputType] = useState<'url' | 'text' | 'pdf'>('url');
  const [currentUrl, setCurrentUrl] = useState('');
  const [showFullText, setShowFullText] = useState(false);

  // Check for URL parameter on component mount
  useEffect(() => {
    const urlParam = searchParams.get('url');
    if (urlParam) {
      setCurrentUrl(urlParam);
    }
  }, [searchParams]);

  const { data: analyzeResult, isLoading, error } = useAnalyze(currentUrl);

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
        {isLoading && (
          <>
            {/* Combined card skeleton for title, metadata, bias and summary */}
            <Card sx={{ mt: 3, boxShadow: 2 }}>
              <CardContent sx={{ p: 3 }}>
                <div className="animate-pulse">
                  {/* Title skeleton */}
                  <div className="h-7 bg-gray-200 rounded w-3/4 mb-2"></div>

                  {/* Source and metadata skeleton */}
                  <div className="flex items-center space-x-2 mb-4">
                    <div className="h-8 bg-blue-200 rounded w-24"></div>
                    <div className="h-4 bg-gray-200 rounded w-20"></div>
                    <div className="h-4 bg-gray-200 rounded w-24"></div>
                  </div>

                  {/* Divider */}
                  <div className="border-t border-gray-200 my-3"></div>

                  {/* Bias and Summary header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="h-6 bg-gray-200 rounded w-40"></div>
                    <div className="w-5 h-5 bg-gray-200 rounded-full"></div>
                  </div>

                  {/* Bias section */}
                  <div className="mb-6">
                    <div className="h-5 bg-gray-200 rounded w-32 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded-full mb-2"></div>
                    <div className="flex justify-between mb-2">
                      <div className="h-3 bg-gray-200 rounded w-20"></div>
                      <div className="h-3 bg-gray-200 rounded w-12"></div>
                      <div className="h-3 bg-gray-200 rounded w-24"></div>
                    </div>
                  </div>

                  {/* Summary section */}
                  <div>
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-full"></div>
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Article text skeleton */}
            <Box sx={{ mt: 3 }}>
              <div className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
                <div className="h-5 bg-gray-200 rounded w-32 mb-4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-full"></div>
                  <div className="h-4 bg-gray-200 rounded w-full"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              </div>
            </Box>
          </>
        )}

        {error && (
          <>
            <Alert severity="error" sx={{ mt: 2 }}>
              Failed to extract content. Please check the URL and try again.
            </Alert>
            {/* Show small error alert for bias and summary analysis failure */}
            <Alert severity="warning" sx={{ mt: 2 }} variant="outlined">
              Bias and summary analysis unavailable for this request.
            </Alert>
          </>
        )}

        {analyzeResult && !isLoading && !error && (
          <>
            {/* Single card with Title, Source, Metadata, Bias and Summary */}
            <Card sx={{ mt: 3, boxShadow: 2 }}>
              <CardContent sx={{ p: 3 }}>
                <ArticleMetadata result={analyzeResult.extract} formatDate={formatDate} />

                {/* Paywall and status messages */}
                {analyzeResult.extract.paywalled && (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    This article appears to be behind a paywall. Content may be limited.
                  </Alert>
                )}
                {analyzeResult.extract.extractStatus !== 'extracted' && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Couldn't fetch full text. You can still proceed with summary later.
                  </Alert>
                )}

                {/* Divider between metadata and bias/summary */}
                <div className="border-t border-gray-200 my-3"></div>

                <BiasAndSummarySection
                  bias={analyzeResult.bias || null}
                  result={analyzeResult.extract}
                  summaryResult={analyzeResult.summary || undefined}
                  isSummarizing={false}
                  summaryError={null}
                  onRegenerate={() => {}} // No regenerate for combined endpoint
                />
              </CardContent>
            </Card>

            {/* Article Text */}
            <ArticleTextCard
              result={analyzeResult.extract}
              showFullText={showFullText}
              onToggleText={handleToggleText}
              getPreviewText={getPreviewText}
            />
          </>
        )}
      </Box>
    </Container>
  );
};

export default AnalyzePage;
