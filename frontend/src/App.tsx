import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { ProtectedRoute } from './components/ProtectedRoute'
import { CompanyDashboardPage } from './pages/CompanyDashboardPage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { TalentDashboardPage } from './pages/TalentDashboardPage'

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route
          path="talento"
          element={
            <ProtectedRoute allowedRoles={['talento']}>
              <TalentDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="empresa"
          element={
            <ProtectedRoute allowedRoles={['empresa']}>
              <CompanyDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
