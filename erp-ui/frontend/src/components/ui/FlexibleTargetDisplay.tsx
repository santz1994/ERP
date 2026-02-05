/**
 * Flexible Target Display Component
 * Purpose: Universal Actual/Target display with percentage and buffer logic
 * Format: Actual/Target pcs (Percentage%)
 * 
 * Features:
 * - Color-coded status (Red: <80%, Yellow: 80-95%, Green: >95%, Blue: >100%)
 * - Buffer visualization (MO target vs SPK target)
 * - Constraint logic display
 * - Exceed target indicator
 * 
 * Usage:
 * <FlexibleTargetDisplay
 *   actual={250}
 *   spkTarget={200}
 *   moTarget={180}
 *   showBuffer={true}
 *   showPercentage={true}
 * />
 */

import React from 'react';
import { TrendingUp, TrendingDown, Target, AlertCircle } from 'lucide-react';

interface FlexibleTargetDisplayProps {
  actual: number;
  spkTarget: number;
  moTarget?: number;
  bufferPercent?: number;
  maxConstraint?: number; // Max allowed based on previous dept
  showBuffer?: boolean;
  showPercentage?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'compact' | 'detailed';
  label?: string;
}

export const FlexibleTargetDisplay: React.FC<FlexibleTargetDisplayProps> = ({
  actual,
  spkTarget,
  moTarget,
  bufferPercent,
  maxConstraint,
  showBuffer = true,
  showPercentage = true,
  size = 'md',
  variant = 'default',
  label
}) => {
  // Calculate percentage against SPK Target
  const percentage = spkTarget > 0 ? (actual / spkTarget) * 100 : 0;
  const diff = actual - spkTarget;
  
  // Calculate buffer info
  const buffer = moTarget ? spkTarget - moTarget : 0;
  const actualBufferPercent = moTarget && moTarget > 0 ? (buffer / moTarget) * 100 : 0;

  // Determine status color
  const getStatusColor = () => {
    if (percentage >= 100) return 'blue'; // Exceed target
    if (percentage >= 95) return 'green'; // Excellent
    if (percentage >= 80) return 'yellow'; // Warning
    return 'red'; // Critical
  };

  const statusColor = getStatusColor();

  // Constraint check
  const hasConstraintViolation = maxConstraint && spkTarget > maxConstraint;

  // Size variants
  const sizeClasses = {
    sm: {
      text: 'text-lg',
      label: 'text-xs',
      icon: 'w-4 h-4',
      padding: 'p-2'
    },
    md: {
      text: 'text-2xl',
      label: 'text-sm',
      icon: 'w-5 h-5',
      padding: 'p-3'
    },
    lg: {
      text: 'text-4xl',
      label: 'text-base',
      icon: 'w-6 h-6',
      padding: 'p-4'
    }
  };

  const colorClasses = {
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-300',
      text: 'text-blue-900',
      badge: 'bg-blue-600 text-white'
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-300',
      text: 'text-green-900',
      badge: 'bg-green-600 text-white'
    },
    yellow: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-300',
      text: 'text-yellow-900',
      badge: 'bg-yellow-600 text-white'
    },
    red: {
      bg: 'bg-red-50',
      border: 'border-red-300',
      text: 'text-red-900',
      badge: 'bg-red-600 text-white'
    }
  };

  if (variant === 'compact') {
    return (
      <div className={`inline-flex items-center gap-2 ${sizeClasses[size].padding} ${colorClasses[statusColor].bg} border ${colorClasses[statusColor].border} rounded-lg`}>
        <span className={`font-bold ${colorClasses[statusColor].text} ${sizeClasses[size].text}`}>
          {actual}/{spkTarget}
        </span>
        {showPercentage && (
          <span className={`px-2 py-1 rounded ${colorClasses[statusColor].badge} font-semibold ${sizeClasses[size].label}`}>
            {percentage.toFixed(1)}%
          </span>
        )}
      </div>
    );
  }

  if (variant === 'detailed') {
    return (
      <div className={`${colorClasses[statusColor].bg} border-2 ${colorClasses[statusColor].border} rounded-lg ${sizeClasses[size].padding}`}>
        {label && (
          <p className={`${sizeClasses[size].label} font-semibold text-gray-700 mb-2`}>{label}</p>
        )}
        
        {/* Main Display */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <Target className={sizeClasses[size].icon + ` ${colorClasses[statusColor].text}`} />
            <span className={`font-bold ${colorClasses[statusColor].text} ${sizeClasses[size].text}`}>
              {actual} / {spkTarget} pcs
            </span>
          </div>
          <span className={`px-3 py-1 rounded-lg ${colorClasses[statusColor].badge} font-bold text-lg`}>
            {percentage.toFixed(1)}%
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
          <div
            className={`h-3 rounded-full transition-all ${
              statusColor === 'blue' ? 'bg-blue-600' :
              statusColor === 'green' ? 'bg-green-600' :
              statusColor === 'yellow' ? 'bg-yellow-600' :
              'bg-red-600'
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>

        {/* Additional Info */}
        <div className="space-y-1 text-xs">
          {showBuffer && moTarget && (
            <div className="flex justify-between">
              <span className="text-gray-600">MO Target:</span>
              <span className="font-semibold">{moTarget} pcs</span>
            </div>
          )}
          {showBuffer && buffer > 0 && (
            <div className="flex justify-between">
              <span className="text-gray-600">Buffer:</span>
              <span className="font-semibold text-purple-600">
                +{buffer} pcs ({actualBufferPercent.toFixed(1)}%)
              </span>
            </div>
          )}
          {maxConstraint && (
            <div className="flex justify-between">
              <span className="text-gray-600">Max Allowed:</span>
              <span className={`font-semibold ${hasConstraintViolation ? 'text-red-600' : 'text-gray-800'}`}>
                {maxConstraint} pcs {hasConstraintViolation && '⚠️'}
              </span>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-gray-600">Difference:</span>
            <span className={`font-semibold ${diff >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {diff >= 0 ? '+' : ''}{diff} pcs
            </span>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="mt-3 pt-3 border-t border-gray-300">
          {percentage >= 100 && (
            <div className="flex items-center gap-2 text-blue-700">
              <TrendingUp className="w-4 h-4" />
              <span className="text-xs font-semibold">✅ Exceeded target by {(percentage - 100).toFixed(1)}%!</span>
            </div>
          )}
          {percentage >= 95 && percentage < 100 && (
            <div className="flex items-center gap-2 text-green-700">
              <span className="text-xs font-semibold">✅ Excellent progress!</span>
            </div>
          )}
          {percentage >= 80 && percentage < 95 && (
            <div className="flex items-center gap-2 text-yellow-700">
              <span className="text-xs font-semibold">⚠️ Need {spkTarget - actual} more to reach target</span>
            </div>
          )}
          {percentage < 80 && (
            <div className="flex items-center gap-2 text-red-700">
              <TrendingDown className="w-4 h-4" />
              <span className="text-xs font-semibold">🚨 Behind target! Need {spkTarget - actual} pcs</span>
            </div>
          )}
          {hasConstraintViolation && (
            <div className="flex items-center gap-2 text-red-700 mt-2">
              <AlertCircle className="w-4 h-4" />
              <span className="text-xs font-semibold">
                🚫 Target exceeds constraint! Reduce to {maxConstraint} pcs
              </span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Default variant
  return (
    <div className={`${colorClasses[statusColor].bg} border ${colorClasses[statusColor].border} rounded-lg ${sizeClasses[size].padding}`}>
      {label && (
        <p className={`${sizeClasses[size].label} font-medium text-gray-700 mb-1`}>{label}</p>
      )}
      <div className="flex items-center justify-between">
        <span className={`font-bold ${colorClasses[statusColor].text} ${sizeClasses[size].text}`}>
          {actual}/{spkTarget} pcs
        </span>
        {showPercentage && (
          <span className={`px-2 py-1 rounded ${colorClasses[statusColor].badge} font-semibold ${sizeClasses[size].label}`}>
            {percentage.toFixed(1)}%
          </span>
        )}
      </div>
      {showBuffer && moTarget && buffer > 0 && (
        <p className="text-xs text-gray-600 mt-1">
          MO: {moTarget} + Buffer: {buffer} ({actualBufferPercent.toFixed(1)}%)
        </p>
      )}
    </div>
  );
};

export default FlexibleTargetDisplay;
