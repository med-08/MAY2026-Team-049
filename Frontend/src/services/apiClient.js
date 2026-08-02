// Thin fetch wrapper around the Flask Admin Dashboard API.
//
// Assumes the backend's standard response envelope:
//   success: { success: true, data?: ..., message?: ..., meta?: ... }
//   error:   { success: false, message: "...", errors?: ... }
//
// Auth: the backend uses a real session cookie (Flask session, set by
// POST /login) to authenticate /admin/* routes via @admin_required. Every
// request here sends `credentials: 'include'` so that cookie is attached.
//
// Configure the API origin via VITE_API_BASE_URL (see .env.example). Falls
// back to http://localhost:5000 for local development against the Flask
// dev server started with `python app.py`.

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
 * @param {string} path - e.g. '/admin/students'
 * @param {object} [opts]
 * @param {'GET'|'POST'|'PUT'|'PATCH'|'DELETE'} [opts.method]
 * @param {object} [opts.body] - JSON-serializable request body
 * @param {object} [opts.params] - query string params (undefined/null/'' values are omitted)
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

  let response
  try {
    response = await fetch(url.toString(), {
      method,
      credentials: 'include', // send the Flask session cookie set by /login
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch (networkErr) {
    // fetch() throws (rather than resolving) on network failures, CORS
    // rejections, or the API being unreachable entirely.
    throw new ApiError(
      'Could not reach the LearnAtHome server. Please check your connection and try again.',
      0,
      networkErr.message
    )
  }

  let payload = null
  try {
    payload = await response.json()
  } catch {
    // Some responses (e.g. a 500 from an unhandled server crash) may not
    // return JSON at all; fall through with payload = null.
  }

  if (response.status === 401) {
    // The session expired or was never established. Clear the stale
    // client-side auth flag so the router guard sends the user back to
    // /login on their next navigation, instead of showing a broken page.
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  if (!response.ok || payload?.success === false) {
    const message = payload?.message || `Request failed with status ${response.status}.`
    throw new ApiError(message, response.status, payload?.errors)
  }

  return payload ?? {}
}
