import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card, Badge, Button } from '../../../components/common'

// Mock data
const todaySimulations = [
  {
    id: 1,
    client: 'Juan Pérez',
    time: '10:00 AM',
    visaType: 'Visa de Estudio',
    status: 'upcoming'
  },
  {
    id: 2,
    client: 'María García',
    time: '11:30 AM',
    visaType: 'Visa de Trabajo',
    status: 'upcoming'
  },
  {
    id: 3,
    client: 'Carlos López',
    time: '02:00 PM',
    visaType: 'Visa de Estudio',
    status: 'upcoming'
  }
]

const pendingReviews = [
  {
    id: 'SOL-2024-001',
    client: 'Ana Martínez',
    visaType: 'Visa de Trabajo',
    submittedAt: '2024-01-25',
    documentsCount: 5,
    priority: 'high'
  },
  {
    id: 'SOL-2024-002',
    client: 'Pedro Sánchez',
    visaType: 'Visa de Estudio',
    submittedAt: '2024-01-24',
    documentsCount: 4,
    priority: 'medium'
  },
  {
    id: 'SOL-2024-003',
    client: 'Laura Díaz',
    visaType: 'Visa de Vivienda',
    submittedAt: '2024-01-23',
    documentsCount: 6,
    priority: 'low'
  }
]

const recentActivity = [
  { type: 'review', message: 'Aprobaste la solicitud de Carlos López', time: 'Hace 2 horas' },
  { type: 'simulation', message: 'Completaste simulacro con María García', time: 'Hace 5 horas' },
  { type: 'document', message: 'Rechazaste documento de Juan Pérez', time: 'Ayer' },
  { type: 'feedback', message: 'Enviaste feedback a Ana Martínez', time: 'Ayer' }
]

export default function AdvisorDashboard() {
  const stats = [
    { 
      label: 'Simulacros Hoy', 
      value: todaySimulations.length, 
      icon: '📅',
      color: 'bg-blue-50 text-blue-600'
    },
    { 
      label: 'Revisiones Pendientes', 
      value: pendingReviews.length, 
      icon: '📋',
      color: 'bg-amber-50 text-amber-600'
    },
    { 
      label: 'Clientes Activos', 
      value: 24, 
      icon: '👥',
      color: 'bg-green-50 text-green-600'
    },
    { 
      label: 'Este Mes', 
      value: 18, 
      subtext: 'simulacros',
      icon: '📊',
      color: 'bg-purple-50 text-purple-600'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">¡Buenos días, María!</h1>
        <p className="text-primary-100">
          Tienes {todaySimulations.length} simulacros programados para hoy y {pendingReviews.length} solicitudes pendientes de revisión.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${stat.color}`}>
                {stat.icon}
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {stat.value}
                  {stat.subtext && (
                    <span className="text-sm font-normal text-gray-500 ml-1">{stat.subtext}</span>
                  )}
                </div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Today's Simulations */}
        <div className="lg:col-span-2">
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Simulacros de Hoy</h2>
              <Link to="/asesor/simulacros" className="text-sm text-primary-600 hover:text-primary-700">
                Ver todos →
              </Link>
            </div>

            <div className="space-y-3">
              {todaySimulations.map((sim) => (
                <div 
                  key={sim.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-semibold">
                      {sim.client.charAt(0)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{sim.client}</p>
                      <p className="text-sm text-gray-500">{sim.visaType}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-700">{sim.time}</span>
                    <Link to={`/asesor/simulacros/${sim.id}/room`}>
                      <Button size="sm">Iniciar</Button>
                    </Link>
                  </div>
                </div>
              ))}

              {todaySimulations.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No tienes simulacros programados para hoy
                </div>
              )}
            </div>
          </Card>

          {/* Quick Access - Entrevistas */}
          <Card className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Agendamiento de Entrevistas</h2>
              <Link to="/asesor/entrevistas" className="text-sm text-primary-600 hover:text-primary-700">
                Ver todo →
              </Link>
            </div>
            <div className="bg-gradient-to-r from-blue-50 to-primary-50 p-4 rounded-xl">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center text-2xl">
                  📅
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Gestiona las entrevistas consulares</p>
                  <p className="text-sm text-gray-600">Agenda, reprograma y da seguimiento a entrevistas</p>
                </div>
                <Link to="/asesor/entrevistas">
                  <Button size="sm">Ir a Entrevistas</Button>
                </Link>
              </div>
            </div>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Actividad Reciente</h2>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-start gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  activity.type === 'review' ? 'bg-green-100 text-green-600' :
                  activity.type === 'simulation' ? 'bg-blue-100 text-blue-600' :
                  activity.type === 'document' ? 'bg-red-100 text-red-600' :
                  'bg-purple-100 text-purple-600'
                }`}>
                  {activity.type === 'review' && '✓'}
                  {activity.type === 'simulation' && '📹'}
                  {activity.type === 'document' && '📄'}
                  {activity.type === 'feedback' && '💬'}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 line-clamp-2">{activity.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Pending Reviews */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Solicitudes Pendientes de Revisión</h2>
          <Link to="/asesor/solicitudes" className="text-sm text-primary-600 hover:text-primary-700">
            Ver todas →
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Solicitud</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Cliente</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tipo de Visa</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Documentos</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Prioridad</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Acción</th>
              </tr>
            </thead>
            <tbody>
              {pendingReviews.map((review) => (
                <tr key={review.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <span className="font-medium text-gray-900">{review.id}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-gray-700">{review.client}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-gray-600 text-sm">{review.visaType}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-gray-600">{review.documentsCount} archivos</span>
                  </td>
                  <td className="py-3 px-4">
                    <Badge 
                      variant={
                        review.priority === 'high' ? 'danger' :
                        review.priority === 'medium' ? 'warning' : 'default'
                      }
                      size="sm"
                    >
                      {review.priority === 'high' ? 'Alta' :
                       review.priority === 'medium' ? 'Media' : 'Baja'}
                    </Badge>
                  </td>
                  <td className="py-3 px-4">
                    <Link to={`/asesor/solicitudes/${review.id}`}>
                      <Button variant="secondary" size="sm">Revisar</Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
