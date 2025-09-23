import React from 'react';
import { Card, CardContent } from '@mui/material';
import { ExtractResult } from '../../types/api';
import ArticleTextSection from './ArticleTextSection';

interface ArticleTextCardProps {
  result: ExtractResult;
  showFullText: boolean;
  onToggleText: () => void;
  getPreviewText: (text: string, maxLength?: number) => string;
}

const ArticleTextCard: React.FC<ArticleTextCardProps> = ({
  result,
  showFullText,
  onToggleText,
  getPreviewText,
}) => {
  return (
    <Card sx={{ mt: 3, boxShadow: 2 }}>
      <CardContent sx={{ p: 3 }}>
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

export default ArticleTextCard;
