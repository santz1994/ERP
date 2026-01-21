import React from 'react';

export interface BigButtonProps {
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'success' | 'danger' | 'warning' | 'secondary';
  size?: 'large' | 'xlarge';
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const BigButton: React.FC<BigButtonProps> = ({
  onClick,
  disabled = false,
  variant = 'primary',
  size = 'large',
  icon,
  children,
  className = '',
}) => {
  const baseClasses = 'font-bold rounded-lg transition-all duration-200 cursor-pointer';
  
  const sizeClasses = {
    large: 'w-full py-6 px-8 text-2xl min-h-24',
    xlarge: 'w-full py-8 px-10 text-3xl min-h-32',
  };

  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-400',
    success: 'bg-green-600 hover:bg-green-700 text-white disabled:bg-gray-400',
    danger: 'bg-red-600 hover:bg-red-700 text-white disabled:bg-gray-400',
    warning: 'bg-yellow-500 hover:bg-yellow-600 text-white disabled:bg-gray-400',
    secondary: 'bg-gray-400 hover:bg-gray-500 text-white disabled:bg-gray-300',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${baseClasses}
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
        flex items-center justify-center gap-4 shadow-lg active:shadow-md
      `}
    >
      {icon && <span className="text-4xl">{icon}</span>}
      <span>{children}</span>
    </button>
  );
};
