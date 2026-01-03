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
  round?: string
  ask?: string
  valuation?: string
  sector?: string
  [key: string]: any
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
}
