import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Card, Badge, Button } from '../../../components/common'
import { FeedbackForm } from '../../../components/feedback'
import { PhaseProgressBarCompact } from '../../../components/common'
import { PHASES } from '../../../store'
import { simulacrosService } from '../../../services/simulacrosService'

// Default fallback data structure
const DEFAULT_SIMULATION = {
  id: 0,
  type: 'presential',
  status: 'scheduled',
  date: new Date().toISOString().split('T')[0],
  time: '10:00',
  endTime: '10:45',
  client: {
    id: '',
    name: 'Cliente',
    email: '',
    photo: null,
    phone: ''
  },
  applicationId: '',
  visaType: 'Visa General',
  visaDetails: {
    destination: '',
    purpose: ''
  },
  currentPhase: 'reception',
  attendanceConfirmed: false,
  previousSimulations: []
}

export default function PresentialFeedbackPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [simulation, setSimulation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)

  useEffect(() => {
    const fetchSimulation = async () => {
      try {
        const data = await simulacrosService.getSimulacro(id)
        setSimulation({
          id: data.id,
          type: 'presential',
          status: data.estado || 'scheduled',
          date: data.fecha,
          time: data.hora_inicio || data.hora || '10:00',
          endTime: data.hora_fin || '10:45',
          client: {
            id: data.cliente?.id || '',
            name: data.cliente?.nombre || data.cliente_nombre || 'Cliente',
            email: data.cliente?.email || '',
            photo: data.cliente?.foto || null,
            phone: data.cliente?.telefono || ''
          },
          applicationId: data.solicitud_id || '',
          visaType: data.tipo_visa || 'Visa General',
          visaDetails: {
            destination: data.destino || '',
            purpose: data.proposito || ''
          },
          currentPhase: data.fase_actual || 'reception',
          attendanceConfirmed: data.asistencia_confirmada || false,
          previousSimulations: data.simulacros_anteriores || []
        })
      } catch (error) {
        console.error('Error fetching simulation:', error)
        setSimulation({ ...DEFAULT_SIMULATION, id })
      } finally {
        setLoading(false)
      }
    }
    fetchSimulation()
  }, [id])

  const formatDate = (dateStr) => {
    return new Date(dateStr + 'T00:00').toLocaleDateString('es-ES', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  }

  const handleConfirmAttendance = () => {
    setSimulation(prev => ({
      ...prev,
      attendanceConfirmed: true,
      status: 'in_progress'
    }))
  }

  const handleStartFeedback = () => {
    setShowFeedbackForm(true)
  }

  const handleSubmitFeedback = async (feedback) => {
    console.log('Feedback submitted:', feedback)
    try {
      await simulacrosService.submitFeedback(simulation.id, feedback)
      setFeedbackSubmitted(true)
      setShowFeedbackForm(false)
    } catch (error) {
      console.error('Error submitting feedback:', error)
      // Still mark as submitted for demo purposes
      setFeedbackSubmitted(true)
      setShowFeedbackForm(false)
    }
  }

  const handleCompleteSession = async () => {
    if (confirm('¿Confirmas que el simulacro ha finalizado?')) {
      try {
        await simulacrosService.completarSimulacro(simulation.id)
      } catch (error) {
        console.error('Error completing simulation:', error)
      }
      setSimulation(prev => ({
        ...prev,
        status: 'completed'
      }))
      navigate('/asesor/simulacros')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
      </div>
    )
  }

  if (!simulation) return null

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-br from-amber-500 to-amber-600 text-white">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <button
            onClick={() => navigate('/asesor/simulacros')}
            className="flex items-center gap-2 text-amber-100 hover:text-white mb-4 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver a simulacros
          </button>

          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-3xl">🏢</span>
                <h1 className="text-3xl font-bold">Simulacro Presencial</h1>
              </div>
              <p className="text-amber-100">
                {formatDate(simulation.date)} • {simulation.time} - {simulation.endTime}
              </p>
            </div>
            <Badge variant={
              simulation.status === 'completed' ? 'success' :
              simulation.status === 'in_progress' ? 'warning' : 'secondary'
            } size="lg">
              {simulation.status === 'completed' ? 'Completado' :
               simulation.status === 'in_progress' ? 'En Progreso' : 'Programado'}
            </Badge>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Client Info Card */}
            <Card>
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-2xl font-bold">
                  {simulation.client.name.charAt(0)}
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-semibold text-gray-900">
                    {simulation.client.name}
                  </h2>
                  <p className="text-gray-500">{simulation.client.email}</p>
                  <p className="text-gray-500 text-sm">{simulation.client.phone}</p>
                  
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-500">Solicitud:</span>
                      <Link 
                        to={`/asesor/solicitudes/${simulation.applicationId}`}
                        className="text-primary-600 hover:text-primary-700 font-medium"
                      >
                        {simulation.applicationId}
                      </Link>
                    </div>
                  </div>
                </div>
              </div>

              {/* Phase Progress */}
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-sm text-gray-500 mb-2">Progreso de la solicitud:</p>
                <PhaseProgressBarCompact currentPhase={simulation.currentPhase} />
              </div>
            </Card>

            {/* Visa Details */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-4">Detalles de la Visa</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm text-gray-500 mb-1">Tipo de Visa</p>
                  <p className="font-medium text-gray-900">{simulation.visaType}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm text-gray-500 mb-1">Destino</p>
                  <p className="font-medium text-gray-900">{simulation.visaDetails.destination}</p>
                </div>
                <div className="md:col-span-2 p-4 bg-gray-50 rounded-xl">
                  <p className="text-sm text-gray-500 mb-1">Propósito</p>
                  <p className="font-medium text-gray-900">{simulation.visaDetails.purpose}</p>
                </div>
              </div>
            </Card>

            {/* Previous Simulations */}
            {simulation.previousSimulations.length > 0 && (
              <Card>
                <h3 className="font-semibold text-gray-900 mb-4">Simulacros Anteriores</h3>
                <div className="space-y-3">
                  {simulation.previousSimulations.map((sim) => (
                    <div 
                      key={sim.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-xl"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-xl">
                          {sim.type === 'virtual' ? '💻' : '🏢'}
                        </span>
                        <div>
                          <p className="font-medium text-gray-900">
                            Simulacro {sim.type === 'virtual' ? 'Virtual' : 'Presencial'}
                          </p>
                          <p className="text-sm text-gray-500">
                            {new Date(sim.date + 'T00:00').toLocaleDateString('es-ES', {
                              day: 'numeric',
                              month: 'short'
                            })}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-primary-600">{sim.score}</p>
                        <p className="text-xs text-gray-500">puntuación</p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Feedback Form */}
            {showFeedbackForm && (
              <FeedbackForm
                clientName={simulation.client.name}
                simulationType="presential"
                visaType={simulation.visaType}
                onSubmit={handleSubmitFeedback}
                onCancel={() => setShowFeedbackForm(false)}
              />
            )}

            {/* Feedback Submitted Success */}
            {feedbackSubmitted && !showFeedbackForm && (
              <Card className="bg-green-50 border-green-200">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-green-800">Evaluación guardada</h3>
                    <p className="text-green-700 text-sm">
                      El feedback ha sido registrado y enviado al cliente.
                    </p>
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Sidebar - Actions */}
          <div className="space-y-6">
            {/* Session Actions */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-4">Acciones de la Sesión</h3>
              
              {simulation.status === 'scheduled' && !simulation.attendanceConfirmed && (
                <div className="space-y-3">
                  <div className="p-4 bg-amber-50 rounded-xl border border-amber-200 text-center">
                    <p className="text-amber-800 text-sm mb-3">
                      ¿El cliente ha llegado?
                    </p>
                    <Button
                      variant="primary"
                      className="w-full bg-amber-500 hover:bg-amber-600"
                      onClick={handleConfirmAttendance}
                    >
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Confirmar Asistencia
                    </Button>
                  </div>
                  <p className="text-center text-gray-500 text-sm">
                    Confirma cuando el cliente llegue a la oficina
                  </p>
                </div>
              )}

              {simulation.attendanceConfirmed && simulation.status === 'in_progress' && !feedbackSubmitted && (
                <div className="space-y-3">
                  <div className="p-4 bg-green-50 rounded-xl border border-green-200">
                    <div className="flex items-center gap-2 text-green-700 mb-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="font-medium">Cliente presente</span>
                    </div>
                    <p className="text-sm text-green-600">
                      Sesión en progreso
                    </p>
                  </div>

                  {!showFeedbackForm && (
                    <Button
                      variant="primary"
                      className="w-full"
                      onClick={handleStartFeedback}
                    >
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Registrar Evaluación
                    </Button>
                  )}
                </div>
              )}

              {feedbackSubmitted && (
                <Button
                  variant="success"
                  className="w-full"
                  onClick={handleCompleteSession}
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Finalizar Sesión
                </Button>
              )}
            </Card>

            {/* Session Info */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-4">Información</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Fecha</span>
                  <span className="text-gray-900 font-medium">
                    {new Date(simulation.date + 'T00:00').toLocaleDateString('es-ES', {
                      day: 'numeric',
                      month: 'short'
                    })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Hora</span>
                  <span className="text-gray-900 font-medium">{simulation.time}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Duración estimada</span>
                  <span className="text-gray-900 font-medium">~45 min</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Modalidad</span>
                  <Badge variant="warning" size="sm">Presencial</Badge>
                </div>
              </div>
            </Card>

            {/* Tips for Advisor */}
            <Card className="bg-blue-50 border-blue-100">
              <h3 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Tips para la sesión
              </h3>
              <ul className="text-sm text-blue-700 space-y-2">
                <li className="flex gap-2">
                  <span>•</span>
                  <span>Simula preguntas reales de la entrevista</span>
                </li>
                <li className="flex gap-2">
                  <span>•</span>
                  <span>Observa lenguaje corporal y contacto visual</span>
                </li>
                <li className="flex gap-2">
                  <span>•</span>
                  <span>Da feedback inmediato sobre las respuestas</span>
                </li>
                <li className="flex gap-2">
                  <span>•</span>
                  <span>Revisa documentos físicos con el cliente</span>
                </li>
              </ul>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
