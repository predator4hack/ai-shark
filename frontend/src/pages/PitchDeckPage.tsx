import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Stack,
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import DownloadIcon from '@mui/icons-material/Download'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'

import { DragDropZone } from '../components/FileUpload/DragDropZone'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { setJobId, updateStatus, setResult, setError, reset } from '../store/slices/pitchDeckSlice'
import { documentsApi } from '../api/endpoints/documents'
import { POLLING } from '../utils/constants'

export const PitchDeckPage: React.FC = () => {
  const dispatch = useAppDispatch()
  const pitchDeck = useAppSelector((state) => state.pitchDeck)
  const [polling, setPolling] = useState(false)

  // Handle file upload
  const handleFileSelect = async (file: File) => {
    try {
      dispatch(updateStatus({ status: 'uploading', progressMessage: 'Uploading file...' }))

      const response = await documentsApi.uploadPitchDeck(file)
      dispatch(setJobId(response.job_id))
      setPolling(true)
    } catch (error: any) {
      dispatch(setError(error.response?.data?.detail || 'Upload failed'))
    }
  }

  // Poll job status
  useEffect(() => {
    if (!polling || !pitchDeck.jobId) return

    const pollInterval = setInterval(async () => {
      try {
        const status = await documentsApi.getJobStatus(pitchDeck.jobId!)

        dispatch(updateStatus({
          status: status.status as any,
          progressMessage: status.progress_message,
        }))

        if (status.status === 'completed' && status.result) {
          dispatch(setResult({
            companyName: status.result.company_name,
            files: status.result.files_created,
            metadata: {
              company_name: status.result.company_name,
              ...status.result.metadata
            },
          }))
          setPolling(false)
        } else if (status.status === 'failed') {
          dispatch(setError(status.error || 'Processing failed'))
          setPolling(false)
        }
      } catch (error: any) {
        console.error('Polling error:', error)
        dispatch(setError('Failed to fetch job status'))
        setPolling(false)
      }
    }, POLLING.INTERVAL_MS)

    return () => clearInterval(pollInterval)
  }, [polling, pitchDeck.jobId, dispatch])

  // Handle reset
  const handleReset = () => {
    dispatch(reset())
    setPolling(false)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Chip label="Phase 1" color="primary" sx={{ mb: 2 }} />
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Pitch Deck Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Upload your pitch deck (PDF or PowerPoint) to extract company metadata,
          table of contents, and structured analysis.
        </Typography>
      </Box>

      {/* Upload Zone */}
      {pitchDeck.status === 'idle' && (
        <Box sx={{ my: 4 }}>
          <DragDropZone onFileSelect={handleFileSelect} />
        </Box>
      )}

      {/* Processing Status */}
      {(pitchDeck.status === 'uploading' || pitchDeck.status === 'processing') && (
        <Card sx={{ my: 4 }} elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                Processing Pitch Deck...
              </Typography>
            </Box>
            <LinearProgress sx={{ my: 2 }} />
            <Typography variant="body2" color="text.secondary">
              {pitchDeck.progressMessage}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Error */}
      {pitchDeck.status === 'failed' && (
        <Box sx={{ my: 4 }}>
          <Alert
            severity="error"
            action={
              <Button color="inherit" size="small" onClick={handleReset}>
                Try Again
              </Button>
            }
          >
            {pitchDeck.error}
          </Alert>
        </Box>
      )}

      {/* Results */}
      {pitchDeck.status === 'completed' && pitchDeck.companyName && (
        <Card sx={{ my: 4 }} elevation={3}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <CheckCircleIcon color="success" sx={{ fontSize: 40, mr: 2 }} />
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Processing Complete
              </Typography>
            </Box>

            {/* Company Info */}
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                {pitchDeck.companyName}
              </Typography>
              {pitchDeck.metadata && (
                <Stack spacing={1} sx={{ mt: 1 }}>
                  {pitchDeck.metadata.sector && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>Sector:</strong> {pitchDeck.metadata.sector}
                    </Typography>
                  )}
                  {pitchDeck.metadata.website && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>Website:</strong> {pitchDeck.metadata.website}
                    </Typography>
                  )}
                  {pitchDeck.metadata.founding_year && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>Founded:</strong> {pitchDeck.metadata.founding_year}
                    </Typography>
                  )}
                  {pitchDeck.metadata.location && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>Location:</strong> {pitchDeck.metadata.location}
                    </Typography>
                  )}
                </Stack>
              )}
            </Box>

            {/* Files List */}
            <Typography variant="h6" sx={{ mt: 3, mb: 2, fontWeight: 600 }}>
              Generated Files
            </Typography>
            <List>
              {pitchDeck.files.map((file) => {
                const fileName = file.split('/').pop() || file
                return (
                  <ListItem
                    key={file}
                    sx={{
                      bgcolor: 'background.paper',
                      mb: 1,
                      borderRadius: 1,
                      border: '1px solid',
                      borderColor: 'divider'
                    }}
                  >
                    <ListItemIcon>
                      <DescriptionIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={fileName}
                      secondary={file}
                    />
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      href={documentsApi.downloadFile(pitchDeck.companyName!, fileName)}
                      target="_blank"
                      size="small"
                    >
                      Download
                    </Button>
                  </ListItem>
                )
              })}
            </List>

            {/* Reset Button */}
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Button variant="outlined" onClick={handleReset}>
                Process Another Pitch Deck
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}
    </Container>
  )
}
