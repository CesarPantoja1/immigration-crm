import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, Badge, Button, Modal } from '../../../components/common'
import { PhaseProgressBarCompact } from '../../../components/common'
import { solicitudesService } from '../../../services'

// Estados de solicitud con sus fases
const APPLICATION_STATES = {
  pendiente: { label: 'Pendiente de Revisión', variant: 'warning', phase: 'approval' },
  pending_review: { label: 'Pendiente de Revisión', variant: 'warning', phase: 'approval' },
  en_revision: { label: 'En Revisión', variant: 'info', phase: 'approval' },
  in_review: { label: 'En Revisión', variant: 'info', phase: 'approval' },
  aprobada: { label: 'Aprobada por Asesor', variant: 'success', phase: 'approval' },
  approved: { label: 'Aprobada por Asesor', variant: 'success', phase: 'approval' },
  enviada_embajada: { label: 'Enviada a Embajada', variant: 'info', phase: 'approval' },
  sent_to_embassy: { label: 'Enviada a Embajada', variant: 'info', phase: 'approval' },
  esperando_decision_embajada: { label: 'Esperando Decisión', variant: 'warning', phase: 'approval' },
  aprobada_embajada: { label: 'Aprobada por Embajada', variant: 'success', phase: 'scheduling' },
  rechazada_embajada: { label: 'Rechazada por Embajada', variant: 'danger', phase: 'approval' },
  embassy_approved: { label: 'Aprobada por Embajada', variant: 'success', phase: 'scheduling' },
  embassy_rejected: { label: 'Rechazada por Embajada', variant: 'danger', phase: 'approval' },
  entrevista_agendada: { label: 'Entrevista Agendada', variant: 'success', phase: 'preparation' },
  interview_scheduled: { label: 'Entrevista Agendada', variant: 'success', phase: 'preparation' },
  rechazada: { label: 'Rechazada', variant: 'danger', phase: 'approval' },
  rejected: { label: 'Rechazada', variant: 'danger', phase: 'approval' },
  completada: { label: 'Completada', variant: 'success', phase: 'completed' }
}

