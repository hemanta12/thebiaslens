import React, { useState } from 'react';
import { Card, Typography, Tooltip, IconButton } from '@mui/material';
import { HelpOutline } from '@mui/icons-material';
import { useFactCheck } from '../../hooks/useFactCheck';
import { FACTCHECK_COPY } from '../../copy/factcheck';
import type { FactCheckItem as FactCheckItemType } from '../../types/api';

interface FactCheckSectionProps {
  headline: string;
  sourceDomain?: string;
  summary?: string;
}

const VerdictChip: React.FC<{ verdict?: string | null }> = ({ verdict }) => {
  if (!verdict) return null;

  const getVerdictStyle = (verdict: string) => {
    switch (verdict.toLowerCase()) {
      case 'true':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'false':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'mixed':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'unverified':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'unknown':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getVerdictStyle(verdict)}`}
    >
      {verdict}
    </span>
  );
};

const RelationBadge: React.FC<{ matchReason?: string }> = ({ matchReason }) => {
  const getMatchReasonText = (reason?: string) => {
    if (!reason) return FACTCHECK_COPY.matchReasons.keywords;

    // Check if we have a mapping for this reason
    const reasonKey = reason as keyof typeof FACTCHECK_COPY.matchReasons;
    return FACTCHECK_COPY.matchReasons[reasonKey] || FACTCHECK_COPY.matchReasons.keywords;
  };

  const getBadgeStyle = (reason?: string) => {
    if (!reason) return 'bg-gray-100 text-gray-700 border-gray-200';

    switch (reason) {
      case 'highly_related':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'moderately_related':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'somewhat_related':
        return 'bg-slate-100 text-slate-700 border-slate-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${getBadgeStyle(matchReason)}`}
    >
      {getMatchReasonText(matchReason)}
    </span>
  );
};

