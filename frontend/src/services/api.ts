import axios from 'axios'

export const TOKEN_STORAGE_KEY = 'alcsr_token'

const DEFAULT_ERROR_MESSAGE = 'Something went wrong. Try again.'

/** A 401 from these endpoints means wrong credentials, not an expired session. */
const CREDENTIAL_ENDPOINTS = ['/auth/login', '/auth/signup']

/** Access to the stored token. Storage can be unavailable (private mode), so never throw. */
export const tokenStorage = {
  get(): string | null {
    try {
      return window.localStorage.getItem(TOKEN_STORAGE_KEY)
    } catch {
      return null
    }
  },
  set(token: string): void {
    try {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token)
    } catch {
      // The session then lasts only until the page is reloaded.
    }
  },
  clear(): void {
    try {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY)
    } catch {
      // Nothing was stored, so there is nothing to clear.
    }
  },
}

let unauthorizedHandler: (() => void) | null = null

/**
 * Register what happens when the server rejects the token. AuthProvider uses this to clear
 * the signed-in user, after which ProtectedRoute sends the browser to /login.
 */
export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 15_000,
  headers: { Accept: 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = tokenStorage.get()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const url = error.config?.url ?? ''
      if (!CREDENTIAL_ENDPOINTS.some((endpoint) => url.includes(endpoint))) {
        tokenStorage.clear()
        if (unauthorizedHandler) {
          unauthorizedHandler()
        } else if (window.location.pathname !== '/login') {
          window.location.assign('/login')
        }
      }
    }
    return Promise.reject(error)
  },
)

interface ValidationIssue {
  msg?: unknown
}

function readDetail(data: unknown): string | null {
  if (typeof data !== 'object' || data === null || !('detail' in data)) {
    return null
  }
  const { detail } = data
  if (typeof detail === 'string') {
    return detail
  }
  // FastAPI reports request validation errors as a list of issues.
  if (Array.isArray(detail)) {
    const messages = (detail as ValidationIssue[])
      .map((issue) => (typeof issue?.msg === 'string' ? issue.msg : null))
      .filter((message): message is string => message !== null)
    return messages.length > 0 ? messages.join('. ') : null
  }
  return null
}

/** Turn any thrown value from an API call into a message that can be shown to the user. */
export function getErrorMessage(error: unknown, fallback: string = DEFAULT_ERROR_MESSAGE): string {
  if (axios.isCancel(error)) {
    return fallback
  }
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return 'Cannot reach the server. Check your connection and try again.'
    }
    return readDetail(error.response.data) ?? fallback
  }
  return fallback
}
