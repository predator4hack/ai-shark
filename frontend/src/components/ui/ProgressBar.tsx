import React from 'react';

interface ProgressBarProps {
  value?: number; // 0-100
  indeterminate?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value = 0,
  indeterminate = false,
  className = '',
}) => {
  return (
    <div className={`w-full bg-slate-200 rounded-full h-2 overflow-hidden ${className}`}>
      {indeterminate ? (
        <div className="h-full bg-blue-600 rounded-full animate-pulse" style={{ width: '100%' }} />
      ) : (
        <div
          className="h-full bg-blue-600 rounded-full transition-all duration-300"
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      )}
    </div>
  );
};
