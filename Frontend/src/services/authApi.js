import { apiRequest } from './apiClient'

export const authApi = {
  login: (email, password, remember = false) =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: { email, password, remember }
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

  getSubjects: () =>
    apiRequest('/auth/subjects', {
      method: 'GET'
    }),

  logout: () =>
    apiRequest('/auth/logout', {
      method: 'POST'
    })
}