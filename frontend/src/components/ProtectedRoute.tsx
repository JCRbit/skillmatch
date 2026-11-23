import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import type { UserRole } from '../types/auth'

interface ProtectedRouteProps {
  children: ReactNode
  allowedRoles?: UserRole[]
}

export function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {
  const { session, isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated || !session) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (allowedRoles && !allowedRoles.includes(session.role)) {
    const fallbackRoute = session.role === 'empresa' ? '/empresa' : '/talento'
    return <Navigate to={fallbackRoute} replace />
  }

  return <>{children}</>
}
