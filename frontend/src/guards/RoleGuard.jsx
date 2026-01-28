import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { ROUTES_BY_ROLE } from '../store/permissions'

/**
 * RoleGuard - Guard de verificación de rol
 * Redirige al dashboard correspondiente si el rol no coincide
 */
export default function RoleGuard({ children, allowedRoles }) {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (!allowedRoles.includes(user.role)) {
    // Redirigir al dashboard del rol correspondiente
    const routes = ROUTES_BY_ROLE[user.role]
    const defaultRoute = routes?.dashboard || '/'
    return <Navigate to={defaultRoute} replace />
  }

  return children
}