const FactCheckItemComponent: React.FC<{ item: FactCheckItemType }> = ({ item }) => {
  const similarityPercentage = item.similarityPercentage || 50;

  const getRelationLevel = (percentage: number): string => {
    if (percentage > 75) return 'highly_related';
    if (percentage >= 30) return 'moderately_related';
    return 'somewhat_related';
  };

  const relationLevel = getRelationLevel(similarityPercentage);

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'Recent';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return 'Recent';
    }
  };

  const extractKeyTerms = (claim: string) => {
    const words = claim
      .split(' ')
      .filter((word) => word.length > 4)
      .slice(0, 2)
      .map((word) => word.replace(/[^\w\s]/gi, ''));
    return words;
  };

  const keyTerms = extractKeyTerms(item.claim);

  return (
    <div className="border border-gray-200 rounded-lg p-3 space-y-3 hover:border-gray-300 hover:shadow-sm transition-all duration-200 bg-gradient-to-r from-gray-50/30 to-white">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2 flex-wrap">
            <VerdictChip verdict={item.verdict} />
            <RelationBadge matchReason={relationLevel} />
            <span className="text-gray-500 text-xs font-medium">{similarityPercentage}% match</span>
          </div>
          {item.source && (
            <div className="flex items-center gap-1 text-xs text-gray-600">
              <span className="font-medium">{item.source}</span>
              <span className="text-gray-400">•</span>
              <span>{formatDate(item.publishedAt)}</span>
            </div>
          )}
        </div>
      </div>

      <div>
        <p
          className="text-sm text-gray-900 leading-relaxed"
          style={{
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          "{item.claim}"
        </p>
      </div>

      {keyTerms.length > 0 && (
        <div className="flex items-center gap-2 text-xs">
          <span className="text-gray-500 font-medium">Key terms:</span>
          <div className="flex gap-1 flex-wrap">
            {keyTerms.map((term, index) => (
              <span
                key={index}
                className="px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium"
              >
                {term}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between pt-1 border-t border-gray-100">
        <span className="text-xs text-gray-500">Check scope & methodology</span>
        {item.url && (
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors flex items-center gap-1"
          >
            {FACTCHECK_COPY.readFullCheckLabel}
          </a>
        )}
      </div>
    </div>
  );
};

const SkeletonItem: React.FC = () => (
  <div className="border rounded-lg p-4 space-y-4 animate-pulse">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-16 h-6 bg-gray-200 rounded-full"></div>
        <div className="w-20 h-4 bg-gray-200 rounded"></div>
        <div className="w-1 h-1 bg-gray-200 rounded-full"></div>
        <div className="w-12 h-4 bg-gray-200 rounded"></div>
      </div>
    </div>

    <div className="w-24 h-3 bg-gray-200 rounded"></div>
    <div>
      <div className="w-20 h-3 bg-gray-200 rounded mb-2"></div>
      <div className="space-y-1">
        <div className="w-full h-4 bg-gray-200 rounded"></div>
        <div className="w-3/4 h-4 bg-gray-200 rounded"></div>
      </div>
    </div>

    {/* Relation section skeleton */}
    <div>
      <div className="w-32 h-3 bg-gray-200 rounded mb-2"></div>
      <div className="flex items-center gap-3 mb-2">
        <div className="w-20 h-6 bg-gray-200 rounded"></div>
        <div className="w-24 h-4 bg-gray-200 rounded"></div>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-24 h-3 bg-gray-200 rounded"></div>
        <div className="w-16 h-5 bg-gray-200 rounded"></div>
        <div className="w-20 h-5 bg-gray-200 rounded"></div>
        <div className="w-18 h-5 bg-gray-200 rounded"></div>
      </div>
    </div>

    <div className="flex items-center justify-between pt-2">
      <div className="w-12 h-3 bg-gray-200 rounded"></div>
      <div className="w-24 h-4 bg-gray-200 rounded"></div>
    </div>
  </div>
);

export const FactCheckSection: React.FC<FactCheckSectionProps> = ({
  headline,
  sourceDomain,
  summary,
}) => {
  const { data, isLoading, error } = useFactCheck({ headline, sourceDomain, summary });
  const [showDetailedInfo, setShowDetailedInfo] = useState(false);

  const sectionId = 'factcheck-section';

  return (
    <Card sx={{ mb: 3, mt: 3 }}>
      <div className="p-4">
        <div className="mb-4">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex items-center gap-2">
              <div className="w-2 h-6 bg-gradient-to-b from-blue-500 to-green-500 rounded-full"></div>
              <Typography
                variant="h6"
                component="h3"
                sx={{ fontWeight: 600 }}
                id={sectionId}
                className="text-gray-800"
              >
                {FACTCHECK_COPY.title}
              </Typography>
            </div>
            <Tooltip
              title={showDetailedInfo ? FACTCHECK_COPY.detailedSubtitle : 'Click for more details'}
              arrow
            >
              <IconButton
                size="small"
                onClick={() => setShowDetailedInfo(!showDetailedInfo)}
                className="text-gray-400 hover:text-gray-600"
              >
                <HelpOutline fontSize="small" />
              </IconButton>
            </Tooltip>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-green-50 border border-blue-100 rounded-lg p-3 mb-3">
            <p className="text-sm text-gray-700 mb-1 font-medium">
              {showDetailedInfo ? FACTCHECK_COPY.detailedSubtitle : FACTCHECK_COPY.subtitle}
            </p>
            <p className="text-xs text-gray-600">
              {showDetailedInfo
                ? FACTCHECK_COPY.detailedTopDisclaimer
                : FACTCHECK_COPY.topDisclaimer}
            </p>
          </div>
        </div>

        <div className="space-y-3 mb-4" aria-labelledby={sectionId} role="region">
          {isLoading && (
            <>
              <SkeletonItem />
              <SkeletonItem />
              <SkeletonItem />
            </>
          )}

          {!isLoading && data?.status === 'found' && data.items.length > 0 && (
            <>
              {data.items.slice(0, 3).map((item, index) => (
                <FactCheckItemComponent key={index} item={item} />
              ))}
            </>
          )}

          {!isLoading && (data?.status === 'none' || data?.items.length === 0) && (
            <div className="py-6 text-center">
              <p className="text-gray-500 text-sm leading-relaxed max-w-md mx-auto">
                {FACTCHECK_COPY.emptyStateText}
              </p>
            </div>
          )}

          {error && (
            <p className="text-red-600 text-sm py-4">Unable to load fact-checks at this time</p>
          )}
        </div>

        <div className="pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-400 leading-relaxed">{FACTCHECK_COPY.footerDisclaimer}</p>
        </div>
      </div>
    </Card>
  );
};
