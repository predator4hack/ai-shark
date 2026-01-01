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
