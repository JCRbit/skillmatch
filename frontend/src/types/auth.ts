export type UserRole = 'talento' | 'empresa'

export interface RegisterPayload {
  email: string
  password: string
  role: UserRole
}

export interface RegisterResponse {
  user_id: number
  message: string
}

export interface LoginPayload {
  email: string
  password: string
  role?: UserRole
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface AuthSession {
  accessToken: string
  tokenType: string
  email: string
  role: UserRole
  userId?: number
}
