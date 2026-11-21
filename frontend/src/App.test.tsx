import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { App } from './App'
import { AuthProvider } from './context/AuthProvider'
import type { AuthSession } from './types/auth'

function renderAt(path: string, session: AuthSession | null = null): string {
  return renderToStaticMarkup(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider initialSession={session}>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('App shell y rutas protegidas', () => {
  it('carga la portada pública con los accesos de registro y login', () => {
    const html = renderAt('/')
    expect(html).toContain('SkillMatch')
    expect(html).toContain('Conecta talento junior con oportunidades reales')
    expect(html).toContain('Iniciar sesión')
    expect(html).toContain('Crear cuenta')
  })

  it('renderiza el formulario de registro con selector de rol talento y empresa', () => {
    const html = renderAt('/register')
    expect(html).toContain('Crear cuenta en SkillMatch')
    expect(html).toContain('Talento (Busco oportunidades)')
    expect(html).toContain('Empresa (Publico vacantes)')
  })

  it('redirige a /login cuando un usuario no autenticado intenta entrar a una ruta protegida', () => {
    const html = renderAt('/talento')
    expect(html).toContain('Iniciar sesión')
    expect(html).not.toContain('Panel del Talento')
  })

  it('permite el acceso al panel de talento cuando existe sesión con rol talento', () => {
    const html = renderAt('/talento', {
      accessToken: 'token-de-prueba',
      tokenType: 'bearer',
      email: 'ana@talento.es',
      role: 'talento',
    })
    expect(html).toContain('Panel del Talento')
    expect(html).toContain('ana@talento.es')
  })

  it('permite el acceso al panel de empresa cuando existe sesión con rol empresa', () => {
    const html = renderAt('/empresa', {
      accessToken: 'token-de-prueba',
      tokenType: 'bearer',
      email: 'rr@h@empresa.es',
      role: 'empresa',
    })
    expect(html).toContain('Panel de Empresa')
    expect(html).toContain('rr@h@empresa.es')
  })
})
