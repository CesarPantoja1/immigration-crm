import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, Badge, Button, EmptyState, EmptyStateIcons } from '../../../components/common'
import { useAuth } from '../../../contexts/AuthContext'
import { NOTIFICATION_TYPES } from '../../../store/constants'
import { notificacionesService } from '../../../services'

export default function InboxPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [notifications, setNotifications] = useState([])
  const [filter, setFilter] = useState('all') // all, unread
  const [typeFilter, setTypeFilter] = useState('all')
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    fetchNotifications()
  }, [filter, typeFilter])

  const fetchNotifications = async () => {
    try {
      setLoading(true)
      const params = {}
      if (filter === 'unread') params.leida = false
      if (typeFilter !== 'all') params.tipo = typeFilter
      
      const data = await notificacionesService.getAll(params)
      const results = data.results || data || []
      
      // Transform to component format
      const transformed = results.map(n => ({
        id: n.id,
        type: n.tipo,
        title: n.titulo,
        message: n.mensaje,
        timestamp: n.created_at,
        read: n.leida,
        deepLink: n.link_accion || null,
        metadata: n.datos_adicionales || {}
      }))
      
      setNotifications(transformed)
    } catch (error) {
      console.error('Error fetching notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const unreadCount = notifications.filter(n => !n.read).length
  
  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread' && n.read) return false
    if (typeFilter !== 'all' && n.type !== typeFilter) return false
    return true
  })

  const handleMarkAsRead = async (id) => {
    try {
      await notificacionesService.marcarLeida(id)
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      )
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificacionesService.marcarTodasLeidas()
      setNotifications(prev => prev.map(n => ({ ...n, read: true })))
    } catch (error) {
      console.error('Error marking all as read:', error)
    }
  }

  const handleDelete = async (id) => {
    try {
      await notificacionesService.delete(id)
      setNotifications(prev => prev.filter(n => n.id !== id))
    } catch (error) {
      console.error('Error deleting notification:', error)
    }
  }

  const handleNavigate = (notification) => {
    handleMarkAsRead(notification.id)
    navigate(notification.deepLink)
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffHours < 1) return 'Hace unos minutos'
    if (diffHours < 24) return `Hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`
    if (diffDays === 1) return 'Ayer'
    if (diffDays < 7) return `Hace ${diffDays} días`
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  }

  const getTypeInfo = (type) => {
    const typeData = NOTIFICATION_TYPES[type.toUpperCase()] || {}
    return {
      icon: typeData.icon || '📌',
      color: typeData.color || 'gray'
    }
  }

  const getTypeColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-600',
      amber: 'bg-amber-100 text-amber-600',
      green: 'bg-green-100 text-green-600',
      purple: 'bg-purple-100 text-purple-600',
      red: 'bg-red-100 text-red-600',
      gray: 'bg-gray-100 text-gray-600'
    }
    return colors[color] || colors.gray
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Bandeja de Entrada</h1>
        <p className="text-gray-500 mt-1">
          {unreadCount > 0 
            ? `Tienes ${unreadCount} notificación${unreadCount > 1 ? 'es' : ''} sin leer`
            : 'Todas tus notificaciones al día'}
        </p>
      </div>

      {/* Filters & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-2">
          {/* Read Filter */}
          <div className="inline-flex items-center gap-1 p-1 bg-gray-100 rounded-xl">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === 'all' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Todas
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === 'unread' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              No leídas
              {unreadCount > 0 && (
                <span className="ml-1.5 px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full">
                  {unreadCount}
                </span>
              )}
            </button>
          </div>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="all">Todos los tipos</option>
            <option value="application_update">Solicitudes</option>
            <option value="document_review">Documentos</option>
            <option value="simulation_scheduled">Simulacros</option>
            <option value="embassy_response">Embajada</option>
            <option value="feedback_received">Retroalimentación</option>
          </select>
        </div>

        {unreadCount > 0 && (
          <Button variant="secondary" size="sm" onClick={handleMarkAllAsRead}>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Marcar todo como leído
          </Button>
        )}
      </div>

      {/* Notifications List */}
      {filteredNotifications.length === 0 ? (
        <EmptyState
          icon={EmptyStateIcons.inbox}
          title="Sin notificaciones"
          description={filter === 'unread' 
            ? 'No tienes notificaciones sin leer' 
            : 'Tu bandeja de entrada está vacía'}
          variant="card"
        />
      ) : (
        <div className="space-y-3">
          {filteredNotifications.map((notification) => {
            const typeInfo = getTypeInfo(notification.type)
            const isExpanded = expandedId === notification.id

            return (
              <Card
                key={notification.id}
                className={`transition-all hover:shadow-md cursor-pointer ${
                  !notification.read ? 'border-l-4 border-l-primary-500 bg-primary-50/30' : ''
                }`}
                onClick={() => setExpandedId(isExpanded ? null : notification.id)}
              >
                <div className="flex gap-4">
                  {/* Icon */}
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0 ${
                    getTypeColorClasses(typeInfo.color)
                  }`}>
                    {typeInfo.icon}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <h3 className={`font-medium ${!notification.read ? 'text-gray-900' : 'text-gray-700'}`}>
                          {notification.title}
                        </h3>
                        <p className={`text-sm mt-1 ${isExpanded ? '' : 'line-clamp-2'} ${
                          !notification.read ? 'text-gray-600' : 'text-gray-500'
                        }`}>
                          {notification.message}
                        </p>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        {!notification.read && (
                          <span className="w-2 h-2 bg-primary-500 rounded-full" />
                        )}
                        <span className="text-xs text-gray-400 whitespace-nowrap">
                          {formatTimestamp(notification.timestamp)}
                        </span>
                      </div>
                    </div>

                    {/* Expanded Actions */}
                    {isExpanded && (
                      <div className="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleNavigate(notification)
                          }}
                          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors"
                        >
                          Ver detalle
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                          </svg>
                        </button>

                        {!notification.read && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleMarkAsRead(notification.id)
                            }}
                            className="px-4 py-2 text-gray-600 hover:text-gray-900 text-sm font-medium rounded-lg hover:bg-gray-100 transition-colors"
                          >
                            Marcar como leída
                          </button>
                        )}

                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDelete(notification.id)
                          }}
                          className="px-4 py-2 text-red-600 hover:text-red-700 text-sm font-medium rounded-lg hover:bg-red-50 transition-colors ml-auto"
                        >
                          Eliminar
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
