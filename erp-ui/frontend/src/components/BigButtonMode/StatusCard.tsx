import React from 'react';

export interface StatusCardProps {
  status: 'ready' | 'processing' | 'warning' | 'error' | 'completed';
  title: string;
  details?: Record<string, string | number>;
  children?: React.ReactNode;
  className?: string;
}

const statusConfig = {
  ready: {
    bg: 'bg-green-50',
    border: 'border-green-300',
    textColor: 'text-green-700',
    icon: '🟢',
  },
  processing: {
    bg: 'bg-blue-50',
    border: 'border-blue-300',
    textColor: 'text-blue-700',
    icon: '🔵',
  },
  warning: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-300',
    textColor: 'text-yellow-700',
    icon: '🟡',
  },
  error: {
    bg: 'bg-red-50',
    border: 'border-red-300',
    textColor: 'text-red-700',
    icon: '🔴',
  },
  completed: {
    bg: 'bg-green-50',
    border: 'border-green-300',
    textColor: 'text-green-700',
    icon: '✅',
  },
};

export const StatusCard: React.FC<StatusCardProps> = ({
  status,
  title,
  details,
  children,
  className = '',
}) => {
  const config = statusConfig[status];

  return (
    <div
      className={`
        ${config.bg}
        ${config.border}
        border-4 rounded-xl p-8 mb-6
        ${className}
      `}
    >
      {/* Status Header */}
      <div className="flex items-center gap-4 mb-4">
        <span className="text-5xl">{config.icon}</span>
        <h2 className={`text-3xl font-bold ${config.textColor}`}>{title}</h2>
      </div>

      {/* Details */}
      {details && (
        <div className="space-y-3 mb-6">
          {Object.entries(details).map(([key, value]) => (
            <div key={key} className="flex justify-between text-lg">
              <span className="font-semibold text-gray-700">{key}:</span>
              <span className={`${config.textColor} font-bold`}>{value}</span>
            </div>
          ))}
        </div>
      )}

      {/* Children */}
      {children && <div>{children}</div>}
    </div>
  );
};
