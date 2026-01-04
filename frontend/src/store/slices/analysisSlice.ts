import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { AnalysisState, CompanyMetadata, AgentWeights, AgentInfo } from '../../types/models'

const initialState: AnalysisState = {
  companyName: null,
  metadata: null,
  documents: {
    pitchDeckPath: null,
    additionalDocs: [],
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
      status: 'pending',
      progressMessage: '',
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
  currentActivePhase: 1,
  overallStatus: 'idle',
  error: null,
  uploadJobId: null,
  uploadStatus: 'idle',
  uploadProgress: '',
  // Phase 2: Multi-agent analysis
  availableAgents: [],
  selectedAgents: [],
  analysisJobId: null,
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
    setUploadJobId: (state, action: PayloadAction<string>) => {
      state.uploadJobId = action.payload
      state.uploadStatus = 'processing'
      state.phases.phase1.status = 'running'
      state.phases.phase1.progressMessage = 'Processing pitch deck...'
    },
    updateUploadStatus: (state, action: PayloadAction<{
      status: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed'
      progressMessage: string
    }>) => {
      state.uploadStatus = action.payload.status
      state.uploadProgress = action.payload.progressMessage
      state.phases.phase1.progressMessage = action.payload.progressMessage
    },
    setUploadResult: (state, action: PayloadAction<{
      companyName: string
      metadata: CompanyMetadata
      files: string[]
    }>) => {
      state.companyName = action.payload.companyName
      state.metadata = action.payload.metadata
      state.documents.pitchDeckPath = action.payload.files[0] || null
      state.uploadStatus = 'completed'
      state.phases.phase1.status = 'completed'
      state.phases.phase1.progressMessage = 'Pitch deck processed successfully'
      state.phases.phase1.result = { files: action.payload.files }
      state.currentActivePhase = 2
    },
    setUploadError: (state, action: PayloadAction<string>) => {
      state.uploadStatus = 'failed'
      state.phases.phase1.status = 'failed'
      state.phases.phase1.error = action.payload
      state.error = action.payload
    },
    resetUpload: (state) => {
      state.uploadJobId = null
      state.uploadStatus = 'idle'
      state.uploadProgress = ''
      state.companyName = null
      state.metadata = null
      state.documents.pitchDeckPath = null
      state.phases.phase1.status = 'pending'
      state.phases.phase1.progressMessage = ''
      state.phases.phase1.error = undefined
      state.currentActivePhase = 1
      state.error = null
    },
    // Phase 2: Multi-agent analysis actions
    setAvailableAgents: (state, action: PayloadAction<AgentInfo[]>) => {
      state.availableAgents = action.payload
      // Auto-select all available agents by default
      state.selectedAgents = action.payload
        .filter(agent => agent.available)
        .map(agent => agent.agent_type)
    },
    toggleAgentSelection: (state, action: PayloadAction<string>) => {
      const agentType = action.payload
      const index = state.selectedAgents.indexOf(agentType)
      if (index > -1) {
        // Deselect agent
        state.selectedAgents = state.selectedAgents.filter(a => a !== agentType)
      } else {
        // Select agent (only if it's available)
        const agent = state.availableAgents.find(a => a.agent_type === agentType)
        if (agent && agent.available) {
          state.selectedAgents.push(agentType)
        }
      }
    },
    setSelectedAgents: (state, action: PayloadAction<string[]>) => {
      // Filter to only include available agents
      const availableAgentTypes = state.availableAgents
        .filter(a => a.available)
        .map(a => a.agent_type)
      state.selectedAgents = action.payload.filter(a =>
        availableAgentTypes.includes(a)
      )
    },
    setAnalysisJobId: (state, action: PayloadAction<string>) => {
      state.analysisJobId = action.payload
      state.phases.phase3.status = 'running'
      state.phases.phase3.progressMessage = 'Running multi-agent analysis...'
    },
    setAnalysisResult: (state, action: PayloadAction<any>) => {
      state.phases.phase3.status = 'completed'
      state.phases.phase3.progressMessage = 'Multi-agent analysis completed!'
      state.phases.phase3.result = action.payload
      state.analysisJobId = null
      state.currentActivePhase = 4
    },
    setAnalysisError: (state, action: PayloadAction<string>) => {
      state.phases.phase3.status = 'failed'
      state.phases.phase3.error = action.payload
      state.error = action.payload
      state.analysisJobId = null
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
  setUploadJobId,
  updateUploadStatus,
  setUploadResult,
  setUploadError,
  resetUpload,
  setAvailableAgents,
  toggleAgentSelection,
  setSelectedAgents,
  setAnalysisJobId,
  setAnalysisResult,
  setAnalysisError,
  reset,
} = analysisSlice.actions

export default analysisSlice.reducer
