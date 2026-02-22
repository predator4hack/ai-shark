export interface UploadPitchDeckResponse {
  job_id: string
  message: string
}

export interface JobStatusResponse {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress_message: string
  result?: {
    success: boolean
    company_name: string
    files_created: string[]
    metadata: Record<string, any>
  }
  error?: string
}

export interface FileDownloadResponse {
  filename: string
  download_url: string
  expires_in: number
}

// SSE Event Types
export interface SSEProgressEvent {
  stage: string
  message: string
  progress?: {
    current: number
    total: number
    percent: number
  }
}

export interface SSECompleteEvent {
  job_id: string
  result: {
    success: boolean
    company_name: string
    files_created: string[]
    metadata: Record<string, any>
    processing_time: number
  }
}

export interface SSEErrorEvent {
  job_id: string
  error: string
  stage: string
}
