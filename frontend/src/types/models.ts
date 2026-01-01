export interface PitchDeckMetadata {
  company_name: string
  sector?: string
  website?: string
  founding_year?: string
  location?: string
  [key: string]: any
}

export interface PitchDeckState {
  jobId: string | null
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed'
  progressMessage: string
  companyName: string | null
  files: string[]
  metadata: PitchDeckMetadata | null
  error: string | null
}
