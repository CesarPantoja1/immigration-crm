/**
 * Contexto de Notificaciones
 * Maneja el estado global de notificaciones y alertas en tiempo real
 */
import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import { notificacionesService } from '../services/notificacionesService'
import { useAuth } from './AuthContext'

const NotificationContext = createContext(null)

// Intervalo de polling en ms (15 segundos para un balance entre tiempo real y rendimiento)
const POLLING_INTERVAL = 15000

// Tipos de notificación con sus iconos y colores
export const NOTIFICATION_TYPES = {
  // Solicitudes
  solicitud_creada: { icon: '📄', color: 'blue', label: 'Nueva Solicitud' },
  solicitud_aprobada: { icon: '✅', color: 'green', label: 'Solicitud Aprobada' },
  solicitud_rechazada: { icon: '❌', color: 'red', label: 'Solicitud Rechazada' },
  solicitud_enviada: { icon: '📨', color: 'purple', label: 'Solicitud Enviada' },
  solicitud_asignada: { icon: '👤', color: 'blue', label: 'Solicitud Asignada' },
  
  // Contratos
  contrato_generado: { icon: '📋', color: 'blue', label: 'Contrato Generado' },
  contrato_pendiente: { icon: '⏳', color: 'yellow', label: 'Contrato Pendiente' },
  contrato_firmado: { icon: '✍️', color: 'green', label: 'Contrato Firmado' },
  contrato_aprobado: { icon: '✅', color: 'green', label: 'Contrato Aprobado' },
  
  // Documentos
  documento_subido: { icon: '📎', color: 'blue', label: 'Documento Subido' },
  documento_aprobado: { icon: '✅', color: 'green', label: 'Documento Aprobado' },
  documento_rechazado: { icon: '⚠️', color: 'red', label: 'Documento Rechazado' },
  
  // Entrevistas
  entrevista_agendada: { icon: '📅', color: 'blue', label: 'Entrevista Agendada' },
  entrevista_reprogramada: { icon: '🔄', color: 'yellow', label: 'Entrevista Reprogramada' },
  entrevista_cancelada: { icon: '❌', color: 'red', label: 'Entrevista Cancelada' },
  recordatorio_entrevista: { icon: '⏰', color: 'orange', label: 'Recordatorio' },
  
  // Simulacros
  simulacro_propuesto: { icon: '🎬', color: 'blue', label: 'Simulacro Propuesto' },
  simulacro_confirmado: { icon: '✅', color: 'green', label: 'Simulacro Confirmado' },
  simulacion_completada: { icon: '🎉', color: 'green', label: 'Simulacro Completado' },
  recomendaciones_listas: { icon: '📝', color: 'purple', label: 'Recomendaciones' },
  
  // Preparación
  preparacion_recomendada: { icon: '📚', color: 'blue', label: 'Preparación' },
  
  // General
  general: { icon: '🔔', color: 'gray', label: 'Notificación' },
  mensaje: { icon: '💬', color: 'blue', label: 'Mensaje' },
}

