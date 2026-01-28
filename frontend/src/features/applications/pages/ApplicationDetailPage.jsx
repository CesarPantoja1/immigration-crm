import { useState, useEffect } from 'react'
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

  useEffect(() => {
    const fetchApplication = async () => {
      try {
        const data = await solicitudesService.getSolicitud(id)
        
        // Map status to display name
        const statusMap = {
          'pendiente': 'Pendiente',
          'en_revision': 'En Revisión',
          'aprobada': 'Aprobada',
          'rechazada': 'Rechazada',
          'completada': 'Completada',
          'enviada_embajada': 'Enviada a Embajada',
          'entrevista_agendada': 'Entrevista Agendada',
          'borrador': 'Borrador'
        }
        
        // Map visa type to display name (solo 3 tipos)
        const visaTypeMap = {
          'estudio': 'Visa de Estudio',
          'trabajo': 'Visa de Trabajo',
          'vivienda': 'Visa de Vivienda'
        }

        // Helper para construir URL absoluta
        const buildAbsoluteUrl = (url) => {
          if (!url) return null
          if (url.startsWith('http')) return url
          const baseUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000'
          return `${baseUrl}${url}`
        }

        // Transform documentos
        const docs = (data.documentos_adjuntos || []).map(doc => ({
          id: doc.id,
          name: doc.nombre,
          status: doc.estado,
          statusName: doc.estado === 'aprobado' ? 'Aprobado' : doc.estado === 'rechazado' ? 'Rechazado' : 'Pendiente',
          url: buildAbsoluteUrl(doc.archivo_url || doc.archivo),
          motivo_rechazo: doc.motivo_rechazo,
          fecha_revision: doc.fecha_revision,
          size: doc.tamanio || 'PDF',
          uploadDate: doc.fecha_subida ? new Date(doc.fecha_subida).toLocaleDateString('es-ES') : 'Desconocido'
        }))

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
            type: 'reviewing',
            action: `Asignada a ${data.asesor_nombre || 'un asesor'}`,
            user: 'Sistema',
            date: new Date(data.fecha_asignacion).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
          })
        }
        if (data.fecha_revision) {
          timeline.push({
            id: timelineId++,
            type: data.estado === 'aprobada' ? 'approved' : 'reviewing',
            action: `Solicitud ${statusMap[data.estado] || data.estado}`,
            user: data.asesor_nombre || 'Asesor',
            date: new Date(data.fecha_revision).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
          })
        }
        if (docs.length > 0) {
          timeline.push({
            id: timelineId++,
            type: 'upload',
            action: `${docs.length} documento(s) adjuntado(s)`,
            user: 'Cliente',
            date: ''
          })
        }
        
        setApp({
          id: data.id,
          displayId: `SOL-${data.id}`,
          type: data.tipo_visa || 'general',
          typeName: data.tipo_visa_display || visaTypeMap[data.tipo_visa] || 'Visa',
          embassy: data.embajada || '',
          embassyName: data.embajada_display || data.embajada || 'Embajada',
          status: data.estado || 'pendiente',
          statusName: data.estado_display || statusMap[data.estado] || 'Pendiente',
          date: data.created_at ? data.created_at.split('T')[0] : new Date().toISOString().split('T')[0],
          applicantName: data.cliente_nombre || 'Solicitante',
          email: data.datos_personales?.email || '',
          phone: data.datos_personales?.telefono || '',
          documents: docs,
          timeline: timeline,
          observaciones: data.observaciones,
          notas_asesor: data.notas_asesor,
          asesor_nombre: data.asesor_nombre,
          entrevista: data.entrevista
        })
      } catch (error) {
        console.error('Error fetching application:', error)
        setApp({ ...DEFAULT_APPLICATION, id, displayId: `SOL-${id}` })
      } finally {
        setLoading(false)
      }
    }
    fetchApplication()
  }, [id])

  const getStatusVariant = (status) => {
    switch (status) {
      case 'aprobada':
      case 'aprobado':
      case 'approved': 
      case 'completada':
        return 'success'
      case 'pendiente':
      case 'borrador':
      case 'pending': 
        return 'warning'
      case 'en_revision':
      case 'enviada_embajada':
      case 'entrevista_agendada':
      case 'reviewing': 
        return 'info'
      case 'rechazada':
      case 'rechazado':
      case 'rejected': 
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
      default:
        return null
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
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      doc.status === 'approved' ? 'bg-green-100' :
                      doc.status === 'pending' ? 'bg-amber-100' : 'bg-blue-100'
                    }`}>
                      <svg className={`w-6 h-6 ${
                        doc.status === 'approved' ? 'text-green-600' :
                        doc.status === 'pending' ? 'text-amber-600' : 'text-blue-600'
                      }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{doc.name}</p>
                      <p className="text-sm text-gray-500">{doc.size} • Subido el {doc.uploadDate}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant={getStatusVariant(doc.status)}>
                      {doc.status === 'approved' ? 'Aprobado' :
                       doc.status === 'pending' ? 'Pendiente' : 'En Revisión'}
                    </Badge>
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
                    {app.applicantName.charAt(0)}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{app.applicantName}</p>
                  <p className="text-sm text-gray-500">{app.email}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Teléfono</p>
                <p className="font-medium text-gray-900">{app.phone}</p>
              </div>
            </div>
          </Card>

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
                    width: `${(app.documents.filter(d => d.status === 'approved').length / app.documents.length) * 100}%` 
                  }}
                />
              </div>
              <div className="flex gap-4 text-xs">
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
