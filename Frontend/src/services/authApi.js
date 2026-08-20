import { apiRequest } from './apiClient'

export const authApi = {
  login: (email, password, remember = false, role = '') =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: { email, password, remember, role }
    }),

  getSubjects: () =>
    apiRequest('/auth/subjects', {
      method: 'GET'
    }),

  register: (payload) =>
    apiRequest('/auth/register', {
      method: 'POST',
      body: payload
    }),

  checkParentEmail: (email) =>
    apiRequest('/auth/check-parent-email', {
      method: 'GET',
      params: { email }
    }),

  logout: () =>
    apiRequest('/auth/logout', {
      method: 'POST'
    })
}