import type { components } from './schema'
import type {
  LoginPayload,
  RegisterPayload,
  RegisterResponse,
  TokenResponse,
} from '../types/auth'

export type HealthResponse = components['schemas']['HealthResponse']

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const API_V1_URL = `${API_BASE_URL}/api/v1`

interface FastApiErrorBody {
  detail?: string | Array<{ msg?: string }>
  title?: string
}

async function extractApiError(response: Response, fallback: string): Promise<string> {
  try {
    const data = (await response.json()) as FastApiErrorBody

    if (typeof data.detail === 'string' && data.detail.trim().length > 0) {
      return data.detail
    }

    if (Array.isArray(data.detail) && data.detail[0]?.msg) {
      return data.detail[0].msg
    }

    if (typeof data.title === 'string' && data.title.trim().length > 0) {
      return data.title
    }
  } catch {
    // Ignore non-JSON error bodies and use fallback
  }

  return fallback
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error(`Error al consultar la API: ${response.status}`)
  }

  return response.json() as Promise<HealthResponse>
}

export async function registerUser(payload: RegisterPayload): Promise<RegisterResponse> {
  const response = await fetch(`${API_V1_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const message = await extractApiError(
      response,
      `No se pudo completar el registro (${response.status})`,
    )
    throw new Error(message)
  }

  return response.json() as Promise<RegisterResponse>
}

export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  const response = await fetch(`${API_V1_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const message = await extractApiError(
      response,
      `No se pudo iniciar sesión (${response.status})`,
    )
    throw new Error(message)
  }

  return response.json() as Promise<TokenResponse>
}
