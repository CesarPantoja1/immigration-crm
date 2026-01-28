import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card, Badge, Button, Input, Modal } from '../../../components/common'
import { solicitudesService } from '../../../services'

export default function ApplicationsListPage() {
  const [loading, setLoading] = useState(true)
  const [applications, setApplications] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterType, setFilterType] = useState('all')
  const [previewDoc, setPreviewDoc] = useState(null)

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true)
        const params = {}
        if (filterStatus !== 'all') params.estado = filterStatus
        if (filterType !== 'all') params.tipo_visa = filterType
        if (searchTerm) params.search = searchTerm
        
        const data = await solicitudesService.getAll(params)
        const results = data.results || data || []
        
        // Transform to component format
        const transformed = results.map(s => ({
          id: `SOL-${s.id}`,
          rawId: s.id,
          type: s.tipo_visa,
          typeName: s.tipo_visa_display || s.tipo_visa,
          embassy: s.embajada,
          embassyName: s.embajada_display || s.embajada,
          status: s.estado,
          statusName: s.estado_display || s.estado,
          date: s.created_at?.split('T')[0],
          documents: (s.documentos_adjuntos || []).map(d => ({
            name: d.nombre,
            status: d.estado
          }))
        }))
        
        setApplications(transformed)
      } catch (error) {
        console.error('Error fetching applications:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchApplications()
  }, [filterStatus, filterType, searchTerm])

  const filteredApplications = applications.filter(app => {
    const matchesSearch = app.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.typeName.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesSearch
  })

  const getStatusVariant = (status) => {
    switch (status) {
      case 'aprobada':
      case 'approved': return 'success'
      case 'pendiente':
      case 'pending': return 'warning'
      case 'en_revision':
      case 'reviewing': return 'info'
      case 'rechazada':
      case 'rejected': return 'danger'
      default: return 'default'
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'study':
        return (
          <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
        )
      case 'work':
        return (
          <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        )
      case 'residence':
        return (
          <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mis Solicitudes</h1>
          <p className="text-gray-500 mt-1">Gestiona y monitorea tus solicitudes de visa</p>
        </div>
        <Link to="/nueva-solicitud">
          <Button>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nueva Solicitud
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Buscar por ID o tipo..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
            >
              <option value="all">Todos los estados</option>
              <option value="pending">Pendiente</option>
              <option value="reviewing">En Revisión</option>
              <option value="approved">Aprobada</option>
              <option value="rejected">Rechazada</option>
            </select>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
            >
              <option value="all">Todos los tipos</option>
              <option value="study">Estudio</option>
              <option value="work">Trabajo</option>
              <option value="residence">Vivienda</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Applications List */}
      <div className="space-y-4">
        {filteredApplications.length === 0 ? (
          <Card className="text-center py-12">
            <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay solicitudes</h3>
            <p className="text-gray-500 mb-6">No tienes solicitudes que coincidan con los filtros</p>
            <Link to="/nueva-solicitud">
              <Button>Crear primera solicitud</Button>
            </Link>
          </Card>
        ) : (
          filteredApplications.map((app) => (
            <Card key={app.id} hover>
              <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                {/* Icon & Info */}
                <div className="flex items-center gap-4 flex-1">
                  {getTypeIcon(app.type)}
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-gray-900">{app.id}</h3>
                      <Badge variant={getStatusVariant(app.status)} dot>
                        {app.statusName}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      {app.typeName} • Embajada de {app.embassyName}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Registrada el {new Date(app.date).toLocaleDateString('es-ES', { 
                        year: 'numeric', month: 'long', day: 'numeric' 
                      })}
                    </p>
                  </div>
                </div>

                {/* Documents Preview */}
                <div className="flex items-center gap-2">
                  {app.documents.slice(0, 3).map((doc, i) => (
                    <div
                      key={i}
                      className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-medium cursor-pointer ${
                        doc.status === 'approved' ? 'bg-green-100 text-green-600' :
                        doc.status === 'pending' ? 'bg-amber-100 text-amber-600' :
                        'bg-blue-100 text-blue-600'
                      }`}
                      title={doc.name}
                      onClick={() => setPreviewDoc(doc)}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                  ))}
                  {app.documents.length > 3 && (
                    <span className="text-xs text-gray-400">+{app.documents.length - 3}</span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPreviewDoc(app.documents[0])}
                    className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="Ver documentos"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <Link 
                    to={`/solicitudes/${app.rawId}`}
                    className="px-4 py-2 bg-primary-50 text-primary-600 font-medium rounded-lg hover:bg-primary-100 transition-colors"
                  >
                    Ver Detalle
                  </Link>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Document Preview Modal */}
      <Modal
        isOpen={!!previewDoc}
        onClose={() => setPreviewDoc(null)}
        title="Vista Previa de Documento"
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
                  <p className="text-sm text-gray-500">documento.pdf • 2.4 MB</p>
                </div>
              </div>
              <Badge variant={getStatusVariant(previewDoc.status)}>
                {previewDoc.status === 'approved' ? 'Aprobado' :
                 previewDoc.status === 'pending' ? 'Pendiente' : 'En Revisión'}
              </Badge>
            </div>
            
            {/* PDF Preview Placeholder */}
            <div className="aspect-[3/4] bg-gray-100 rounded-xl flex items-center justify-center">
              <div className="text-center text-gray-400">
                <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>Vista previa del documento</p>
                <p className="text-sm">(Se mostrará el PDF aquí)</p>
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={() => setPreviewDoc(null)}>
                Cerrar
              </Button>
              <Button>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Descargar
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
