import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button, Card, Modal } from '../../../components/common'
import { simulacrosService } from '../../../services/simulacrosService'
import { useAuth } from '../../../contexts/AuthContext'

// Default simulation data
const defaultSimulationData = {
  id: '',
  client: {
    name: 'Cliente',
    visaType: 'Visa',
    avatar: 'C'
  },
  scheduledTime: '',
  date: ''
}

export default function AdvisorMeetingRoomPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const jitsiContainerRef = useRef(null)
  const jitsiApiRef = useRef(null)
  
  const [simulationData, setSimulationData] = useState(defaultSimulationData)
  const [loading, setLoading] = useState(true)
  const [isInSession, setIsInSession] = useState(false)
  const [sessionTime, setSessionTime] = useState(0)
  const [showEndModal, setShowEndModal] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [rating, setRating] = useState(0)
  const [salaInfo, setSalaInfo] = useState(null)
  const [estadoSala, setEstadoSala] = useState(null)
  const [notes, setNotes] = useState('')
  const [jitsiLoaded, setJitsiLoaded] = useState(false)
  const [jitsiError, setJitsiError] = useState(null)

  // Cargar datos del simulacro y sala
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [simResponse, salaResponse] = await Promise.all([
          simulacrosService.getSimulacro(id),
          simulacrosService.getInfoSala(id)
        ])
        
        const simData = simResponse.data || simResponse
        const salaData = salaResponse.data || salaResponse
        
        console.log('Datos simulacro:', simData)
        console.log('Datos sala:', salaData)
        
        const clientName = simData?.cliente_nombre || 'Cliente'
        setSimulationData({
          id: simData?.id,
          client: {
            name: clientName,
            visaType: simData?.tipo_visa || 'Visa',
            avatar: clientName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
          },
          scheduledTime: simData?.hora_propuesta || simData?.hora || '',
          date: simData?.fecha_propuesta ? new Date(simData.fecha_propuesta + 'T00:00').toLocaleDateString('es-ES', {
            day: 'numeric', month: 'long', year: 'numeric'
          }) : ''
        })
        
        setSalaInfo(salaData)
        
        // Si ya está en progreso, mostrar Jitsi
        if (salaData?.en_progreso) {
          setIsInSession(true)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  // Polling del estado de la sala
  useEffect(() => {
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
  }, [id])

  // Session timer
  useEffect(() => {
    let interval
    if (isInSession) {
      interval = setInterval(() => {
        setSessionTime(prev => prev + 1)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isInSession])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // Inicializar Jitsi Meet
  const initJitsi = useCallback(() => {
    if (!salaInfo || !jitsiContainerRef.current) {
      console.log('No se puede iniciar Jitsi - salaInfo:', !!salaInfo, 'container:', !!jitsiContainerRef.current)
      return
    }

    const domain = salaInfo.jitsi_domain || 'meet.jit.si'
    const roomName = salaInfo.room_name
    
    console.log('Asesor: Inicializando Jitsi:', { domain, roomName })

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
        displayName: user?.name || user?.email || 'Asesor (Moderador)'
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
        startAudioOnly: false,
        // Botones del asesor (con herramientas de moderador)
        toolbarButtons: [
          'microphone',
          'camera',
          'desktop',
          'fullscreen',
          'fodeviceselection',
          'hangup',
          'chat',
          'recording',
          'settings',
          'videoquality',
          'tileview',
          'participants-pane',
          'security'
        ],
        disableThirdPartyRequests: true,
        disableInviteFunctions: true
      },
      interfaceConfigOverwrite: {
        SHOW_JITSI_WATERMARK: false,
        SHOW_WATERMARK_FOR_GUESTS: false,
        SHOW_BRAND_WATERMARK: false,
        TOOLBAR_ALWAYS_VISIBLE: true,
        MOBILE_APP_PROMO: false,
        DISABLE_JOIN_LEAVE_NOTIFICATIONS: false,
        HIDE_INVITE_MORE_HEADER: true,
        SHOW_CHROME_EXTENSION_BANNER: false,
        SHOW_PROMOTIONAL_CLOSE_PAGE: false,
        SETTINGS_SECTIONS: ['devices', 'language', 'moderator', 'profile']
      }
    }

    const createJitsiInstance = () => {
      try {
        console.log('Asesor: Creando instancia JitsiMeetExternalAPI')
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
      console.log('Asesor: Cargando script de Jitsi desde:', domain)
      const existingScript = document.querySelector(`script[src*="${domain}/external_api.js"]`)
      if (existingScript) {
        existingScript.remove()
      }
      
      const script = document.createElement('script')
      script.src = `https://${domain}/external_api.js`
      script.async = true
      script.onload = () => {
        console.log('Asesor: Script de Jitsi cargado')
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
      console.log('Asesor unido a la conferencia')
    })

    jitsiApiRef.current.addEventListener('videoConferenceLeft', () => {
      console.log('Asesor salió de la conferencia')
    })

    jitsiApiRef.current.addEventListener('participantJoined', (participant) => {
      console.log('Participante unido:', participant)
    })
  }

  // Inicializar Jitsi cuando inicia la sesión
  useEffect(() => {
    if (isInSession && salaInfo) {
      initJitsi()
    }

    return () => {
      if (jitsiApiRef.current) {
        jitsiApiRef.current.dispose()
        jitsiApiRef.current = null
      }
    }
  }, [isInSession, salaInfo, initJitsi])

  const handleStartSession = async () => {
    try {
      // Llamar al backend para iniciar el simulacro
      await simulacrosService.iniciarSimulacro(id)
      setIsInSession(true)
    } catch (error) {
      console.error('Error iniciando sesión:', error)
      // Aún así iniciar localmente para pruebas
      setIsInSession(true)
    }
  }

  const handleEndSession = () => {
    setShowEndModal(true)
  }

  const handleConfirmEndSession = async () => {
    try {
      // Llamar al backend para finalizar
      await simulacrosService.finalizarSimulacro(id, {
        duracion_minutos: Math.ceil(sessionTime / 60),
        notas: notes
      })
    } catch (error) {
      console.error('Error finalizando sesión:', error)
    }
    
    if (jitsiApiRef.current) {
      jitsiApiRef.current.executeCommand('hangup')
    }
    
    setShowEndModal(false)
    setIsInSession(false)
    setShowUploadModal(true)
  }

  const handleSubmitFeedback = async () => {
    try {
      await simulacrosService.submitFeedback(id, {
        calificacion: rating,
        comentarios: feedback
      })
    } catch (error) {
      console.error('Error enviando feedback:', error)
    }
    setShowUploadModal(false)
    navigate('/asesor/simulacros')
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header Controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/asesor/simulacros')}
            className="flex items-center gap-2 text-gray-500 hover:text-gray-700"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver
          </button>
          
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-semibold">
              {simulationData.client.avatar}
            </div>
            <div>
              <p className="font-medium text-gray-900">{simulationData.client.name}</p>
              <p className="text-sm text-gray-500">{simulationData.client.visaType}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {isInSession && (
            <div className="flex items-center gap-2 bg-red-50 px-4 py-2 rounded-full">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="font-mono font-medium text-red-600">{formatTime(sessionTime)}</span>
            </div>
          )}

          {isInSession ? (
            <Button variant="danger" onClick={handleEndSession}>
              Finalizar Sesión
            </Button>
          ) : (
            <Button onClick={handleStartSession}>
              Iniciar Sesión
            </Button>
          )}
        </div>
      </div>

      <div className="flex-1 flex gap-4">
        {/* Jitsi Container */}
        <div className="flex-1 bg-gray-900 rounded-2xl overflow-hidden relative min-h-[400px]">
          {!isInSession ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-medium text-white mb-2">Sesión no iniciada</h3>
                <p className="text-gray-400 mb-2">Haz clic en "Iniciar Sesión" para comenzar</p>
                {estadoSala?.cliente_en_sala && (
                  <p className="text-green-400 text-sm mb-4">✓ El cliente está en la sala de espera</p>
                )}
                <Button onClick={handleStartSession}>
                  Iniciar Sesión
                </Button>
              </div>
            </div>
          ) : (
            <>
              {/* Jitsi Container Real */}
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
                    <h2 className="text-xl font-bold text-white mb-2">Error de conexión</h2>
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
                    <h2 className="text-xl font-bold text-white mb-2">Conectando...</h2>
                    <p className="text-gray-400 max-w-md mx-auto">
                      Iniciando videollamada. Por favor espera un momento.
                    </p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Side Panel */}
        <div className="w-80 flex flex-col gap-4">
          {/* Client Info */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-3">Información del Cliente</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Nombre</span>
                <span className="text-gray-900">{simulationData.client.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Tipo de Visa</span>
                <span className="text-gray-900">{simulationData.client.visaType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Hora agendada</span>
                <span className="text-gray-900">{simulationData.scheduledTime}</span>
              </div>
              {salaInfo?.room_name && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Sala</span>
                  <span className="text-gray-900 text-xs">{salaInfo.room_name}</span>
                </div>
              )}
              {estadoSala?.cliente_en_sala && (
                <div className="flex items-center gap-2 mt-2 p-2 bg-green-50 rounded-lg">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-green-700 text-sm">Cliente en sala de espera</span>
                </div>
              )}
            </div>
          </Card>

          {/* Quick Notes */}
          <Card className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-3">Notas Rápidas</h3>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
              placeholder="Escribe notas durante la sesión..."
            />
          </Card>

          {/* Quick Actions */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-3">Acciones Rápidas</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center gap-3 p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors text-left">
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm text-gray-700">Ver Expediente</span>
              </button>
              <button className="w-full flex items-center gap-3 p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors text-left">
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm text-gray-700">Guía de Preguntas</span>
              </button>
            </div>
          </Card>
        </div>
      </div>

      {/* End Session Modal */}
      <Modal
        isOpen={showEndModal}
        onClose={() => setShowEndModal(false)}
        title="Finalizar Sesión"
        size="md"
      >
        <div className="space-y-4">
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <p className="text-3xl font-bold text-gray-900 mb-1">{formatTime(sessionTime)}</p>
            <p className="text-sm text-gray-500">Duración de la sesión</p>
          </div>

          <p className="text-gray-600">
            ¿Deseas finalizar la sesión? Podrás subir el feedback después.
          </p>

          <div className="flex gap-3 pt-4">
            <Button 
              variant="secondary" 
              className="flex-1"
              onClick={() => setShowEndModal(false)}
            >
              Continuar Sesión
            </Button>
            <Button 
              variant="danger"
              className="flex-1"
              onClick={handleConfirmEndSession}
            >
              Finalizar
            </Button>
          </div>
        </div>
      </Modal>

      {/* Upload Feedback Modal */}
      <Modal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        title="Subir Feedback"
        size="lg"
      >
        <div className="space-y-4">
          {/* Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Calificación General
            </label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  className={`p-2 rounded-lg transition-colors ${
                    rating >= star ? 'text-yellow-500' : 'text-gray-300'
                  }`}
                >
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </button>
              ))}
            </div>
          </div>

          {/* Feedback Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Feedback Detallado
            </label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
              rows={6}
              placeholder="Escribe el feedback para el cliente..."
            />
          </div>

          {/* Upload Document */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Adjuntar Evaluación (PDF)
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-primary-400 transition-colors cursor-pointer">
              <svg className="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <p className="text-sm text-gray-500">Haz clic o arrastra un archivo</p>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button 
              variant="secondary" 
              className="flex-1"
              onClick={() => {
                setShowUploadModal(false)
                navigate('/asesor/simulacros')
              }}
            >
              Subir Después
            </Button>
            <Button 
              className="flex-1"
              onClick={handleSubmitFeedback}
              disabled={!rating || !feedback.trim()}
            >
              Enviar Feedback
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
