import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

export function AppShell() {
  const { session, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header__inner">
          <Link to="/" className="brand">
            <span className="brand__badge">SM</span>
            <span>SkillMatch</span>
          </Link>

          <nav className="nav-links" aria-label="Navegación principal">
            <NavLink to="/" end>
              Inicio
            </NavLink>

            {isAuthenticated && session ? (
              <>
                <NavLink
                  to={session.role === 'empresa' ? '/empresa' : '/talento'	}
                >
                  {session.role === 'empresa'
                    ? 'Panel Empresa'
                    : 'Panel Talento'}
                </NavLink>
                <span className="session-pill">
                  {session.email} ({session.role})
                </span>
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={handleLogout}
                >
                  Cerrar sesión
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login">Iniciar sesión</NavLink>
                <NavLink to="/register" className="btn btn--primary">
                  Crear cuenta
                </NavLink>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}
