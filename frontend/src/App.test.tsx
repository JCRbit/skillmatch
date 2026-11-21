import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App panel de empresa y formulario de vacante', () => {
  it('renderiza el formulario de publicación de vacante con requisitos separados', () => {
    const html = renderToStaticMarkup(<App />)
    expect(html).toContain('Publicar nueva vacante')
    expect(html).toContain('2. Requisitos esenciales (imprescindibles)')
    expect(html).toContain('3. Requisitos deseables (valorables / no excluyentes)')
    expect(html).toContain('4. Condiciones objetivas de la oferta')
  })
})
