const BASE_URL = 'http://localhost:5000/student';

/**
 * Helper to execute HTTP requests with JWT token + credentials
 */
async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;

  // Get token from localStorage
  const token = localStorage.getItem('token');

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    credentials: 'include',
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.message || `HTTP Error ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`[studentApi] Request to ${endpoint} failed:`, err.message);
    throw err;
  }
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
    body: JSON.stringify({ answers }),
  }),

  // Features 5 & 6: Booking
  getBookingSlots: () => request('/booking-slots'),
  bookSession: (sessionId) => request('/book-session', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  }),
  rescheduleSession: (currentSessionId, targetSessionId) => request('/reschedule-session', {
    method: 'POST',
    body: JSON.stringify({ current_session_id: currentSessionId, target_session_id: targetSessionId }),
  }),

  // Feature 7: Sessions
  getSessions: () => request('/sessions'),
  getUpcomingSessions: () => request('/upcoming-sessions'),
  getNextSession: () => request('/next-session'),

  // Feature 8: Study Tips
  getStudyTips: () => request('/study-tips'),

  // Feature 9: Assignments
  getAssignments: () => request('/assignments'),
  updateAssignmentProgress: (assignmentId, progress) => request(`/assignments/${assignmentId}/update-progress`, {
    method: 'POST',
    body: JSON.stringify({ progress }),
  }),
  submitAssignment: (assignmentId) => request(`/assignments/${assignmentId}/submit`, {
    method: 'POST',
    body: JSON.stringify({ progress: 100 }),
  }),

  // Additional
  getTimetable: () => request('/timetable'),
  getResources: () => request('/resources'),
  getProfile: () => request('/profile'),
  updateProfile: (data) => request('/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
};

export default studentApi;