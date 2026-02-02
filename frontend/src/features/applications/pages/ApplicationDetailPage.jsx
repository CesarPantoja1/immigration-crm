import { useState, useEffect, useRef } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Card, Badge, Button, Modal } from '../../../components/common'
import { solicitudesService } from '../../../services/solicitudesService'

// Default fallback data structure
const DEFAULT_APPLICATION = {
  id: '',
  type: '',
  typeName: 'Visa',
  embassy: '',
  embassyName: 'Embajada',
  status: 'pending',
  statusName: 'Pendiente',
  date: new Date().toISOString().split('T')[0],
  applicantName: 'Solicitante',
  email: '',
  phone: '',
  documents: [],
  timeline: []
}

export default function ApplicationDetailPage() {
  const { id: rawId } = useParams()
  // Extraer el ID numérico si viene en formato SOL-X
  const id = rawId?.startsWith('SOL-') ? rawId.replace('SOL-', '') : rawId
  const [previewDoc, setPreviewDoc] = useState(null)
  const [app, setApp] = useState(null)
  const [loading, setLoading] = useState(true)
  const [resubmitDoc, setResubmitDoc] = useState(null)
  const [resubmitLoading, setResubmitLoading] = useState(false)
  const fileInputRef = useRef(null)

  // Helper para construir URL absoluta
  const buildAbsoluteUrl = (url) => {
    if (!url) return null
    if (url.startsWith('http')) return url
    const baseUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000'
    return `${baseUrl}${url}`
  }

  // Map status to display name (SINCRONIZADO con backend)
  const statusMap = {
    'borrador': 'Borrador',
    'pendiente': 'Pendiente',
    'en_revision': 'En Revisión',
    'aprobada': 'Aprobada por Asesor',
    'rechazada': 'Rechazada',
    'enviada_embajada': 'Enviada a Embajada',
    // Nuevos estados de decisión de embajada
    'esperando_decision_embajada': 'Esperando Decisión de Embajada',
    'aprobada_embajada': 'Aprobada por Embajada',
    'rechazada_embajada': 'Rechazada por Embajada',
    // Estados finales
    'entrevista_agendada': 'Entrevista Agendada',
    'completada': 'Completada'
  }

  // Función para cargar datos de la aplicación
  const fetchApplication = async () => {
    try {
      const data = await solicitudesService.getSolicitud(id)
      
      // Map visa type to display name (solo 3 tipos)
      const visaTypeMap = {
        'estudio': 'Visa de Estudio',
        'trabajo': 'Visa de Trabajo',
        'vivienda': 'Visa de Vivienda'
      }

      // Transform documentos (estados sincronizados con backend)
      const documentStatusMap = {
        'pendiente': { name: 'Pendiente', variant: 'pending' },
        'en_revision': { name: 'En Revisión', variant: 'reviewing' },
        'aprobado': { name: 'Aprobado', variant: 'approved' },
        'rechazado': { name: 'Rechazado', variant: 'rejected' }
      }

      const docs = (data.documentos_adjuntos || []).map(doc => {
        const statusInfo = documentStatusMap[doc.estado] || { name: 'Pendiente', variant: 'pending' }
        return {
          id: doc.id,
          name: doc.nombre,
          status: statusInfo.variant,
          backendStatus: doc.estado,
          statusName: statusInfo.name,
          url: buildAbsoluteUrl(doc.archivo_url || doc.archivo),
          motivo_rechazo: doc.motivo_rechazo,
          fecha_revision: doc.fecha_revision,
          size: doc.tamanio || 'PDF',
          uploadDate: doc.fecha_subida ? new Date(doc.fecha_subida).toLocaleDateString('es-ES') : 'Desconocido'
        }
      })

      // Generate timeline from data
      const timeline = []
      let timelineId = 1
      if (data.created_at) {
        timeline.push({
          id: timelineId++,
          type: 'created',
          action: 'Solicitud creada',
          user: 'Sistema',
          date: new Date(data.created_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
        })
      }
      if (data.fecha_asignacion) {
        timeline.push({
          id: timelineId++,
          type: 'assigned',
          action: `Asignada a ${data.asesor_nombre || 'asesor'}`,
          user: 'Sistema',
          date: new Date(data.fecha_asignacion).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
        })
      }
      // Agregar evento de envío a embajada si existe
      if (data.fecha_envio_embajada) {
        timeline.push({
          id: timelineId++,
          type: 'embassy',
          action: 'Enviada a la embajada',
          user: data.asesor_nombre || 'Asesor',
          date: new Date(data.fecha_envio_embajada).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
        })
      }
      // Agregar evento de aprobación de embajada
      if (data.estado === 'aprobada_embajada' || data.estado === 'entrevista_agendada' || data.estado === 'completada') {
        timeline.push({
          id: timelineId++,
          type: 'approved',
          action: 'Aprobada por la embajada',
          user: 'Embajada',
          date: ''
        })
      }
      // Agregar evento de entrevista agendada
      if (data.entrevista) {
        timeline.push({
          id: timelineId++,
          type: 'interview',
          action: `Entrevista agendada para el ${new Date(data.entrevista.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'long' })} a las ${data.entrevista.hora}`,
          user: data.asesor_nombre || 'Asesor',
          date: data.entrevista.created_at ? new Date(data.entrevista.created_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' }) : ''
        })
      }

      const formattedApp = {
        originalId: data.id,
        id: data.numero ? `SOL-${data.numero}` : `SOL-${id}`,
        // Datos del cliente - usar valores del backend o defaults seguros
        applicantName: data.cliente_nombre || data.datos_personales?.nombre || 'Cliente',
        email: data.datos_personales?.email || '',
        phone: data.datos_personales?.telefono || '',
        // Tipo y embajada
        type: data.tipo_visa,
        typeName: visaTypeMap[data.tipo_visa] || data.tipo_visa_display || data.tipo_visa || 'Visa',
        embassy: data.embajada,
        embassyName: data.embajada_display || data.embajada || 'Embajada',
        // Estado
        status: data.estado,
        statusName: statusMap[data.estado] || data.estado_display || data.estado,
        // Documentos y timeline
        documents: docs,
        timeline,
        // Fechas
        date: data.created_at ? data.created_at.split('T')[0] : new Date().toISOString().split('T')[0],
        createdAt: data.created_at,
        fechaSolicitud: data.created_at ? new Date(data.created_at).toLocaleDateString('es-ES', {
          day: 'numeric', month: 'long', year: 'numeric'
        }) : '',
        // Información de la entrevista (si existe)
        entrevista: data.entrevista ? {
          id: data.entrevista.id,
          fecha: data.entrevista.fecha,
          hora: data.entrevista.hora,
          ubicacion: data.entrevista.ubicacion || 'Por confirmar',
          estado: data.entrevista.estado,
          estadoDisplay: data.entrevista.estado_display || data.entrevista.estado,
          notas: data.entrevista.notas || '',
          fechaFormateada: data.entrevista.fecha ? new Date(data.entrevista.fecha).toLocaleDateString('es-ES', {
            weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
          }) : ''
        } : null,
        // Motivo de rechazo de embajada (si aplica)
        motivo_rechazo_embajada: data.motivo_rechazo_embajada || null,
        // Otros datos
        observaciones: data.observaciones,
        notas_asesor: data.notas_asesor,
        asesor_nombre: data.asesor_nombre
      }

      setApp(formattedApp)
    } catch (error) {
      console.error('Error loading application:', error)
    }
  }

  // Función para resubir documento
  const handleResubmitDocument = async (doc) => {
    setResubmitDoc(doc)
    // Trigger click on hidden file input
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  // Manejar selección de archivo
  const handleFileSelected = async (event) => {
    const file = event.target.files?.[0]
    if (!file || !resubmitDoc) return
    
    try {
      setResubmitLoading(true)
      await solicitudesService.resubirDocumento(resubmitDoc.id, file)
      
      // Esperar un poco y recargar los datos desde el servidor
      await new Promise(resolve => setTimeout(resolve, 500))
      await fetchApplication()
      
      alert('Documento resubido exitosamente. Será revisado nuevamente por tu asesor.')
    } catch (error) {
      console.error('Error resubiendo documento:', error)
      alert('Error al resubir el documento. Por favor intenta nuevamente.')
    } finally {
      setResubmitLoading(false)
      setResubmitDoc(null)
      // Limpiar input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }
        
  useEffect(() => {
    setLoading(true)
    fetchApplication().finally(() => setLoading(false))
  }, [id])

  const getStatusVariant = (status) => {
    switch (status) {
      // Estados de éxito (verde)
      case 'aprobada':
      case 'aprobado':
      case 'approved':
      case 'completada':
      case 'aprobada_embajada':
        return 'success'
      // Estados de advertencia/pendiente (amarillo)
      case 'pendiente':
      case 'borrador':
      case 'pending':
        return 'warning'
      // Estados informativos/en proceso (azul)
      case 'en_revision':
      case 'enviada_embajada':
      case 'esperando_decision_embajada':
      case 'entrevista_agendada':
      case 'reviewing':
        return 'info'
      // Estados de rechazo/error (rojo)
      case 'rechazada':
      case 'rechazado':
      case 'rejected':
      case 'rechazada_embajada':
        return 'danger'
      default: return 'default'
    }
  }

  const getTimelineIcon = (type) => {
    switch (type) {
      case 'created':
        return (
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </div>
        )
      case 'upload':
        return (
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
        )
      case 'approved':
        return (
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )
      case 'reviewing':
        return (
          <div className="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        )
      case 'assigned':
        return (
          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        )
      case 'embassy':
        return (
          <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
        )
      case 'interview':
        return (
          <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )
      default:
        return (
          <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        )
    }
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!app) return null

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link to="/solicitudes" className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-4">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Volver a solicitudes
        </Link>
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-gray-900">{app.id}</h1>
              <Badge variant={getStatusVariant(app.status)} size="lg" dot>
                {app.statusName}
              </Badge>
            </div>
            <p className="text-gray-500 mt-1">{app.typeName} • Embajada de {app.embassyName}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Documents */}
          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Documentos</h2>
            <div className="space-y-3">
              {app.documents.map((doc) => (
                <div
                  key={doc.id}
                  className={`flex items-center justify-between p-4 rounded-xl transition-colors ${
                    doc.status === 'rejected'
                      ? 'bg-red-50 border border-red-200 hover:bg-red-100'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      doc.status === 'approved' ? 'bg-green-100' :
                      doc.status === 'rejected' ? 'bg-red-100' :
                      doc.status === 'pending' ? 'bg-amber-100' : 'bg-blue-100'
                    }`}>
                      <svg className={`w-6 h-6 ${
                        doc.status === 'approved' ? 'text-green-600' :
                        doc.status === 'rejected' ? 'text-red-600' :
                        doc.status === 'pending' ? 'text-amber-600' : 'text-blue-600'
                      }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        {doc.status === 'rejected' ? (
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        ) : (
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        )}
                      </svg>
                    </div>
                    <div>
                      <p className={`font-medium ${doc.status === 'rejected' ? 'text-red-900' : 'text-gray-900'}`}>
                        {doc.name}
                      </p>
                      <p className={`text-sm ${doc.status === 'rejected' ? 'text-red-600' : 'text-gray-500'}`}>
                        {doc.size} • Subido el {doc.uploadDate}
                      </p>
                      {/* Mostrar motivo de rechazo si existe */}
                      {doc.status === 'rejected' && doc.motivo_rechazo && (
                        <p className="text-sm text-red-700 mt-1 flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {doc.motivo_rechazo}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant={getStatusVariant(doc.status)}>
                      {doc.statusName}
                    </Badge>
                    {/* Botón para resubir documento rechazado */}
                    {doc.status === 'rejected' && (
                      <button
                        onClick={() => handleResubmitDocument(doc)}
                        disabled={resubmitLoading && resubmitDoc?.id === doc.id}
                        className="px-3 py-1.5 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        {resubmitLoading && resubmitDoc?.id === doc.id ? (
                          <>
                            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Subiendo...
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                            </svg>
                            Resubir
                          </>
                        )}
                      </button>
                    )}
                    <button
                      onClick={() => setPreviewDoc(doc)}
                      className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Input oculto para subir archivo */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelected}
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              className="hidden"
            />
          </Card>

          {/* Timeline */}
          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Historial de la Solicitud</h2>
            <div className="space-y-4">
              {app.timeline.map((event, index) => (
                <div key={event.id} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    {getTimelineIcon(event.type)}
                    {index < app.timeline.length - 1 && (
                      <div className="w-0.5 h-full bg-gray-200 my-2" />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <p className="font-medium text-gray-900">{event.action}</p>
                    <p className="text-sm text-gray-500">
                      {event.user} • {event.date}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Application Info */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-4">Información de Solicitud</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">ID de Solicitud</p>
                <p className="font-medium text-gray-900">{app.id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Tipo de Visa</p>
                <p className="font-medium text-gray-900">{app.typeName}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Embajada</p>
                <p className="font-medium text-gray-900">{app.embassyName}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Fecha de Registro</p>
                <p className="font-medium text-gray-900">
                  {new Date(app.date).toLocaleDateString('es-ES', {
                    year: 'numeric', month: 'long', day: 'numeric'
                  })}
                </p>
              </div>
            </div>
          </Card>

          {/* Applicant Info */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-4">Datos del Solicitante</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-lg font-semibold text-primary-600">
                    {(app.applicantName || 'C').charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{app.applicantName || 'Cliente'}</p>
                  <p className="text-sm text-gray-500">{app.email || 'Sin email'}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Teléfono</p>
                <p className="font-medium text-gray-900">{app.phone || 'Sin teléfono'}</p>
              </div>
            </div>
          </Card>

          {/* Alerta de Rechazo de Embajada - Solo mostrar si la solicitud fue rechazada por embajada */}
          {app.status === 'rechazada_embajada' && (
            <Card className="border-2 border-red-300 bg-red-50">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-red-800">Solicitud Rechazada por Embajada</h3>
              </div>
              
              {app.motivo_rechazo_embajada ? (
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <p className="text-sm text-red-600 font-medium mb-1">Motivo del Rechazo:</p>
                      <p className="text-red-800">{app.motivo_rechazo_embajada}</p>
                    </div>
                  </div>
                  
                  <div className="mt-4 p-3 bg-white rounded-lg border border-red-200">
                    <p className="text-sm text-gray-600">
                      <strong>¿Qué puedo hacer?</strong> Si considera que hubo un error o desea más información, 
                      contacte a su asesor para discutir las opciones disponibles, como apelar la decisión 
                      o iniciar una nueva solicitud.
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-red-700 text-sm">
                  La embajada ha rechazado su solicitud. Por favor contacte a su asesor para más detalles.
                </p>
              )}
            </Card>
          )}

          {/* Entrevista Info - Solo mostrar si hay entrevista agendada */}
          {app.entrevista && (
            <Card className="border-2 border-primary-200 bg-primary-50/30">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900">Entrevista Agendada</h3>
              </div>
              
              <div className="space-y-3">
                {/* Fecha */}
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <div>
                    <p className="text-sm text-gray-500">Fecha</p>
                    <p className="font-medium text-gray-900 capitalize">{app.entrevista.fechaFormateada}</p>
                  </div>
                </div>
                
                {/* Hora */}
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p className="text-sm text-gray-500">Hora</p>
                    <p className="font-medium text-gray-900">{app.entrevista.hora}</p>
                  </div>
                </div>
                
                {/* Ubicación */}
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <div>
                    <p className="text-sm text-gray-500">Ubicación</p>
                    <p className="font-medium text-gray-900">{app.entrevista.ubicacion}</p>
                  </div>
                </div>
                
                {/* Estado de la entrevista */}
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p className="text-sm text-gray-500">Estado</p>
                    <Badge variant={app.entrevista.estado === 'confirmada' ? 'success' : 'info'} size="sm">
                      {app.entrevista.estadoDisplay}
                    </Badge>
                  </div>
                </div>
                
                {/* Notas si existen */}
                {app.entrevista.notas && (
                  <div className="mt-3 p-3 bg-white rounded-lg border border-gray-200">
                    <p className="text-sm text-gray-500 mb-1">Instrucciones:</p>
                    <p className="text-sm text-gray-700">{app.entrevista.notas}</p>
                  </div>
                )}
              </div>
              
              {/* Botón de agregar al calendario */}
              <div className="mt-4 pt-4 border-t border-primary-200">
                <button
                  onClick={() => {
                    // Crear evento de calendario
                    const startDate = new Date(`${app.entrevista.fecha}T${app.entrevista.hora}`)
                    const endDate = new Date(startDate.getTime() + 60 * 60 * 1000) // 1 hora después
                    const title = encodeURIComponent(`Entrevista de Visa - ${app.typeName}`)
                    const details = encodeURIComponent(`Entrevista para solicitud ${app.id}\nUbicación: ${app.entrevista.ubicacion}`)
                    const location = encodeURIComponent(app.entrevista.ubicacion)
                    
                    // Formato para Google Calendar
                    const googleUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${startDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z/${endDate.toISOString().replace(/[-:]/g, '').split('.')[0]}Z&details=${details}&location=${location}`
                    
                    window.open(googleUrl, '_blank')
                  }}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Agregar a Calendario
                </button>
              </div>
            </Card>
          )}

          {/* Progress Summary */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-4">Progreso de Documentos</h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Documentos aprobados</span>
                <span className="font-medium text-gray-900">
                  {app.documents.filter(d => d.status === 'approved').length} de {app.documents.length}
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 rounded-full"
                  style={{
                    width: `${(app.documents.filter(d => d.status === 'approved').length / Math.max(1, app.documents.length)) * 100}%`
                  }}
                />
              </div>
              <div className="flex flex-wrap gap-3 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  <span className="text-gray-500">
                    {app.documents.filter(d => d.status === 'approved').length} Aprobados
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                  <span className="text-gray-500">
                    {app.documents.filter(d => d.status === 'reviewing').length} En revisión
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-amber-500 rounded-full" />
                  <span className="text-gray-500">
                    {app.documents.filter(d => d.status === 'pending').length} Pendientes
                  </span>
                </div>
                {/* Mostrar rechazados si existen */}
                {app.documents.filter(d => d.status === 'rejected').length > 0 && (
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-red-500 rounded-full" />
                    <span className="text-red-600 font-medium">
                      {app.documents.filter(d => d.status === 'rejected').length} Rechazados
                    </span>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Document Preview Modal */}
      <Modal
        isOpen={!!previewDoc}
        onClose={() => setPreviewDoc(null)}
        title={previewDoc?.name}
        size="lg"
      >
        {previewDoc && (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{previewDoc.name}</p>
                  <p className="text-sm text-gray-500">{previewDoc.size}</p>
                </div>
              </div>
              <Badge variant={getStatusVariant(previewDoc.status)}>
                {previewDoc.status === 'approved' ? 'Aprobado' :
                 previewDoc.status === 'pending' ? 'Pendiente' : 'En Revisión'}
              </Badge>
            </div>
            
            <div className="aspect-[3/4] bg-gray-100 rounded-xl overflow-hidden">
              {previewDoc.url ? (
                <iframe
                  src={`${previewDoc.url}#toolbar=1`}
                  className="w-full h-full"
                  title={previewDoc.name}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  <div className="text-center">
                    <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p>Vista previa no disponible</p>
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={() => setPreviewDoc(null)}>
                Cerrar
              </Button>
              {previewDoc.url && (
                <Button onClick={() => window.open(previewDoc.url, '_blank')}>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Descargar
                </Button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
