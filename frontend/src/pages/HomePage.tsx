import { Link } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

export function HomePage() {
  const { isAuthenticated, session } = useAuth()

  return (
    <section className="hero-card">
      <p className="eyebrow">Matching auditable por competencias verificables</p>
      <h1>Conecta talento junior con oportunidades reales</h1>
      <p className="lead">
        SkillMatch vincula habilidades demostradamente verificadas con vacantes
        de empresas mediante explicaciones claras y trazables.
      </p>

      <div className="hero-actions">
        {isAuthenticated && session ? (
          <Link
            to={session.role === 'empresa' ? '/empresa' : '/talento'}
            className="btn btn--primary"
          >
            Ir a mi panel ({session.role})
          </Link>
        ) : (
          <>
            <Link to="/register" className="btn btn--primary">
              Comenzar ahora
            </Link>
            <Link to="/login" className="btn btn--secondary">
              Ya tengo cuenta
            </Link>
          </>
        )}
      </div>

      <div className="role-grid">
        <article className="info-card">
          <h2>Para Talento</h2>
          <p>
            Registra tus competencias con evidencias verificables y accede a
            ofertas alineadas con tu perfil real.
          </p>
        </article>
        <article className="info-card">
          <h2>Para Empresas</h2>
          <p>
            Publica vacantes basadas en competencias concretas y evalúa
            candidaturas con criterios transparentes.
          </p>
        </article>
      </div>
    </section>
  )
}
