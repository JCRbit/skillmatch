import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import type { UserRole } from '../types/auth'

export function RegisterPage() {
  const { register, isLoading, error, clearError } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<UserRole>('talento')
  const [validationError, setValidationError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    clearError()
    setValidationError(null)

    const trimmedEmail = email.trim()

    if (!trimmedEmail || !trimmedEmail.includes('@')) {
      setValidationError('Introduce un correo electrónico válido.')
      return
    }

    if (password.length < 12 || password.length > 128) {
      setValidationError(
        'La contraseña debe tener entre 12 y 128 caracteres.',
      )
      return
    }

    try {
      const assignedRole = await register({
        email: trimmedEmail,
        password,
        role,
      })

      navigate(assignedRole === 'empresa' ? '/empresa' : '/talento', {
        replace: true,
      })
    } catch {
      // Error state is already stored in AuthContext
    }
  }

  const activeError = validationError ?? error

  return (
    <section className="auth-card">
      <h1>Crear cuenta en SkillMatch</h1>

      <p className="muted">
        Elige tu perfil para acceder al espacio de trabajo correspondiente.
      </p>

      <form onSubmit={handleSubmit} className="auth-form" noValidate>
        <fieldset className="role-selector">
          <legend>Tipo de cuenta</legend>

          <label className="role-option">
            <input
              type="radio"
              name="role"
              value="talento"
              checked={role === 'talento'}
              onChange={() => setRole('talento')}
            />
            <span>Talento (Busco oportunidades)</span>
          </label>

          <label className="role-option">
            <input
              type="radio"
              name="role"
              value="empresa"
              checked={role === 'empresa'}
              onChange={() => setRole('empresa')}
            />
            <span>Empresa (Publico vacantes)</span>
          </label>
        </fieldset>

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
          <span>Contraseña (entre 12 y 128 caracteres)</span>
          <input
            type="password"
            name="password"
            autoComplete="new-password"
            placeholder="••••••••••••"
            minLength={12}
            maxLength={128}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
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
          {isLoading ? 'Registrando...' : 'Registrarme'}
        </button>
      </form>

      <p className="auth-footer">
        ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
      </p>
    </section>
  )
}
