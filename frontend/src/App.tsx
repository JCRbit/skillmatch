import { useState } from 'react'
import { createCompanyVacancy } from './api/vacancies'
import { VacancyForm } from './components/VacancyForm'
import type { VacancyCreatePayload, VacancyRecord } from './types/vacancy'

function App() {
  const [vacancies, setVacancies] = useState<VacancyRecord[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleCreateVacancy(payload: VacancyCreatePayload) {
    setIsSubmitting(true)
    try {
      const token = window.localStorage.getItem('skillmatch_session')
      let accessToken: string | null = null
      if (token) {
        try {
          const parsed = JSON.parse(token) as { accessToken?: string }
          accessToken = parsed.accessToken ?? null
        } catch {
          accessToken = null
        }
      }

      const created = await createCompanyVacancy(payload, accessToken)
      setVacancies((prev) => [created, ...prev])
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="app-container">
      <header className="page-header">
        <p className="eyebrow">SkillMatch - Panel de Empresa</p>
        <h1>Publicar nueva vacante</h1>
        <p className="subtitle">
          Define por separado los requisitos esenciales, los deseables y las condiciones objetivas para un matching explicable y sin sesgos.
        </p>
      </header>

      <section className="card">
        <VacancyForm onSubmitVacancy={handleCreateVacancy} isSubmitting={isSubmitting} />
      </section>

      <section className="card" aria-label="Vacantes registradas">
        <h2>Vacantes registradas ({vacancies.length})</h2>
        {vacancies.length === 0 ? (
          <p className="empty-hint">Todavia no has publicado ninguna vacante en esta sesion.</p>
        ) : (
          <div className="vacancy-list">
            {vacancies.map((item) => (
              <article key={item.id} className="vacancy-card">
                <header className="vacancy-card-header">
                  <h3>{item.title}</h3>
                  <span className="badge">{item.seniority} - {item.status}</span>
                </header>
                <p>{item.description}</p>
                <div className="vacancy-groups">
                  <div>
                    <strong>Esenciales:</strong> {item.essential_requirements.join(', ')}
                  </div>
                  <div>
                    <strong>Deseables:</strong> {item.desirable_requirements.length > 0 ? item.desirable_requirements.join(', ') : 'Ninguno'}
                  </div>
                  <div>
                    <strong>Condiciones objetivas:</strong> {item.objective_conditions.mode} - {item.objective_conditions.location} - {item.objective_conditions.contract_type}
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  )
}

export default App
