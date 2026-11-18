import { describe, expect, it } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'
import App from './App'

describe('App', () => {
  it('renders the SkillMatch application', () => {
    const html = renderToStaticMarkup(<App />)

    expect(html).toContain('SkillMatch')
    expect(html).toContain('Frontend inicializado correctamente')
  })
})
