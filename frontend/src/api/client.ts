import type { components } from './schema'

export type HealthResponse = components['schemas']['HealthResponse']

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error(`Error al consultar la API: ${response.status}`)
  }

  return response.json() as Promise<HealthResponse>
}
