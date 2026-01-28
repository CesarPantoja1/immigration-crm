import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { ROUTES_BY_ROLE } from '../store/permissions'

/**
 * ProtectedRoute - Guard de autenticación y roles
 * Redirige a login si el usuario no está autenticado
 * Redirige al dashboard correcto si el rol no coincide
 */
export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, isLoading, user } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Verificando sesión...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    // Guardar la ruta intentada para redirigir después del login
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Si se especifican roles permitidos, verificar que el usuario tenga el rol correcto
  if (allowedRoles && allowedRoles.length > 0 && user) {
    if (!allowedRoles.includes(user.role)) {
      // Redirigir al dashboard correspondiente al rol del usuario
      const routes = ROUTES_BY_ROLE[user.role]
      const defaultRoute = routes?.dashboard || '/'
      return <Navigate to={defaultRoute} replace />
    }
  }

  return children
}
