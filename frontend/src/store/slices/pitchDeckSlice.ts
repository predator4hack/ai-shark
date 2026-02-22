import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { PitchDeckState, PitchDeckMetadata } from '../../types/models'
import type { SSECompleteEvent } from '../../types/api'

const initialState: PitchDeckState = {
  jobId: null,
  status: 'idle',
  progressMessage: '',
  currentStage: null,
  progressPercent: null,
  progressDetails: null,
  companyName: null,
  files: [],
  metadata: null,
  error: null,
}

const pitchDeckSlice = createSlice({
  name: 'pitchDeck',
  initialState,
  reducers: {
    setJobId: (state, action: PayloadAction<string>) => {
      state.jobId = action.payload
      state.status = 'processing'
    },
    updateStatus: (state, action: PayloadAction<{
      status: PitchDeckState['status']
      progressMessage: string
    }>) => {
      state.status = action.payload.status
      state.progressMessage = action.payload.progressMessage
    },
    updateProgress: (state, action: PayloadAction<{
      stage: string
      message: string
      progress?: {
        current: number
        total: number
        percent: number
      }
    }>) => {
      state.status = 'processing'
      state.currentStage = action.payload.stage
      state.progressMessage = action.payload.message
      if (action.payload.progress) {
        state.progressPercent = action.payload.progress.percent
        state.progressDetails = {
          current: action.payload.progress.current,
          total: action.payload.progress.total,
        }
      } else {
        state.progressPercent = null
        state.progressDetails = null
      }
    },
    setResult: (state, action: PayloadAction<{
      companyName: string
      files: string[]
      metadata: PitchDeckMetadata
    }>) => {
      state.status = 'completed'
      state.companyName = action.payload.companyName
      state.files = action.payload.files
      state.metadata = action.payload.metadata
    },
    setResultFromSSE: (state, action: PayloadAction<SSECompleteEvent>) => {
      state.status = 'completed'
      state.jobId = action.payload.job_id
      state.companyName = action.payload.result.company_name
      state.files = action.payload.result.files_created
      state.metadata = {
        company_name: action.payload.result.company_name,
        ...action.payload.result.metadata,
      }
      state.progressPercent = 100
    },
    setError: (state, action: PayloadAction<string>) => {
      state.status = 'failed'
      state.error = action.payload
    },
    setErrorFromSSE: (state, action: PayloadAction<{
      error: string
      stage?: string
    }>) => {
      state.status = 'failed'
      state.error = action.payload.error
      if (action.payload.stage) {
        state.currentStage = action.payload.stage
      }
    },
    reset: () => {
      return initialState
    },
  },
})

export const {
  setJobId,
  updateStatus,
  updateProgress,
  setResult,
  setResultFromSSE,
  setError,
  setErrorFromSSE,
  reset
} = pitchDeckSlice.actions
export default pitchDeckSlice.reducer
