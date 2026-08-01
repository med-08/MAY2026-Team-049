// Typed(ish) wrapper functions for every Admin Dashboard endpoint. Views
// should import from here rather than calling apiRequest directly, so the
// URL paths only live in one place.
//
// Base path is '/admin' (no '/api' prefix) to match the Flask blueprint's
// url_prefix in Backend/admin/__init__.py.
import { apiRequest } from './apiClient'

const BASE = '/admin'

export const adminApi = {
  // ---- Dashboard ----
  getStats: () => apiRequest(`${BASE}/dashboard/stats`),
  getStudentsPerSubject: () => apiRequest(`${BASE}/dashboard/analytics/students-per-subject`),
  getMonthlyRegistrations: (months = 7) =>
    apiRequest(`${BASE}/dashboard/analytics/monthly-registrations`, { params: { months } }),

  // ---- Students ----
  listStudents: (params) => apiRequest(`${BASE}/students`, { params }),
  getStudent: (id) => apiRequest(`${BASE}/students/${id}`),
  updateStudentStatus: (id, status) =>
    apiRequest(`${BASE}/students/${id}/status`, { method: 'PATCH', body: { status } }),
  deleteStudent: (id) => apiRequest(`${BASE}/students/${id}`, { method: 'DELETE' }),

  // ---- Parents ----
  listParents: (params) => apiRequest(`${BASE}/parents`, { params }),
  getParent: (id) => apiRequest(`${BASE}/parents/${id}`),
  updateParentStatus: (id, status) =>
    apiRequest(`${BASE}/parents/${id}/status`, { method: 'PATCH', body: { status } }),
  deleteParent: (id) => apiRequest(`${BASE}/parents/${id}`, { method: 'DELETE' }),

  // ---- Tutors ----
  listTutors: (params) => apiRequest(`${BASE}/tutors`, { params }),
  getTutor: (id) => apiRequest(`${BASE}/tutors/${id}`),

  // ---- Approvals ----
  listApprovals: (status = 'Pending') => apiRequest(`${BASE}/approvals`, { params: { status } }),
  approveEntity: (entityType, id) =>
    apiRequest(`${BASE}/approvals/${entityType}/${id}/approve`, { method: 'PATCH' }),
  rejectEntity: (entityType, id) =>
    apiRequest(`${BASE}/approvals/${entityType}/${id}/reject`, { method: 'PATCH' }),

  // ---- Profile (self-service, derived from the session -- no id needed) ----
  getProfile: () => apiRequest(`${BASE}/profile/me`),
  updateProfile: (payload) => apiRequest(`${BASE}/profile/me`, { method: 'PUT', body: payload }),
  changePassword: (payload) => apiRequest(`${BASE}/profile/me/password`, { method: 'PUT', body: payload }),

  // ---- Auth (login/logout live at the app root, not under /admin) ----
  login: (identifier, password, remember = false) =>
    apiRequest('/login', { method: 'POST', body: { identifier, password, remember } }),
  logout: () => apiRequest('/logout', { method: 'POST' }),
}
