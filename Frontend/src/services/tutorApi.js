import { apiRequest } from './apiClient'

const BASE = '/tutor'

export const tutorApi = {

  // ==========================================================
  // DASHBOARD
  // ==========================================================

  getDashboard: () =>
    apiRequest(`${BASE}/dashboard`),


  // ==========================================================
  // SCHEDULE
  // ==========================================================

  getSchedule: () =>
    apiRequest(`${BASE}/schedule`),

  addClass: (payload) =>
    apiRequest(
      `${BASE}/schedule/class`,
      {
        method: 'POST',
        body: payload
      }
    ),

  updateClass: (sessionId, payload) =>
    apiRequest(
      `${BASE}/schedule/class/${sessionId}`,
      {
        method: 'PUT',
        body: payload
      }
    ),

  deleteClass: (sessionId) =>
    apiRequest(
      `${BASE}/schedule/class/${sessionId}`,
      {
        method: 'DELETE'
      }
    ),

  startClass: (sessionId) =>
    apiRequest(
      `${BASE}/schedule/class/${sessionId}/start`,
      {
        method: 'POST'
      }
    ),

  endClass: (sessionId) =>
    apiRequest(
      `${BASE}/schedule/class/${sessionId}/end`,
      {
        method: 'POST'
      }
    ),


  // ==========================================================
  // MEETING REQUESTS
  // ==========================================================

  getMeetingRequests: () =>
    apiRequest(
      `${BASE}/meetings/requests`
    ),

  decideMeeting: (
    meetingId,
    payload
  ) =>
    apiRequest(
      `${BASE}/meetings/${meetingId}/decision`,
      {
        method: 'POST',
        body: payload
      }
    ),

  requestMeeting: (payload) =>
    apiRequest(
      `${BASE}/meetings/request`,
      {
        method: 'POST',
        body: payload
      }
    ),

  getSessionDetails: (sessionId) =>
    apiRequest(
      `${BASE}/session/${sessionId}/details`
    ),

  saveSessionDetails: (
    sessionId,
    records
  ) =>
    apiRequest(
      `${BASE}/session/${sessionId}/details`,
      {
        method: 'PUT',
        body: {
          records
        }
      }
    ),


  // ==========================================================
  // STUDENTS
  // ==========================================================

  getStudents: () =>
    apiRequest(
      `${BASE}/students`
    ),


  // ==========================================================
  // ATTENDANCE
  // ==========================================================

  getAttendance: () =>
    apiRequest(
      `${BASE}/attendance`
    ),

  markAttendance: (records) =>
    apiRequest(
      `${BASE}/attendance`,
      {
        method: 'POST',
        body: {
          records
        }
      }
    ),


  // ==========================================================
  // SESSION UPDATE
  // ==========================================================

  sendSessionUpdate: (payload) =>
    apiRequest(
      `${BASE}/session-update`,
      {
        method: 'POST',
        body: payload
      }
    ),


  // ==========================================================
  // MESSAGES
  // ==========================================================

  getConversations: () =>
    apiRequest(
      `${BASE}/messages/conversations`
    ),

  sendMessage: (payload) =>
    apiRequest(
      `${BASE}/messages/send`,
      {
        method: 'POST',
        body: payload
      }
    ),


  // ==========================================================
  // ASSIGNMENTS
  // ==========================================================

  getAssignments: () =>
    apiRequest(
      `${BASE}/assignments`
    ),

  createAssignment: (payload) =>
    apiRequest(
      `${BASE}/assignments`,
      {
        method: 'POST',
        body: payload
      }
    ),

  aiGenerateQuestions: (payload = {}) =>
    apiRequest(
      `${BASE}/assignments/ai-generate`,
      {
        method: 'POST',
        body: payload
      }
    ),

  deleteAssignment: (id) =>
    apiRequest(
      `${BASE}/assignments/${id}`,
      {
        method: 'DELETE'
      }
    ),


  // ==========================================================
  // QUIZZES
  // ==========================================================

  getQuizzes: () =>
    apiRequest(
      `${BASE}/quizzes`
    ),

  createQuiz: (payload) =>
    apiRequest(
      `${BASE}/quizzes`,
      {
        method: 'POST',
        body: payload
      }
    ),

  addQuizQuestion: (
    quizId,
    payload
  ) =>
    apiRequest(
      `${BASE}/quizzes/${quizId}/questions`,
      {
        method: 'POST',
        body: payload
      }
    ),


  // ==========================================================
  // FLASHCARDS
  // ==========================================================

  aiGenerateFlashcards: (payload = {}) =>
    apiRequest(
      `${BASE}/flashcards/ai-generate`,
      {
        method: 'POST',
        body: payload
      }
    ),

  getFlashcardSets: () =>
    apiRequest(
      `${BASE}/flashcard-sets`
    ),

  createFlashcardSet: (payload) =>
    apiRequest(
      `${BASE}/flashcard-sets`,
      {
        method: 'POST',
        body: payload
      }
    ),

  addFlashcard: (
    setId,
    payload
  ) =>
    apiRequest(
      `${BASE}/flashcard-sets/${setId}/cards`,
      {
        method: 'POST',
        body: payload
      }
    ),


  // ==========================================================
  // MATERIALS
  // ==========================================================

  getMaterials: () =>
    apiRequest(
      `${BASE}/materials`
    ),

  uploadMaterial: (payload) =>
    apiRequest(
      `${BASE}/materials`,
      {
        method: 'POST',
        body: payload
      }
    ),

  deleteMaterial: (id) =>
    apiRequest(
      `${BASE}/materials/${id}`,
      {
        method: 'DELETE'
      }
    ),


  // ==========================================================
  // Q&A
  // ==========================================================

  getQaEntries: () =>
    apiRequest(
      `${BASE}/qa`
    ),

  publishQaEntry: (payload) =>
    apiRequest(
      `${BASE}/qa`,
      {
        method: 'POST',
        body: payload
      }
    ),

  deleteQaEntry: (id) =>
    apiRequest(
      `${BASE}/qa/${id}`,
      {
        method: 'DELETE'
      }
    ),


  // ==========================================================
  // DOUBTS
  // ==========================================================

  getDoubts: () =>
    apiRequest(
      `${BASE}/doubts`
    ),

  replyDoubt: (
    doubtId,
    reply
  ) =>
    apiRequest(
      `${BASE}/doubts/${doubtId}/reply`,
      {
        method: 'POST',
        body: {
          reply
        }
      }
    ),


  // ==========================================================
  // PROFILE
  // ==========================================================

  getProfile: () =>
    apiRequest(
      `${BASE}/profile`
    ),

  updateProfile: (payload) =>
    apiRequest(
      `${BASE}/profile`,
      {
        method: 'PUT',
        body: payload
      }
    ),


  // ==========================================================
  // NOTIFICATIONS
  // ==========================================================

  getNotifications: () =>
    apiRequest(
      `${BASE}/notifications`
    ),

  markNotificationRead: (id) =>
    apiRequest(
      `${BASE}/notifications/${id}/read`,
      {
        method: 'PATCH'
      }
    ),


  // ==========================================================
  // LOGOUT
  // ==========================================================

  logout: () =>
    apiRequest(
      '/logout',
      {
        method: 'POST'
      }
    )

}
