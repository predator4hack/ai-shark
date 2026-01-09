import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  shadow?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Card: React.FC<CardProps> = ({ children, className = '', shadow = 'md' }) => {
  const shadowStyles = {
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  };

  return (
    <div className={`bg-white rounded-xl border border-slate-200 ${shadowStyles[shadow]} ${className}`}>
      {children}
    </div>
  );
};

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const CardContent: React.FC<CardContentProps> = ({ children, className = '' }) => {
  return <div className={`p-6 ${className}`}>{children}</div>;
};
