import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, Badge, Button, Modal, ConfirmModal, ModalityFilter, ModalityBadge } from '../../../components/common'
import { useAuth } from '../../../contexts/AuthContext'
import { simulacrosService, recomendacionesService, solicitudesService } from '../../../services'

export default function SimulationsPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('proposals')
  const [showProposeModal, setShowProposeModal] = useState(false)
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [showRequestModal, setShowRequestModal] = useState(false)
  const [selectedSimulation, setSelectedSimulation] = useState(null)
  const [proposedDate, setProposedDate] = useState('')
  const [proposedTime, setProposedTime] = useState('')
  const [proposeReason, setProposeReason] = useState('')
  const [modalityFilter, setModalityFilter] = useState('all')
  const [requestData, setRequestData] = useState({
    solicitudId: '',
    fechaPreferida: '',
    horaPreferida: '',
    modalidad: 'virtual',
    observaciones: ''
  })
  const [solicitudesDisponibles, setSolicitudesDisponibles] = useState([])
  const [submitting, setSubmitting] = useState(false)

  // Data from API
  const [proposals, setProposals] = useState([])
  const [upcoming, setUpcoming] = useState([])
  const [completed, setCompleted] = useState([])
  const [disponibilidad, setDisponibilidad] = useState({ disponibles: 2, usados: 0 })

  useEffect(() => {
    fetchSimulacros()
  }, [])

  const fetchSimulacros = async () => {
    try {
      setLoading(true)
      const [simulacrosResponse, disponibilidadData] = await Promise.all([
        simulacrosService.getMisSimulacros(),
        simulacrosService.getDisponibilidad()
      ])

      // Handle both array and object with results
      const simulacrosData = Array.isArray(simulacrosResponse) 
        ? simulacrosResponse 
        : (simulacrosResponse?.results || [])

      // Separate by status
      // 'solicitado' y 'propuesto' van a proposals (pendientes de confirmación)
      const propuestos = simulacrosData.filter(s => 
        ['propuesto', 'solicitado', 'pendiente_respuesta'].includes(s.estado)
      )
      const confirmados = simulacrosData.filter(s => 
        ['confirmado', 'en_progreso'].includes(s.estado)
      )
      const completados = simulacrosData.filter(s => s.estado === 'completado')

      // Transform to component format
      setProposals(propuestos.map(s => ({
        id: s.id,
        date: s.fecha_propuesta,
        time: s.hora_propuesta,
        advisor: s.asesor_nombre || 'Asesor asignado',
        modality: s.modalidad || 'virtual',
        visaType: s.solicitud_tipo || 'Entrevista',
        status: 'pending',
        location: s.ubicacion
      })))

      setUpcoming(confirmados.map(s => {
        const fechaHora = new Date(`${s.fecha_propuesta}T${s.hora_propuesta}`)
        const horasRestantes = (fechaHora - new Date()) / (1000 * 60 * 60)
        return {
          id: s.id,
          date: s.fecha_propuesta,
          time: s.hora_propuesta,
          advisor: s.asesor_nombre || 'Asesor asignado',
          modality: s.modalidad || 'virtual',
          visaType: s.solicitud_tipo || 'Entrevista',
          status: 'confirmed',
          hoursUntil: Math.max(0, Math.round(horasRestantes)),
          location: s.ubicacion
        }
      }))

      setCompleted(completados.map(s => ({
        id: s.id,
        date: s.fecha_propuesta,
        time: s.hora_propuesta,
        advisor: s.asesor_nombre || 'Asesor asignado',
        modality: s.modalidad || 'virtual',
        visaType: s.solicitud_tipo || 'Entrevista',
        duration: s.duracion_minutos ? `${s.duracion_minutos} min` : '-',
        feedbackStatus: s.tiene_recomendaciones ? 'received' : 'pending'
      })))

      // Normalizar disponibilidad
      const disponibilidadNormalizada = {
        disponibles: disponibilidadData?.simulacros_disponibles ?? disponibilidadData?.disponibles ?? 2,
        usados: disponibilidadData?.simulacros_realizados ?? disponibilidadData?.usados ?? 0
      }
      setDisponibilidad(disponibilidadNormalizada)

    } catch (error) {
      console.error('Error fetching simulacros:', error)
    } finally {
      setLoading(false)
    }
  }

  const simulationsUsed = disponibilidad.usados
  const simulationsTotal = disponibilidad.usados + disponibilidad.disponibles

  // Filtrar por modalidad
  const filterByModality = (items) => {
    if (modalityFilter === 'all') return items
    return items.filter(item => item.modality === modalityFilter)
  }

  const filteredProposals = filterByModality(proposals)
  const filteredUpcoming = filterByModality(upcoming)
  const filteredCompleted = filterByModality(completed)

  // Handler para ir a la sala o a info presencial
  const handleGoToSimulation = (simulation) => {
    if (simulation.modality === 'presential') {
      navigate(`/simulacros/${simulation.id}/presencial`)
    } else {
      navigate(`/simulacros/${simulation.id}/room`)
    }
  }

  const handleAcceptSimulation = async (simulation) => {
    try {
      await simulacrosService.aceptarPropuesta(simulation.id)
      fetchSimulacros() // Refresh data
    } catch (error) {
      console.error('Error confirming simulation:', error)
    }
  }

  const handleProposeDate = async () => {
    try {
      await simulacrosService.proponerFechaAlternativa(selectedSimulation.id, {
        fecha: proposedDate,
        hora: proposedTime
      })
      setShowProposeModal(false)
      fetchSimulacros() // Refresh data
    } catch (error) {
      console.error('Error proposing new date:', error)
    }
  }

  const handleCancelSimulation = async () => {
    try {
      await simulacrosService.cancelar(selectedSimulation.id)
      setShowCancelModal(false)
      fetchSimulacros() // Refresh data
    } catch (error) {
      console.error('Error cancelling simulation:', error)
    }
  }

  // Handler para abrir modal de solicitar simulacro
  const handleOpenRequestModal = async () => {
    try {
      // Obtener solicitudes del cliente que puedan tener simulacro
      const response = await solicitudesService.getMisSolicitudes()
      const solicitudes = Array.isArray(response) ? response : (response?.results || [])
      
      // Filtrar solicitudes que pueden tener simulacro (estados del backend)
      const disponibles = solicitudes.filter(s => 
        ['pendiente', 'en_revision', 'aprobada', 'enviada_embajada', 'entrevista_agendada'].includes(s.estado)
      )
      
      setSolicitudesDisponibles(disponibles)
      setShowRequestModal(true)
    } catch (error) {
      console.error('Error loading solicitudes:', error)
    }
  }

  // Handler para solicitar simulacro
  const handleRequestSimulation = async () => {
    if (!requestData.solicitudId) {
      return
    }
    
    try {
      setSubmitting(true)
      await simulacrosService.solicitarSimulacro(requestData.solicitudId, {
        fecha_propuesta: requestData.fechaPreferida,
        hora_propuesta: requestData.horaPreferida,
        modalidad: requestData.modalidad,
        observaciones: requestData.observaciones
      })
      
      setShowRequestModal(false)
      setRequestData({
        solicitudId: '',
        fechaPreferida: '',
        horaPreferida: '',
        modalidad: 'virtual',
        observaciones: ''
      })
      
      fetchSimulacros() // Refresh data
    } catch (error) {
      console.error('Error requesting simulation:', error)
    } finally {
      setSubmitting(false)
    }
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
          <Button 
            disabled={simulationsUsed >= simulationsTotal}
            onClick={handleOpenRequestModal}
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Solicitar Simulacro
          </Button>
        </div>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b border-gray-200">
        {[
          { id: 'proposals', label: 'Propuestas Pendientes', count: filteredProposals.length },
          { id: 'upcoming', label: 'Próximos Simulacros', count: filteredUpcoming.length },
          { id: 'completed', label: 'Completados', count: filteredCompleted.length }
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

      {/* Modality Filter */}
      <div className="mb-6">
        <ModalityFilter value={modalityFilter} onChange={setModalityFilter} />
      </div>

      {/* Proposals Tab */}
      {activeTab === 'proposals' && (
        <div className="space-y-4">
          {filteredProposals.length === 0 ? (
            <Card className="text-center py-12">
              <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Sin propuestas pendientes</h3>
              <p className="text-gray-500">No tienes propuestas de simulacro por revisar</p>
            </Card>
          ) : (
            filteredProposals.map((proposal) => (
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
          {filteredUpcoming.length === 0 ? (
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
              
              {filteredUpcoming.map((simulation, index) => (
                <div key={simulation.id} className="relative flex gap-6 pb-8">
                  {/* Timeline dot */}
                  <div className={`relative z-10 w-14 h-14 rounded-xl flex items-center justify-center border-4 border-white ${
                    simulation.modality === 'presential' ? 'bg-amber-100' : 'bg-primary-100'
                  }`}>
                    {simulation.modality === 'presential' ? (
                      <span className="text-2xl">🏢</span>
                    ) : (
                      <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    )}
                  </div>

                  <Card className="flex-1">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold text-gray-900">
                            Simulacro {simulation.modality === 'presential' ? 'Presencial' : 'Virtual'}
                          </h3>
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
                        {/* Location for presential */}
                        {simulation.location && (
                          <div className="flex items-center gap-1 mt-2 text-sm text-amber-700 bg-amber-50 px-2 py-1 rounded-lg w-fit">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            {simulation.location}
                          </div>
                        )}
                        <div className="flex gap-2 mt-3">
                          <ModalityBadge modality={simulation.modality} />
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
                        <Button onClick={() => handleGoToSimulation(simulation)}>
                          {simulation.modality === 'presential' ? (
                            <>
                              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              Ver Información
                            </>
                          ) : (
                            <>
                              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                              </svg>
                              Ingresar a Reunión
                            </>
                          )}
                        </Button>
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
          {filteredCompleted.length === 0 ? (
            <Card className="text-center py-12">
              <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Sin simulacros completados</h3>
              <p className="text-gray-500">Aún no has completado ningún simulacro</p>
            </Card>
          ) : (
            filteredCompleted.map((simulation) => (
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
                      <div className="flex gap-2 mt-2">
                        <ModalityBadge modality={simulation.modality} />
                        <Badge variant="info">{simulation.visaType}</Badge>
                      </div>
                    </div>
                  </div>
                  <Link to={`/simulacros/${simulation.id}/resumen`}>
                    <Button variant="secondary">
                      Ver Resumen
                    </Button>
                  </Link>
                </div>
              </Card>
            ))
          )}
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

      {/* Request Simulation Modal */}
      <Modal
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        title="Solicitar Simulacro"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Solicita un simulacro de entrevista consular. Tu asesor recibirá la solicitud y te propondrá una fecha.
          </p>
          
          {/* Selección de solicitud */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Solicitud asociada <span className="text-red-500">*</span>
            </label>
            {solicitudesDisponibles.length > 0 ? (
              <select
                value={requestData.solicitudId}
                onChange={(e) => setRequestData({ ...requestData, solicitudId: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Selecciona una solicitud</option>
                {solicitudesDisponibles.map(sol => (
                  <option key={sol.id} value={sol.id}>
                    {sol.tipo_visa_display || sol.tipo_visa} - {sol.estado_display || sol.estado}
                  </option>
                ))}
              </select>
            ) : (
              <div className="p-4 bg-amber-50 text-amber-700 rounded-xl text-sm">
                No tienes solicitudes activas para solicitar un simulacro. Primero debes crear una solicitud de visa.
              </div>
            )}
          </div>

          {/* Modalidad */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Modalidad preferida</label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="modalidad"
                  value="virtual"
                  checked={requestData.modalidad === 'virtual'}
                  onChange={(e) => setRequestData({ ...requestData, modalidad: e.target.value })}
                  className="text-primary-600"
                />
                <span className="text-sm">🎥 Virtual</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="modalidad"
                  value="presential"
                  checked={requestData.modalidad === 'presential'}
                  onChange={(e) => setRequestData({ ...requestData, modalidad: e.target.value })}
                  className="text-primary-600"
                />
                <span className="text-sm">🏢 Presencial</span>
              </label>
            </div>
          </div>

          {/* Fecha y hora preferida (opcional) */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha preferida (opcional)
              </label>
              <input
                type="date"
                value={requestData.fechaPreferida}
                onChange={(e) => setRequestData({ ...requestData, fechaPreferida: e.target.value })}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hora preferida (opcional)
              </label>
              <input
                type="time"
                value={requestData.horaPreferida}
                onChange={(e) => setRequestData({ ...requestData, horaPreferida: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Observaciones */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Observaciones (opcional)
            </label>
            <textarea
              value={requestData.observaciones}
              onChange={(e) => setRequestData({ ...requestData, observaciones: e.target.value })}
              placeholder="Indica cualquier preferencia o información adicional..."
              rows={3}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 resize-none"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="secondary" className="flex-1" onClick={() => setShowRequestModal(false)}>
              Cancelar
            </Button>
            <Button 
              className="flex-1" 
              onClick={handleRequestSimulation}
              disabled={!requestData.solicitudId || submitting}
            >
              {submitting ? 'Enviando...' : 'Solicitar Simulacro'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
