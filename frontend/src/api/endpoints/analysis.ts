import { apiClient } from '../client'
import type {
  DiscoverAgentsResponse,
  RunAnalysisRequest,
  RunAnalysisResponse,
} from '../../types/models'

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
}
