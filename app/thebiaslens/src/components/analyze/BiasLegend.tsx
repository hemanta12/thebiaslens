import React from 'react';

interface BiasLegendProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BiasLegend: React.FC<BiasLegendProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md mx-4 shadow-xl">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Bias Analysis Legend</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
            aria-label="Close legend"
          >
            ×
          </button>
        </div>

        <div className="space-y-3">
          {/* Left bias */}
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
            <div>
              <div className="font-medium text-blue-600">Left (liberal)</div>
              <div className="text-sm text-gray-600">
                Language tends to support progressive framing
              </div>
            </div>
          </div>

          {/* Neutral bias */}
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-gray-600 rounded-full mt-2 flex-shrink-0" />
            <div>
              <div className="font-medium text-gray-600">Neutral</div>
              <div className="text-sm text-gray-600">Little framing detected</div>
            </div>
          </div>

          {/* Right bias */}
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-red-600 rounded-full mt-2 flex-shrink-0" />
            <div>
              <div className="font-medium text-red-600">Right (conservative)</div>
              <div className="text-sm text-gray-600">
                Language tends to support conservative framing
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-500 italic">AI estimate of framing. Use your judgment.</p>
        </div>
      </div>
    </div>
  );
};
