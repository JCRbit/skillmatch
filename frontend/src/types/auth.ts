export type UserRole = 'talento' | 'empresa'

export interface RegisterPayload {
  email: string
  password: string
  role: UserRole
}

export interface RegisterResponse {
  id: number
  email: string
  role: UserRole
  status: string
  created_at: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface AuthenticatedUser {
  id: number
  email: string
  role: UserRole
}

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number
  user: AuthenticatedUser
}

export interface AuthSession {
  accessToken: string
  tokenType: string
  email: string
  role: UserRole
  userId?: number
}
