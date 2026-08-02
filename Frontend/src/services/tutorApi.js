import { apiRequest } from './apiClient'

const BASE = '/tutor'

export const tutorApi = {
  // ---- Dashboard ----
  getDashboard: () => apiRequest(`${BASE}/dashboard`),

  // ---- Schedule ----
  getSchedule: () => apiRequest(`${BASE}/schedule`),
  addClass: (payload) => apiRequest(`${BASE}/schedule/class`, { method: 'POST', body: payload }),

  // ---- Students ----
  getStudents: () => apiRequest(`${BASE}/students`),

  // ---- Attendance ----
  getAttendance: () => apiRequest(`${BASE}/attendance`),
  markAttendance: (records) => apiRequest(`${BASE}/attendance`, { method: 'POST', body: { records } }),
  sendSessionUpdate: (payload) => apiRequest(`${BASE}/session-update`, { method: 'POST', body: payload }),

  // ---- Assignments ----
  getAssignments: () => apiRequest(`${BASE}/assignments`),
  createAssignment: (payload) => apiRequest(`${BASE}/assignments`, { method: 'POST', body: payload }),
  aiGenerateQuestions: () => apiRequest(`${BASE}/assignments/ai-generate`, { method: 'POST' }),
  deleteAssignment: (id) => apiRequest(`${BASE}/assignments/${id}`, { method: 'DELETE' }),

  // ---- Materials ----
  getMaterials: () => apiRequest(`${BASE}/materials`),
  uploadMaterial: (payload) => apiRequest(`${BASE}/materials`, { method: 'POST', body: payload }),
  deleteMaterial: (id) => apiRequest(`${BASE}/materials/${id}`, { method: 'DELETE' }),

  // ---- Q&A Board ----
  getQaEntries: () => apiRequest(`${BASE}/qa`),
  publishQaEntry: (payload) => apiRequest(`${BASE}/qa`, { method: 'POST', body: payload }),

  // ---- Doubts ----
  getDoubts: () => apiRequest(`${BASE}/doubts`),
  replyDoubt: (doubtId, reply) => apiRequest(`${BASE}/doubts/${doubtId}/reply`, { method: 'POST', body: { reply } }),

  // ---- Messages & Meetings ----
  getConversations: () => apiRequest(`${BASE}/messages/conversations`),
  sendMessage: (payload) => apiRequest(`${BASE}/messages/send`, { method: 'POST', body: payload }),
  requestMeeting: (payload) => apiRequest(`${BASE}/meetings/request`, { method: 'POST', body: payload }),

  // ---- Earnings ----
  getEarnings: () => apiRequest(`${BASE}/earnings`),

  // ---- Profile ----
  getProfile: () => apiRequest(`${BASE}/profile`),
  updateProfile: (payload) => apiRequest(`${BASE}/profile`, { method: 'PUT', body: payload }),

  // ---- Notifications ----
  getNotifications: () => apiRequest(`${BASE}/notifications`),
  markNotificationRead: (id) => apiRequest(`${BASE}/notifications/${id}/read`, { method: 'PATCH' }),

  // ---- Auth ----
  logout: () => apiRequest('/logout', { method: 'POST' })
}
