import React from 'react';
import { BiasResult, BiasLabel } from '../../types/api';

// Bias styling constants
const biasTokens = {
  trackGradient: 'linear-gradient(90deg, #b8d3f0 0%, #d9dee4 50%, #f2c5c5 100%)',
  needleColor: {
    Left: '#2563eb', // blue-600
    Neutral: '#4b5563', // gray-600
    Right: '#dc2626', // red-600
  } satisfies Record<BiasLabel, string>,
};

interface BiasMeterProps {
  bias: BiasResult | null;
  className?: string;
}

export const BiasMeter: React.FC<BiasMeterProps> = ({ bias, className = '' }) => {
  const scoreOrZero = bias?.score ?? 0;
  const label = bias?.label ?? 'Neutral';
  const confidence = bias?.confidence ?? 0;

  // Convert score from [-1, 1] to percentage [0, 100]
  const percent = ((scoreOrZero + 1) / 2) * 100;

  return (
    <div className={`w-full ${className}`}>
      {/* Meter track and needle */}
      <div className="relative">
        {/* Track with gradient background - 12px height with rounded ends */}
        <div
          className="h-3 rounded-full relative"
          style={{ background: biasTokens.trackGradient }}
          role="meter"
          aria-valuemin={-1}
          aria-valuemax={1}
          aria-valuenow={scoreOrZero}
          aria-label="Bias from left to right"
        >
          {/* Needle - 2px wide vertical line with rounded caps and slight shadow */}
          <div
            className="absolute top-0 w-0.5 h-3 rounded-full shadow-sm"
            style={{
              left: `${percent}%`,
              backgroundColor: biasTokens.needleColor[label],
              transform: 'translateX(-50%)',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            }}
          />
        </div>

        {/* Labels under the track - 12-13px medium */}
        <div className="flex justify-between mt-2 text-xs font-medium text-gray-600">
          <span>Left (liberal)</span>
          <span>Neutral</span>
          <span>Right (conservative)</span>
        </div>

        {/* Status line - 14-15px medium */}
        <div className="mt-2 text-sm font-medium text-gray-700">
          {bias === null ? (
            <span>Bias: Neutral (not computed)</span>
          ) : (
            <span>
              Bias: {label} ({Math.round(confidence * 100)}% confidence)
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
