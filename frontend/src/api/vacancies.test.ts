import { afterEach, describe, expect, it, vi } from 'vitest'
import { createCompanyVacancy } from './vacancies'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('createCompanyVacancy (F-03)', () => {
  it('envia esenciales, deseables, seniority y condiciones objetivas separadas', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        id: 'job-001',
        created_at: '2026-11-21T03:00:00Z',
        title: 'Backend Python Junior',
        description: 'Desarrollo de APIs REST con FastAPI y PostgreSQL.',
        seniority: 'junior',
        essential_requirements: ['Python', 'SQL'],
        desirable_requirements: ['Docker'],
        objective_conditions: {
          location: 'Madrid',
          mode: 'hybrid',
          contract_type: 'indefinido',
          salary_min: 24000,
          salary_max: 28000,
          currency: 'EUR',
        },
        status: 'published',
      }),
    } as Response)

    const result = await createCompanyVacancy(
      {
        title: 'Backend Python Junior',
        description: 'Desarrollo de APIs REST con FastAPI y PostgreSQL.',
        seniority: 'junior',
        essential_requirements: ['Python', 'SQL'],
        desirable_requirements: ['Docker'],
        objective_conditions: {
          location: 'Madrid',
          mode: 'hybrid',
          contract_type: 'indefinido',
          salary_min: 24000,
          salary_max: 28000,
          currency: 'EUR',
        },
        status: 'published',
      },
      'token-empresa',
    )

    expect(result.id).toBe('job-001')
    expect(fetchSpy).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/companies/me/jobs',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer token-empresa',
        },
      }),
    )
  })
})
