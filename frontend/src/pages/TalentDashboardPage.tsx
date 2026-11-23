import { useAuth } from '../context/useAuth'

export function TalentDashboardPage() {
  const { session } = useAuth()

  return (
    <section className="dashboard-card">
      <p className="eyebrow">Espacio protegido • Rol Talento</p>
      <h1>Panel del Talento</h1>
      <p className="lead">
        Sesión activa como <strong>{session?.email}</strong>. Desde aquí
        gestionarás tu perfil de competencias, evidencias de trabajo y
        recomendaciones de vacantes.
      </p>
    </section>
  )
}
