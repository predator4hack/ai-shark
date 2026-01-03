import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { AnalysisState, CompanyMetadata, AgentWeights } from '../../types/models'

const initialState: AnalysisState = {
  companyName: 'Nebula Robotics',
  metadata: {
    company_name: 'Nebula Robotics',
    round: 'Series A',
    ask: '$12M @ $60M Pre',
    sector: 'Deep Tech / AI',
  },
  documents: {
    pitchDeckPath: 'Nebula_Robotics_Series_A.pdf',
    additionalDocs: ['Nebula_Financials_FY23.xlsx'],
  },
  agentWeights: {
    business: { weight: 30, enabled: true },
    market: { weight: 40, enabled: true },
    tech: { weight: 20, enabled: true },
    risk: { weight: 10, enabled: true },
  },
  simulationMode: 'context',
  phases: {
    phase1: {
      id: 'phase1',
      status: 'completed',
      progressMessage: 'Pitch deck processed successfully',
    },
    phase2: {
      id: 'phase2',
      status: 'pending',
      progressMessage: '',
    },
    phase3: {
      id: 'phase3',
      status: 'pending',
      progressMessage: '',
    },
    phase4: {
      id: 'phase4',
      status: 'pending',
      progressMessage: '',
    },
    phase5: {
      id: 'phase5',
      status: 'pending',
      progressMessage: '',
    },
  },
  currentActivePhase: 2,
  overallStatus: 'idle',
  error: null,
}

const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    setCompanyData: (state, action: PayloadAction<{
      companyName: string
      metadata: CompanyMetadata
    }>) => {
      state.companyName = action.payload.companyName
      state.metadata = action.payload.metadata
    },
    uploadPitchDeck: (state, action: PayloadAction<string>) => {
      state.documents.pitchDeckPath = action.payload
      state.phases.phase1.status = 'completed'
      state.phases.phase1.progressMessage = 'Pitch deck processed successfully'
    },
    uploadAdditionalDocument: (state, action: PayloadAction<string>) => {
      state.documents.additionalDocs.push(action.payload)
    },
    removeDocument: (state, action: PayloadAction<string>) => {
      state.documents.additionalDocs = state.documents.additionalDocs.filter(
        doc => doc !== action.payload
      )
    },
    updatePhaseStatus: (state, action: PayloadAction<{
      phaseId: 'phase1' | 'phase2' | 'phase3' | 'phase4' | 'phase5'
      status: 'pending' | 'running' | 'completed' | 'failed'
      progressMessage?: string
      result?: any
      error?: string
    }>) => {
      const { phaseId, status, progressMessage, result, error } = action.payload
      state.phases[phaseId].status = status
      if (progressMessage !== undefined) {
        state.phases[phaseId].progressMessage = progressMessage
      }
      if (result !== undefined) {
        state.phases[phaseId].result = result
      }
      if (error !== undefined) {
        state.phases[phaseId].error = error
      }
    },
    updateAgentWeights: (state, action: PayloadAction<AgentWeights>) => {
      state.agentWeights = action.payload
    },
    applyWeightTemplate: (state, action: PayloadAction<'balanced' | 'tech-focused' | 'market-focused'>) => {
      const template = action.payload
      switch (template) {
        case 'balanced':
          state.agentWeights = {
            business: { weight: 30, enabled: true },
            market: { weight: 40, enabled: true },
            tech: { weight: 20, enabled: true },
            risk: { weight: 10, enabled: true },
          }
          break
        case 'tech-focused':
          state.agentWeights = {
            business: { weight: 20, enabled: true },
            market: { weight: 20, enabled: true },
            tech: { weight: 50, enabled: true },
            risk: { weight: 10, enabled: true },
          }
          break
        case 'market-focused':
          state.agentWeights = {
            business: { weight: 20, enabled: true },
            market: { weight: 50, enabled: true },
            tech: { weight: 20, enabled: true },
            risk: { weight: 10, enabled: true },
          }
          break
      }
    },
    setSimulationMode: (state, action: PayloadAction<'context' | 'direct-qa'>) => {
      state.simulationMode = action.payload
    },
    setCurrentActivePhase: (state, action: PayloadAction<number>) => {
      state.currentActivePhase = action.payload
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload
      state.overallStatus = 'failed'
    },
    clearError: (state) => {
      state.error = null
    },
    reset: () => {
      return initialState
    },
  },
})

export const {
  setCompanyData,
  uploadPitchDeck,
  uploadAdditionalDocument,
  removeDocument,
  updatePhaseStatus,
  updateAgentWeights,
  applyWeightTemplate,
  setSimulationMode,
  setCurrentActivePhase,
  setError,
  clearError,
  reset,
} = analysisSlice.actions

export default analysisSlice.reducer
