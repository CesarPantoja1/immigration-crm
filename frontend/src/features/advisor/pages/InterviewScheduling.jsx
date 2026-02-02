import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Card, Button, Badge } from '../../../components/common'
import { entrevistasService } from '../../../services/entrevistasService'
import { solicitudesService } from '../../../services/solicitudesService'

export default function InterviewScheduling() {
  const [searchParams] = useSearchParams()
  const solicitudIdFromUrl = searchParams.get('solicitud')
  
  const [solicitudes, setSolicitudes] = useState([])
  const [entrevistas, setEntrevistas] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState('pendientes') // 'pendientes' | 'agendadas'
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [selectedSolicitud, setSelectedSolicitud] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [scheduleForm, setScheduleForm] = useState({
    fecha: '',
    hora: '',
    ubicacion: '',
    ubicacionSeleccionada: '', // Para el dropdown
    ubicacionPersonalizada: '', // Para el campo de texto cuando selecciona "Otros"
    modoAsignacion: 'fecha_fija', // 'fecha_fija' | 'opciones'
    // Campos adicionales para mejor experiencia
    notas: '',
    duracionEstimada: '30',
    recordatorioEmail: true,
    recordatorioSMS: false
  })
  const [opciones, setOpciones] = useState([
    { id: 'opt1', fecha: '', hora: '' }
  ])

  useEffect(() => {
    fetchData()
  }, [solicitudIdFromUrl])

  const fetchData = async () => {
    try {
      setLoading(true)
      
      // Optimización: Pedir al backend solo solicitudes aprobadas por embajada
      const [solicitudesResponse, entrevistasResponse] = await Promise.all([
        solicitudesService.getSolicitudesAsignadas({ estado: 'aprobada_embajada' }).catch(() => []),
        entrevistasService.getEntrevistasAsesor().catch(() => [])
      ])

      // Handle both array and object with results
      const solicitudesData = Array.isArray(solicitudesResponse) 
        ? solicitudesResponse 
        : (solicitudesResponse?.results || [])
      
      const entrevistasData = Array.isArray(entrevistasResponse)
        ? entrevistasResponse
        : (entrevistasResponse?.results || [])

      // Transform solicitudes - SOLO las aprobadas por la embajada (listas para agendar entrevista)
      // CRÍTICO: El flujo correcto es Asesor aprueba -> Envía a embajada -> Embajada aprueba -> ENTONCES se puede agendar
      const solList = solicitudesData
        .filter(s => s.estado === 'aprobada_embajada')
        .map(s => ({
          id: s.id || s.numero,
          cliente: s.cliente_nombre || s.cliente?.nombre || 'Cliente',
          clienteEmail: s.cliente_email || s.cliente?.email || '',
          clienteTelefono: s.cliente_telefono || s.cliente?.telefono || '',
          tipoVisa: s.tipo_visa_display || s.tipo_visa || 'Visa',
          embajada: s.embajada_display || s.embajada || 'Embajada',
          embajadaCode: s.embajada,
          estado: s.estado || 'aprobada_embajada',
          fechaSolicitud: s.fecha_creacion || s.created_at || '',
          prioridad: s.prioridad || 'media'
        }))

      // Transform entrevistas
      const entList = entrevistasData.map(e => ({
        id: e.id,
        codigo: e.codigo || `INT-${e.id}`,
        solicitudId: e.solicitud_id || e.solicitud,
        cliente: e.cliente_nombre || e.cliente?.nombre || 'Cliente',
        embajada: e.embajada_nombre || e.embajada || 'Embajada',
        estado: e.estado || 'AGENDADA',
        fecha: e.fecha,
        hora: e.hora,
        ubicacion: e.ubicacion || 'Por confirmar',
        vecesReprogramada: e.veces_reprogramada || 0
      }))

      setSolicitudes(solList)
      setEntrevistas(entList)
      
      // Si viene un ID de solicitud en la URL, abrir el modal automáticamente
      if (solicitudIdFromUrl) {
        const solicitudParaAgendar = solList.find(s => String(s.id) === String(solicitudIdFromUrl))
        if (solicitudParaAgendar) {
          setSelectedSolicitud(solicitudParaAgendar)
          setShowScheduleModal(true)
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Ubicaciones predefinidas por embajada
  const ubicacionesPorEmbajada = {
    'Estados Unidos': [
      'Embajada de EE.UU. - Ciudad de México',
      'Consulado de EE.UU. - Guadalajara',
      'Consulado de EE.UU. - Monterrey',
      'Consulado de EE.UU. - Tijuana',
      'Consulado de EE.UU. - Ciudad Juárez'
    ],
    'Canadá': [
      'Embajada de Canadá - Ciudad de México',
      'Consulado de Canadá - Guadalajara',
      'Consulado de Canadá - Monterrey'
    ],
    'España': [
      'Embajada de España - Ciudad de México',
      'Consulado de España - Guadalajara',
      'Consulado de España - Monterrey'
    ]
  }

  const getEstadoBadge = (estado) => {
    const badges = {
      'APROBADA_SIN_ENTREVISTA': { variant: 'warning', text: 'Pendiente de Agendar' },
      'AGENDADA': { variant: 'info', text: 'Agendada' },
      'CONFIRMADA': { variant: 'success', text: 'Confirmada' },
      'REPROGRAMADA': { variant: 'warning', text: 'Reprogramada' },
      'CANCELADA': { variant: 'danger', text: 'Cancelada' },
      'COMPLETADA': { variant: 'default', text: 'Completada' }
    }
    return badges[estado] || { variant: 'default', text: estado }
  }

  const getPrioridadColor = (prioridad) => {
    const colors = {
      'alta': 'text-red-600 bg-red-50',
      'media': 'text-amber-600 bg-amber-50',
      'baja': 'text-green-600 bg-green-50'
    }
    return colors[prioridad] || 'text-gray-600 bg-gray-50'
  }

  const handleScheduleInterview = (solicitud) => {
    setSelectedSolicitud(solicitud)
    // Resetear el formulario con valores por defecto
    setScheduleForm({
      fecha: '',
      hora: '',
      ubicacion: '',
      ubicacionSeleccionada: '',
      ubicacionPersonalizada: '',
      modoAsignacion: 'fecha_fija',
      notas: '',
      duracionEstimada: '30',
      recordatorioEmail: true,
      recordatorioSMS: false
    })
    setShowScheduleModal(true)
  }

  const handleSubmitSchedule = async (e) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      // Determinar la ubicación final
      const ubicacionFinal = scheduleForm.ubicacionSeleccionada === 'otros'
        ? scheduleForm.ubicacionPersonalizada
        : scheduleForm.ubicacionSeleccionada

      // Usar el servicio de entrevistas para agendar
      // Pasar solicitudId como primer parámetro y los datos como segundo parámetro
      const response = await entrevistasService.agendarEntrevista(
        selectedSolicitud.id,
        {
          fecha: scheduleForm.fecha,
          hora: scheduleForm.hora,
          ubicacion: ubicacionFinal,
          notas: scheduleForm.notas,
          duracion_estimada: parseInt(scheduleForm.duracionEstimada),
          recordatorio_email: scheduleForm.recordatorioEmail,
          recordatorio_sms: scheduleForm.recordatorioSMS
        }
      )

      if (response && (response.entrevista?.id || response.id || response.success)) {
        // Mostrar mensaje de éxito
        alert(`¡Entrevista agendada exitosamente!\n\nCliente: ${selectedSolicitud.cliente}\nFecha: ${scheduleForm.fecha}\nHora: ${scheduleForm.hora}\nUbicación: ${ubicacionFinal}\n\nSe ha enviado una notificación al cliente.`)
        
        setShowScheduleModal(false)
        // Resetear formulario
        setScheduleForm({
          fecha: '',
          hora: '',
          ubicacion: '',
          ubicacionSeleccionada: '',
          ubicacionPersonalizada: '',
          modoAsignacion: 'fecha_fija',
          notas: '',
          duracionEstimada: '30',
          recordatorioEmail: true,
          recordatorioSMS: false
        })
        // Recargar datos
        fetchData()
      } else {
        throw new Error(response?.error || 'Error desconocido')
      }
    } catch (error) {
      console.error('Error completo:', error)
      const errorMsg = error.response?.data?.error || error.message || 'Error al agendar la entrevista'
      alert('Error: ' + errorMsg)
    } finally {
      setSubmitting(false)
    }
  }

  const addOpcion = () => {
    setOpciones([...opciones, { id: `opt${opciones.length + 1}`, fecha: '', hora: '' }])
  }

  const removeOpcion = (index) => {
    setOpciones(opciones.filter((_, i) => i !== index))
  }

  const updateOpcion = (index, field, value) => {
    const newOpciones = [...opciones]
    newOpciones[index][field] = value
    setOpciones(newOpciones)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agendamiento de Entrevistas</h1>
          <p className="text-gray-600 mt-1">Gestiona las entrevistas consulares de tus clientes</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-amber-50 border-amber-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center text-2xl">
              ⏳
            </div>
            <div>
              <div className="text-2xl font-bold text-amber-900">{solicitudes.length}</div>
              <div className="text-sm text-amber-700">Pendientes de Agendar</div>
            </div>
          </div>
        </Card>

        <Card className="bg-blue-50 border-blue-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-2xl">
              📅
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-900">
                {entrevistas.filter(e => e.estado === 'AGENDADA').length}
              </div>
              <div className="text-sm text-blue-700">Agendadas</div>
            </div>
          </div>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-2xl">
              ✓
            </div>
            <div>
              <div className="text-2xl font-bold text-green-900">
                {entrevistas.filter(e => e.estado === 'CONFIRMADA').length}
              </div>
              <div className="text-sm text-green-700">Confirmadas</div>
            </div>
          </div>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-2xl">
              📊
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-900">{entrevistas.length}</div>
              <div className="text-sm text-purple-700">Total Este Mes</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setSelectedTab('pendientes')}
          className={`px-4 py-2 font-medium transition-colors ${
            selectedTab === 'pendientes'
              ? 'text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Solicitudes Pendientes ({solicitudes.length})
        </button>
        <button
          onClick={() => setSelectedTab('agendadas')}
          className={`px-4 py-2 font-medium transition-colors ${
            selectedTab === 'agendadas'
              ? 'text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Entrevistas Agendadas ({entrevistas.length})
        </button>
      </div>

      {/* Content */}
      {selectedTab === 'pendientes' && (
        <Card>
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Solicitudes Aprobadas por la Embajada - Pendientes de Agendar Entrevista
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Solo se muestran solicitudes que ya fueron aprobadas por la embajada y están listas para agendar entrevista
            </p>
          </div>
          
          {solicitudes.length === 0 ? (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No hay solicitudes listas para agendar entrevista
              </h3>
              <p className="text-gray-500 max-w-md mx-auto">
                Las solicitudes aparecerán aquí una vez que la embajada las haya aprobado. 
                Recuerda que primero debes enviar las solicitudes a la embajada y esperar su decisión.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Solicitud</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Cliente</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tipo de Visa</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Embajada</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Prioridad</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Fecha Solicitud</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {solicitudes.map((solicitud) => (
                  <tr key={solicitud.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <span className="font-medium text-gray-900">{solicitud.id}</span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-semibold text-sm">
                          {solicitud.cliente.charAt(0)}
                        </div>
                        <span className="text-gray-700">{solicitud.cliente}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-600 text-sm">{solicitud.tipoVisa}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-600 text-sm">{solicitud.embajada}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPrioridadColor(solicitud.prioridad)}`}>
                        {solicitud.prioridad.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-600 text-sm">{solicitud.fechaSolicitud}</span>
                    </td>
                    <td className="py-3 px-4">
                      <Button
                        size="sm"
                        onClick={() => handleScheduleInterview(solicitud)}
                      >
                        Agendar Entrevista
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          )}
        </Card>
      )}

      {selectedTab === 'agendadas' && (
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Entrevistas Agendadas
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Código</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Cliente</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Embajada</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Fecha y Hora</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Ubicación</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Estado</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {entrevistas.map((entrevista) => (
                  <tr key={entrevista.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <span className="font-medium text-gray-900">{entrevista.codigo}</span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-semibold text-sm">
                          {entrevista.cliente.charAt(0)}
                        </div>
                        <span className="text-gray-700">{entrevista.cliente}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-600 text-sm">{entrevista.embajada}</span>
                    </td>
                    <td className="py-3 px-4">
                      <div>
                        <div className="font-medium text-gray-900">{entrevista.fecha}</div>
                        <div className="text-sm text-gray-500">{entrevista.hora}</div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-600 text-sm">{entrevista.ubicacion}</span>
                    </td>
                    <td className="py-3 px-4">
                      <Badge
                        variant={getEstadoBadge(entrevista.estado).variant}
                        size="sm"
                      >
                        {getEstadoBadge(entrevista.estado).text}
                      </Badge>
                      {entrevista.vecesReprogramada > 0 && (
                        <div className="text-xs text-amber-600 mt-1">
                          Reprogramada {entrevista.vecesReprogramada}x
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        <Button variant="secondary" size="sm">Ver Detalles</Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Modal para Agendar Entrevista - MEJORADO */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header con info del cliente */}
            <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-primary-50 to-blue-50">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">📅 Agendar Entrevista Consular</h2>
                  <div className="mt-3 space-y-1">
                    <p className="text-gray-700">
                      <span className="font-medium">Solicitud:</span> #{selectedSolicitud?.id}
                    </p>
                    <p className="text-gray-700">
                      <span className="font-medium">Cliente:</span> {selectedSolicitud?.cliente}
                    </p>
                    <p className="text-gray-700">
                      <span className="font-medium">Tipo de Visa:</span> {selectedSolicitud?.tipoVisa}
                    </p>
                    <p className="text-gray-700">
                      <span className="font-medium">Embajada:</span> {selectedSolicitud?.embajada}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setShowScheduleModal(false)}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmitSchedule} className="p-6 space-y-6">
              {/* Información importante */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-sm text-blue-700">
                    <p className="font-medium">Información importante</p>
                    <p className="mt-1">Al confirmar la entrevista, se enviará automáticamente una notificación al cliente con todos los detalles de la cita.</p>
                  </div>
                </div>
              </div>

              {/* Sección: Fecha y Hora */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-sm font-bold">1</span>
                  Fecha y Hora de la Entrevista
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha *
                    </label>
                    <input
                      type="date"
                      required
                      min={new Date().toISOString().split('T')[0]}
                      value={scheduleForm.fecha}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, fecha: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Hora *
                    </label>
                    <select
                      required
                      value={scheduleForm.hora}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, hora: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      <option value="">Seleccionar hora</option>
                      <option value="08:00">08:00 AM</option>
                      <option value="08:30">08:30 AM</option>
                      <option value="09:00">09:00 AM</option>
                      <option value="09:30">09:30 AM</option>
                      <option value="10:00">10:00 AM</option>
                      <option value="10:30">10:30 AM</option>
                      <option value="11:00">11:00 AM</option>
                      <option value="11:30">11:30 AM</option>
                      <option value="12:00">12:00 PM</option>
                      <option value="14:00">02:00 PM</option>
                      <option value="14:30">02:30 PM</option>
                      <option value="15:00">03:00 PM</option>
                      <option value="15:30">03:30 PM</option>
                      <option value="16:00">04:00 PM</option>
                      <option value="16:30">04:30 PM</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Duración Estimada
                    </label>
                    <select
                      value={scheduleForm.duracionEstimada}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, duracionEstimada: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      <option value="15">15 minutos</option>
                      <option value="30">30 minutos</option>
                      <option value="45">45 minutos</option>
                      <option value="60">1 hora</option>
                      <option value="90">1 hora 30 min</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Sección: Ubicación */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-sm font-bold">2</span>
                  Ubicación
                </h3>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sede de la Entrevista *
                  </label>
                  <select
                    required
                    value={scheduleForm.ubicacionSeleccionada}
                    onChange={(e) => setScheduleForm({
                      ...scheduleForm,
                      ubicacionSeleccionada: e.target.value,
                      ubicacionPersonalizada: ''
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">Selecciona una ubicación</option>
                    {(ubicacionesPorEmbajada[selectedSolicitud?.embajada] || ubicacionesPorEmbajada['Estados Unidos'] || []).map((ubicacion, idx) => (
                      <option key={idx} value={ubicacion}>
                        {ubicacion}
                      </option>
                    ))}
                    <option value="otros">📍 Otra ubicación (especificar)</option>
                  </select>

                  {scheduleForm.ubicacionSeleccionada === 'otros' && (
                    <div className="mt-3">
                      <input
                        type="text"
                        required
                        placeholder="Ingresa la dirección completa de la sede"
                        value={scheduleForm.ubicacionPersonalizada}
                        onChange={(e) => setScheduleForm({
                          ...scheduleForm,
                          ubicacionPersonalizada: e.target.value
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Sección: Notas y Recordatorios */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-sm font-bold">3</span>
                  Detalles Adicionales
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notas para el Cliente (opcional)
                    </label>
                    <textarea
                      rows={3}
                      placeholder="Ej: Llevar pasaporte original, fotografías tamaño pasaporte, comprobante de pago de la visa..."
                      value={scheduleForm.notas}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, notas: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Recordatorios Automáticos
                    </label>
                    <div className="flex flex-wrap gap-4">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={scheduleForm.recordatorioEmail}
                          onChange={(e) => setScheduleForm({ ...scheduleForm, recordatorioEmail: e.target.checked })}
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        />
                        <span className="text-sm text-gray-700">📧 Enviar recordatorio por email (24h antes)</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={scheduleForm.recordatorioSMS}
                          onChange={(e) => setScheduleForm({ ...scheduleForm, recordatorioSMS: e.target.checked })}
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        />
                        <span className="text-sm text-gray-700">📱 Enviar recordatorio por SMS (2h antes)</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              {/* Resumen antes de confirmar */}
              {scheduleForm.fecha && scheduleForm.hora && scheduleForm.ubicacionSeleccionada && (
                <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                  <h4 className="font-medium text-green-900 mb-2">✓ Resumen de la Entrevista</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm text-green-800">
                    <p><span className="font-medium">Fecha:</span> {new Date(scheduleForm.fecha + 'T12:00:00').toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}</p>
                    <p><span className="font-medium">Hora:</span> {scheduleForm.hora}</p>
                    <p className="col-span-2"><span className="font-medium">Ubicación:</span> {scheduleForm.ubicacionSeleccionada === 'otros' ? scheduleForm.ubicacionPersonalizada : scheduleForm.ubicacionSeleccionada}</p>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowScheduleModal(false)}
                  className="flex-1"
                  disabled={submitting}
                >
                  Cancelar
                </Button>
                <Button 
                  type="submit" 
                  className="flex-1"
                  disabled={submitting || !scheduleForm.fecha || !scheduleForm.hora || !scheduleForm.ubicacionSeleccionada}
                >
                  {submitting ? (
                    <>
                      <svg className="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Agendando...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      Confirmar y Agendar
                    </>
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
