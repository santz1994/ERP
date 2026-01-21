import React from 'react';

export interface FullScreenLayoutProps {
  children: React.ReactNode;
  title?: string;
  showBackButton?: boolean;
  onBack?: () => void;
  className?: string;
}

export const FullScreenLayout: React.FC<FullScreenLayoutProps> = ({
  children,
  title,
  showBackButton = false,
  onBack,
  className = '',
}) => {
  return (
    <div className={`w-full h-screen bg-white overflow-auto ${className}`}>
      {/* Header */}
      <div className="bg-gray-100 border-b-4 border-gray-300 p-4 flex items-center justify-between sticky top-0 z-10">
        {showBackButton && (
          <button
            onClick={onBack}
            className="text-4xl font-bold text-blue-600 hover:text-blue-700 px-4"
          >
            ← BACK
          </button>
        )}
        {title && (
          <h1 className="text-3xl font-bold text-center flex-1 text-gray-800">
            {title}
          </h1>
        )}
        <div className="w-20" />
      </div>

      {/* Main Content */}
      <div className="p-8 space-y-6 max-w-5xl mx-auto">
        {children}
      </div>
    </div>
  );
};
