/**
 * Unified Loading States Components
 * ERP Quty Karunia - UI Standardization
 * Date: 4 Februari 2026
 */

import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

/**
 * LoadingSpinner - Animated spinner icon
 * 
 * @param size - Size variant: 'sm' | 'md' | 'lg' | 'xl'
 * @param className - Additional Tailwind classes
 * 
 * @example
 * <LoadingSpinner size="md" />
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };
  
  return (
    <Loader2 className={`${sizeClasses[size]} animate-spin text-brand-600 ${className}`} />
  );
};

interface LoadingOverlayProps {
  message?: string;
  showSpinner?: boolean;
}

/**
 * LoadingOverlay - Full-screen loading overlay
 * 
 * @param message - Loading message to display
 * @param showSpinner - Whether to show animated spinner
 * 
 * @example
 * {isSubmitting && <LoadingOverlay message="Saving changes..." />}
 */
export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  message = 'Loading...',
  showSpinner = true
}) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-white rounded-lg shadow-2xl p-6 flex flex-col items-center gap-4 min-w-[200px]">
        {showSpinner && <LoadingSpinner size="lg" />}
        <p className="text-gray-700 font-medium text-center">{message}</p>
      </div>
    </div>
  );
};

interface LoadingCardProps {
  message?: string;
  icon?: React.ReactNode;
}

/**
 * LoadingCard - Card-style loading indicator
 * 
 * @param message - Loading message
 * @param icon - Optional custom icon
 * 
 * @example
 * {isLoading && <LoadingCard message="Loading work orders..." />}
 */
export const LoadingCard: React.FC<LoadingCardProps> = ({ 
  message = 'Loading...',
  icon
}) => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-8 flex flex-col items-center gap-4">
      {icon || <LoadingSpinner size="lg" />}
      <p className="text-gray-600">{message}</p>
    </div>
  );
};

interface LoadingSkeletonProps {
  lines?: number;
  avatar?: boolean;
  className?: string;
}

/**
 * LoadingSkeleton - Skeleton placeholder for content
 * 
 * @param lines - Number of skeleton lines
 * @param avatar - Whether to show avatar skeleton
 * @param className - Additional classes
 * 
 * @example
 * {isLoading ? <LoadingSkeleton lines={5} avatar /> : <ActualContent />}
 */
export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  lines = 3,
  avatar = false,
  className = ''
}) => {
  return (
    <div className={`space-y-3 ${className}`}>
      {avatar && (
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-gray-200 rounded-full animate-pulse" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-1/3 animate-pulse" />
            <div className="h-3 bg-gray-200 rounded w-1/2 animate-pulse" />
          </div>
        </div>
      )}
      
      {Array.from({ length: lines }).map((_, i) => (
        <div 
          key={i} 
          className="h-4 bg-gray-200 rounded animate-pulse"
          style={{ width: `${Math.random() * 40 + 60}%` }}
        />
      ))}
    </div>
  );
};

interface LoadingTableProps {
  rows?: number;
  columns?: number;
}

/**
 * LoadingTable - Skeleton for table layouts
 * 
 * @param rows - Number of table rows
 * @param columns - Number of columns
 * 
 * @example
 * {isLoading ? <LoadingTable rows={10} columns={6} /> : <DataTable />}
 */
export const LoadingTable: React.FC<LoadingTableProps> = ({ 
  rows = 5,
  columns = 4
}) => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 bg-gray-50">
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, i) => (
            <div key={i} className="h-4 bg-gray-300 rounded animate-pulse" />
          ))}
        </div>
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="border-b border-gray-100 p-4 last:border-b-0">
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {Array.from({ length: columns }).map((_, colIdx) => (
              <div key={colIdx} className="h-4 bg-gray-200 rounded animate-pulse" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

interface LoadingListProps {
  items?: number;
}

/**
 * LoadingList - Skeleton for list layouts
 * 
 * @param items - Number of list items
 * 
 * @example
 * {isLoading ? <LoadingList items={8} /> : <ItemList />}
 */
export const LoadingList: React.FC<LoadingListProps> = ({ items = 5 }) => {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gray-200 rounded animate-pulse" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse" />
              <div className="h-3 bg-gray-200 rounded w-1/2 animate-pulse" />
            </div>
            <div className="w-20 h-8 bg-gray-200 rounded animate-pulse" />
          </div>
        </div>
      ))}
    </div>
  );
};

/**
 * InlineLoader - Compact inline loading indicator
 * 
 * @example
 * <button disabled={isLoading}>
 *   {isLoading ? <InlineLoader /> : 'Save'}
 * </button>
 */
export const InlineLoader: React.FC = () => {
  return (
    <div className="flex items-center gap-2">
      <LoadingSpinner size="sm" />
      <span>Loading...</span>
    </div>
  );
};
