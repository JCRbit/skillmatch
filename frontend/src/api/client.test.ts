import { afterEach, describe, expect, it, vi } from 'vitest'
import { getHealth } from './client'

describe('getHealth', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns the health response when the API succeeds', async () => {
    const mockFetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: 'ok' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )

    vi.stubGlobal('fetch', mockFetch)

    await expect(getHealth()).resolves.toEqual({ status: 'ok' })
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/health',
    )
  })

  it('throws an error when the API responds with an HTTP error', async () => {
    const mockFetch = vi.fn().mockResolvedValue(
      new Response(null, { status: 500 }),
    )

    vi.stubGlobal('fetch', mockFetch)

    await expect(getHealth()).rejects.toThrow(
      'Error al consultar la API: 500',
    )
  })
})
