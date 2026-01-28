import { useState, useEffect } from 'react'
import { Card, Button, Badge } from '../../../components/common'

// Mock data - En producción esto vendría de la API
const mockSolicitudes = [
  {
    id: 'SOL-2024-001',
    cliente: 'Ana Martínez',
    tipoVisa: 'Visa de Trabajo',
    embajada: 'Estados Unidos',
    estado: 'APROBADA_SIN_ENTREVISTA',
    fechaSolicitud: '2024-01-25',
    prioridad: 'alta'
  },
  {
    id: 'SOL-2024-002',
    cliente: 'Pedro Sánchez',
    tipoVisa: 'Visa de Estudio',
    embajada: 'Canadá',
    estado: 'APROBADA_SIN_ENTREVISTA',
    fechaSolicitud: '2024-01-24',
    prioridad: 'media'
  },
  {
    id: 'SOL-2024-003',
    cliente: 'Laura Díaz',
    tipoVisa: 'Visa de Residencia',
    embajada: 'España',
    estado: 'APROBADA_SIN_ENTREVISTA',
    fechaSolicitud: '2024-01-23',
    prioridad: 'baja'
  }
]

const mockEntrevistas = [
  {
    id: 'ENT-001',
    codigo: 'INT-2024-001',
    solicitudId: 'SOL-2024-004',
    cliente: 'Carlos López',
    embajada: 'Estados Unidos',
    estado: 'AGENDADA',
    fecha: '2026-02-15',
    hora: '10:00',
    ubicacion: 'Embajada de EE.UU. - Ciudad de México',
    vecesReprogramada: 0
  },
  {
    id: 'ENT-002',
    codigo: 'INT-2024-002',
    solicitudId: 'SOL-2024-005',
    cliente: 'María García',
    embajada: 'Canadá',
    estado: 'CONFIRMADA',
    fecha: '2026-02-20',
    hora: '14:00',
    ubicacion: 'Consulado de Canadá',
    vecesReprogramada: 1
  }
]