export default function AdvisorApplicationsListPage() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterPhase, setFilterPhase] = useState('all')
  const [showEmbassyModal, setShowEmbassyModal] = useState(false)
  const [selectedApplication, setSelectedApplication] = useState(null)
  const [showDecisionModal, setShowDecisionModal] = useState(false)
  const [embassyDecision, setEmbassyDecision] = useState('aprobada')
  const [rejectionReason, setRejectionReason] = useState('')
  const [actionLoading, setActionLoading] = useState(false)
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    pendientes: 0,
    enEmbajada: 0,
    aprobadas: 0,
    total: 0
  })

  // Función para cargar/refrescar las solicitudes
  const fetchApplications = async () => {
    try {
      setLoading(true)
      const response = await solicitudesService.getSolicitudesAsignadas()
      const data = Array.isArray(response) ? response : (response?.results || [])
      
      // Transform API data to component format
      const transformedApps = data.map(app => {
        const docs = app.documentos_adjuntos || []
        const docsAprobados = docs.filter(d => d.estado === 'aprobado').length
        
        return {
          id: `SOL-${app.id}`,
          originalId: app.id,
          client: {
            name: app.cliente_nombre || 'Cliente',
            email: app.cliente_email || '',
            phone: app.cliente_telefono || ''
          },
          visaType: app.tipo_visa,
          visaTypeName: app.tipo_visa_display || app.tipo_visa,
          embassy: app.embajada_display || app.embajada,
          embajadaCode: app.embajada,
          status: app.estado,
          submittedAt: app.created_at?.split('T')[0] || '',
          documentsCount: docs.length,
          documentsApproved: docsAprobados,
          priority: app.prioridad || 'medium',
          currentPhase: APPLICATION_STATES[app.estado]?.phase || 'approval',
          motivoRechazoEmbajada: app.motivo_rechazo_embajada || ''
        }
      })
      
      setApplications(transformedApps)
      
      // Calculate stats
      setStats({
        pendientes: transformedApps.filter(a => ['pendiente', 'pending_review'].includes(a.status)).length,
        enEmbajada: transformedApps.filter(a => ['enviada_embajada', 'esperando_decision_embajada', 'sent_to_embassy'].includes(a.status)).length,
        aprobadas: transformedApps.filter(a => ['aprobada', 'approved', 'aprobada_embajada', 'embassy_approved', 'entrevista_agendada', 'interview_scheduled'].includes(a.status)).length,
        total: transformedApps.length
      })
    } catch (error) {
      console.error('Error fetching applications:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchApplications()
  }, [])

  const filteredApplications = applications.filter(app => {
    const matchesSearch = 
      app.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.client.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || app.status === filterStatus
    const matchesPhase = filterPhase === 'all' || app.currentPhase === filterPhase
    return matchesSearch && matchesStatus && matchesPhase
  })

  const getVisaTypeIcon = (type) => {
    const icons = {
      // Solo 3 tipos de visa: vivienda, trabajo, estudio
      vivienda: { bg: 'bg-purple-100', text: 'text-purple-600', icon: '🏠' },
      trabajo: { bg: 'bg-green-100', text: 'text-green-600', icon: '💼' },
      estudio: { bg: 'bg-blue-100', text: 'text-blue-600', icon: '🎓' }
    }
    return icons[type] || { bg: 'bg-gray-100', text: 'text-gray-600', icon: '📄' }
  }

  const getPriorityBadge = (priority) => {
    const styles = {
      high: 'bg-red-100 text-red-700',
      medium: 'bg-amber-100 text-amber-700',
      low: 'bg-gray-100 text-gray-600'
    }
    const labels = { high: 'Alta', medium: 'Media', low: 'Baja' }
    return (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${styles[priority]}`}>
        {labels[priority]}
      </span>
    )
  }

  const handleSendToEmbassy = (app) => {
    setSelectedApplication(app)
    setShowEmbassyModal(true)
  }

  const handleScheduleInterview = (app) => {
    // Redirigir a la página de agendamiento de entrevistas con el ID de la solicitud
    navigate(`/asesor/entrevistas?solicitud=${app.originalId}`)
  }

  const handleRecordDecision = (app) => {
    setSelectedApplication(app)
    setEmbassyDecision('aprobada')
    setRejectionReason('')
    setShowDecisionModal(true)
  }

  // Enviar solicitud a embajada - IMPLEMENTACIÓN COMPLETA
  const confirmSendToEmbassy = async () => {
    if (!selectedApplication) return
    
    try {
      setActionLoading(true)
      await solicitudesService.enviarAEmbajada(selectedApplication.originalId)
      setShowEmbassyModal(false)
      setSelectedApplication(null)
      // Refrescar la lista de solicitudes
      await fetchApplications()
    } catch (error) {
      console.error('Error enviando a embajada:', error)
      alert('Error al enviar la solicitud a la embajada. Intente nuevamente.')
    } finally {
      setActionLoading(false)
    }
  }

  // Registrar decisión de embajada - IMPLEMENTACIÓN COMPLETA
  const confirmEmbassyDecision = async () => {
    if (!selectedApplication) return
    
    if (embassyDecision === 'rechazada' && !rejectionReason.trim()) {
      alert('Debe proporcionar un motivo de rechazo')
      return
    }
    
    try {
      setActionLoading(true)
      await solicitudesService.registrarDecisionEmbajada(
        selectedApplication.originalId,
        embassyDecision,
        rejectionReason
      )
      
      const solicitudId = selectedApplication.originalId
      setShowDecisionModal(false)
      setSelectedApplication(null)
      setRejectionReason('')
      
      // Si fue aprobada, redirigir a agendamiento de entrevista
      if (embassyDecision === 'aprobada') {
        // Breve delay para que el usuario vea el cambio
        setTimeout(() => {
          navigate(`/asesor/entrevistas?solicitud=${solicitudId}`)
        }, 500)
      } else {
        // Si fue rechazada, solo refrescar la lista
        await fetchApplications()
      }
    } catch (error) {
      console.error('Error registrando decisión:', error)
      alert('Error al registrar la decisión de la embajada. Intente nuevamente.')
    } finally {
      setActionLoading(false)
    }
  }

  const getActionButton = (app) => {
    switch (app.status) {
      case 'pendiente':
      case 'pending_review':
      case 'en_revision':
      case 'in_review':
        return (
          <Link to={`/asesor/solicitudes/${app.originalId}`}>
            <Button size="sm">
              <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              Realizar Revisión
            </Button>
          </Link>
        )
      case 'aprobada':
      case 'approved':
        return (
          <Button size="sm" onClick={() => handleSendToEmbassy(app)}>
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            Enviar a Embajada
          </Button>
        )
      case 'enviada_embajada':
      case 'sent_to_embassy':
      case 'esperando_decision_embajada':
        return (
          <Button size="sm" variant="warning" onClick={() => handleRecordDecision(app)}>
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Registrar Decisión
          </Button>
        )
      case 'aprobada_embajada':
      case 'embassy_approved':
        return (
          <Button size="sm" onClick={() => handleScheduleInterview(app)}>
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Agendar Entrevista
          </Button>
        )
      case 'rechazada_embajada':
      case 'embassy_rejected':
        return (
          <div className="flex flex-col items-end gap-1">
            <Badge variant="danger">Rechazada</Badge>
            {app.motivoRechazoEmbajada && (
              <span className="text-xs text-red-600 max-w-[200px] truncate" title={app.motivoRechazoEmbajada}>
                {app.motivoRechazoEmbajada}
              </span>
            )}
          </div>
        )
      case 'entrevista_agendada':
      case 'interview_scheduled':
        return (
          <Link to={`/asesor/solicitudes/${app.originalId}`}>
            <Button size="sm" variant="secondary">
              <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Ver Detalles
            </Button>
          </Link>
        )
      default:
        return (
          <Link to={`/asesor/solicitudes/${app.originalId}`}>
            <Button size="sm" variant="secondary">Ver Detalles</Button>
          </Link>
        )
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Solicitudes Asignadas</h1>
        <p className="text-gray-500 mt-1">Revisa y gestiona las solicitudes de tus clientes</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card className="bg-amber-50 border-amber-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <div className="text-2xl font-bold text-amber-700">
                {stats.pendientes}
              </div>
              <div className="text-sm text-amber-600">Pendientes</div>
            </div>
          </div>
        </Card>
        <Card className="bg-blue-50 border-blue-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-700">
                {stats.enEmbajada}
              </div>
              <div className="text-sm text-blue-600">En Embajada</div>
            </div>
          </div>
        </Card>
        <Card className="bg-green-50 border-green-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-700">
                {stats.aprobadas}
              </div>
              <div className="text-sm text-green-600">Aprobadas</div>
            </div>
          </div>
        </Card>
        <Card className="bg-purple-50 border-purple-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-700">
                {stats.total}
              </div>
              <div className="text-sm text-purple-600">Total Asignadas</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Buscar por ID o nombre del cliente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <select
              value={filterPhase}
              onChange={(e) => setFilterPhase(e.target.value)}
              className="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 bg-white"
            >
              <option value="all">Todas las fases</option>
              <option value="approval">📋 Fase: Aprobación</option>
              <option value="scheduling">📅 Fase: Agendamiento</option>
              <option value="preparation">🎯 Fase: Preparación</option>
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 bg-white"
            >
              <option value="all">Todos los estados</option>
              <option value="pendiente">Pendiente de Revisión</option>
              <option value="en_revision">En Revisión</option>
              <option value="aprobada">Aprobada por Asesor</option>
              <option value="enviada_embajada">Enviada a Embajada</option>
              <option value="esperando_decision_embajada">Esperando Decisión</option>
              <option value="aprobada_embajada">Aprobada por Embajada</option>
              <option value="rechazada_embajada">Rechazada por Embajada</option>
              <option value="entrevista_agendada">Entrevista Agendada</option>
              <option value="completada">Completada</option>
              <option value="rechazada">Rechazada</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Applications List */}
      <div className="space-y-6">
        {loading ? (
          <Card className="text-center py-12">
            <div className="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-500">Cargando solicitudes...</p>
          </Card>
        ) : filteredApplications.length === 0 ? (
          <Card className="text-center py-12">
            <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay solicitudes</h3>
            <p className="text-gray-500">No tienes solicitudes que coincidan con los filtros</p>
          </Card>
        ) : (
          filteredApplications.map((app) => {
            const visaIcon = getVisaTypeIcon(app.visaType)
            const stateInfo = APPLICATION_STATES[app.status] || APPLICATION_STATES.pending_review
            
            return (
              <Card key={app.id} hover className="overflow-hidden">
                {/* Phase indicator bar */}
                <div className={`h-1 -mx-6 -mt-6 mb-4 ${
                  app.currentPhase === 'approval' ? 'bg-blue-500' :
                  app.currentPhase === 'scheduling' ? 'bg-amber-500' :
                  'bg-green-500'
                }`} />
                
                <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                  {/* Icon & Client Info */}
                  <div className="flex items-center gap-4 flex-1">
                    <div className={`w-12 h-12 ${visaIcon.bg} rounded-xl flex items-center justify-center text-2xl`}>
                      {visaIcon.icon}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 flex-wrap">
                        <h3 className="font-semibold text-gray-900">{app.id}</h3>
                        <Badge variant={stateInfo.variant} dot>
                          {stateInfo.label}
                        </Badge>
                        {getPriorityBadge(app.priority)}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        <span className="font-medium">{app.client.name}</span>
                        <span className="text-gray-400 mx-2">•</span>
                        {app.visaTypeName}
                        <span className="text-gray-400 mx-2">•</span>
                        {app.embassy}
                      </p>
                    </div>
                  </div>

                  {/* Documents Progress */}
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <div className="text-sm text-gray-500 mb-1">Documentos</div>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all ${
                              app.documentsCount === 0 ? 'bg-gray-300' :
                              app.documentsApproved === app.documentsCount ? 'bg-green-500' :
                              app.documentsApproved > 0 ? 'bg-yellow-500' : 'bg-gray-300'
                            }`}
                            style={{ width: app.documentsCount > 0 ? `${(app.documentsApproved / app.documentsCount) * 100}%` : '0%' }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-700">
                          {app.documentsApproved}/{app.documentsCount}
                        </span>
                      </div>
                    </div>

                    {/* Interview Date if scheduled */}
                    {app.interviewDate && (
                      <div className="text-center">
                        <div className="text-sm text-gray-500 mb-1">Entrevista</div>
                        <div className="text-sm font-medium text-green-600">
                          {new Date(app.interviewDate).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}
                        </div>
                      </div>
                    )}

                    {/* Action Button */}
                    {getActionButton(app)}
                  </div>
                </div>
              </Card>
            )
          })
        )}
      </div>

      {/* Modal: Enviar a Embajada */}
      <Modal
        isOpen={showEmbassyModal}
        onClose={() => setShowEmbassyModal(false)}
        title="Enviar Solicitud a Embajada"
      >
        {selectedApplication && (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h4 className="font-medium text-blue-900">Confirmación de envío</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Estás a punto de enviar la solicitud <strong>{selectedApplication.id}</strong> de{' '}
                    <strong>{selectedApplication.client.name}</strong> a la embajada de{' '}
                    <strong>{selectedApplication.embassy}</strong>.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-xl p-4">
              <h4 className="font-medium text-gray-900 mb-2">Documentos incluidos:</h4>
              <ul className="space-y-1">
                <li className="flex items-center gap-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Pasaporte vigente
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Fotografía 2x2
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Certificado de Antecedentes
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Documentos adicionales según tipo de visa
                </li>
              </ul>
            </div>

            <div className="flex gap-3 pt-2">
              <Button variant="secondary" onClick={() => setShowEmbassyModal(false)} className="flex-1" disabled={actionLoading}>
                Cancelar
              </Button>
              <Button onClick={confirmSendToEmbassy} className="flex-1" disabled={actionLoading}>
                {actionLoading ? (
                  <>
                    <svg className="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Enviando...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    Confirmar Envío
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Modal: Registrar Decisión de Embajada */}
      <Modal
        isOpen={showDecisionModal}
        onClose={() => setShowDecisionModal(false)}
        title="Registrar Decisión de Embajada"
      >
        {selectedApplication && (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div>
                  <h4 className="font-medium text-blue-900">Decisión de la Embajada</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Registra la respuesta de la embajada de <strong>{selectedApplication.embassy}</strong> para la solicitud <strong>{selectedApplication.id}</strong> de <strong>{selectedApplication.client.name}</strong>.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Decisión de la Embajada
              </label>
              <div className="space-y-2">
                <label className={`flex items-center gap-3 p-4 border rounded-xl cursor-pointer transition-all ${
                  embassyDecision === 'aprobada' 
                    ? 'border-green-500 bg-green-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}>
                  <input
                    type="radio"
                    name="embassyDecision"
                    value="aprobada"
                    checked={embassyDecision === 'aprobada'}
                    onChange={(e) => setEmbassyDecision(e.target.value)}
                    className="text-green-600"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="font-medium text-gray-900">Aprobada</span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">La embajada ha aprobado la solicitud. Se podrá agendar entrevista.</p>
                  </div>
                </label>

                <label className={`flex items-center gap-3 p-4 border rounded-xl cursor-pointer transition-all ${
                  embassyDecision === 'rechazada' 
                    ? 'border-red-500 bg-red-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}>
                  <input
                    type="radio"
                    name="embassyDecision"
                    value="rechazada"
                    checked={embassyDecision === 'rechazada'}
                    onChange={(e) => setEmbassyDecision(e.target.value)}
                    className="text-red-600"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="font-medium text-gray-900">Rechazada</span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">La embajada ha rechazado la solicitud. Se notificará al cliente.</p>
                  </div>
                </label>
              </div>
            </div>

            {embassyDecision === 'rechazada' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Motivo del Rechazo <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  rows={3}
                  placeholder="Ingrese el motivo del rechazo proporcionado por la embajada..."
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                />
              </div>
            )}

            <div className="flex gap-3 pt-2">
              <Button variant="secondary" onClick={() => setShowDecisionModal(false)} className="flex-1" disabled={actionLoading}>
                Cancelar
              </Button>
              <Button 
                onClick={confirmEmbassyDecision} 
                className="flex-1"
                variant={embassyDecision === 'rechazada' ? 'danger' : 'primary'}
                disabled={actionLoading || (embassyDecision === 'rechazada' && !rejectionReason.trim())}
              >
                {actionLoading ? (
                  <>
                    <svg className="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Registrando...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Confirmar Decisión
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
