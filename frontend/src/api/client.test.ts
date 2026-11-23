import { afterEach, describe, expect, it, vi } from 'vitest'
import { getHealth, loginUser, registerUser } from './client'

const testPassword = 'test-password'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('cliente HTTP de SkillMatch', () => {
  it('devuelve el estado de /health cuando la API responde 200', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        status: 'ok',
        service: 'SkillMatch API',
        version: '0.1.0',
      }),
    } as Response)

    const result = await getHealth()

    expect(result.status).toBe('ok')
  })

  it('envía JSON a /api/v1/auth/register y recibe el usuario creado', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        id: 1,
        email: 'talento@example.com',
        role: 'talento',
        status: 'active',
        created_at: '2026-11-23T15:00:00Z',
      }),
    } as Response)

    const payload = {
      email: 'talento@example.com',
      password: testPassword,
      role: 'talento' as const,
    }

    const result = await registerUser(payload)

    expect(result.id).toBe(1)
    expect(result.email).toBe(payload.email)
    expect(result.role).toBe('talento')

    expect(fetchSpy).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/auth/register',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }),
    )
  })

  it('envía JSON a /api/v1/auth/login y recibe el token con la identidad', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        access_token: 'jwt-token',
        token_type: 'bearer',
        expires_in: 3600,
        user: {
          id: 1,
          email: 'talento@example.com',
          role: 'talento',
        },
      }),
    } as Response)

    const payload = {
      email: 'talento@example.com',
      password: testPassword,
    }

    const result = await loginUser(payload)

    expect(result.access_token).toBe('jwt-token')
    expect(result.user.id).toBe(1)
    expect(result.user.role).toBe('talento')

    expect(fetchSpy).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }),
    )
  })
})
