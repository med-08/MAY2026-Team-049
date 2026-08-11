const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

export class ApiError extends Error {
  constructor(message, status, details) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.details = details
  }
}

/**
 * Generic API request helper
 * - Sends JWT token (from localStorage) if available
 * - Also sends session cookies
 */
export async function apiRequest(path, { method = 'GET', body, params } = {}) {
  const url = new URL(BASE_URL + path)

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.set(key, value)
      }
    })
  }

  const token = localStorage.getItem('token')

  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData
  const headers = {
    ...(body !== undefined && !isFormData && { 'Content-Type': 'application/json' }),
    ...(token && { Authorization: `Bearer ${token}` }),
  }

  let response
  try {
    response = await fetch(url.toString(), {
      method,
      credentials: 'include',
      headers,
      body: body !== undefined ? (isFormData ? body : JSON.stringify(body)) : undefined,
    })
  } catch (networkErr) {
    throw new ApiError(
      'Could not reach the LearnAtHome server. Please check your connection.',
      0,
      networkErr.message
    )
  }

  let payload = null
  try {
    payload = await response.json()
  } catch {
    payload = null
  }

  if (response.status === 401) {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    localStorage.removeItem('parent_id')
    localStorage.removeItem('student_id')
    localStorage.removeItem('tutor_id')
  }

  if (!response.ok || payload?.success === false || payload?.status === 'error') {
    const message = payload?.message || `Request failed with status ${response.status}.`
    throw new ApiError(message, response.status, payload?.errors)
  }

  return payload ?? {}
}