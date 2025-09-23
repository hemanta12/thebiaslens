import React from 'react';
import { Box, Divider, Typography, Button } from '@mui/material';

interface ArticleTextSectionProps {
  result: { body?: string };
  showFullText: boolean;
  onToggleText: () => void;
  getPreviewText: (text: string, maxLength?: number) => string;
}

const ArticleTextSection: React.FC<ArticleTextSectionProps> = ({
  result,
  showFullText,
  onToggleText,
  getPreviewText,
}) => {
  const hasContent = result.body && result.body.length > 0;
  const previewText = hasContent ? getPreviewText(result.body!, 400) : '';
  const showExpandButton = hasContent && result.body!.length > 400;

  if (!hasContent) {
    return null;
  }

  return (
    <Box>
      <Divider sx={{ mb: 2 }} />
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
        }}
      >
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          Extracted Article Text
        </Typography>
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
        {/* Render paragraphs for better readability */}
        {(() => {
          const text = showFullText ? result.body || '' : previewText;

          // First try to split by double newlines (proper paragraphs)
          let paragraphs = text
            .split(/\n\s*\n+|\r\n\s*\r\n+|\n\n+|\r\n\r\n+/)
            .filter((para) => para.trim().length > 0);

          // If we only get one paragraph, try splitting by single newlines and group by sentence count
          if (paragraphs.length === 1) {
            const sentences = text
              .split(/[.!?]+\s+/)
              .filter((sentence) => sentence.trim().length > 0);

            // Group sentences into paragraphs (approximately 3-4 sentences per paragraph)
            paragraphs = [];
            for (let i = 0; i < sentences.length; i += 3) {
              const paragraph = sentences.slice(i, i + 3).join('. ');
              if (paragraph.trim()) {
                paragraphs.push(paragraph + (paragraph.endsWith('.') ? '' : '.'));
              }
            }
          }

          return paragraphs.slice(0, showFullText ? undefined : 4).map((para, idx) => (
            <Typography
              key={idx}
              variant="body1"
              paragraph
              sx={{
                lineHeight: 1.8,
                fontSize: '1rem',
                color: 'text.primary',
                mb: 2,
                '&:last-child': { mb: 0 },
              }}
            >
              {para.trim()}
            </Typography>
          ));
        })()}

        {showExpandButton && (
          <Button
            onClick={onToggleText}
            variant="text"
            size="small"
            sx={{ mt: 2, fontWeight: 600 }}
          >
            {showFullText ? 'Show less' : 'Show more'}
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default ArticleTextSection;
