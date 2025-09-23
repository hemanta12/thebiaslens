import React from 'react';
import { Stack, Typography, Chip } from '@mui/material';
import { Public } from '@mui/icons-material';
import { ExtractResult } from '../../types/api';

interface ArticleMetadataProps {
  result: ExtractResult;
  formatDate: (dateString?: string) => string | null;
}

const ArticleMetadata: React.FC<ArticleMetadataProps> = ({ result, formatDate }) => {
  return (
    <>
      {/* Prominent Headline - First */}
      {result.headline ? (
        <Typography
          variant="h4"
          component="h2"
          gutterBottom
          sx={{
            fontWeight: 600,
            lineHeight: 1.1,
            mb: 1,
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
      {/* Source and Metadata Row - Combined */}
      <Stack
        direction="row"
        spacing={2}
        alignItems="center"
        sx={{
          mb: 1,
          py: 2,
          backgroundColor: 'grey.50',
          borderRadius: 1,
          border: '1px solid',
          borderColor: 'grey.200',
        }}
      >
        {/* Source chip on the left */}
        <Chip
          icon={<Public />}
          label={result.source}
          color="primary"
          variant="filled"
          sx={{
            fontSize: '0.875rem',
            fontWeight: 600,
          }}
        />

        {/* Metadata items on the right */}
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
    </>
  );
};

export default ArticleMetadata;
