import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card, Badge, Button, Modal, ConfirmModal } from '../../../components/common'
import { useAuth } from '../../../contexts/AuthContext'

// Mock data
const MOCK_PROPOSALS = [
  {
    id: 1,
    date: '2026-01-30',
    time: '10:00 AM',
    advisor: 'María González',
    modality: 'Virtual',
    visaType: 'Estudio',
    status: 'pending'
  }
]

const MOCK_UPCOMING = [
  {
    id: 2,
    date: '2026-02-05',
    time: '03:00 PM',
    advisor: 'María González',
    modality: 'Virtual',
    visaType: 'Estudio',
    status: 'confirmed',
    hoursUntil: 192
  }
]

const MOCK_COMPLETED = [
  {
    id: 3,
    date: '2026-01-15',
    time: '11:00 AM',
    advisor: 'María González',
    modality: 'Virtual',
    visaType: 'Estudio',
    duration: '28 min',
    feedbackStatus: 'received'
  }
]

export default function SimulationsPage() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('proposals')
  const [showProposeModal, setShowProposeModal] = useState(false)
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [selectedSimulation, setSelectedSimulation] = useState(null)
  const [proposedDate, setProposedDate] = useState('')
  const [proposedTime, setProposedTime] = useState('')
  const [proposeReason, setProposeReason] = useState('')

  const simulationsUsed = user?.simulationsUsed || 1
  const simulationsTotal = user?.simulationsTotal || 2

  const handleAcceptSimulation = (simulation) => {
    console.log('Accepted:', simulation)
    // TODO: API call
  }

  const handleProposeDate = () => {
    console.log('Proposed:', { date: proposedDate, time: proposedTime, reason: proposeReason })
    setShowProposeModal(false)
    // TODO: API call
  }

  const handleCancelSimulation = () => {
    console.log('Cancelled:', selectedSimulation)
    setShowCancelModal(false)
    // TODO: API call
  }

  const getCancellationMessage = (hoursUntil) => {
    if (hoursUntil < 24) {
      return {
        canCancel: false,
        variant: 'danger',
        message: 'No puedes cancelar con menos de 24 horas de anticipación.'
      }
    } else if (hoursUntil < 72) {
      return {
        canCancel: true,
        variant: 'warning',
        message: 'Si cancelas ahora, contará como un intento utilizado (entre 1-3 días de anticipación).'
      }
    } else {
      return {
        canCancel: true,
        variant: 'primary',
        message: 'Puedes cancelar sin penalización (más de 3 días de anticipación).'
      }
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Mis Simulacros</h1>
        <p className="text-gray-500 mt-1">Gestiona tus simulacros de entrevista</p>
      </div>

      {/* Simulation Counter */}
      <Card className="mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-2">Simulacros Disponibles</h3>
            <p className="text-sm text-gray-500 mb-4">
              {simulationsUsed < simulationsTotal 
                ? `Puedes solicitar hasta ${simulationsTotal} simulacros en total`
                : 'Has alcanzado el límite de simulacros por proceso'}
            </p>
            <div className="flex items-center gap-4">
              <div className="flex-1 max-w-xs">
                <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all ${
                      simulationsUsed === 0 ? 'bg-green-500' :
                      simulationsUsed === 1 ? 'bg-amber-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${(simulationsUsed / simulationsTotal) * 100}%` }}
                  />
                </div>
              </div>
              <span className="text-lg font-bold text-gray-900">
                {simulationsUsed}/{simulationsTotal}
              </span>
            </div>
          </div>
          <Button disabled={simulationsUsed >= simulationsTotal}>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Solicitar Simulacro
          </Button>
        </div>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        {[
          { id: 'proposals', label: 'Propuestas Pendientes', count: MOCK_PROPOSALS.length },
          { id: 'upcoming', label: 'Próximos Simulacros', count: MOCK_UPCOMING.length },
          { id: 'completed', label: 'Completados', count: MOCK_COMPLETED.length }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                activeTab === tab.id ? 'bg-primary-100 text-primary-600' : 'bg-gray-100 text-gray-600'
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Proposals Tab */}
      {activeTab === 'proposals' && (
        <div className="space-y-4">
          {MOCK_PROPOSALS.length === 0 ? (
            <Card className="text-center py-12">
              <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Sin propuestas pendientes</h3>
              <p className="text-gray-500">No tienes propuestas de simulacro por revisar</p>
            </Card>
          ) : (
            MOCK_PROPOSALS.map((proposal) => (
              <Card key={proposal.id}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 bg-primary-100 rounded-xl flex items-center justify-center">
                      <svg className="w-7 h-7 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">Propuesta de Simulacro</h3>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          {proposal.date}
                        </span>
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {proposal.time}
                        </span>
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                          {proposal.advisor}
                        </span>
                      </div>
                      <div className="flex gap-2 mt-3">
                        <Badge variant="primary">{proposal.modality}</Badge>
                        <Badge variant="info">{proposal.visaType}</Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      onClick={() => {
                        setSelectedSimulation(proposal)
                        setShowProposeModal(true)
                      }}
                    >
                      Proponer otra fecha
                    </Button>
                    <Button onClick={() => handleAcceptSimulation(proposal)}>
                      Aceptar simulacro
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Upcoming Tab */}
      {activeTab === 'upcoming' && (
        <div className="space-y-4">
          {MOCK_UPCOMING.length === 0 ? (
            <Card className="text-center py-12">
              <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Sin simulacros próximos</h3>
              <p className="text-gray-500">No tienes simulacros programados</p>
            </Card>
          ) : (
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-7 top-0 bottom-0 w-0.5 bg-gray-200" />
              
              {MOCK_UPCOMING.map((simulation, index) => (
                <div key={simulation.id} className="relative flex gap-6 pb-8">
                  {/* Timeline dot */}
                  <div className="relative z-10 w-14 h-14 bg-primary-100 rounded-xl flex items-center justify-center border-4 border-white">
                    <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>

                  <Card className="flex-1">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold text-gray-900">Simulacro Confirmado</h3>
                          <Badge variant="success" dot>Confirmado</Badge>
                        </div>
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            {simulation.date}
                          </span>
                          <span className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {simulation.time}
                          </span>
                          <span className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            {simulation.advisor}
                          </span>
                        </div>
                        <div className="flex gap-2 mt-3">
                          <Badge variant="primary">{simulation.modality}</Badge>
                          <Badge variant="info">{simulation.visaType}</Badge>
                        </div>
                      </div>
                      <div className="flex gap-3">
                        <Button
                          variant="secondary"
                          onClick={() => {
                            setSelectedSimulation(simulation)
                            setShowCancelModal(true)
                          }}
                        >
                          Cancelar
                        </Button>
                        <Link to={`/simulacros/${simulation.id}/sala`}>
                          <Button>
                            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                            Ingresar a Reunión
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </Card>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Completed Tab */}
      {activeTab === 'completed' && (
        <div className="space-y-4">
          {MOCK_COMPLETED.map((simulation) => (
            <Card key={simulation.id}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 bg-green-100 rounded-xl flex items-center justify-center">
                    <svg className="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-gray-900">Simulacro Completado</h3>
                      <Badge 
                        variant={simulation.feedbackStatus === 'received' ? 'success' : 'warning'}
                      >
                        {simulation.feedbackStatus === 'received' ? 'Feedback recibido' : 'Pendiente feedback'}
                      </Badge>
                    </div>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-gray-500">
                      <span>{simulation.date} • {simulation.time}</span>
                      <span>Duración: {simulation.duration}</span>
                      <span>Asesor: {simulation.advisor}</span>
                    </div>
                  </div>
                </div>
                <Button variant="secondary">
                  Ver Resumen
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Propose Date Modal */}
      <Modal
        isOpen={showProposeModal}
        onClose={() => setShowProposeModal(false)}
        title="Proponer otra fecha"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Propón una nueva fecha y hora para tu simulacro. Tu asesor recibirá la propuesta.
          </p>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
              <input
                type="date"
                value={proposedDate}
                onChange={(e) => setProposedDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hora</label>
              <input
                type="time"
                value={proposedTime}
                onChange={(e) => setProposedTime(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Motivo (opcional)
            </label>
            <textarea
              value={proposeReason}
              onChange={(e) => setProposeReason(e.target.value)}
              placeholder="Explica brevemente por qué propones otra fecha..."
              rows={3}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 resize-none"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="secondary" className="flex-1" onClick={() => setShowProposeModal(false)}>
              Cancelar
            </Button>
            <Button 
              className="flex-1" 
              onClick={handleProposeDate}
              disabled={!proposedDate || !proposedTime}
            >
              Enviar Propuesta
            </Button>
          </div>
        </div>
      </Modal>

      {/* Cancel Confirmation Modal */}
      {selectedSimulation && (
        <Modal
          isOpen={showCancelModal}
          onClose={() => setShowCancelModal(false)}
          title="Cancelar Simulacro"
          size="sm"
        >
          {(() => {
            const cancellation = getCancellationMessage(selectedSimulation.hoursUntil || 0)
            return (
              <div className="space-y-4">
                <div className={`p-4 rounded-xl ${
                  cancellation.variant === 'danger' ? 'bg-red-50 border border-red-200' :
                  cancellation.variant === 'warning' ? 'bg-amber-50 border border-amber-200' :
                  'bg-blue-50 border border-blue-200'
                }`}>
                  <div className="flex items-start gap-3">
                    <svg className={`w-5 h-5 mt-0.5 ${
                      cancellation.variant === 'danger' ? 'text-red-600' :
                      cancellation.variant === 'warning' ? 'text-amber-600' : 'text-blue-600'
                    }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <div>
                      <p className={`font-medium ${
                        cancellation.variant === 'danger' ? 'text-red-800' :
                        cancellation.variant === 'warning' ? 'text-amber-800' : 'text-blue-800'
                      }`}>
                        Política de Cancelación
                      </p>
                      <p className={`text-sm mt-1 ${
                        cancellation.variant === 'danger' ? 'text-red-700' :
                        cancellation.variant === 'warning' ? 'text-amber-700' : 'text-blue-700'
                      }`}>
                        {cancellation.message}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button variant="secondary" className="flex-1" onClick={() => setShowCancelModal(false)}>
                    Volver
                  </Button>
                  {cancellation.canCancel && (
                    <Button 
                      variant="primary" 
                      className="flex-1 !bg-red-600 hover:!bg-red-700" 
                      onClick={handleCancelSimulation}
                    >
                      Confirmar Cancelación
                    </Button>
                  )}
                </div>
              </div>
            )
          })()}
        </Modal>
      )}
    </div>
  )
}
