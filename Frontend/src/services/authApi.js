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

  logout: () =>
    apiRequest('/auth/logout', {
      method: 'POST'
    })
}