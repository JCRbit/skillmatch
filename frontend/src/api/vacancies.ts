import type { VacancyCreatePayload, VacancyRecord } from '../types/vacancy'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'

export async function createCompanyVacancy(
  payload: VacancyCreatePayload,
  accessToken?: string | null,
): Promise<VacancyRecord> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/companies/me/jobs`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
	...payload,
	location: payload.objective_conditions.location,
	mode: payload.objective_conditions.mode,
	contract_type: payload.objective_conditions.contract_type,
	salary_min: payload.objective_conditions.salary_min,
	salary_max: payload.objective_conditions.salary_max,
	currency: payload.objective_conditions.currency,
    }),
  })

  if (!response.ok) {
    let detail = 'No se pudo publicar la vacante'
    try {
      const errorData = (await response.json()) as { detail?: string }
      if (typeof errorData.detail === 'string') {
        detail = errorData.detail
      }
    } catch {
      // ignore non-json error body
    }
    throw new Error(detail)
  }

  return (await response.json()) as VacancyRecord
}
