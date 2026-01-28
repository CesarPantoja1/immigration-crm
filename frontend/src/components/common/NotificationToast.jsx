/**
 * Componente NotificationToast
 * Muestra alertas de notificaciones en tiempo real con sonido de campana
 */
import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useNotifications, NOTIFICATION_TYPES } from '../../contexts/NotificationContext'

// Colores por tipo
const colorClasses = {
  blue: 'bg-blue-50 border-blue-500 text-blue-800',
  green: 'bg-green-50 border-green-500 text-green-800',
  red: 'bg-red-50 border-red-500 text-red-800',
  yellow: 'bg-yellow-50 border-yellow-500 text-yellow-800',
  orange: 'bg-orange-50 border-orange-500 text-orange-800',
  purple: 'bg-purple-50 border-purple-500 text-purple-800',
  gray: 'bg-gray-50 border-gray-500 text-gray-800',
}

const iconBgClasses = {
  blue: 'bg-blue-100',
  green: 'bg-green-100',
  red: 'bg-red-100',
  yellow: 'bg-yellow-100',
  orange: 'bg-orange-100',
  purple: 'bg-purple-100',
  gray: 'bg-gray-100',
}

// Función para reproducir sonido de notificación (campana)
function playNotificationSound() {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    
    // Frecuencias para simular una campana (acorde mayor)
    const frequencies = [523.25, 659.25, 783.99] // C5, E5, G5
    
    frequencies.forEach((freq, index) => {
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()
      
      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)
      
      oscillator.frequency.value = freq
      oscillator.type = 'sine'
      
      const now = audioContext.currentTime
      const startTime = now + (index * 0.04)
      
      gainNode.gain.setValueAtTime(0, startTime)
      gainNode.gain.linearRampToValueAtTime(0.12, startTime + 0.02)
      gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + 0.4)
      
      oscillator.start(startTime)
      oscillator.stop(startTime + 0.4)
    })
  } catch (error) {
    console.warn('No se pudo reproducir el sonido:', error)
  }
}

function SingleToast({ toast, onClose, onNavigate }) {
  const [isVisible, setIsVisible] = useState(false)
  const [isExiting, setIsExiting] = useState(false)
  const [progress, setProgress] = useState(100)
  
  const colorClass = colorClasses[toast.color] || colorClasses.blue
  const iconBgClass = iconBgClasses[toast.color] || iconBgClasses.blue

  useEffect(() => {
    // Animar entrada
    requestAnimationFrame(() => {
      setIsVisible(true)
    })
    
    // Animación de progreso
    const duration = 6000
    const interval = 50
    const decrement = (interval / duration) * 100
    
    const timer = setInterval(() => {
      setProgress(prev => {
        if (prev <= 0) {
          clearInterval(timer)
          return 0
        }
        return prev - decrement
      })
    }, interval)

    return () => clearInterval(timer)
  }, [])

  const handleClose = () => {
    setIsExiting(true)
    setTimeout(() => onClose(toast.id), 300)
  }

  const handleClick = () => {
    if (toast.url) {
      onNavigate(toast.url)
      handleClose()
    }
  }

  return (
    <div
      className={`
        relative overflow-hidden
        w-80 sm:w-96 max-w-[calc(100vw-2rem)]
        border-l-4 rounded-lg shadow-2xl bg-white
        transform transition-all duration-300 ease-out
        ${!isVisible ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}
        ${isExiting ? 'translate-x-full opacity-0 scale-95' : ''}
        ${colorClass}
        ${toast.url ? 'cursor-pointer hover:scale-[1.02]' : ''}
      `}
      onClick={toast.url ? handleClick : undefined}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Icono */}
          <div className={`flex-shrink-0 w-10 h-10 rounded-full ${iconBgClass} flex items-center justify-center text-xl shadow-sm`}>
            {toast.icon}
          </div>
          
          {/* Contenido */}
          <div className="flex-1 min-w-0 pr-2">
            <p className="font-semibold text-sm leading-tight">
              {toast.title}
            </p>
            <p className="text-sm opacity-75 line-clamp-2 mt-1">
              {toast.message}
            </p>
            {toast.url && (
              <p className="text-xs opacity-60 mt-2 flex items-center gap-1 font-medium">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
                Ver detalles
              </p>
            )}
          </div>
          
          {/* Botón cerrar */}
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleClose()
            }}
            className="flex-shrink-0 p-1.5 rounded-full hover:bg-black/10 transition-colors -mr-1 -mt-1"
            title="Cerrar"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Barra de progreso */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/5">
        <div 
          className="h-full bg-current opacity-40"
          style={{ 
            width: `${progress}%`,
            transition: 'width 50ms linear'
          }}
        />
      </div>
    </div>
  )
}

export default function NotificationToast() {
  const { toasts, removeToast } = useNotifications()
  const navigate = useNavigate()
  const previousToastCount = useRef(0)

  // Reproducir sonido cuando llegue una nueva notificación
  useEffect(() => {
    if (toasts.length > previousToastCount.current && toasts.length > 0) {
      playNotificationSound()
    }
    previousToastCount.current = toasts.length
  }, [toasts.length])

  const handleNavigate = (url) => {
    navigate(url)
  }

  // Siempre renderizar el contenedor
  return (
    <div 
      className="fixed top-20 right-4 z-[9999] flex flex-col gap-3 pointer-events-none"
      aria-live="polite"
      aria-label="Notificaciones"
    >
      {toasts.map(toast => (
        <div key={toast.id} className="pointer-events-auto animate-slide-in-right">
          <SingleToast
            toast={toast}
            onClose={removeToast}
            onNavigate={handleNavigate}
          />
        </div>
      ))}
    </div>
  )
}
