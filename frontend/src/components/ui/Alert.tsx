import React from 'react';
import { Icon } from '@iconify/react';

interface AlertProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  onClose,
  className = '',
}) => {
  const styles = {
    info: {
      container: 'bg-blue-50 border-blue-200 text-blue-900',
      icon: 'lucide:info',
      iconColor: 'text-blue-600',
    },
    success: {
      container: 'bg-green-50 border-green-200 text-green-900',
      icon: 'lucide:check-circle',
      iconColor: 'text-green-600',
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200 text-yellow-900',
      icon: 'lucide:alert-triangle',
      iconColor: 'text-yellow-600',
    },
    error: {
      container: 'bg-red-50 border-red-200 text-red-900',
      icon: 'lucide:alert-circle',
      iconColor: 'text-red-600',
    },
  };

  const currentStyle = styles[type];

  return (
    <div className={`rounded-lg border p-4 ${currentStyle.container} ${className}`}>
      <div className="flex gap-3">
        <Icon icon={currentStyle.icon} className={`shrink-0 ${currentStyle.iconColor}`} width="20" />
        <div className="flex-1">
          {title && <p className="font-semibold mb-1">{title}</p>}
          <div className="text-sm">{children}</div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="shrink-0 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <Icon icon="lucide:x" width="18" />
          </button>
        )}
      </div>
    </div>
  );
};
