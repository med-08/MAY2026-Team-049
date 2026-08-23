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

  getSchedule: (parentId) => apiRequest(`${BASE}/schedule/${parentId}`),
  updateScheduleSession: (sessionId, payload) => apiRequest(`${BASE}/schedule/session/${sessionId}`, { method: 'PUT', body: payload }),
  startScheduleSession: (sessionId) => apiRequest(`${BASE}/schedule/session/${sessionId}/start`, { method: 'POST' }),
  endScheduleSession: (sessionId) => apiRequest(`${BASE}/schedule/session/${sessionId}/end`, { method: 'POST' }),
  cancelScheduleSession: (sessionId) => apiRequest(`${BASE}/schedule/session/${sessionId}`, { method: 'DELETE' }),
  requestAttendanceConfirmation: (studentId, sessionId) => apiRequest(`${BASE}/attendance-query`, { method: 'POST', body: { student_id: studentId, session_id: sessionId } }),
  markNotificationRead: (id) => apiRequest(`${BASE}/notifications/${id}/read`, { method: 'PATCH' }),

  // Two-Way Parent-Tutor Communication
  getMessages: (parentId) => apiRequest(`${BASE}/messages/${parentId}`),

  sendMessage: (payload) =>
    apiRequest(`${BASE}/messages/send`, { method: 'POST', body: payload }),

  // Weekly Progress Summary Report
  getWeeklySummary: (parentId, studentId) =>
    apiRequest(`${BASE}/weekly-summary/${parentId}/${studentId}`),

  generateWeeklyReport: (parentId, studentId) =>
    apiRequest(`${BASE}/ai-weekly-report/${parentId}/${studentId}`, { method: 'POST' }),

  getNotifications: (parentId) => apiRequest(`${BASE}/notifications/${parentId}`)
}

export default parentApi
