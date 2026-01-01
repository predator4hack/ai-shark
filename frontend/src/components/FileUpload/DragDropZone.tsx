import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Typography, Paper } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import { FILE_UPLOAD } from '../../utils/constants'

interface DragDropZoneProps {
  onFileSelect: (file: File) => void
  acceptedFileTypes?: string[]
  maxSizeMB?: number
  disabled?: boolean
}

export const DragDropZone: React.FC<DragDropZoneProps> = ({
  onFileSelect,
  acceptedFileTypes = FILE_UPLOAD.ACCEPTED_TYPES,
  maxSizeMB = FILE_UPLOAD.MAX_SIZE_MB,
  disabled = false,
}) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0])
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: FILE_UPLOAD.MIME_TYPES,
    maxSize: maxSizeMB * 1024 * 1024,
    multiple: false,
    disabled,
  })

  return (
    <Paper
      {...getRootProps()}
      elevation={3}
      sx={{
        p: 4,
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        border: '2px dashed',
        borderColor: isDragActive ? 'primary.main' : 'grey.300',
        bgcolor: isDragActive ? 'action.hover' : 'background.paper',
        transition: 'all 0.2s ease',
        '&:hover': {
          borderColor: disabled ? 'grey.300' : 'primary.main',
          bgcolor: disabled ? 'background.paper' : 'action.hover',
        },
      }}
    >
      <input {...getInputProps()} />

      <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />

      <Typography variant="h6" gutterBottom>
        {isDragActive ? 'Drop the file here' : 'Drag & drop your pitch deck'}
      </Typography>

      <Typography variant="body2" color="text.secondary">
        or click to browse
      </Typography>

      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        Supported formats: {acceptedFileTypes.join(', ')} (Max {maxSizeMB}MB)
      </Typography>

      {fileRejections.length > 0 && (
        <Typography color="error" variant="body2" sx={{ mt: 2 }}>
          {fileRejections[0].errors[0].message}
        </Typography>
      )}
    </Paper>
  )
}
