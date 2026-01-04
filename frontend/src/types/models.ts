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

// Analysis domain types
export interface AgentConfig {
  weight: number
  enabled: boolean
}

export interface AgentWeights {
  business: AgentConfig
  market: AgentConfig
  tech: AgentConfig
  risk: AgentConfig
}

export interface PhaseResult {
  id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progressMessage: string
  result?: any
  error?: string
}

export interface AnalysisDocuments {
  pitchDeckPath: string | null
  additionalDocs: string[]
}

export interface CompanyMetadata {
  company_name: string
  startup_name?: string
  sector?: string
  sub_sector?: string
  website?: string | null
  round?: string
  ask?: string
  valuation?: string
  [key: string]: any
}

// Multi-agent analysis types
export interface AgentInfo {
  agent_type: string
  agent_name: string
  description: string
  available: boolean
}

export interface DiscoverAgentsResponse {
  agents: AgentInfo[]
  total_agents: number
  available_agents: number
}

export interface RunAnalysisRequest {
  company_name: string
  selected_agents: string[]
}

export interface RunAnalysisResponse {
  job_id: string
  message: string
  company_name: string
  selected_agents: string[]
}

export interface AnalysisState {
  companyName: string | null
  metadata: CompanyMetadata | null
  documents: AnalysisDocuments
  agentWeights: AgentWeights
  simulationMode: 'context' | 'direct-qa'
  phases: {
    phase1: PhaseResult
    phase2: PhaseResult
    phase3: PhaseResult
    phase4: PhaseResult
    phase5: PhaseResult
  }
  currentActivePhase: number
  overallStatus: 'idle' | 'analyzing' | 'completed' | 'failed'
  error: string | null
  uploadJobId: string | null
  uploadStatus: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed'
  uploadProgress: string
  // Phase 2: Multi-agent analysis
  availableAgents: AgentInfo[]
  selectedAgents: string[]
  analysisJobId: string | null
}
