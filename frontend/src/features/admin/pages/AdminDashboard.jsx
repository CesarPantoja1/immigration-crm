import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card, Badge, Button } from '../../../components/common'
import { useAuth } from '../../../contexts/AuthContext'

export default function AdminDashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalAdvisors: 0,
    totalClients: 0,
    totalApplications: 0,
    pendingApplications: 0,
    todaySimulations: 0
  })

  useEffect(() => {
    // TODO: Fetch real stats from API
    setStats({
      totalUsers: 156,
      totalAdvisors: 12,
      totalClients: 144,
      totalApplications: 89,
      pendingApplications: 23,
      todaySimulations: 8
    })
  }, [])

  const statCards = [
    { 
      label: 'Total Usuarios', 
      value: stats.totalUsers, 
      icon: '👥',
      color: 'bg-blue-50 text-blue-600',
      link: '/admin/usuarios'
    },
    { 
      label: 'Asesores Activos', 
      value: stats.totalAdvisors, 
      icon: '👔',
      color: 'bg-green-50 text-green-600',
      link: '/admin/asesores'
    },
    { 
      label: 'Clientes', 
      value: stats.totalClients, 
      icon: '🧑‍💼',
      color: 'bg-purple-50 text-purple-600',
      link: '/admin/usuarios'
    },
    { 
      label: 'Solicitudes Totales', 
      value: stats.totalApplications, 
      icon: '📋',
      color: 'bg-amber-50 text-amber-600',
      link: '/admin/solicitudes'
    },
    { 
      label: 'Pendientes', 
      value: stats.pendingApplications, 
      icon: '⏳',
      color: 'bg-red-50 text-red-600',
      link: '/admin/solicitudes'
    },
    { 
      label: 'Simulacros Hoy', 
      value: stats.todaySimulations, 
      icon: '🎥',
      color: 'bg-cyan-50 text-cyan-600',
      link: '/admin/reportes'
    }
  ]

  const quickActions = [
    { label: 'Gestionar Usuarios', icon: '👥', path: '/admin/usuarios', color: 'primary' },
    { label: 'Ver Solicitudes', icon: '📋', path: '/admin/solicitudes', color: 'green' },
    { label: 'Asignar Asesores', icon: '👔', path: '/admin/asesores', color: 'purple' },
    { label: 'Ver Reportes', icon: '📊', path: '/admin/reportes', color: 'amber' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Panel de Administración</h1>
                <p className="text-sm text-gray-500">MigraFácil CRM</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="primary">Admin</Badge>
              <span className="text-gray-700">{user?.name}</span>
              <Link to="/login" onClick={() => localStorage.clear()}>
                <Button variant="outline" size="sm">
                  Cerrar Sesión
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Banner */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-6 text-white mb-8">
          <h2 className="text-2xl font-bold mb-2">¡Bienvenido, {user?.name?.split(' ')[0] || 'Admin'}!</h2>
          <p className="text-primary-100">
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
                  <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
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

        {/* Recent Activity */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Actividad Reciente</h3>
          <div className="space-y-4">
            {[
              { action: 'Nueva solicitud registrada', user: 'Juan Pérez', time: 'Hace 5 min', type: 'application' },
              { action: 'Simulacro completado', user: 'María García', time: 'Hace 15 min', type: 'simulation' },
              { action: 'Documentos aprobados', user: 'Carlos López', time: 'Hace 1 hora', type: 'document' },
              { action: 'Nuevo usuario registrado', user: 'Ana Martínez', time: 'Hace 2 horas', type: 'user' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-3 border-b last:border-0">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    activity.type === 'application' ? 'bg-blue-100 text-blue-600' :
                    activity.type === 'simulation' ? 'bg-purple-100 text-purple-600' :
                    activity.type === 'document' ? 'bg-green-100 text-green-600' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {activity.type === 'application' && '📋'}
                    {activity.type === 'simulation' && '🎥'}
                    {activity.type === 'document' && '✅'}
                    {activity.type === 'user' && '👤'}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{activity.action}</p>
                    <p className="text-sm text-gray-500">{activity.user}</p>
                  </div>
                </div>
                <span className="text-sm text-gray-400">{activity.time}</span>
              </div>
            ))}
          </div>
        </Card>
      </main>
    </div>
  )
}
