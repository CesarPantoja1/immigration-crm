import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { notificacionesService } from '../services/notificacionesService'

export default function ClientLayout({ children }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Contador de notificaciones no leídas (desde la API)
  const [unreadNotifications, setUnreadNotifications] = useState(0)

  useEffect(() => {
    const fetchUnreadCount = async () => {
      try {
        const response = await notificacionesService.getConteoNoLeidas()
        setUnreadNotifications(response.data?.count || 0)
      } catch (error) {
        console.warn('No se pudo obtener el conteo de notificaciones:', error)
        setUnreadNotifications(0)
      }
    }
    
    fetchUnreadCount()
    
    // Actualizar cada 30 segundos
    const interval = setInterval(fetchUnreadCount, 30000)
    return () => clearInterval(interval)
  }, [])

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Bandeja de Entrada', href: '/inbox', icon: InboxIcon, badge: unreadNotifications },
    { name: 'Mis Solicitudes', href: '/solicitudes', icon: DocumentIcon },
    { name: 'Simulacros', href: '/simulacros', icon: VideoIcon },
    { name: 'Práctica', href: '/practica', icon: BookIcon },
    { name: 'Calendario', href: '/calendario', icon: CalendarIcon },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-50">
        <div className="h-full px-4 lg:px-8 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-8">
            <Link to="/dashboard" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-xl font-bold text-gray-900 hidden sm:block">MigraFácil</span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-1">
              {navigation.map((item) => {
                const isActive = location.pathname.startsWith(item.href)
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`relative px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    {item.name}
                    {item.badge && item.badge > 0 && (
                      <span className="absolute -top-1 -right-1 px-1.5 py-0.5 text-xs font-medium bg-red-500 text-white rounded-full min-w-[18px] text-center">
                        {item.badge > 9 ? '9+' : item.badge}
                      </span>
                    )}
                  </Link>
                )
              })}
            </nav>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-3">
            {/* Simulation Counter */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-full">
              <div className={`w-2 h-2 rounded-full ${
                user?.simulationsUsed === 0 ? 'bg-green-500' :
                user?.simulationsUsed === 1 ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span className="text-xs font-medium text-gray-600">
                {(user?.simulationsTotal || 2) - (user?.simulationsUsed || 0)}/2 simulacros
              </span>
            </div>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-3 p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-white">
                    {user?.name?.charAt(0) || 'U'}
                  </span>
                </div>
                <span className="hidden md:block text-sm font-medium text-gray-700">
                  {user?.name?.split(' ')[0]}
                </span>
                <svg className="hidden md:block w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                  </div>
                  <Link to="/perfil" className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Mi Perfil
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Cerrar Sesión
                  </button>
                </div>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-white border-t border-gray-200 py-2">
            {navigation.map((item) => {
              const isActive = location.pathname.startsWith(item.href)
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-4 py-3 text-sm font-medium ${
                    isActive ? 'bg-primary-50 text-primary-700' : 'text-gray-600'
                  }`}
                >
                  {item.name}
                </Link>
              )
            })}
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="pt-16 min-h-screen">
        <div className="p-4 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  )
}

function HomeIcon() { return null }
function InboxIcon() { return null }
function DocumentIcon() { return null }
function VideoIcon() { return null }
function BookIcon() { return null }
function CalendarIcon() { return null }
