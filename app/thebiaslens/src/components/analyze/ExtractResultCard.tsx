import React from 'react';
import { Card, CardContent, Alert } from '@mui/material';
import { ExtractResult } from '../../types/api';
import ArticleMetadata from './ArticleMetadata';

interface ExtractResultCardProps {
  result: ExtractResult;
  formatDate: (dateString?: string) => string | null;
}

const ExtractResultCard: React.FC<ExtractResultCardProps> = ({ result, formatDate }) => {
  return (
    <Card sx={{ mt: 3, boxShadow: 2 }}>
      <CardContent sx={{ p: 3 }}>
        <ArticleMetadata result={result} formatDate={formatDate} />

        {/* Paywall and status messages */}
        {result.paywalled && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            This article appears to be behind a paywall. Content may be limited.
          </Alert>
        )}
        {result.extractStatus !== 'extracted' && (
          <Alert severity="info" sx={{ mb: 0 }}>
            Couldn't fetch full text. You can still proceed with summary later.
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ExtractResultCard;
