import React from 'react'
import { Alert, AlertTitle } from '@mui/material'

interface ErrorAlertProps {
  title?: string
  message: string
  onClose?: () => void
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  title = 'Error',
  message,
  onClose
}) => {
  return (
    <Alert severity="error" onClose={onClose}>
      <AlertTitle>{title}</AlertTitle>
      {message}
    </Alert>
  )
}