export function NotificationProvider({ children }) {
  const { user, isAuthenticated } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [lastFetchedIds, setLastFetchedIds] = useState(new Set())
  const [toasts, setToasts] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  
  const pollingRef = useRef(null)
  const lastCheckRef = useRef(null)

  // Agregar un toast
  const addToast = useCallback((notification) => {
    const id = Date.now() + Math.random()
    const typeConfig = NOTIFICATION_TYPES[notification.tipo] || NOTIFICATION_TYPES.general
    
    const toast = {
      id,
      title: notification.titulo,
      message: notification.mensaje,
      type: notification.tipo,
      icon: typeConfig.icon,
      color: typeConfig.color,
      url: notification.url_accion,
      notificationId: notification.id,
      createdAt: new Date()
    }
    
    setToasts(prev => [...prev, toast])
    
    // Auto-remover después de 6 segundos
    setTimeout(() => {
      removeToast(id)
    }, 6000)
    
    return id
  }, [])

  // Remover un toast
  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  // Obtener el conteo de no leídas
  const fetchUnreadCount = useCallback(async () => {
    if (!isAuthenticated) return
    
    try {
      const response = await notificacionesService.getConteoNoLeidas()
      const count = response.data?.count || 0
      setUnreadCount(count)
      return count
    } catch (error) {
      console.warn('Error fetching unread count:', error)
      return 0
    }
  }, [isAuthenticated])

  // Obtener notificaciones recientes
  const fetchNotifications = useCallback(async (showNewToasts = true) => {
    if (!isAuthenticated) return []
    
    try {
      setIsLoading(true)
      const response = await notificacionesService.getNoLeidas()
      const newNotifications = response.data?.results || response.data || []
      
      // Detectar nuevas notificaciones para mostrar toasts
      if (showNewToasts && lastFetchedIds.size > 0) {
        const newIds = new Set(newNotifications.map(n => n.id))
        const brandNew = newNotifications.filter(n => !lastFetchedIds.has(n.id))
        
        // Mostrar toasts para las nuevas
        brandNew.forEach(notification => {
          addToast(notification)
        })
      }
      
      // Actualizar IDs conocidos
      setLastFetchedIds(new Set(newNotifications.map(n => n.id)))
      setNotifications(newNotifications)
      setUnreadCount(newNotifications.length)
      
      return newNotifications
    } catch (error) {
      console.warn('Error fetching notifications:', error)
      return []
    } finally {
      setIsLoading(false)
    }
  }, [isAuthenticated, lastFetchedIds, addToast])

  // Marcar como leída
  const markAsRead = useCallback(async (notificationId) => {
    try {
      await notificacionesService.marcarLeida(notificationId)
      
      setNotifications(prev => 
        prev.filter(n => n.id !== notificationId)
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
      setLastFetchedIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(notificationId)
        return newSet
      })
      
      return true
    } catch (error) {
      console.error('Error marking as read:', error)
      return false
    }
  }, [])

  // Marcar todas como leídas
  const markAllAsRead = useCallback(async () => {
    try {
      await notificacionesService.marcarTodasLeidas()
      setNotifications([])
      setUnreadCount(0)
      setLastFetchedIds(new Set())
      return true
    } catch (error) {
      console.error('Error marking all as read:', error)
      return false
    }
  }, [])

  // Polling para notificaciones en tiempo real
  useEffect(() => {
    if (!isAuthenticated) {
      setNotifications([])
      setUnreadCount(0)
      setLastFetchedIds(new Set())
      return
    }

    // Fetch inicial
    fetchNotifications(false)

    // Configurar polling
    pollingRef.current = setInterval(() => {
      fetchNotifications(true)
    }, POLLING_INTERVAL)

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
      }
    }
  }, [isAuthenticated, fetchNotifications])

  // Limpiar cuando el usuario cierre sesión
  useEffect(() => {
    if (!user) {
      setNotifications([])
      setUnreadCount(0)
      setToasts([])
      setLastFetchedIds(new Set())
    }
  }, [user])

  const value = {
    // Estado
    notifications,
    unreadCount,
    toasts,
    isLoading,
    
    // Acciones
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    addToast,
    removeToast,
    
    // Helpers
    getNotificationType: (type) => NOTIFICATION_TYPES[type] || NOTIFICATION_TYPES.general,
    
    // Función de prueba - puede llamarse desde la consola con: window.testNotification()
    testNotification: () => {
      const testTypes = ['solicitud_creada', 'documento_aprobado', 'entrevista_agendada', 'contrato_firmado']
      const randomType = testTypes[Math.floor(Math.random() * testTypes.length)]
      const typeConfig = NOTIFICATION_TYPES[randomType] || NOTIFICATION_TYPES.general
      
      addToast({
        id: Date.now(),
        tipo: randomType,
        titulo: `Prueba: ${typeConfig.label}`,
        mensaje: 'Esta es una notificación de prueba para verificar que el sistema funciona correctamente.',
        url_accion: '/dashboard'
      })
    }
  }

  // Exponer función de prueba globalmente en desarrollo
  if (typeof window !== 'undefined' && process.env.NODE_ENV !== 'production') {
    window.testNotification = value.testNotification
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}

export function useNotifications() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}

export default NotificationContext
