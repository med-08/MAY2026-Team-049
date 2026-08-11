import { apiRequest } from './apiClient'

const BASE = '/parent'

export const parentApi = {
  checkHealth: () => apiRequest(`${BASE}/health`),

  getProfile: (parentId) => apiRequest(`${BASE}/profile/${parentId}`),

  updateProfile: (parentId, data) =>
    apiRequest(`${BASE}/profile/${parentId}`, { method: 'PUT', body: data }),

  getOverview: (parentId) => apiRequest(`${BASE}/overview/${parentId}`),

  requestMeeting: (payload) =>
    apiRequest(`${BASE}/meeting-request`, { method: 'POST', body: payload }),

  getMeetings: (parentId) =>
    apiRequest(`${BASE}/meetings/${parentId}`),

  getChildProgress: (parentId, studentId) =>
    apiRequest(`${BASE}/child-progress/${parentId}/${studentId}`),

  getChildCurriculum: (studentId) =>
    apiRequest(`${BASE}/curriculum/${studentId}`),

  generateWeeklyReport: (studentId) =>
    apiRequest(`${BASE}/generate-report/${studentId}`, { method: 'POST' })
}