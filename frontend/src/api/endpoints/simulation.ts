import { apiClient } from '../client'

export interface SimulateQAResponse {
  job_id: string
  message: string
  company_name: string
}

export const simulationApi = {
  /**
   * Trigger AI Q&A simulation
   */
  simulateQA: async (companyName: string): Promise<SimulateQAResponse> => {
    const response = await apiClient.post('/v1/analysis/simulate-qa', {
      company_name: companyName
    })
    return response.data
  },

  /**
   * Upload direct Q&A document
   */
  uploadDirectQA: async (file: File, companyName: string): Promise<SimulateQAResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('company_name', companyName)

    const response = await apiClient.post('/v1/analysis/upload-qa', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }
}
