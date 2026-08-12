import { apiRequest } from './apiClient'

const BASE = '/tutor'

export const tutorApi = {
  // ---- Dashboard ----
  getDashboard: () => apiRequest(`${BASE}/dashboard`),

  // ---- Schedule ----
  getSchedule: () => apiRequest(`${BASE}/schedule`),
  addClass: (payload) => apiRequest(`${BASE}/schedule/class`, { method: 'POST', body: payload }),
  startClass: (sessionId) => apiRequest(`${BASE}/schedule/class/${sessionId}/start`, { method: 'POST' }),

  // ---- Students ----
  getStudents: () => apiRequest(`${BASE}/students`),

  // ---- Attendance ----
  getAttendance: () => apiRequest(`${BASE}/attendance`),
  markAttendance: (records) => apiRequest(`${BASE}/attendance`, { method: 'POST', body: { records } }),
  sendSessionUpdate: (payload) => apiRequest(`${BASE}/session-update`, { method: 'POST', body: payload }),
  aiGenerateSessionSummary: (bulletPoints) => apiRequest(`${BASE}/session-summary/draft`, { method: 'POST', body: { bullet_points: bulletPoints } }),

  // ---- Assignments & Submissions ----
  getAssignments: () => apiRequest(`${BASE}/assignments`),
  createAssignment: (payload) => apiRequest(`${BASE}/assignments`, { method: 'POST', body: payload }),
  aiGenerateQuestions: (topic) => apiRequest(`${BASE}/assignments/ai-generate`, { method: 'POST', body: { topic } }),
  aiGenerateQuizFull: (payload) => apiRequest(`${BASE}/assignments/ai-generate`, { method: 'POST', body: payload }),
  createAndAssignQuiz: (payload) => apiRequest(`${BASE}/assignments/create-and-assign`, { method: 'POST', body: payload }),
  deleteAssignment: (id) => apiRequest(`${BASE}/assignments/${id}`, { method: 'DELETE' }),
  getSubmissions: () => apiRequest(`${BASE}/assignments/submissions`),
  gradeSubmission: (subId, payload) => apiRequest(`${BASE}/assignments/submissions/${subId}/grade`, { method: 'POST', body: payload }),
  getQuizzes: () => apiRequest(`${BASE}/quizzes`),
  createQuiz: (payload) => apiRequest(`${BASE}/quizzes`, { method: 'POST', body: payload }),
  addQuizQuestion: (quizId, payload) => apiRequest(`${BASE}/quizzes/${quizId}/questions`, { method: 'POST', body: payload }),

  // ---- Teaching Plans & Weekly Summaries ----
  getTeachingPlans: () => apiRequest(`${BASE}/teaching-plans`),
  createTeachingPlan: (payload) => apiRequest(`${BASE}/teaching-plans`, { method: 'POST', body: payload }),
  getWeeklySummaries: () => apiRequest(`${BASE}/weekly-summaries`),
  createWeeklySummary: (payload) => apiRequest(`${BASE}/weekly-summaries`, { method: 'POST', body: payload }),

  // ---- Materials ----
  getMaterials: () => apiRequest(`${BASE}/materials`),
  uploadMaterial: (payload) => apiRequest(`${BASE}/materials`, { method: 'POST', body: payload }),
  deleteMaterial: (id) => apiRequest(`${BASE}/materials/${id}`, { method: 'DELETE' }),

  // ---- Q&A Board ----
  getQaEntries: () => apiRequest(`${BASE}/qa`),
  publishQaEntry: (payload) => apiRequest(`${BASE}/qa`, { method: 'POST', body: payload }),
  deleteQaEntry: (id) => apiRequest(`${BASE}/qa/${id}`, { method: 'DELETE' }),

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
