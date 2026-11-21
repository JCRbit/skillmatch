import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it, vi } from 'vitest'
import { VacancyForm } from './VacancyForm'

describe('VacancyForm (F-03)', () => {
  it('renderiza secciones separadas para esenciales, deseables y condiciones objetivas', () => {
    const html = renderToStaticMarkup(<VacancyForm onSubmitVacancy={vi.fn()} />)

    expect(html).toContain('1. Definicion del puesto y seniority')
    expect(html).toContain('2. Requisitos esenciales (imprescindibles)')
    expect(html).toContain('3. Requisitos deseables')
    expect(html).toContain('4. Condiciones objetivas de la oferta')
    expect(html).toContain('Anadir esencial')
    expect(html).toContain('Anadir deseable')
    expect(html).toContain('Salario minimo anual bruto')
    expect(html).toContain('Salario maximo anual bruto')
  })
})
