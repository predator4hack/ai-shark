import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { Button } from '../components/ui/Button';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <Icon icon="lucide:alert-circle" className="mx-auto mb-6 text-slate-400" width="80" />
        <h1 className="text-4xl font-semibold text-slate-900 mb-3">404 - Page Not Found</h1>
        <p className="text-lg text-slate-600 mb-8">
          The page you're looking for doesn't exist.
        </p>
        <Button variant="primary" onClick={() => navigate('/')}>
          <Icon icon="lucide:home" width="18" />
          Go Home
        </Button>
      </div>
    </div>
  );
};
