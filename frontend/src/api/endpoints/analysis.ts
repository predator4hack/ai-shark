import { apiClient } from '../client'
import type {
  DiscoverAgentsResponse,
  RunAnalysisRequest,
  RunAnalysisResponse,
} from '../../types/models'

export interface GenerateMemoRequest {
  company_name: string
  agent_weights: {
    [key: string]: number // e.g., { "business": 25, "market": 25, ... }
  }
}

export interface GenerateMemoResponse {
  job_id: string
  message: string
  company_name: string
}

export const analysisApi = {
  /**
   * Discover available analysis agents
   */
  discoverAgents: async (): Promise<DiscoverAgentsResponse> => {
    const response = await apiClient.get<DiscoverAgentsResponse>(
      '/v1/analysis/discover-agents'
    )
    return response.data
  },

  /**
   * Run multi-agent analysis with selected agents
   */
  runAnalysis: async (request: RunAnalysisRequest): Promise<RunAnalysisResponse> => {
    const response = await apiClient.post<RunAnalysisResponse>(
      '/v1/analysis/run-agents',
      request
    )
    return response.data
  },

  /**
   * Generate final investment memo with weighted analysis
   */
  generateMemo: async (request: GenerateMemoRequest): Promise<GenerateMemoResponse> => {
    const response = await apiClient.post<GenerateMemoResponse>(
      '/v1/analysis/generate-memo',
      request
    )
    return response.data
  },
}