export default function InterviewScheduling() {
  const [solicitudes, setSolicitudes] = useState(mockSolicitudes)
  const [entrevistas, setEntrevistas] = useState(mockEntrevistas)
  const [selectedTab, setSelectedTab] = useState('pendientes') // 'pendientes' | 'agendadas'
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [selectedSolicitud, setSelectedSolicitud] = useState(null)
  const [scheduleForm, setScheduleForm] = useState({
    fecha: '',
    hora: '',
    ubicacion: '',
    ubicacionSeleccionada: '', // Para el dropdown
    ubicacionPersonalizada: '', // Para el campo de texto cuando selecciona "Otros"
    modoAsignacion: 'fecha_fija' // 'fecha_fija' | 'opciones'
  })
  const [opciones, setOpciones] = useState([
    { id: 'opt1', fecha: '', hora: '' }
  ])

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
    setShowScheduleModal(true)
  }

  const handleSubmitSchedule = async (e) => {
    e.preventDefault()

    try {
      let endpoint = '/api/agendamiento/'
      let body = {}

      // Determinar la ubicación final
      const ubicacionFinal = scheduleForm.ubicacionSeleccionada === 'otros'
        ? scheduleForm.ubicacionPersonalizada
        : scheduleForm.ubicacionSeleccionada

      if (scheduleForm.modoAsignacion === 'fecha_fija') {
        endpoint += 'asignar-fecha-fija/'
        body = {
          solicitud_id: selectedSolicitud.id,
          embajada: selectedSolicitud.embajada,
          fecha: scheduleForm.fecha,
          hora: scheduleForm.hora,
          ubicacion: ubicacionFinal
        }
      } else {
        endpoint += 'ofrecer-opciones/'
        body = {
          solicitud_id: selectedSolicitud.id,
          embajada: selectedSolicitud.embajada,
          opciones: opciones.map((opt, idx) => ({
            id: `opt${idx + 1}`,
            fecha: opt.fecha,
            hora: opt.hora
          }))
        }
      }

      console.log('Enviando datos:', body) // Para debug

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      })

      const data = await response.json()

      if (data.success) {
        alert('Entrevista agendada exitosamente')
        setShowScheduleModal(false)
        // Resetear formulario
        setScheduleForm({
          fecha: '',
          hora: '',
          ubicacion: '',
          ubicacionSeleccionada: '',
          ubicacionPersonalizada: '',
          modoAsignacion: 'fecha_fija'
        })
        // Recargar datos
        // En producción, hacer fetch real de la API
      } else {
        alert('Error al agendar: ' + data.error)
      }
    } catch (error) {
      console.error('Error completo:', error)
      alert('Error al agendar la entrevista: ' + error.message)
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
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Solicitudes Aprobadas - Pendientes de Agendar Entrevista
          </h2>
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

      {/* Modal para Agendar Entrevista */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Agendar Entrevista</h2>
              <p className="text-gray-600 mt-1">
                Solicitud: {selectedSolicitud?.id} - {selectedSolicitud?.cliente}
              </p>
            </div>

            <form onSubmit={handleSubmitSchedule} className="p-6 space-y-6">
              {/* Modo de Asignación */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Modo de Asignación
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="modoAsignacion"
                      value="fecha_fija"
                      checked={scheduleForm.modoAsignacion === 'fecha_fija'}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, modoAsignacion: e.target.value })}
                      className="mr-2"
                    />
                    Fecha Fija (Embajada asigna)
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="modoAsignacion"
                      value="opciones"
                      checked={scheduleForm.modoAsignacion === 'opciones'}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, modoAsignacion: e.target.value })}
                      className="mr-2"
                    />
                    Ofrecer Opciones (Cliente elige)
                  </label>
                </div>
              </div>

              {scheduleForm.modoAsignacion === 'fecha_fija' ? (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Fecha *
                      </label>
                      <input
                        type="date"
                        required
                        value={scheduleForm.fecha}
                        onChange={(e) => setScheduleForm({ ...scheduleForm, fecha: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Hora *
                      </label>
                      <input
                        type="time"
                        required
                        value={scheduleForm.hora}
                        onChange={(e) => setScheduleForm({ ...scheduleForm, hora: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ubicación *
                    </label>
                    <select
                      required
                      value={scheduleForm.ubicacionSeleccionada}
                      onChange={(e) => setScheduleForm({
                        ...scheduleForm,
                        ubicacionSeleccionada: e.target.value,
                        ubicacionPersonalizada: '' // Limpiar el campo personalizado
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      <option value="">Selecciona una ubicación</option>
                      {(ubicacionesPorEmbajada[selectedSolicitud?.embajada] || []).map((ubicacion, idx) => (
                        <option key={idx} value={ubicacion}>
                          {ubicacion}
                        </option>
                      ))}
                      <option value="otros">Otros (especificar)</option>
                    </select>

                    {/* Campo de texto que aparece solo cuando selecciona "Otros" */}
                    {scheduleForm.ubicacionSeleccionada === 'otros' && (
                      <div className="mt-3">
                        <input
                          type="text"
                          required
                          placeholder="Escribe la ubicación personalizada"
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
                </>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="block text-sm font-medium text-gray-700">
                      Opciones de Horario
                    </label>
                    <Button type="button" size="sm" onClick={addOpcion}>
                      + Agregar Opción
                    </Button>
                  </div>

                  {opciones.map((opcion, index) => (
                    <div key={index} className="flex gap-4 items-start bg-gray-50 p-4 rounded-lg">
                      <div className="flex-1 grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Fecha
                          </label>
                          <input
                            type="date"
                            required
                            value={opcion.fecha}
                            onChange={(e) => updateOpcion(index, 'fecha', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Hora
                          </label>
                          <input
                            type="time"
                            required
                            value={opcion.hora}
                            onChange={(e) => updateOpcion(index, 'hora', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          />
                        </div>
                      </div>
                      {opciones.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeOpcion(index)}
                          className="mt-6 text-red-600 hover:text-red-700"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowScheduleModal(false)}
                  className="flex-1"
                >
                  Cancelar
                </Button>
                <Button type="submit" className="flex-1">
                  Agendar Entrevista
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
