import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { AuthContext, type AuthContextValue } from './auth-context'
import { api, setUnauthorizedHandler, tokenStorage } from '../services/api'
import type { AuthResponse, User } from '../types'

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(() => tokenStorage.get())
  // Only a stored token needs checking; without one the visitor is simply signed out.
  const [isLoading, setIsLoading] = useState<boolean>(() => tokenStorage.get() !== null)

  const clearSession = useCallback(() => {
    tokenStorage.clear()
    setToken(null)
    setUser(null)
  }, [])

  // When any request is rejected with 401, the API client clears the token and calls this.
  useEffect(() => {
    setUnauthorizedHandler(clearSession)
    return () => setUnauthorizedHandler(null)
  }, [clearSession])

  // Validate a token left over from a previous visit.
  useEffect(() => {
    if (tokenStorage.get() === null) {
      return
    }
    const controller = new AbortController()
    api
      .get<User>('/auth/me', { signal: controller.signal })
      .then(({ data }) => setUser(data))
      .catch(() => {
        // A 401 has already cleared the session through the API client. For any other
        // failure (such as the server being down) the token is kept for the next visit.
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      })
    return () => controller.abort()
  }, [])

  const startSession = useCallback((auth: AuthResponse) => {
    tokenStorage.set(auth.access_token)
    setToken(auth.access_token)
    setUser(auth.user)
  }, [])

  const login = useCallback(
    async (email: string, password: string) => {
      const { data } = await api.post<AuthResponse>('/auth/login', { email, password })
      startSession(data)
    },
    [startSession],
  )

  const signup = useCallback(
    async (fullName: string, email: string, password: string) => {
      const { data } = await api.post<AuthResponse>('/auth/signup', {
        full_name: fullName,
        email,
        password,
      })
      startSession(data)
    },
    [startSession],
  )

  const value = useMemo<AuthContextValue>(
    () => ({ user, token, isLoading, login, signup, logout: clearSession }),
    [user, token, isLoading, login, signup, clearSession],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
