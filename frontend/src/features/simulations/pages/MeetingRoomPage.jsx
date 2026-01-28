import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../../../components/common'
import simulacrosService from '../../../services/simulacrosService'
import { useAuth } from '../../../contexts/AuthContext'

export default function MeetingRoomPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const videoRef = useRef(null)
  const jitsiContainerRef = useRef(null)
  const jitsiApiRef = useRef(null)
  
  const [deviceCheck, setDeviceCheck] = useState({
    camera: false,
    microphone: false,
    lighting: false,
    quiet: false,
    documents: false
  })
  const [isReady, setIsReady] = useState(false)
  const [hasJoined, setHasJoined] = useState(false)
  const [micLevel, setMicLevel] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [salaInfo, setSalaInfo] = useState(null)
  const [estadoSala, setEstadoSala] = useState(null)
  const [duracion, setDuracion] = useState(0)
  const [jitsiLoaded, setJitsiLoaded] = useState(false)
  const [jitsiError, setJitsiError] = useState(null)

  // Cargar información de la sala
  useEffect(() => {
    const cargarInfoSala = async () => {
      try {
        const response = await simulacrosService.getInfoSala(id)
        console.log('Info sala cargada:', response)
        setSalaInfo(response.data || response)
      } catch (err) {
        console.error('Error cargando info sala:', err)
        setError('No se pudo cargar la información de la sala')
      }
    }
    cargarInfoSala()
  }, [id])

  // Polling del estado de la sala
  useEffect(() => {
    if (!hasJoined) return

    const pollEstado = async () => {
      try {
        const response = await simulacrosService.getEstadoSala(id)
        setEstadoSala(response.data)
      } catch (err) {
        console.error('Error polling estado:', err)
      }
    }

    pollEstado()
    const interval = setInterval(pollEstado, 5000)
    return () => clearInterval(interval)
  }, [id, hasJoined])

  // Timer de duración
  useEffect(() => {
    if (!hasJoined || estadoSala?.estado !== 'en_progreso') return
    
    const interval = setInterval(() => {
      setDuracion(prev => prev + 1)
    }, 1000)
    
    return () => clearInterval(interval)
  }, [hasJoined, estadoSala?.estado])

  // Simular detección de cámara en pre-sala
  useEffect(() => {
    if (hasJoined) return

    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
        setDeviceCheck(prev => ({ ...prev, camera: true, microphone: true }))
        
        // Simular nivel de micrófono
        const interval = setInterval(() => {
          setMicLevel(Math.random() * 100)
        }, 100)

        return () => {
          clearInterval(interval)
          stream.getTracks().forEach(track => track.stop())
        }
      } catch (err) {
        console.error('Error accessing media devices:', err)
      }
    }

    const cleanup = startCamera()
    return () => {
      cleanup?.then(fn => fn?.())
    }
  }, [hasJoined])

  // Detener cámara local cuando se une a Jitsi
  useEffect(() => {
    if (hasJoined && videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop())
      videoRef.current.srcObject = null
    }
  }, [hasJoined])

  useEffect(() => {
    const allChecked = Object.values(deviceCheck).every(v => v)
    setIsReady(allChecked)
  }, [deviceCheck])

  // Inicializar Jitsi Meet
  const initJitsi = useCallback(() => {
    if (!salaInfo || !jitsiContainerRef.current) {
      console.log('No se puede iniciar Jitsi - salaInfo:', !!salaInfo, 'container:', !!jitsiContainerRef.current)
      return
    }

    // Usar meet.jit.si que es más permisivo con la configuración
    const domain = salaInfo.jitsi_domain || 'meet.jit.si'
    const roomName = salaInfo.room_name
    
    console.log('Inicializando Jitsi:', { domain, roomName })

    // Limpiar instancia anterior
    if (jitsiApiRef.current) {
      jitsiApiRef.current.dispose()
      jitsiApiRef.current = null
    }

    const options = {
      roomName: roomName,
      width: '100%',
      height: '100%',
      parentNode: jitsiContainerRef.current,
      userInfo: {
        displayName: user?.name || user?.email || 'Cliente'
      },
      configOverwrite: {
        startWithAudioMuted: false,
        startWithVideoMuted: false,
        // Deshabilitar pre-join - entrar directamente
        prejoinPageEnabled: false,
        // Configuración general
        disableDeepLinking: true,
        enableClosePage: false,
        enableWelcomePage: false,
        requireDisplayName: false,
        disableModeratorIndicator: true,
        startAudioOnly: false,
        // Botones de la barra de herramientas (sin funciones de moderador)
        toolbarButtons: [
          'microphone',
          'camera',
          'desktop',
          'fullscreen',
          'fodeviceselection',
          'hangup',
          'chat',
          'settings',
          'videoquality',
          'tileview'
        ],
        // Desactivar características que podrían mostrar popups
        disableThirdPartyRequests: true,
        disableInviteFunctions: true,
        // Desactivar grabación y streaming para clientes
        fileRecordingsEnabled: false,
        liveStreamingEnabled: false
      },
      interfaceConfigOverwrite: {
        SHOW_JITSI_WATERMARK: false,
        SHOW_WATERMARK_FOR_GUESTS: false,
        SHOW_BRAND_WATERMARK: false,
        TOOLBAR_ALWAYS_VISIBLE: true,
        MOBILE_APP_PROMO: false,
        DISABLE_JOIN_LEAVE_NOTIFICATIONS: false,
        HIDE_INVITE_MORE_HEADER: true,
        DISABLE_RINGING: true,
        SHOW_CHROME_EXTENSION_BANNER: false,
        SHOW_PROMOTIONAL_CLOSE_PAGE: false,
        SETTINGS_SECTIONS: ['devices', 'language']
      }
    }

    const createJitsiInstance = () => {
      try {
        console.log('Creando instancia JitsiMeetExternalAPI')
        jitsiApiRef.current = new window.JitsiMeetExternalAPI(domain, options)
        setupJitsiEvents()
        setJitsiLoaded(true)
        setJitsiError(null)
      } catch (err) {
        console.error('Error creando Jitsi:', err)
        setJitsiError('Error al iniciar la videollamada')
      }
    }

    // Cargar el script de Jitsi si no está cargado
    if (!window.JitsiMeetExternalAPI) {
      console.log('Cargando script de Jitsi desde:', domain)
      const existingScript = document.querySelector(`script[src*="${domain}/external_api.js"]`)
      if (existingScript) {
        existingScript.remove()
      }
      
      const script = document.createElement('script')
      script.src = `https://${domain}/external_api.js`
      script.async = true
      script.onload = () => {
        console.log('Script de Jitsi cargado')
        createJitsiInstance()
      }
      script.onerror = () => {
        console.error('Error cargando script de Jitsi')
        setJitsiError('Error al cargar el servicio de videollamada')
      }
      document.body.appendChild(script)
    } else {
      createJitsiInstance()
    }
  }, [salaInfo, user])

  const setupJitsiEvents = () => {
    if (!jitsiApiRef.current) return

    jitsiApiRef.current.addEventListener('videoConferenceJoined', () => {
      console.log('Unido a la conferencia')
    })

    jitsiApiRef.current.addEventListener('videoConferenceLeft', () => {
      console.log('Salió de la conferencia')
      navigate(`/simulacros/${id}/resumen`)
    })

    jitsiApiRef.current.addEventListener('participantJoined', (participant) => {
      console.log('Participante unido:', participant)
    })
  }

  // Inicializar Jitsi cuando se une
  useEffect(() => {
    if (hasJoined && salaInfo) {
      initJitsi()
    }

    return () => {
      if (jitsiApiRef.current) {
        jitsiApiRef.current.dispose()
        jitsiApiRef.current = null
      }
    }
  }, [hasJoined, salaInfo, initJitsi])

  const handleJoinMeeting = async () => {
    setLoading(true)
    try {
      // Ingresar a la sala de espera
      await simulacrosService.ingresarSalaEspera(id)
      setHasJoined(true)
    } catch (err) {
      console.error('Error al unirse:', err)
      setError(err.response?.data?.error || 'No se pudo unir al simulacro')
    } finally {
      setLoading(false)
    }
  }

  const formatDuration = (seconds) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const handleLeave = () => {
    if (jitsiApiRef.current) {
      jitsiApiRef.current.executeCommand('hangup')
    }
    navigate(`/simulacros/${id}/resumen`)
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Error</h2>
          <p className="text-gray-400 mb-4">{error}</p>
          <Button onClick={() => navigate('/simulacros')}>
            Volver a mis simulacros
          </Button>
        </div>
      </div>
    )
  }

  // Pre-sala de verificación
  if (!hasJoined) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Pre-sala de Verificación</h1>
            <p className="text-gray-400">Verifica tus dispositivos antes de unirte al simulacro</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Camera Preview */}
            <div className="space-y-4">
              <div className="aspect-video bg-gray-800 rounded-2xl overflow-hidden relative">
                <video 
                  ref={videoRef} 
                  autoPlay 
                  muted 
                  playsInline
                  className="w-full h-full object-cover"
                />
                {!deviceCheck.camera && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
                    <div className="text-center text-gray-400">
                      <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      <p>Accediendo a la cámara...</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Mic Level */}
              <div className="bg-gray-800 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Nivel de micrófono</span>
                  <svg className={`w-5 h-5 ${micLevel > 20 ? 'text-green-500' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-green-500 to-green-400 rounded-full transition-all duration-100"
                    style={{ width: `${micLevel}%` }}
                  />
                </div>
              </div>

              {/* Device Selector */}
              <div className="flex gap-3">
                <select className="flex-1 px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-gray-300 focus:ring-2 focus:ring-primary-500">
                  <option>Cámara integrada</option>
                </select>
                <select className="flex-1 px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-gray-300 focus:ring-2 focus:ring-primary-500">
                  <option>Micrófono integrado</option>
                </select>
              </div>
            </div>

            {/* Checklist */}
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Lista de Verificación</h3>
                <div className="space-y-3">
                  {[
                    { key: 'camera', label: '¿Tu cámara funciona correctamente?', auto: true },
                    { key: 'microphone', label: '¿Tu micrófono detecta audio?', auto: true },
                    { key: 'lighting', label: '¿Tienes buena iluminación?' },
                    { key: 'quiet', label: '¿Estás en un lugar tranquilo?' },
                    { key: 'documents', label: '¿Tienes tus documentos a mano?' }
                  ].map((item) => (
                    <label 
                      key={item.key}
                      className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors ${
                        deviceCheck[item.key] ? 'bg-green-900/30' : 'bg-gray-700/50 hover:bg-gray-700'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={deviceCheck[item.key]}
                        onChange={(e) => !item.auto && setDeviceCheck(prev => ({ 
                          ...prev, 
                          [item.key]: e.target.checked 
                        }))}
                        disabled={item.auto}
                        className="w-5 h-5 rounded border-gray-600 bg-gray-700 text-green-500 focus:ring-green-500"
                      />
                      <span className={`text-sm ${deviceCheck[item.key] ? 'text-green-400' : 'text-gray-300'}`}>
                        {item.label}
                      </span>
                      {deviceCheck[item.key] && (
                        <svg className="w-5 h-5 text-green-500 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </label>
                  ))}
                </div>
              </div>

              {/* Info Card */}
              <div className="bg-blue-900/30 border border-blue-800 rounded-xl p-4">
                <div className="flex gap-3">
                  <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p className="text-sm text-blue-300 font-medium">Información del Simulacro</p>
                    <p className="text-xs text-blue-400 mt-1">
                      Simulacro #{id}
                      {salaInfo?.otro_participante && ` • Con ${salaInfo.otro_participante}`}
                    </p>
                    {salaInfo?.room_name && (
                      <p className="text-xs text-gray-500 mt-1">
                        Sala: {salaInfo.room_name}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Join Button */}
              <Button
                onClick={handleJoinMeeting}
                disabled={!isReady || loading}
                className="w-full py-4 text-lg"
                size="lg"
              >
                {loading ? (
                  <>
                    <svg className="w-5 h-5 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Conectando...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Unirse al Simulacro
                  </>
                )}
              </Button>

              {!isReady && (
                <p className="text-center text-sm text-gray-500">
                  Completa la lista de verificación para continuar
                </p>
              )}

              <button
                onClick={() => navigate('/simulacros')}
                className="w-full py-2 text-gray-400 hover:text-white text-sm transition-colors"
              >
                Cancelar y volver
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Sala de reunión con Jitsi Meet
  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Meeting Header */}
      <div className="h-14 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span className="text-white font-medium">Simulacro #{id}</span>
          {salaInfo?.otro_participante && (
            <span className="text-gray-400 text-sm">• Con {salaInfo.otro_participante.nombre || salaInfo.otro_participante}</span>
          )}
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-green-400">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm">
              {estadoSala?.estado === 'en_progreso' ? 'En vivo' : 'Sala de espera'}
            </span>
          </div>
          <div className="px-3 py-1 bg-gray-700 rounded-lg text-white text-sm font-mono">
            {formatDuration(duracion)}
          </div>
        </div>

        <button
          onClick={handleLeave}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Salir
        </button>
      </div>

      {/* Jitsi Meeting Area */}
      <div className="flex-1 relative min-h-0">
        {/* Contenedor de Jitsi - importante que tenga dimensiones absolutas */}
        <div 
          ref={jitsiContainerRef} 
          className="absolute inset-0"
          style={{ minHeight: '400px' }}
        />
        
        {/* Error de Jitsi */}
        {jitsiError && (
          <div className="absolute inset-0 bg-gray-900 flex items-center justify-center z-20">
            <div className="text-center">
              <div className="w-20 h-20 bg-red-900/50 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-10 h-10 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Error de conexión</h2>
              <p className="text-gray-400 max-w-md mx-auto mb-4">{jitsiError}</p>
              <Button onClick={() => window.location.reload()}>
                Reintentar
              </Button>
            </div>
          </div>
        )}

        {/* Cargando Jitsi */}
        {!jitsiLoaded && !jitsiError && (
          <div className="absolute inset-0 bg-gray-900 flex items-center justify-center z-10">
            <div className="text-center">
              <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-10 h-10 text-primary-400 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Conectando...</h2>
              <p className="text-gray-400 max-w-md mx-auto">
                Iniciando videollamada. Por favor espera un momento.
              </p>
            </div>
          </div>
        )}
        
        {/* Mensaje de espera si el asesor no ha iniciado */}
        {jitsiLoaded && estadoSala?.estado === 'en_sala_espera' && (
          <div className="absolute inset-0 bg-gray-900/80 flex items-center justify-center z-10">
            <div className="text-center">
              <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-10 h-10 text-primary-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Esperando al asesor</h2>
              <p className="text-gray-400 max-w-md mx-auto">
                El asesor iniciará la sesión en breve. Por favor mantente en esta pantalla.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
