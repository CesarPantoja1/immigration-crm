import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button, Card, Modal } from '../../../components/common'
import { simulacrosService } from '../../../services/simulacrosService'

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
  const [simulationData, setSimulationData] = useState(defaultSimulationData)
  const [loading, setLoading] = useState(true)
  const [isInSession, setIsInSession] = useState(false)
  const [sessionTime, setSessionTime] = useState(0)
  const [showEndModal, setShowEndModal] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [rating, setRating] = useState(0)

  useEffect(() => {
    const fetchSimulationData = async () => {
      try {
        const data = await simulacrosService.getSimulacro(id)
        const clientName = data.cliente_nombre || data.cliente?.nombre || 'Cliente'
        setSimulationData({
          id: data.id,
          client: {
            name: clientName,
            visaType: data.tipo_visa || 'Visa',
            avatar: clientName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
          },
          scheduledTime: data.hora_propuesta || data.hora || '',
          date: data.fecha_propuesta ? new Date(data.fecha_propuesta + 'T00:00').toLocaleDateString('es-ES', {
            day: 'numeric', month: 'long', year: 'numeric'
          }) : ''
        })
      } catch (error) {
        console.error('Error fetching simulation:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchSimulationData()
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

  const handleStartSession = () => {
    setIsInSession(true)
  }

  const handleEndSession = () => {
    setShowEndModal(true)
  }

  const handleSubmitFeedback = () => {
    // Submit feedback and navigate
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
        <div className="flex-1 bg-gray-900 rounded-2xl overflow-hidden relative">
          {!isInSession ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-medium text-white mb-2">Sesión no iniciada</h3>
                <p className="text-gray-400 mb-6">Haz clic en "Iniciar Sesión" para comenzar</p>
                <Button onClick={handleStartSession}>
                  Iniciar Sesión
                </Button>
              </div>
            </div>
          ) : (
            <>
              {/* Jitsi iframe placeholder */}
              <div className="w-full h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="w-24 h-24 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-medium text-white mb-2">Sesión en curso</h3>
                  <p className="text-gray-400">Jitsi Meet se integraría aquí</p>
                  <p className="text-gray-500 text-sm mt-2">
                    Room ID: migrafacil-sim-{id}
                  </p>
                </div>
              </div>

              {/* Video Controls */}
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3 bg-gray-800/90 px-4 py-2 rounded-full">
                <button className="p-3 bg-gray-700 hover:bg-gray-600 rounded-full transition-colors">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </button>
                <button className="p-3 bg-gray-700 hover:bg-gray-600 rounded-full transition-colors">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
                <button className="p-3 bg-gray-700 hover:bg-gray-600 rounded-full transition-colors">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </button>
                <div className="w-px h-8 bg-gray-600" />
                <button 
                  onClick={handleEndSession}
                  className="p-3 bg-red-600 hover:bg-red-700 rounded-full transition-colors"
                >
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.279 3H5z" />
                  </svg>
                </button>
              </div>
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
            </div>
          </Card>

          {/* Quick Notes */}
          <Card className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-3">Notas Rápidas</h3>
            <textarea
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
              onClick={() => {
                setShowEndModal(false)
                setIsInSession(false)
                setShowUploadModal(true)
              }}
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
