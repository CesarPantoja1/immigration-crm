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
  const [dateError, setDateError] = useState('')
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [successData, setSuccessData] = useState(null)
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
    setDateError('') // Resetear error de fecha
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
        // Mostrar modal de éxito con los datos de la entrevista
        setSuccessData({
          cliente: selectedSolicitud.cliente,
          fecha: scheduleForm.fecha,
          hora: scheduleForm.hora,
          ubicacion: ubicacionFinal,
          clienteEmail: selectedSolicitud.clienteEmail,
          clienteTelefono: selectedSolicitud.clienteTelefono,
          tipoVisa: selectedSolicitud.tipoVisa,
          embajada: selectedSolicitud.embajada
        })
        setShowSuccessModal(true)
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
                  <div className="col-span-1 md:col-span-3">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha * <span className="text-xs text-gray-500">(Solo días laborables: Lunes a Viernes)</span>
                    </label>
                    <div className="relative">
                      <input
                        type="date"
                        required
                        min={new Date().toISOString().split('T')[0]}
                        value={scheduleForm.fecha}
                        onChange={(e) => {
                          const selectedDate = new Date(e.target.value + 'T00:00:00');
                          const dayOfWeek = selectedDate.getDay();
                          // Validar que no sea sábado (6) ni domingo (0)
                          if (dayOfWeek !== 0 && dayOfWeek !== 6) {
                            setScheduleForm({ ...scheduleForm, fecha: e.target.value });
                            setDateError('');
                          } else {
                            const dayName = dayOfWeek === 0 ? 'Domingo' : 'Sábado';
                            setDateError(`❌ ${dayName} no disponible. Solo puedes agendar entrevistas de Lunes a Viernes.`);
                            setScheduleForm({ ...scheduleForm, fecha: '' });
                          }
                        }}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
                          dateError ? 'border-red-500 bg-red-50' : 'border-gray-300'
                        }`}
                        style={{
                          colorScheme: 'light'
                        }}
                      />
                      <style jsx>{`
                        /* Deshabilitar visualmente sábados y domingos en el calendario */
                        input[type="date"]::-webkit-calendar-picker-indicator {
                          cursor: pointer;
                        }
                      `}</style>
                    </div>
                    
                    {/* Mensaje de error elegante con animación */}
                    {dateError && (
                      <div className="mt-3 relative overflow-hidden animate-slideIn">
                        <div className="absolute inset-0 bg-gradient-to-r from-red-400 to-pink-500 animate-pulse opacity-20 rounded-xl"></div>
                        <div className="relative bg-gradient-to-br from-red-50 to-pink-50 border-2 border-red-300 rounded-xl p-4 shadow-lg transform transition-all duration-300 hover:scale-[1.02] animate-shake">
                          <div className="flex items-start gap-3">
                            {/* Icono animado */}
                            <div className="flex-shrink-0 w-10 h-10 bg-red-500 rounded-full flex items-center justify-center animate-bounce">
                              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                              </svg>
                            </div>

                            {/* Contenido del mensaje */}
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <h4 className="text-red-800 font-bold text-base flex items-center gap-2">
                                  Fecha No Disponible
                                </h4>
                                <button
                                  onClick={() => setDateError('')}
                                  className="text-red-400 hover:text-red-600 transition-colors duration-200 hover:scale-110 transform"
                                  aria-label="Cerrar alerta"
                                >
                                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                  </svg>
                                </button>
                              </div>
                              <p className="mt-1 text-sm text-red-700 font-medium">{dateError}</p>
                              <div className="mt-2 text-xs text-red-600 bg-white/50 rounded-lg px-3 py-2 border border-red-200 flex items-start gap-2">
                                <span className="text-base">💼</span>
                                <span><strong>Nota:</strong> Las entrevistas consulares solo están disponibles en días hábiles (Lunes a Viernes).</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {/* Indicador visual de días disponibles mejorado */}
                    <div className="mt-3 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-3 shadow-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <p className="text-xs font-semibold text-green-800 mb-1">📅 Días Laborables Disponibles</p>
                          <div className="flex flex-wrap gap-1.5">
                            {['Lun', 'Mar', 'Mié', 'Jue', 'Vie'].map((day, idx) => (
                              <span key={idx} className="inline-flex items-center px-2.5 py-1 bg-white border border-green-300 rounded-lg text-xs font-bold text-green-700 shadow-sm">
                                ✓ {day}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-xs text-green-700 bg-white/50 rounded-lg px-2 py-1.5">
                        <span className="flex items-center gap-1">
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <strong>Horario:</strong> 8:00 AM - 4:30 PM
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="col-span-1 md:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4">
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

      {/* Modal de Éxito - Entrevista Agendada */}
      {showSuccessModal && successData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-lg w-full shadow-2xl transform animate-slideIn">
            {/* Header con animación */}
            <div className="relative overflow-hidden bg-gradient-to-br from-green-400 via-emerald-500 to-teal-600 p-8 rounded-t-2xl">
              {/* Círculos decorativos animados */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-10 rounded-full -mr-16 -mt-16"></div>
              <div className="absolute bottom-0 left-0 w-24 h-24 bg-white opacity-10 rounded-full -ml-12 -mb-12"></div>

              {/* Icono de éxito con animación */}
              <div className="relative flex justify-center mb-4">
                <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg animate-bounce">
                  <svg className="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>

              {/* Título */}
              <h2 className="text-2xl font-bold text-white text-center mb-2">
                ¡Entrevista Agendada Exitosamente!
              </h2>
              <p className="text-green-50 text-center text-sm">
                Se ha enviado una notificación al cliente
              </p>
            </div>

            {/* Contenido */}
            <div className="p-6 space-y-4">
              {/* Información del Cliente */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide">Cliente</p>
                    <p className="text-lg font-bold text-blue-900">{successData.cliente}</p>
                  </div>
                </div>

                {successData.clienteEmail && (
                  <div className="flex items-center gap-2 text-sm text-blue-700 mb-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span>{successData.clienteEmail}</span>
                  </div>
                )}

                {successData.clienteTelefono && (
                  <div className="flex items-center gap-2 text-sm text-blue-700">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    <span>{successData.clienteTelefono}</span>
                  </div>
                )}
              </div>

              {/* Detalles de la Entrevista */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-purple-600 uppercase">Fecha</p>
                    <p className="text-base font-bold text-purple-900">
                      {new Date(successData.fecha + 'T12:00:00').toLocaleDateString('es-ES', {
                        weekday: 'long',
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric'
                      })}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg border border-orange-200">
                  <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-orange-600 uppercase">Hora</p>
                    <p className="text-base font-bold text-orange-900">{successData.hora}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-teal-50 rounded-lg border border-teal-200">
                  <div className="w-10 h-10 bg-teal-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-teal-600 uppercase">Ubicación</p>
                    <p className="text-sm font-bold text-teal-900">{successData.ubicacion}</p>
                  </div>
                </div>
              </div>

              {/* Información adicional */}
              <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-xs text-amber-800">
                    <p className="font-semibold mb-1">Tipo de Visa: {successData.tipoVisa}</p>
                    <p className="font-semibold">Embajada: {successData.embajada}</p>
                  </div>
                </div>
              </div>

              {/* Mensaje de notificación */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
                </svg>
                <p className="text-xs text-green-700">
                  <strong>✓ Notificación enviada</strong> al correo y teléfono del cliente
                </p>
              </div>
            </div>

            {/* Botón de Aceptar */}
            <div className="p-6 pt-0">
              <button
                onClick={() => {
                  setShowSuccessModal(false)
                  setSuccessData(null)
                  fetchData() // Recargar datos
                }}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold py-3.5 px-6 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-200 flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Aceptar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
