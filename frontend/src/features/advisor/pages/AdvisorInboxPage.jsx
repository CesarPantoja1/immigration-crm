import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, Button, EmptyState, EmptyStateIcons } from '../../../components/common'
import { useAuth } from '../../../contexts/AuthContext'
import { notificacionesService } from '../../../services'

// Configuración de tipos de notificación
const NOTIFICATION_CONFIG = {
  entrevista_agendada: { icon: '📅', color: 'blue', label: 'Entrevista' },
  entrevista_reprogramada: { icon: '🔄', color: 'amber', label: 'Reprogramación' },
  entrevista_cancelada: { icon: '❌', color: 'red', label: 'Cancelación' },
  recordatorio_entrevista: { icon: '⏰', color: 'orange', label: 'Recordatorio' },
  preparacion_recomendada: { icon: '📚', color: 'purple', label: 'Preparación' },
  simulacion_completada: { icon: '✅', color: 'green', label: 'Simulacro' },
  recomendaciones_listas: { icon: '💡', color: 'blue', label: 'Recomendaciones' },
  documento_aprobado: { icon: '✔️', color: 'green', label: 'Documento' },
  documento_rechazado: { icon: '📄', color: 'red', label: 'Documento' },
  solicitud_aprobada: { icon: '🎉', color: 'green', label: 'Solicitud' },
  solicitud_rechazada: { icon: '📋', color: 'red', label: 'Solicitud' },
  solicitud_enviada: { icon: '📤', color: 'blue', label: 'Embajada' },
  simulacro_propuesto: { icon: '📹', color: 'purple', label: 'Simulacro' },
  simulacro_confirmado: { icon: '✅', color: 'green', label: 'Simulacro' },
  nueva_solicitud: { icon: '📥', color: 'blue', label: 'Nueva Solicitud' },
  cliente_mensaje: { icon: '💬', color: 'indigo', label: 'Mensaje' },
  general: { icon: '📌', color: 'gray', label: 'General' }
}

const getTypeConfig = (tipo) => NOTIFICATION_CONFIG[tipo] || NOTIFICATION_CONFIG.general

const getColorClasses = (color) => {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    amber: 'bg-amber-100 text-amber-600',
    orange: 'bg-orange-100 text-orange-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    red: 'bg-red-100 text-red-600',
    indigo: 'bg-indigo-100 text-indigo-600',
    gray: 'bg-gray-100 text-gray-600'
  }
  return colors[color] || colors.gray
}

