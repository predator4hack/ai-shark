export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const FILE_UPLOAD = {
  MAX_SIZE_MB: 100,
  ACCEPTED_TYPES: ['.pdf', '.ppt', '.pptx'],
  MIME_TYPES: {
    'application/pdf': ['.pdf'],
    'application/vnd.ms-powerpoint': ['.ppt'],
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  }
}

export const POLLING = {
  INTERVAL_MS: 2000, // 2 seconds
  MAX_RETRIES: 3,
}

export const ROUTES = {
  HOME: '/',
  PITCH_DECK: '/',
  RESULTS: '/results',
}
