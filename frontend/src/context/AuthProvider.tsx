import { useCallback, useMemo, useState, type ReactNode } from 'react'
import { loginUser, registerUser } from '../api/client'
import type {
  AuthSession,
  LoginPayload,
  RegisterPayload,
  UserRole,
} from '../types/auth'
import { AuthContext } from './AuthContext'

const STORAGE_KEY = 'skillmatch_session'

function readStoredSession(): AuthSession | null {
  if (typeof window === 'undefined' || !window.localStorage) {
    return null
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return null
    }
    const parsed = JSON.parse(raw) as Partial<AuthSession>
    if (
      typeof parsed.accessToken === 'string' &&
      typeof parsed.email === 'string' &&
      (parsed.role === 'talento' || parsed.role === 'empresa')
    ) {
      return {
        accessToken: parsed.accessToken,
        tokenType: parsed.tokenType ?? 'bearer',
        email: parsed.email,
        role: parsed.role,
        userId: parsed.userId,
      }
    }
  } catch {
    // Ignore malformed storage entries
  }
  return null
}

function persistSession(session: AuthSession | null): void {
  if (typeof window === 'undefined' || !window.localStorage) {
    return
  }
  try {
    if (session) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
    } else {
      window.localStorage.removeItem(STORAGE_KEY)
    }
  } catch {
    // Ignore storage quota errors
  }
}

interface AuthProviderProps {
  children: ReactNode
  initialSession?: AuthSession | null
}

export function AuthProvider({ children, initialSession }: AuthProviderProps) {
  const [session, setSession] = useState<AuthSession | null>(() =>
    initialSession !== undefined ? initialSession : readStoredSession(),
  )
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const login = useCallback(async (payload: LoginPayload): Promise<UserRole> => {
    setIsLoading(true)
    setError(null)
    try {
      const token = await loginUser(payload)
      const resolvedRole: UserRole = payload.role ?? 'talento'
      const nextSession: AuthSession = {
        accessToken: token.access_token,
        tokenType: token.token_type,
        email: payload.email.trim(),
        role: resolvedRole,
      }
      setSession(nextSession)
      persistSession(nextSession)
      return resolvedRole
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'No se pudo iniciar sesión'
      setError(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const register = useCallback(
    async (payload: RegisterPayload): Promise<UserRole> => {
      setIsLoading(true)
      setError(null)
      try {
        const created = await registerUser(payload)
        const token = await loginUser({
          email: payload.email,
          password: payload.password,
          role: payload.role,
        })
        const nextSession: AuthSession = {
          accessToken: token.access_token,
          tokenType: token.token_type,
          email: payload.email.trim(),
          role: payload.role,
          userId: created.user_id,
        }
        setSession(nextSession)
        persistSession(nextSession)
        return payload.role
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'No se pudo registrar la cuenta'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [],
  )

  const logout = useCallback(() => {
    setSession(null)
    setError(null)
    persistSession(null)
  }, [])

  const value = useMemo(
    () => ({
      session,
      isAuthenticated: Boolean(session?.accessToken),
      isLoading,
      error,
      clearError,
      login,
      register,
      logout,
    }),
    [session, isLoading, error, clearError, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