export default function AdvisorInboxPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const [loading, setLoading] = useState(true)
  const [notifications, setNotifications] = useState([])
  const [filter, setFilter] = useState('all') // all, unread
  const [typeFilter, setTypeFilter] = useState('all')
  const [sourceFilter, setSourceFilter] = useState('all') // all, mine, clients
  const [expandedId, setExpandedId] = useState(null)
  const [actionLoading, setActionLoading] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true)
      const params = {}
      if (filter === 'unread') params.leida = false
      if (typeFilter !== 'all') params.tipo = typeFilter
      if (sourceFilter === 'mine') params.solo_propias = true
      
      const data = await notificacionesService.getNotificacionesAsesor(params)
      const results = data.results || data || []
      setNotifications(results)
    } catch (error) {
      console.error('Error fetching notifications:', error)
      setNotifications([])
    } finally {
      setLoading(false)
    }
  }, [filter, typeFilter, sourceFilter])

  useEffect(() => {
    fetchNotifications()
  }, [fetchNotifications])

  const unreadCount = notifications.filter(n => !n.leida).length
  const myNotifications = notifications.filter(n => n.usuario_nombre === user?.nombre)
  const clientNotifications = notifications.filter(n => n.usuario_nombre !== user?.nombre)

  const handleMarkAsRead = async (id, e) => {
    if (e) e.stopPropagation()
    try {
      setActionLoading(id)
      await notificacionesService.marcarLeida(id)
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, leida: true } : n)
      )
    } catch (error) {
      console.error('Error marking notification as read:', error)
    } finally {
      setActionLoading(null)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      setActionLoading('all')
      await notificacionesService.marcarTodasLeidas()
      setNotifications(prev => prev.map(n => ({ ...n, leida: true })))
    } catch (error) {
      console.error('Error marking all as read:', error)
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async (id, e) => {
    if (e) e.stopPropagation()
    try {
      setActionLoading(id)
      await notificacionesService.eliminar(id)
      setNotifications(prev => prev.filter(n => n.id !== id))
    } catch (error) {
      console.error('Error deleting notification:', error)
    } finally {
      setActionLoading(null)
    }
  }

  const handleNavigate = (notification) => {
    if (!notification.leida) {
      handleMarkAsRead(notification.id)
    }
    if (notification.url_accion) {
      navigate(notification.url_accion)
    }
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffMins < 1) return 'Ahora'
    if (diffMins < 60) return `Hace ${diffMins} min`
    if (diffHours < 24) return `Hace ${diffHours}h`
    if (diffDays === 1) return 'Ayer'
    if (diffDays < 7) return `Hace ${diffDays} días`
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  }

  // Agrupar notificaciones por fecha
  const groupedNotifications = notifications.reduce((groups, notification) => {
    const date = new Date(notification.created_at)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    
    let groupKey
    if (date.toDateString() === today.toDateString()) {
      groupKey = 'Hoy'
    } else if (date.toDateString() === yesterday.toDateString()) {
      groupKey = 'Ayer'
    } else {
      groupKey = date.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })
    }
    
    if (!groups[groupKey]) groups[groupKey] = []
    groups[groupKey].push(notification)
    return groups
  }, {})

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Centro de Notificaciones</h1>
          <p className="text-gray-500 mt-1">
            {unreadCount > 0 
              ? `${unreadCount} notificación${unreadCount > 1 ? 'es' : ''} sin leer`
              : 'Todas las notificaciones al día'}
          </p>
        </div>
        
        <Button 
          variant="primary"
          onClick={() => setShowCreateModal(true)}
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Nueva Notificación
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-700">{notifications.length}</p>
              <p className="text-sm text-blue-600">Total</p>
            </div>
          </div>
        </Card>
        
        <Card className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-amber-500 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-700">{unreadCount}</p>
              <p className="text-sm text-amber-600">Sin leer</p>
            </div>
          </div>
        </Card>
        
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-700">{clientNotifications.length}</p>
              <p className="text-sm text-purple-600">De clientes</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters & Actions */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
        <div className="flex flex-wrap items-center gap-2">
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
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                filter === 'unread' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              No leídas
              {unreadCount > 0 && (
                <span className="px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full min-w-[20px] text-center">
                  {unreadCount}
                </span>
              )}
            </button>
          </div>

          {/* Source Filter */}
          <div className="inline-flex items-center gap-1 p-1 bg-gray-100 rounded-xl">
            <button
              onClick={() => setSourceFilter('all')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                sourceFilter === 'all' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Todas
            </button>
            <button
              onClick={() => setSourceFilter('mine')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                sourceFilter === 'mine' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Mías
            </button>
            <button
              onClick={() => setSourceFilter('clients')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                sourceFilter === 'clients' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Clientes
            </button>
          </div>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
          >
            <option value="all">Todos los tipos</option>
            <option value="entrevista_agendada">Entrevistas</option>
            <option value="documento_aprobado">Documentos</option>
            <option value="simulacro_propuesto">Simulacros</option>
            <option value="solicitud_aprobada">Solicitudes</option>
            <option value="nueva_solicitud">Nuevas Solicitudes</option>
          </select>
        </div>

        {unreadCount > 0 && (
          <Button 
            variant="secondary" 
            size="sm" 
            onClick={handleMarkAllAsRead}
            disabled={actionLoading === 'all'}
          >
            {actionLoading === 'all' ? (
              <svg className="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
            Marcar todo como leído
          </Button>
        )}
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-white rounded-2xl p-6 animate-pulse">
              <div className="flex gap-4">
                <div className="w-12 h-12 bg-gray-200 rounded-xl"></div>
                <div className="flex-1 space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : notifications.length === 0 ? (
        <EmptyState
          icon={EmptyStateIcons.inbox}
          title="Sin notificaciones"
          description={filter === 'unread' 
            ? 'No tienes notificaciones sin leer' 
            : 'Tu centro de notificaciones está vacío'}
          variant="card"
        />
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedNotifications).map(([date, items]) => (
            <div key={date}>
              <h3 className="text-sm font-medium text-gray-500 mb-3 capitalize">{date}</h3>
              <div className="space-y-3">
                <AnimatePresence>
                  {items.map((notification) => {
                    const config = getTypeConfig(notification.tipo)
                    const isExpanded = expandedId === notification.id
                    const isLoading = actionLoading === notification.id
                    const isFromClient = notification.usuario_nombre !== user?.nombre

                    return (
                      <motion.div
                        key={notification.id}
                        layout
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, x: -100 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Card
                          className={`transition-all hover:shadow-md cursor-pointer ${
                            !notification.leida 
                              ? 'border-l-4 border-l-primary-500 bg-primary-50/30' 
                              : 'bg-white'
                          }`}
                          onClick={() => setExpandedId(isExpanded ? null : notification.id)}
                        >
                          <div className="flex gap-4">
                            {/* Icon */}
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0 ${
                              getColorClasses(config.color)
                            }`}>
                              {config.icon}
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between gap-4">
                                <div className="min-w-0">
                                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${getColorClasses(config.color)}`}>
                                      {config.label}
                                    </span>
                                    {isFromClient && notification.usuario_nombre && (
                                      <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-600">
                                        👤 {notification.usuario_nombre}
                                      </span>
                                    )}
                                  </div>
                                  <h3 className={`font-medium ${!notification.leida ? 'text-gray-900' : 'text-gray-700'}`}>
                                    {notification.titulo}
                                  </h3>
                                  <p className={`text-sm mt-1 ${isExpanded ? '' : 'line-clamp-2'} ${
                                    !notification.leida ? 'text-gray-600' : 'text-gray-500'
                                  }`}>
                                    {notification.mensaje}
                                  </p>
                                </div>

                                <div className="flex items-center gap-2 flex-shrink-0">
                                  {!notification.leida && (
                                    <span className="w-2.5 h-2.5 bg-primary-500 rounded-full animate-pulse" />
                                  )}
                                  <span className="text-xs text-gray-400 whitespace-nowrap">
                                    {notification.tiempo_transcurrido || formatTimestamp(notification.created_at)}
                                  </span>
                                </div>
                              </div>

                              {/* Expanded Actions */}
                              <AnimatePresence>
                                {isExpanded && (
                                  <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    transition={{ duration: 0.2 }}
                                    className="overflow-hidden"
                                  >
                                    <div className="flex flex-wrap items-center gap-3 mt-4 pt-4 border-t border-gray-100">
                                      {notification.url_accion && (
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
                                      )}

                                      {!notification.leida && (
                                        <button
                                          onClick={(e) => handleMarkAsRead(notification.id, e)}
                                          disabled={isLoading}
                                          className="px-4 py-2 text-gray-600 hover:text-gray-900 text-sm font-medium rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
                                        >
                                          {isLoading ? 'Marcando...' : 'Marcar como leída'}
                                        </button>
                                      )}

                                      <button
                                        onClick={(e) => handleDelete(notification.id, e)}
                                        disabled={isLoading}
                                        className="px-4 py-2 text-red-600 hover:text-red-700 text-sm font-medium rounded-lg hover:bg-red-50 transition-colors ml-auto disabled:opacity-50"
                                      >
                                        {isLoading ? 'Eliminando...' : 'Eliminar'}
                                      </button>
                                    </div>
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </div>
                          </div>
                        </Card>
                      </motion.div>
                    )
                  })}
                </AnimatePresence>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Notification Modal */}
      <CreateNotificationModal 
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreated={fetchNotifications}
      />
    </div>
  )
}

// Modal para crear notificaciones
function CreateNotificationModal({ isOpen, onClose, onCreated }) {
  const [loading, setLoading] = useState(false)
  const [clients, setClients] = useState([])
  const [formData, setFormData] = useState({
    usuario_id: '',
    tipo: 'general',
    titulo: '',
    mensaje: '',
    url_accion: ''
  })

  useEffect(() => {
    if (isOpen) {
      // Aquí podrías cargar la lista de clientes del asesor
      // Por ahora dejamos el campo de usuario_id manual
    }
  }, [isOpen])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.usuario_id || !formData.titulo || !formData.mensaje) {
      alert('Por favor completa todos los campos requeridos')
      return
    }

    try {
      setLoading(true)
      await notificacionesService.crearNotificacion({
        ...formData,
        usuario_id: parseInt(formData.usuario_id)
      })
      onCreated()
      onClose()
      setFormData({
        usuario_id: '',
        tipo: 'general',
        titulo: '',
        mensaje: '',
        url_accion: ''
      })
    } catch (error) {
      console.error('Error creating notification:', error)
      alert('Error al crear la notificación')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">Nueva Notificación</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ID del Cliente *
            </label>
            <input
              type="number"
              value={formData.usuario_id}
              onChange={(e) => setFormData(prev => ({ ...prev, usuario_id: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Ingresa el ID del cliente"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Notificación
            </label>
            <select
              value={formData.tipo}
              onChange={(e) => setFormData(prev => ({ ...prev, tipo: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="general">General</option>
              <option value="documento_aprobado">Documento Aprobado</option>
              <option value="documento_rechazado">Documento Rechazado</option>
              <option value="solicitud_aprobada">Solicitud Aprobada</option>
              <option value="solicitud_rechazada">Solicitud Rechazada</option>
              <option value="entrevista_agendada">Entrevista Agendada</option>
              <option value="simulacro_propuesto">Simulacro Propuesto</option>
              <option value="recomendaciones_listas">Recomendaciones Listas</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Título *
            </label>
            <input
              type="text"
              value={formData.titulo}
              onChange={(e) => setFormData(prev => ({ ...prev, titulo: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Título de la notificación"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mensaje *
            </label>
            <textarea
              value={formData.mensaje}
              onChange={(e) => setFormData(prev => ({ ...prev, mensaje: e.target.value }))}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Contenido del mensaje"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL de Acción (opcional)
            </label>
            <input
              type="text"
              value={formData.url_accion}
              onChange={(e) => setFormData(prev => ({ ...prev, url_accion: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="/ruta/destino"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Enviando...' : 'Enviar Notificación'}
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}
