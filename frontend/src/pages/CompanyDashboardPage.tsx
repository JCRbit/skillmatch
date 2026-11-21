import { useAuth } from '../context/useAuth'

export function CompanyDashboardPage() {
  const { session } = useAuth()

  return (
    <section className="dashboard-card">
      <p className="eyebrow">Espacio protegido • Rol Empresa</p>
      <h1>Panel de Empresa</h1>
      <p className="lead">
        Sesión activa como <strong>{session?.email}</strong>. Desde aquí
        publicarás vacantes y revisarás el matching auditable de candidatos.
      </p>
    </section>
  )
}
