import React from 'react';

export interface LargeDisplayProps {
  label: string;
  value: string | number;
  size?: 'large' | 'xlarge';
  className?: string;
}

export const LargeDisplay: React.FC<LargeDisplayProps> = ({
  label,
  value,
  size = 'large',
  className = '',
}) => {
  const sizeClasses = {
    large: 'text-2xl md:text-3xl',
    xlarge: 'text-4xl md:text-5xl',
  };

  return (
    <div className={`${className}`}>
      <p className="text-lg md:text-2xl text-gray-600 font-semibold mb-2">
        {label}
      </p>
      <p className={`${sizeClasses[size]} font-bold text-gray-900`}>
        {value}
      </p>
    </div>
  );
};
