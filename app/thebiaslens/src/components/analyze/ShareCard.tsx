import React from 'react';
import { Box, Typography } from '@mui/material';
import { AnalyzeResult, BiasLabel } from '../../types/api';

interface ShareCardProps {
  data: AnalyzeResult;
}

// Bias styling constants for share card
const biasTokens = {
  trackGradient: 'linear-gradient(90deg, #b8d3f0 0%, #d9dee4 50%, #f2c5c5 100%)',
  needleColor: {
    Left: '#2563eb', // blue-600
    Neutral: '#4b5563', // gray-600
    Right: '#dc2626', // red-600
  } satisfies Record<BiasLabel, string>,
};

export const ShareCard: React.FC<ShareCardProps> = ({ data }) => {
  const { extract, bias, summary } = data;

  // Get domain from source or URL
  const domain =
    extract.source ||
    (() => {
      try {
        return new URL(extract.url).hostname;
      } catch {
        return 'Unknown Source';
      }
    })();

  const title = extract.headline || 'Article Analysis';

  // Bias calculation
  const scoreOrZero = bias?.score ?? 0;
  const label = bias?.label ?? 'Neutral';
  const confidence = bias?.confidence ?? 0;
  // For null bias, center the needle at 50%
  const percent = bias === null ? 50 : ((scoreOrZero + 1) / 2) * 100; // Convert [-1,1] to [0,100]

  // Summary text (200-260 chars, strip newlines)
  const summaryText = summary?.joined
    ? summary.joined.replace(/\n/g, ' ').substring(0, 260).trim() +
      (summary.joined.length > 260 ? '...' : '')
    : '';

  return (
    <Box
      sx={{
        width: '1200px',
        height: '630px',
        backgroundColor: '#ffffff',
        padding: '60px',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        position: 'relative',
        boxSizing: 'border-box',
      }}
    >
      {/* Source domain */}
      <Typography
        sx={{
          fontSize: '22px',
          color: '#6b7280',
          marginBottom: '8px',
          fontWeight: 400,
        }}
      >
        {domain}
      </Typography>

      {/* Title (max 3 lines) */}
      <Typography
        sx={{
          fontSize: '42px',
          fontWeight: 700,
          color: '#111827',
          lineHeight: 1.15,
          marginBottom: '20px',
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          height: '165px', // Height for 3 lines: 48px * 1.15 * 3 = ~165px
          wordBreak: 'break-word',
          hyphens: 'auto',
        }}
      >
        {title}
      </Typography>

      {/* Bias line */}
      <Typography
        sx={{
          fontSize: '26px',
          color: '#374151',
          marginBottom: '8px',
          fontWeight: 400,
        }}
      >
        {bias === null
          ? 'Bias: Neutral (not computed)'
          : `Bias: ${label} (${Math.round(confidence * 100)}% confidence)`}
      </Typography>

      {/* Bias meter container */}
      <Box sx={{ marginBottom: '18px' }}>
        {/* Meter track */}
        <Box
          sx={{
            position: 'relative',
            height: '12px',
            borderRadius: '6px',
            background: biasTokens.trackGradient,
            marginBottom: '8px',
            width: '100%',
          }}
        >
          {/* Needle */}
          <Box
            sx={{
              position: 'absolute',
              top: '-2px',
              left: `${percent}%`,
              transform: 'translateX(-50%)',
              width: '2px',
              height: '16px',
              backgroundColor: biasTokens.needleColor[label],
              borderRadius: '1px',
              boxShadow: '0 2px 4px 0 rgba(0, 0, 0, 0.15)',
            }}
          />
        </Box>

        {/* Labels */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '16px',
            color: '#6b7280',
            fontWeight: 500,
          }}
        >
          <span>Left (liberal)</span>
          <span>Neutral</span>
          <span>Right (conservative)</span>
        </Box>
      </Box>

      {/* Summary text */}
      {summaryText && (
        <Typography
          sx={{
            fontSize: '24px',
            color: '#374151',
            lineHeight: 1.45,
            marginTop: '10px',
            display: '-webkit-box',
            WebkitLineClamp: 4,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            height: '140px', // Precise height for 4 lines: 24px * 1.45 * 4 = 139.2px
          }}
        >
          {summaryText}
        </Typography>
      )}

      {/* Site name in corner */}
      <Typography
        sx={{
          position: 'absolute',
          bottom: '60px',
          right: '60px',
          fontSize: '20px',
          color: '#9ca3af',
          fontWeight: 400,
        }}
      >
        TheBiasLens
      </Typography>
    </Box>
  );
};
