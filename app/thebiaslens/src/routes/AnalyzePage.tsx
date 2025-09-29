import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, Alert, Card, CardContent, Button, Stack } from '@mui/material';
import { useSearchParams } from 'react-router-dom';
import { useAnalyze } from '../hooks/useAnalyze';
import UrlForm from '../components/analyze/UrlForm';
import InputTypeSelector from '../components/analyze/InputTypeSelector';
import ArticleTextCard from '../components/analyze/ArticleTextCard';
import { BiasAndSummarySection } from '../components/analyze/BiasAndSummarySection';
import { FactCheckSection } from '../components/analyze/FactCheckSection';
import ArticleMetadata from '../components/analyze/ArticleMetadata';
import { formatDate, getPreviewText } from '../utils/textUtils';
import SourcesSection from '../components/analyze/SourcesSection';
import { buildAnalyzeLink } from '../lib/links';
import { downloadShareCard } from '../utils/downloadImage';

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
  const [copyLinkSuccess, setCopyLinkSuccess] = useState(false);
  const [downloadImageError, setDownloadImageError] = useState<string | null>(null);

  const handleOpenArticle = () => {
    const target = analyzeResult?.extract.canonicalUrl || currentUrl;
    if (target) window.open(target, '_blank', 'noopener');
  };

  const handleCopyLink = async () => {
    if (!analyzeResult) return;
    const link = buildAnalyzeLink(analyzeResult.id, currentUrl);
    try {
      await navigator.clipboard.writeText(link);
      setCopyLinkSuccess(true);
      setTimeout(() => setCopyLinkSuccess(false), 2000);
    } catch {
      // ignore
    }
  };

  const handleShare = async () => {
    if (!analyzeResult) return;
    const link = buildAnalyzeLink(analyzeResult.id, currentUrl);
    const title = analyzeResult.extract.headline || 'Article Analysis';
    const text = `Bias and summary for ${analyzeResult.extract.source}`;
    if ((navigator as any).share) {
      try {
        await (navigator as any).share({ title, text, url: link });
      } catch {
        // ignored
      }
    } else {
      await navigator.clipboard.writeText(link);
    }
  };

  const handleDownloadImage = async () => {
    if (!analyzeResult) return;

    try {
      setDownloadImageError(null);
      await downloadShareCard(analyzeResult);
    } catch (error) {
      console.error('Download image failed:', error);
      setDownloadImageError(
        'Failed to generate image. If you use content blockers, allow canvas capture and try again.',
      );
    }
  };

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

                  {/* Actions skeleton row */}
                  <div className="flex items-center justify-end mb-4 gap-2">
                    <div className="h-8 bg-gray-200 rounded w-20"></div>
                    <div className="h-8 bg-gray-200 rounded w-24"></div>
                    <div className="h-8 bg-gray-200 rounded w-20"></div>
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
            {/* Download image error alert */}
            {downloadImageError && (
              <Alert
                severity="error"
                sx={{ mt: 2 }}
                onClose={() => setDownloadImageError(null)}
                action={
                  <Button color="inherit" size="small" onClick={handleDownloadImage}>
                    Try Again
                  </Button>
                }
              >
                {downloadImageError}
              </Alert>
            )}

            {/* Single card with Title, Source, Metadata, header actions, Bias and Summary */}
            <Card sx={{ mt: 3, boxShadow: 2 }}>
              <CardContent sx={{ p: 3 }}>
                <ArticleMetadata result={analyzeResult.extract} formatDate={formatDate} />

                {/* Actions row (top-right of card header) */}
                <Stack direction="row" spacing={1} sx={{ justifyContent: 'flex-end', mb: 1 }}>
                  <Button size="small" variant="outlined" onClick={handleOpenArticle}>
                    ↗︎ Open
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleCopyLink}
                    color={copyLinkSuccess ? 'success' : 'primary'}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleCopyLink();
                      }
                    }}
                    tabIndex={0}
                    aria-label={
                      copyLinkSuccess
                        ? 'Link copied to clipboard'
                        : 'Copy analysis link to clipboard'
                    }
                  >
                    {copyLinkSuccess ? '✅ Copied!' : '🔗 Copy Link'}
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleDownloadImage}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleDownloadImage();
                      }
                    }}
                    tabIndex={0}
                    aria-label="Download analysis as image"
                  >
                    💾 Download Image
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleShare}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleShare();
                      }
                    }}
                    tabIndex={0}
                    aria-label="Share analysis"
                  >
                    📤 Share
                  </Button>
                </Stack>

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

            {/* Separate Fact Check Card */}
            <FactCheckSection
              headline={analyzeResult.extract.headline || analyzeResult.extract.url}
              sourceDomain={(() => {
                try {
                  return new URL(analyzeResult.extract.url).hostname;
                } catch {
                  return undefined;
                }
              })()}
              summary={analyzeResult.summary?.joined}
            />

            {/* Article Text */}
            <ArticleTextCard
              result={analyzeResult.extract}
              showFullText={showFullText}
              onToggleText={handleToggleText}
              getPreviewText={getPreviewText}
            />

            {/* Sources & Citations */}
            <SourcesSection
              sourceDomain={analyzeResult.extract.source}
              canonicalUrl={
                analyzeResult.extract.canonicalUrl || analyzeResult.canonicalUrl || currentUrl
              }
              bodyText={analyzeResult.extract.body}
            />

            {/* Disclaimer */}
            <Box sx={{ mt: 3, color: 'text.secondary', fontSize: '12.5px', lineHeight: 1.7 }}>
              Bias and fact-check estimations are AI-generated and may not be fully accurate. This
              is for informational purposes only.
            </Box>
          </>
        )}
      </Box>
    </Container>
  );
};

export default AnalyzePage;
