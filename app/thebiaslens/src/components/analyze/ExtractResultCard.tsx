import React from 'react';
import { Card, CardContent, Alert } from '@mui/material';
import { ExtractResult, SummaryResult } from '../../types/api';
import ArticleMetadata from './ArticleMetadata';
import SummarySection from './SummarySection';
import ArticleTextSection from './ArticleTextSection';

interface ExtractResultCardProps {
  result: ExtractResult;
  summaryResult?: SummaryResult;
  isSummarizing: boolean;
  summaryError: any;
  showFullText: boolean;
  onToggleText: () => void;
  onRegenerate: () => void;
  formatDate: (dateString?: string) => string | null;
  getPreviewText: (text: string, maxLength?: number) => string;
}

const ExtractResultCard: React.FC<ExtractResultCardProps> = ({
  result,
  summaryResult,
  isSummarizing,
  summaryError,
  showFullText,
  onToggleText,
  onRegenerate,
  formatDate,
  getPreviewText,
}) => {
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
          <Alert severity="info" sx={{ mb: 3 }}>
            Couldn't fetch full text. You can still proceed with summary later.
          </Alert>
        )}

        <SummarySection
          result={result}
          summaryResult={summaryResult}
          isSummarizing={isSummarizing}
          summaryError={summaryError}
          onRegenerate={onRegenerate}
        />

        <ArticleTextSection
          result={result}
          showFullText={showFullText}
          onToggleText={onToggleText}
          getPreviewText={getPreviewText}
        />
      </CardContent>
    </Card>
  );
};

export default ExtractResultCard;
