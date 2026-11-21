import { afterEach, describe, expect, it, vi } from 'vitest'
import { getHealth, loginUser, registerUser } from './client'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('cliente HTTP de SkillMatch', () => {
  it('devuelve el estado de /health cuando la API responde 200', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({status: 'ok',service: 'SkillMatch API',version: '0.1.0'}),
    } as Response)

    const result = await getHealth()
    expect(result.status).toBe('ok')
  })

  it('enuía JSON a /api/v1/auth/register al registrar un usuario', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: 1, message: 'Usuario registrado' }),
    } as Response)

    const result = await registerUser({
      email: 'talento@example.com',
      password: 'clave1234',
      role: 'talento',
    })

    expect(result.user_id).toBe(1)
    expect(fetchSpy).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/auth/register',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      }),
    )
  })

  it('enuía formulario OAuth2 a /api/v1/auth/login al iniciar sesión', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ access_token: 'jwt-token', token_type: 'bearer' }),
    } as Response)

    const result = await loginUser({
      email: 'talento@example.com',
      password: 'clave1234',
    })

    expect(result.access_token).toBe('jwt-token')
    expect(fetchSpy).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      }),
     )
  })
})
