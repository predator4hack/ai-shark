import React from 'react';
import { Alert } from '../ui/Alert';

interface ErrorAlertProps {
  title?: string;
  message: string;
  onClose?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  title = 'Error',
  message,
  onClose,
}) => {
  return (
    <Alert type="error" title={title} onClose={onClose}>
      {message}
    </Alert>
  );
};
