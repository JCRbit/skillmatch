import { createContext } from 'react'
import type {
  AuthSession,
  LoginPayload,
  RegisterPayload,
  UserRole,
} from '../types/auth'

export interface AuthContextValue {
  session: AuthSession | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  clearError: () => void
  login: (payload: LoginPayload) => Promise<UserRole>
  register: (payload: RegisterPayload) => Promise<UserRole>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
