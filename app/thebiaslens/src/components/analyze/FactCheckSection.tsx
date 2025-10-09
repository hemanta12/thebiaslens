import React, { useState } from 'react';
import { Card, Typography } from '@mui/material';
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
    const lower = verdict.toLowerCase();
    if (lower === 'true' || lower === 'mostly true') {
      return 'bg-green-100 text-green-800 border-green-200';
    }
    if (lower === 'false' || lower === 'mostly false') {
      return 'bg-red-100 text-red-800 border-red-200';
    }
    if (lower.includes('mixed') || lower.includes('context')) {
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
    if (lower === 'misleading') {
      return 'bg-orange-100 text-orange-800 border-orange-200';
    }
    if (lower.includes('unverified') || lower.includes('unsupported')) {
      return 'bg-gray-100 text-gray-800 border-gray-200';
    }
    if (lower.includes('opinion') || lower.includes('analysis')) {
      return 'bg-blue-100 text-blue-800 border-blue-200';
    }
    if (lower.includes('satire') || lower.includes('parody')) {
      return 'bg-purple-100 text-purple-800 border-purple-200';
    }
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getVerdictStyle(verdict)}`}
    >
      {verdict}
    </span>
  );
};

const FactCheckItemComponent: React.FC<{ item: FactCheckItemType }> = ({ item }) => {
  const formatDate = (dateString?: string | null) => {
    if (!dateString) return null;
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return null;
    }
  };

  const getMatchReasonText = (reason?: string) => {
    if (!reason) return 'Similar claim on the same topic';

    // Check if we have a mapping for this reason
    const reasonKey = reason as keyof typeof FACTCHECK_COPY.matchReasons;
    return FACTCHECK_COPY.matchReasons[reasonKey] || 'Similar claim on the same topic';
  };

  const getActionText = (verdict?: string | null) => {
    if (!verdict) return 'Check scope & methodology';

    const verdictKey = verdict.toLowerCase() as keyof typeof FACTCHECK_COPY.verdictGuidance;
    return FACTCHECK_COPY.verdictGuidance[verdictKey] || 'Check scope & methodology';
  };

  const formattedDate = formatDate(item.publishedAt);

  return (
    <div className="border border-gray-200 rounded-lg p-4 space-y-3 hover:border-gray-300 hover:shadow-sm transition-all duration-200">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 space-y-2">
          <VerdictChip verdict={item.verdict} />

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

          <div className="flex items-center gap-1 text-xs text-gray-600">
            {item.source && <span className="font-medium">{item.source}</span>}
            {item.source && formattedDate && <span className="text-gray-400">•</span>}
            {formattedDate && <span>{formattedDate}</span>}
          </div>
        </div>
      </div>

      <div className="text-xs text-gray-600">
        <p className="mb-1">
          <span className="font-medium">Why it's shown:</span>{' '}
          {getMatchReasonText(item.matchReason)}
        </p>
        <p>
          <span className="font-medium">What to do:</span> {getActionText(item.verdict)}
        </p>
      </div>

      <div className="flex justify-end pt-2 border-t border-gray-100">
        {item.url && (
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors"
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
  // Intelligent default recency: 12 months for court/SCOTUS, 18 months otherwise
  const getDefaultMaxAge = (headline: string) => {
    const headlineLower = headline.toLowerCase();
    return headlineLower.includes('court') || headlineLower.includes('scotus') ? 12 : 18;
  };

  const [maxAgeMonths, setMaxAgeMonths] = useState(() => getDefaultMaxAge(headline));
  const { data, isLoading, error } = useFactCheck({
    headline,
    sourceDomain,
    summary,
    maxAgeMonths,
  });

  const sectionId = 'factcheck-section';

  const handleRecencyChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setMaxAgeMonths(Number(event.target.value));
  };

  return (
    <Card sx={{ mb: 3, mt: 3 }}>
      <div className="p-4">
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
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

          <div className="bg-gradient-to-r from-blue-50 to-green-50 border border-blue-100 rounded-lg p-3 mb-3">
            <p className="text-sm text-gray-700 mb-1 font-medium">{FACTCHECK_COPY.subtitle}</p>
            <p className="text-xs text-gray-600">{FACTCHECK_COPY.topDisclaimer}</p>
          </div>

          {/* Recency Control */}
          <div className="mb-3">
            <label htmlFor="recency-select" className="sr-only">
              Fact-check recency
            </label>
            <select
              id="recency-select"
              value={maxAgeMonths}
              onChange={handleRecencyChange}
              className="text-xs border border-gray-300 rounded px-2 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={9999}>Any time (2+ yrs)</option>
              <option value={24}>24 months</option>
              <option value={18}>
                18 months{getDefaultMaxAge(headline) === 18 ? ' (default)' : ''}
              </option>
              <option value={12}>
                12 months{getDefaultMaxAge(headline) === 12 ? ' (default)' : ''}
              </option>
              <option value={6}>6 months</option>
            </select>
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
