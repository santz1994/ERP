/**
 * Unified Status Badge Component
 * ERP Quty Karunia - UI Standardization
 * Date: 4 Februari 2026
 */

import React from 'react';

interface StatusBadgeProps {
  status: string;
  variant?: 'sm' | 'default' | 'lg';
  className?: string;
}

// Comprehensive color mapping for all statuses across the system
const statusColors: Record<string, string> = {
  // Manufacturing Order Status
  DRAFT: 'bg-gray-100 text-gray-700 border-gray-300',
  PARTIAL: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  RELEASED: 'bg-blue-100 text-blue-700 border-blue-300',
  IN_PROGRESS: 'bg-indigo-100 text-indigo-700 border-indigo-300',
  COMPLETED: 'bg-green-100 text-green-700 border-green-300',
  DONE: 'bg-green-100 text-green-700 border-green-300',
  CANCELLED: 'bg-red-100 text-red-700 border-red-300',
  ON_HOLD: 'bg-orange-100 text-orange-700 border-orange-300',
  
  // SPK/Work Order Status
  PENDING: 'bg-slate-100 text-slate-700 border-slate-300',
  READY: 'bg-cyan-100 text-cyan-700 border-cyan-300',
  WORKING: 'bg-amber-100 text-amber-700 border-amber-300',
  WAITING: 'bg-purple-100 text-purple-700 border-purple-300',
  
  // Approval Status
  APPROVED: 'bg-emerald-100 text-emerald-700 border-emerald-300',
  REJECTED: 'bg-rose-100 text-rose-700 border-rose-300',
  PENDING_APPROVAL: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  
  // QC Status
  PASS: 'bg-green-100 text-green-700 border-green-300',
  FAIL: 'bg-red-100 text-red-700 border-red-300',
  REWORK: 'bg-orange-100 text-orange-700 border-orange-300',
  INSPECTION: 'bg-blue-100 text-blue-700 border-blue-300',
  
  // Stock Status
  IN_STOCK: 'bg-green-100 text-green-700 border-green-300',
  LOW_STOCK: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  OUT_OF_STOCK: 'bg-red-100 text-red-700 border-red-300',
  RESERVED: 'bg-blue-100 text-blue-700 border-blue-300',
  
  // Transfer Status
  REQUESTED: 'bg-cyan-100 text-cyan-700 border-cyan-300',
  SHIPPED: 'bg-indigo-100 text-indigo-700 border-indigo-300',
  RECEIVED: 'bg-green-100 text-green-700 border-green-300',
  IN_TRANSIT: 'bg-purple-100 text-purple-700 border-purple-300',
  
  // User Status
  ACTIVE: 'bg-green-100 text-green-700 border-green-300',
  INACTIVE: 'bg-gray-100 text-gray-700 border-gray-300',
  SUSPENDED: 'bg-red-100 text-red-700 border-red-300',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  default: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

/**
 * StatusBadge - Unified status indicator component
 * 
 * @param status - Status key (e.g., 'PARTIAL', 'COMPLETED', 'PASS')
 * @param variant - Size variant: 'sm' | 'default' | 'lg'
 * @param className - Additional Tailwind classes
 * 
 * @example
 * <StatusBadge status="PARTIAL" />
 * <StatusBadge status="COMPLETED" variant="lg" />
 * <StatusBadge status="REWORK" variant="sm" className="ml-2" />
 */
export const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  variant = 'default',
  className = ''
}) => {
  const colorClass = statusColors[status] || 'bg-gray-100 text-gray-700 border-gray-300';
  const sizeClass = sizeClasses[variant];
  
  return (
    <span 
      className={`
        inline-flex items-center gap-1 rounded-full font-medium border
        ${colorClass} ${sizeClass} ${className}
      `}
    >
      {status.replace(/_/g, ' ')}
    </span>
  );
};

/**
 * StatusIndicator - Dot indicator for compact spaces
 */
interface StatusIndicatorProps {
  status: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ 
  status, 
  showLabel = false,
  size = 'md' 
}) => {
  const dotSizes = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };
  
  const colorClass = statusColors[status] || 'bg-gray-500';
  const bgColor = colorClass.split(' ')[0].replace('bg-', '').replace('-100', '-500');
  
  return (
    <div className="flex items-center gap-2">
      <span className={`${dotSizes[size]} rounded-full bg-${bgColor}`} />
      {showLabel && (
        <span className="text-sm text-gray-700">{status.replace(/_/g, ' ')}</span>
      )}
    </div>
  );
};
