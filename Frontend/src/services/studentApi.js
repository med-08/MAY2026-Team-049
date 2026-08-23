import { apiRequest } from './apiClient'

/**
 * Helper to execute HTTP requests with JWT token + credentials
 */
async function request(endpoint, options = {}) {
  return apiRequest(`/student${endpoint}`, options)
}

export const studentApi = {
  // Feature 1 & 3: Visual Dashboard & Progress Metrics
  getDashboard: () => request('/dashboard'),
  getProgress: () => request('/progress'),

  // Feature 2: FAQs Section
  getFaqs: (query = '') => request(`/faqs${query ? `?q=${encodeURIComponent(query)}` : ''}`),

  // Feature 4: Weekly Quizzes
  getQuizzes: () => request('/quizzes'),
  getQuizDetails: (quizId) => request(`/quizzes/${quizId}`),
  submitQuiz: (quizId, answers) => request(`/quizzes/${quizId}/submit`, {
    method: 'POST',
    body: { answers },
  }),

  // Features 5 & 6: Booking
  getBookingSlots: () => request('/booking-slots'),
  bookSession: (sessionId) => request('/book-session', {
    method: 'POST',
    body: { session_id: sessionId },
  }),
  rescheduleSession: (currentSessionId, targetSessionId) => request('/reschedule-session', {
    method: 'POST',
    body: { current_session_id: currentSessionId, target_session_id: targetSessionId },
  }),

  // Feature 7: Sessions
  getSessions: () => request('/sessions'),
  joinSession: (sessionId) => request(`/sessions/${sessionId}/join`, { method: 'POST' }),
  completeSession: (sessionId) => request(`/sessions/${sessionId}/complete`, { method: 'POST' }),
  getUpcomingSessions: () => request('/upcoming-sessions'),
  getNextSession: () => request('/next-session'),
  requestMeeting: (payload) => request('/meeting-request', { method: 'POST', body: payload }),

  // Feature 8: Study Tips
  getStudyTips: () => request('/study-tips'),
  getPerformanceInsights: () => request('/performance-insights', { method: 'POST' }),
  getFlashcards: (topic = '') => request(`/flashcards${topic ? `?topic=${encodeURIComponent(topic)}` : ''}`),
  getFlashcardSets: () => request('/flashcard-sets'),
  getFlashcardSetCards: (setId) => request(`/flashcard-sets/${setId}/cards`),
  aiGenerateFlashcards: (payload) => request('/flashcards/ai-generate', { method: 'POST', body: payload }),
  createOwnFlashcardSet: (payload) => request('/flashcard-sets/self-generate', { method: 'POST', body: payload }),
  performanceChat: (message) => request('/performance-chat', {
    method: 'POST',
    body: { message },
  }),

  // Feature 9: Assignments
  getAssignments: () => request('/assignments'),
  updateAssignmentProgress: (assignmentId, progress) => request(`/assignments/${assignmentId}/update-progress`, {
    method: 'POST',
    body: { progress },
  }),
  submitAssignment: (assignmentId) => request(`/assignments/${assignmentId}/submit`, {
    method: 'POST',
    body: { progress: 100 },
  }),
  markHomeworkCompleted: (assignmentId) => request(`/assignments/${assignmentId}/complete`, {
    method: 'POST',
  }),

  // Ask Doubt
  getDoubts: () => request('/doubts'),
  askDoubt: (payload) => request('/doubts', {
    method: 'POST',
    body: payload,
  }),
  getDoubtTutors: () => request('/tutors'),

  // Additional
  getTimetable: (year, month) => {
    const params = new URLSearchParams();
    if (year) params.set('year', year);
    if (month) params.set('month', month);
    const qs = params.toString();
    return request(`/timetable${qs ? `?${qs}` : ''}`);
  },
  getResources: () => request('/resources'),
  getSubjects: () => request('/subjects'),
  addSubject: (subjectId) => request('/subjects', { method: 'POST', body: { subject_id: subjectId } }),
  removeSubject: (subjectId) => request('/subjects', { method: 'DELETE', body: { subject_id: subjectId } }),
  getProfile: () => request('/profile'),
  updateProfile: (data) => request('/profile', { method: 'PUT', body: data }),
  changePassword: (data) => request('/profile/password', { method: 'PUT', body: data }),
  getMeetings: () => request('/meetings'),
  getNotifications: () => request('/notifications'),
  markNotificationRead: (id) => request(`/notifications/${id}/read`, { method: 'PATCH' }),
  getMessages: () => request('/messages'),
  sendMessage: (payload) => request('/messages', { method: 'POST', body: payload }),
};

export default studentApi;
