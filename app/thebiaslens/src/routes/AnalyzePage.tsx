import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  Alert,
  Card,
  CardContent,
  Chip,
  Button,
  Divider,
  Stack,
} from '@mui/material';
import { Article, TextSnippet, PictureAsPdf, Public } from '@mui/icons-material';
import { useExtract } from '../hooks/useExtract';
import { ExtractResult } from '../types/api';
import UrlForm from '../components/analyze/UrlForm';
import ResultSkeleton from '../components/ResultSkeleton';

const AnalyzePage = () => {
  const [inputType, setInputType] = useState<'url' | 'text' | 'pdf'>('url');
  const [currentUrl, setCurrentUrl] = useState('');
  const [showFullText, setShowFullText] = useState(false);

  const { data: extractResult, isLoading, error } = useExtract(currentUrl);

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

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const getPreviewText = (text: string, maxLength: number = 600) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  };

  const renderExtractResult = (result: ExtractResult) => {
    const hasContent = result.body && result.body.length > 0;
    const previewText = hasContent ? getPreviewText(result.body!, 400) : ''; // Shorter preview
    const showExpandButton = hasContent && result.body!.length > 400;

    return (
      <Card sx={{ mt: 3, boxShadow: 2 }}>
        <CardContent sx={{ p: 3 }}>
          {/* Prominent Source Badge */}
          <Box sx={{ mb: 2 }}>
            <Chip
              icon={<Public />}
              label={result.source}
              color="primary"
              variant="filled"
              sx={{
                fontSize: '0.875rem',
                fontWeight: 600,
                mb: 2,
              }}
            />
          </Box>

          {/* Prominent Headline */}
          {result.headline ? (
            <Typography
              variant="h4"
              component="h2"
              gutterBottom
              sx={{
                fontWeight: 600,
                lineHeight: 1.3,
                mb: 3,
                color: 'text.primary',
              }}
            >
              {result.headline}
            </Typography>
          ) : (
            <Typography variant="subtitle1" gutterBottom sx={{ color: 'text.secondary', mb: 3 }}>
              Title not available
            </Typography>
          )}

          {/* Metadata Row */}
          <Stack
            direction="row"
            spacing={2}
            alignItems="center"
            sx={{
              mb: 3,
              p: 2,
              backgroundColor: 'grey.50',
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'grey.200',
            }}
          >
            {result.publishedAt && (
              <Typography variant="body2" color="text.secondary">
                📅 {formatDate(result.publishedAt)}
              </Typography>
            )}
            {result.author && (
              <Typography variant="body2" color="text.secondary">
                ✍️ {result.author}
              </Typography>
            )}
            <Typography variant="body2" color="text.secondary">
              📊 {result.wordCount.toLocaleString()} words
            </Typography>
            <Chip
              label={result.extractStatus}
              size="small"
              color={result.extractStatus === 'extracted' ? 'success' : 'warning'}
              variant="outlined"
            />
          </Stack>

          {/* Paywall and status messages */}
          {result.paywalled && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              This article appears to be behind a paywall. Content may be limited.
            </Alert>
          )}
          {result.extractStatus !== 'extracted' && (
            <Alert severity="info" sx={{ mb: 3 }}>
              Couldn't fetch full text. You can still proceed with summary later.
            </Alert>
          )}

          {/* Content Preview Section */}
          {hasContent && (
            <Box>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                Extracted Article Text
              </Typography>

              <Box
                sx={{
                  backgroundColor: 'grey.50',
                  p: 2,
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'grey.100',
                }}
              >
                {/* Render paragraphs for better readability */}
                {(showFullText ? result.body || '' : previewText)
                  .split(/\n\s*\n|\r\n\r\n/)
                  .filter(Boolean)
                  .slice(0, showFullText ? undefined : 4)
                  .map((para, idx) => (
                    <Typography
                      key={idx}
                      variant="body1"
                      paragraph
                      sx={{ lineHeight: 1.8, fontSize: '1rem', color: 'text.primary' }}
                    >
                      {para.trim()}
                    </Typography>
                  ))}

                {showExpandButton && (
                  <Button
                    onClick={() => setShowFullText(!showFullText)}
                    variant="text"
                    size="small"
                    sx={{ mt: 2, fontWeight: 600 }}
                  >
                    {showFullText ? 'Show less' : 'Show more'}
                  </Button>
                )}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>
    );
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

      {/* Input type selector */}
      <Box sx={{ mb: 3 }}>
        <ToggleButtonGroup
          value={inputType}
          exclusive
          onChange={handleInputTypeChange}
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

      {/* URL input form */}
      {inputType === 'url' && <UrlForm onSubmit={handleUrlSubmit} isLoading={isLoading} />}

      {/* Results area */}
      <Box sx={{ mt: 3 }}>
        {isLoading && <ResultSkeleton />}

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Failed to extract content. Please check the URL and try again.
          </Alert>
        )}

        {extractResult && !isLoading && !error && renderExtractResult(extractResult)}
      </Box>
    </Container>
  );
};

export default AnalyzePage;
