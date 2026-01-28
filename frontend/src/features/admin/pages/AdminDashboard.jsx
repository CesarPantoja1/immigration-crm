import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card, Badge, Button } from '../../../components/common'
import { useAuth } from '../../../contexts/AuthContext'
import adminService from '../../../services/adminService'

export default function AdminDashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    total_usuarios: 0,
    total_asesores: 0,
    asesores_activos: 0,
    total_clientes: 0,
    solicitudes_totales: 0,
    solicitudes_pendientes: 0,
    simulacros_hoy: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const data = await adminService.getEstadisticas()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { 
      label: 'Total Usuarios', 
      value: stats.total_usuarios, 
      icon: '👥',
      color: 'bg-blue-50 text-blue-600',
      link: '/admin/usuarios'
    },
    { 
      label: 'Asesores Activos', 
      value: stats.asesores_activos, 
      icon: '👔',
      color: 'bg-green-50 text-green-600',
      link: '/admin/asesores'
    },
    { 
      label: 'Clientes', 
      value: stats.total_clientes, 
      icon: '🧑‍💼',
      color: 'bg-purple-50 text-purple-600',
      link: '/admin/usuarios'
    },
    { 
      label: 'Solicitudes Totales', 
      value: stats.solicitudes_totales, 
      icon: '📋',
      color: 'bg-amber-50 text-amber-600',
      link: '/admin/solicitudes'
    },
    { 
      label: 'Pendientes', 
      value: stats.solicitudes_pendientes, 
      icon: '⏳',
      color: 'bg-red-50 text-red-600',
      link: '/admin/solicitudes'
    },
    { 
      label: 'Simulacros Hoy', 
      value: stats.simulacros_hoy, 
      icon: '🎥',
      color: 'bg-cyan-50 text-cyan-600',
      link: '/admin/reportes'
    }
  ]

  const quickActions = [
    { label: 'Gestionar Asesores', icon: '👔', path: '/admin/asesores', color: 'primary' },
    { label: 'Ver Solicitudes', icon: '📋', path: '/admin/solicitudes', color: 'green' },
    { label: 'Gestionar Usuarios', icon: '👥', path: '/admin/usuarios', color: 'purple' },
    { label: 'Ver Reportes', icon: '📊', path: '/admin/reportes', color: 'amber' },
  ]

  return (
    <div className="p-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-red-600 to-red-700 rounded-2xl p-6 text-white mb-8">
        <h2 className="text-2xl font-bold mb-2">¡Bienvenido, {user?.first_name || 'Admin'}!</h2>
        <p className="text-red-100">
          Tienes acceso completo al sistema. Gestiona usuarios, solicitudes y configuración.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {statCards.map((stat, index) => (
          <Link key={index} to={stat.link}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <div className="text-center">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl mx-auto mb-3 ${stat.color}`}>
                  {stat.icon}
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {loading ? '...' : stat.value}
                </div>
                <div className="text-xs text-gray-500">{stat.label}</div>
              </div>
            </Card>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {quickActions.map((action, index) => (
          <Link key={index} to={action.path}>
            <Card className="hover:shadow-md transition-all hover:-translate-y-1 cursor-pointer">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{action.icon}</span>
                <span className="font-medium text-gray-900">{action.label}</span>
              </div>
            </Card>
          </Link>
        ))}
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Resumen del Sistema</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Total de asesores</span>
              <span className="font-semibold">{stats.total_asesores}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Asesores activos</span>
              <Badge variant="success">{stats.asesores_activos}</Badge>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Clientes activos</span>
              <span className="font-semibold">{stats.clientes_activos || stats.total_clientes}</span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-600">Simulacros esta semana</span>
              <span className="font-semibold">{stats.simulacros_semana || 0}</span>
            </div>
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Accesos Directos</h3>
          <div className="space-y-3">
            <Link 
              to="/admin/asesores"
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
            >
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-xl">➕</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Crear nuevo asesor</p>
                <p className="text-sm text-gray-500">Registra un asesor en el sistema</p>
              </div>
            </Link>
            <Link 
              to="/admin/solicitudes"
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
            >
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <span className="text-xl">📋</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Ver solicitudes pendientes</p>
                <p className="text-sm text-gray-500">{stats.solicitudes_pendientes} solicitudes por revisar</p>
              </div>
            </Link>
            <Link 
              to="/admin/reportes"
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
            >
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-xl">📈</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">Ver reportes</p>
                <p className="text-sm text-gray-500">Métricas y estadísticas del sistema</p>
              </div>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  )
}
