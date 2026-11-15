import { createContext } from 'react'

import type { User } from '../types'

export interface AuthContextValue {
  /** The signed-in user, or null when nobody is signed in. */
  user: User | null
  token: string | null
  /** True while a stored token is being checked with the server on first load. */
  isLoading: boolean
  /** Rejects with the request error if the credentials are wrong or the server is unreachable. */
  login: (email: string, password: string) => Promise<void>
  /** Creates the account and signs the new user in. */
  signup: (fullName: string, email: string, password: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
