import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import type { UserRole } from '../types/auth'

interface LocationState {
  from?: string
}

export function LoginPage() {
  const { login, isLoading, error, clearError } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const state = (location.state as LocationState | null) ?? null
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<UserRole>(
    state?.from === '/empresa' ? 'empresa' : 'talento',
  )
  const [validationError, setValidationError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    clearError()
    setValidationError(null)

    const trimmedEmail = email.trim()
    if (!trimmedEmail || !password) {
      setValidationError('Completa tu correo electrónico y contraseña.')
      return
    }

    try {
      const assignedRole = await login({
        email: trimmedEmail,
        password,
        role,
      })
      const destination =
        state?.from && state.from !== '/login'
          ? state.from
          : assignedRole === 'empresa'
            ? '/empresa'
            : '/talento'
      navigate(destination, { replace: true })
    } catch {
      // Error state is already stored in AuthContext
    }
  }

  const activeError = validationError ?? error

  return (
    <section className="auth-card">
      <h1>Iniciar sesión</h1>
      <p className="muted">
        Accede a tu espacio protegido de SkillMatch con tu correo y contraseña.
      </p>

      <form onSubmit={handleSubmit} className="auth-form" noValidate>
        <label className="field">
          <span>Correo electrónico</span>
          <input
            type="email"
            name="email"
            autoComplete="email"
            placeholder="nombre@dominio.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Contraseña</span>
          <input
            type="password"
            name="password"
            autoComplete="current-password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Espacio de acceso</span>
          <select
            name="role"
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
          >
            <option value="talento">Talento</option>
            <option value="empresa">Empresa</option>
          </select>
        </label>

        {activeError ? (
          <p className="form-error" role="alert">
            {activeError}
          </p>
        ) : null}

        <button
          type="submit"
          className="btn btn--primary btn--full"
          disabled={isLoading}
        >
          {isLoading ? 'Accediendo...' : 'Entrar'}
        </button>
      </form>

      <p className="auth-footer">
        ¿Aún no tienes cuenta? <Link to="/register">Crea una aquí</Link>
      </p>
    </section>
  )
}
