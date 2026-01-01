import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { PitchDeckState, PitchDeckMetadata } from '../../types/models'

const initialState: PitchDeckState = {
  jobId: null,
  status: 'idle',
  progressMessage: '',
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
    setError: (state, action: PayloadAction<string>) => {
      state.status = 'failed'
      state.error = action.payload
    },
    reset: () => {
      return initialState
    },
  },
})

export const { setJobId, updateStatus, setResult, setError, reset } = pitchDeckSlice.actions
export default pitchDeckSlice.reducer
