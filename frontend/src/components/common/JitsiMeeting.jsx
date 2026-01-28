/**
 * Componente reutilizable para Jitsi Meet
 * Integración con la API externa de Jitsi
 */
import { useEffect, useRef, useCallback } from 'react'

/**
 * Props:
 * @param {string} roomName - Nombre de la sala (ej: "migrafacil-sim-123")
 * @param {string} domain - Dominio de Jitsi (default: "meet.jit.si")
 * @param {string} displayName - Nombre del usuario a mostrar
 * @param {function} onJoined - Callback cuando el usuario se une
 * @param {function} onLeft - Callback cuando el usuario sale
 * @param {function} onParticipantJoined - Callback cuando otro participante se une
 * @param {function} onParticipantLeft - Callback cuando otro participante sale
 * @param {object} config - Configuración adicional de Jitsi
 * @param {string} className - Clases CSS para el contenedor
 */
export default function JitsiMeeting({
  roomName,
  domain = 'meet.jit.si',
  displayName = 'Usuario',
  onJoined,
  onLeft,
  onParticipantJoined,
  onParticipantLeft,
  config = {},
  className = ''
}) {
  const containerRef = useRef(null)
  const apiRef = useRef(null)

  const initJitsi = useCallback(() => {
    if (!containerRef.current || !roomName) return

    // Limpiar instancia anterior
    if (apiRef.current) {
      apiRef.current.dispose()
    }

    const defaultConfig = {
      startWithAudioMuted: false,
      startWithVideoMuted: false,
      prejoinPageEnabled: false,
      disableDeepLinking: true,
      enableClosePage: false,
      enableWelcomePage: false,
      toolbarButtons: [
        'microphone',
        'camera',
        'closedcaptions',
        'desktop',
        'fullscreen',
        'fodeviceselection',
        'hangup',
        'chat',
        'settings',
        'videoquality',
        'tileview'
      ]
    }

    const defaultInterfaceConfig = {
      SHOW_JITSI_WATERMARK: false,
      SHOW_WATERMARK_FOR_GUESTS: false,
      SHOW_BRAND_WATERMARK: false,
      TOOLBAR_ALWAYS_VISIBLE: true,
      MOBILE_APP_PROMO: false,
      DISABLE_JOIN_LEAVE_NOTIFICATIONS: false
    }

    const options = {
      roomName,
      width: '100%',
      height: '100%',
      parentNode: containerRef.current,
      userInfo: {
        displayName
      },
      configOverwrite: { ...defaultConfig, ...config.configOverwrite },
      interfaceConfigOverwrite: { ...defaultInterfaceConfig, ...config.interfaceConfigOverwrite }
    }

    const createApi = () => {
      apiRef.current = new window.JitsiMeetExternalAPI(domain, options)
      
      // Configurar eventos
      apiRef.current.addEventListener('videoConferenceJoined', () => {
        console.log('Unido a la conferencia:', roomName)
        onJoined?.()
      })

      apiRef.current.addEventListener('videoConferenceLeft', () => {
        console.log('Salió de la conferencia:', roomName)
        onLeft?.()
      })

      apiRef.current.addEventListener('participantJoined', (participant) => {
        console.log('Participante unido:', participant)
        onParticipantJoined?.(participant)
      })

      apiRef.current.addEventListener('participantLeft', (participant) => {
        console.log('Participante salió:', participant)
        onParticipantLeft?.(participant)
      })
    }

    // Cargar el script de Jitsi si no está cargado
    if (!window.JitsiMeetExternalAPI) {
      const script = document.createElement('script')
      script.src = `https://${domain}/external_api.js`
      script.async = true
      script.onload = createApi
      document.body.appendChild(script)
    } else {
      createApi()
    }
  }, [roomName, domain, displayName, config, onJoined, onLeft, onParticipantJoined, onParticipantLeft])

  useEffect(() => {
    initJitsi()

    return () => {
      if (apiRef.current) {
        apiRef.current.dispose()
        apiRef.current = null
      }
    }
  }, [initJitsi])

  // Exponer métodos útiles
  const hangup = () => {
    apiRef.current?.executeCommand('hangup')
  }

  const toggleAudio = () => {
    apiRef.current?.executeCommand('toggleAudio')
  }

  const toggleVideo = () => {
    apiRef.current?.executeCommand('toggleVideo')
  }

  const toggleShareScreen = () => {
    apiRef.current?.executeCommand('toggleShareScreen')
  }

  return (
    <div 
      ref={containerRef} 
      className={`w-full h-full ${className}`}
    />
  )
}

// Hook para usar Jitsi de forma imperativa
export function useJitsi() {
  const apiRef = useRef(null)
  const containerRef = useRef(null)

  const init = useCallback((options) => {
    if (!containerRef.current || !options.roomName) return

    const domain = options.domain || 'meet.jit.si'

    const createApi = () => {
      apiRef.current = new window.JitsiMeetExternalAPI(domain, {
        roomName: options.roomName,
        width: '100%',
        height: '100%',
        parentNode: containerRef.current,
        userInfo: {
          displayName: options.displayName || 'Usuario'
        },
        configOverwrite: options.config || {},
        interfaceConfigOverwrite: options.interfaceConfig || {}
      })

      if (options.onJoined) {
        apiRef.current.addEventListener('videoConferenceJoined', options.onJoined)
      }
      if (options.onLeft) {
        apiRef.current.addEventListener('videoConferenceLeft', options.onLeft)
      }
    }

    if (!window.JitsiMeetExternalAPI) {
      const script = document.createElement('script')
      script.src = `https://${domain}/external_api.js`
      script.async = true
      script.onload = createApi
      document.body.appendChild(script)
    } else {
      createApi()
    }
  }, [])

  const dispose = useCallback(() => {
    if (apiRef.current) {
      apiRef.current.dispose()
      apiRef.current = null
    }
  }, [])

  const hangup = useCallback(() => {
    apiRef.current?.executeCommand('hangup')
  }, [])

  return {
    containerRef,
    init,
    dispose,
    hangup,
    api: apiRef
  }
}
