import { apiClient } from '../client'
import type { UploadPitchDeckResponse, JobStatusResponse } from '../../types/api'

export const documentsApi = {
  uploadPitchDeck: async (file: File): Promise<UploadPitchDeckResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<UploadPitchDeckResponse>(
      '/v1/documents/pitch-deck',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data
  },

  getJobStatus: async (jobId: string): Promise<JobStatusResponse> => {
    const response = await apiClient.get<JobStatusResponse>(
      `/v1/jobs/${jobId}/status`
    )
    return response.data
  },

  downloadFile: (companyName: string, filePath: string): string => {
    return `${apiClient.defaults.baseURL}/v1/files/download/${companyName}/${filePath}`
  },
}
