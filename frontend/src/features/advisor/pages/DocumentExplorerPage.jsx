import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '../../../components/common'
import { solicitudesService } from '../../../services'

// Mapeo de tipos de visa a iconos y colores (solo 3 tipos: vivienda, trabajo, estudio)
const visaTypeConfig = {
  'vivienda': { icon: '🏠', color: 'purple', name: 'Visa de Vivienda' },
  'trabajo': { icon: '💼', color: 'green', name: 'Visa de Trabajo' },
  'estudio': { icon: '🎓', color: 'blue', name: 'Visa de Estudio' }
}

export default function DocumentExplorerPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [folderStructure, setFolderStructure] = useState([])
  const [documentsMap, setDocumentsMap] = useState({})
  const [solicitudesMap, setSolicitudesMap] = useState({}) // Mapa de folderId a solicitudId
  const [expandedFolders, setExpandedFolders] = useState([])
  const [selectedFolder, setSelectedFolder] = useState(null)
  const [selectedPath, setSelectedPath] = useState([])
  const [viewMode, setViewMode] = useState('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [previewDocument, setPreviewDocument] = useState(null) // Solo para ver documento
  const [error, setError] = useState(null)

  // Cargar solicitudes desde la API y organizarlas por tipo de visa
  useEffect(() => {
    const fetchSolicitudes = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await solicitudesService.getSolicitudesAsignadas()
        const solicitudes = Array.isArray(response) ? response : (response?.results || [])
        
        // Helper para construir URL absoluta
        const buildAbsoluteUrl = (url) => {
          if (!url) return null
          if (url.startsWith('http')) return url
          const baseUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000'
          return `${baseUrl}${url}`
        }
        
        // Organizar solicitudes por tipo de visa
        const solicitudesPorTipo = {}
        const docsMap = {}
        const solsMap = {} // Mapa de folderId a solicitudId
        
        solicitudes.forEach(sol => {
          const tipoVisa = sol.tipo_visa || 'otro'
          if (!solicitudesPorTipo[tipoVisa]) {
            solicitudesPorTipo[tipoVisa] = []
          }
          solicitudesPorTipo[tipoVisa].push(sol)
          
          // Guardar documentos en el mapa
          const clientFolderId = `client-${sol.id}`
          solsMap[clientFolderId] = sol.id // Guardar referencia a solicitudId
          const documentos = sol.documentos_adjuntos || []
          docsMap[clientFolderId] = documentos.map(doc => ({
            id: doc.id,
            name: doc.nombre || 'Documento',
            type: doc.archivo ? doc.archivo.split('.').pop() : 'pdf',
            size: 'N/A',
            uploadedAt: new Date(doc.created_at).toLocaleDateString('es-ES'),
            status: doc.estado || 'pendiente',
            preview: buildAbsoluteUrl(doc.archivo_url || doc.archivo),
            archivo: buildAbsoluteUrl(doc.archivo_url || doc.archivo)
          }))
        })
        
        // Construir estructura de carpetas
        const structure = Object.entries(solicitudesPorTipo).map(([tipoVisa, sols]) => {
          const config = visaTypeConfig[tipoVisa] || { icon: '📄', color: 'gray', name: tipoVisa }
          
          return {
            id: `visa-${tipoVisa}`,
            name: config.name,
            icon: config.icon,
            type: 'visa-type',
            color: config.color,
            children: sols.map(sol => ({
              id: `client-${sol.id}`,
              name: sol.cliente_nombre || `Cliente #${sol.id}`,
              type: 'client-folder',
              applicationId: `SOL-${sol.id}`,
              solicitudId: sol.id,
              status: sol.estado || 'pendiente',
              docCount: (sol.documentos_adjuntos || []).length
            }))
          }
        })
        
        setFolderStructure(structure)
        setDocumentsMap(docsMap)
        setSolicitudesMap(solsMap)
        
        // Expandir el primer tipo de visa si existe
        if (structure.length > 0) {
          setExpandedFolders([structure[0].id])
        }
        
      } catch (err) {
        console.error('Error loading documents:', err)
        setError('Error al cargar los documentos')
      } finally {
        setLoading(false)
      }
    }
    
    fetchSolicitudes()
  }, [])

  // Obtener documentos del folder seleccionado
  const documents = selectedFolder ? (documentsMap[selectedFolder] || []) : []

  const toggleFolder = (folderId) => {
    setExpandedFolders(prev => 
      prev.includes(folderId) 
        ? prev.filter(id => id !== folderId)
        : [...prev, folderId]
    )
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'complete':
      case 'approved':
      case 'aprobado':
        return 'bg-green-100 text-green-600'
      case 'pending':
      case 'pending_review':
      case 'pendiente':
        return 'bg-yellow-100 text-yellow-600'
      case 'incomplete':
      case 'missing':
      case 'rejected':
      case 'rechazado':
        return 'bg-red-100 text-red-600'
      case 'draft':
        return 'bg-gray-100 text-gray-500'
      default:
        return 'bg-gray-100 text-gray-500'
    }
  }

  const getVisaTypeColor = (color) => {
    switch (color) {
      case 'purple': return 'bg-purple-50 border-purple-200 text-purple-700'
      case 'blue': return 'bg-blue-50 border-blue-200 text-blue-700'
      case 'green': return 'bg-green-50 border-green-200 text-green-700'
      default: return 'bg-gray-50 border-gray-200 text-gray-700'
    }
  }

  // Solo abrir documento para ver (sin revisión)
  const handleViewDocument = (doc) => {
    if (doc.archivo || doc.preview) {
      window.open(doc.archivo || doc.preview, '_blank')
    }
  }

  // Navegar a la solicitud para realizar revisión
  const handleGoToSolicitud = () => {
    if (selectedFolder && solicitudesMap[selectedFolder]) {
      navigate(`/asesor/solicitudes/${solicitudesMap[selectedFolder]}/revisar`)
    }
  }

  const selectFolder = (folderId, path) => {
    setSelectedFolder(folderId)
    setSelectedPath(path)
  }

  const renderFolderItem = (item, depth = 0, parentPath = []) => {
    const isExpanded = expandedFolders.includes(item.id)
    const isSelected = selectedFolder === item.id
    const hasChildren = item.children && item.children.length > 0
    const currentPath = [...parentPath, item.name]

    return (
      <div key={item.id}>
        <button
          onClick={() => {
            if (hasChildren) {
              toggleFolder(item.id)
            }
            if (item.type !== 'folder' && item.type !== 'visa-type' || !hasChildren || item.docCount !== undefined) {
              selectFolder(item.id, currentPath)
            }
          }}
          className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left transition-colors ${
            isSelected 
              ? 'bg-primary-50 text-primary-700' 
              : item.type === 'visa-type'
                ? `${getVisaTypeColor(item.color)} border`
                : 'hover:bg-gray-100 text-gray-700'
          }`}
          style={{ paddingLeft: `${8 + depth * 16}px` }}
        >
          {/* Expand/Collapse Arrow */}
          {hasChildren ? (
            <svg 
              className={`w-4 h-4 text-gray-400 transition-transform flex-shrink-0 ${isExpanded ? 'rotate-90' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          ) : (
            <div className="w-4 flex-shrink-0" />
          )}

          {/* Folder/Client Icon */}
          {item.type === 'client-folder' ? (
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0 ${
              isSelected ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              {item.name.charAt(0)}
            </div>
          ) : (
            <span className="text-lg flex-shrink-0">
              {item.icon || (isExpanded ? '📂' : '📁')}
            </span>
          )}

          {/* Folder Name */}
          <span className="text-sm truncate flex-1">{item.name}</span>

          {/* Status Badge for clients */}
          {item.type === 'client-folder' && item.status && (
            <span className={`text-xs px-1.5 py-0.5 rounded flex-shrink-0 ${getStatusColor(item.status)}`}>
              {item.status === 'pending_review' ? '⏳' : item.status === 'approved' ? '✓' : '○'}
            </span>
          )}

          {/* Status Badge for document folders */}
          {item.status && item.type === 'folder' && (
            <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
              item.status === 'complete' ? 'bg-green-500' :
              item.status === 'pending' ? 'bg-yellow-500' :
              item.status === 'missing' ? 'bg-red-500' :
              'bg-gray-300'
            }`} />
          )}

          {/* Document Count */}
          {item.docCount !== undefined && (
            <span className="text-xs text-gray-400 flex-shrink-0">{item.docCount}</span>
          )}
        </button>

        {/* Children */}
        {hasChildren && isExpanded && (
          <div className="mt-0.5">
            {item.children.map(child => renderFolderItem(child, depth + 1, currentPath))}
          </div>
        )}
      </div>
    )
  }

  // Estado de carga
  if (loading) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando documentos...</p>
        </div>
      </div>
    )
  }

  // Estado de error
  if (error) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">{error}</h3>
          <p className="text-gray-500 text-sm">Intenta recargar la página</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-6">
      {/* Sidebar - Folder Tree */}
      <div className="w-72 flex-shrink-0">
        <Card className="h-full flex flex-col overflow-hidden">
          <div className="p-4 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Explorador</h2>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
            {folderStructure.length > 0 ? (
              folderStructure.map(item => renderFolderItem(item))
            ) : (
              <div className="text-center py-8 text-gray-500 text-sm">
                No hay solicitudes asignadas
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Main Content - Documents */}
      <div className="flex-1 flex flex-col min-w-0">
        {selectedFolder ? (
          <>
            {/* Breadcrumb & Header */}
            <div className="flex items-center justify-between mb-4 gap-4">
              <div className="min-w-0">
                {/* Breadcrumb */}
                <div className="flex items-center gap-1 text-sm text-gray-500 mb-1">
                  <button 
                    onClick={() => setSelectedFolder(null)}
                    className="hover:text-primary-600"
                  >
                    Inicio
                  </button>
                  {selectedPath.map((pathItem, index) => (
                    <span key={index} className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                      <span className={index === selectedPath.length - 1 ? 'text-gray-900 font-medium' : ''}>
                        {pathItem}
                      </span>
                    </span>
                  ))}
                </div>
                <h1 className="text-xl font-bold text-gray-900 truncate">
                  {selectedPath[selectedPath.length - 1]}
                </h1>
              </div>

              <div className="flex items-center gap-3 flex-shrink-0">
                {/* Botón para ir a la solicitud */}
                {selectedFolder && solicitudesMap[selectedFolder] && (
                  <button
                    onClick={handleGoToSolicitud}
                    className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    Revisar Solicitud
                  </button>
                )}

                {/* Search */}
                <div className="relative">
                  <svg className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Buscar..."
                    className="w-48 pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                {/* View Mode Toggle */}
                <div className="flex items-center bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm' : ''}`}
                  >
                    <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-1.5 rounded ${viewMode === 'list' ? 'bg-white shadow-sm' : ''}`}
                  >
                    <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            {/* Documents */}
            <Card className="flex-1 overflow-y-auto">
              {documents.length > 0 ? (
                viewMode === 'grid' ? (
                  <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="bg-gray-50 rounded-xl p-3 hover:bg-gray-100 transition-colors group"
                      >
                        {/* Preview Thumbnail */}
                        <div className="aspect-[4/3] bg-white rounded-lg overflow-hidden mb-3 border border-gray-200 group-hover:border-primary-300 transition-colors relative">
                          {doc.type === 'pdf' ? (
                            <div className="w-full h-full flex items-center justify-center bg-red-50">
                              <svg className="w-16 h-16 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M10.92,12.31C10.68,11.54 10.15,9.08 11.55,9.04C12.95,9 12.03,12.16 12.03,12.16C12.42,13.65 14.05,14.72 14.05,14.72C14.55,14.57 17.4,14.24 17,15.72C16.57,17.2 13.5,15.81 13.5,15.81C11.55,15.95 10.09,16.47 10.09,16.47C8.96,18.58 7.64,19.5 7.1,18.61C6.43,17.5 9.23,16.07 9.23,16.07C10.68,13.7 10.92,12.31 10.92,12.31Z" />
                              </svg>
                            </div>
                          ) : (
                            <img 
                              src={doc.preview} 
                              alt={doc.name}
                              className="w-full h-full object-cover"
                            />
                          )}
                          {/* Status Badge */}
                          <div className={`absolute top-2 right-2 px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(doc.status)}`}>
                            {doc.status === 'approved' || doc.status === 'aprobado' ? 'Aprobado' :
                             doc.status === 'pending' || doc.status === 'pendiente' ? 'Pendiente' :
                             doc.status === 'rejected' || doc.status === 'rechazado' ? 'Rechazado' : doc.status}
                          </div>
                        </div>
                        <p className="font-medium text-gray-900 text-sm truncate">{doc.name}</p>
                        <div className="flex items-center justify-between mt-1 mb-3">
                          <span className="text-xs text-gray-500">{doc.size}</span>
                          <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                            doc.type === 'pdf' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'
                          }`}>
                            {doc.type.toUpperCase()}
                          </span>
                        </div>
                        {/* Ver Documento Button */}
                        <button
                          onClick={() => handleViewDocument(doc)}
                          className="w-full py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                          Ver Documento
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Nombre</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Estado</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tipo</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tamaño</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Fecha</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {documents.map((doc) => (
                        <tr key={doc.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
                                {doc.type === 'pdf' ? (
                                  <svg className="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M10.92,12.31C10.68,11.54 10.15,9.08 11.55,9.04C12.95,9 12.03,12.16 12.03,12.16C12.42,13.65 14.05,14.72 14.05,14.72C14.55,14.57 17.4,14.24 17,15.72C16.57,17.2 13.5,15.81 13.5,15.81C11.55,15.95 10.09,16.47 10.09,16.47C8.96,18.58 7.64,19.5 7.1,18.61C6.43,17.5 9.23,16.07 9.23,16.07C10.68,13.7 10.92,12.31 10.92,12.31Z" />
                                  </svg>
                                ) : (
                                  <img 
                                    src={doc.preview} 
                                    alt={doc.name}
                                    className="w-full h-full object-cover"
                                  />
                                )}
                              </div>
                              <span className="font-medium text-gray-900">{doc.name}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`text-xs font-medium px-2 py-1 rounded ${getStatusColor(doc.status)}`}>
                              {doc.status === 'approved' || doc.status === 'aprobado' ? 'Aprobado' :
                               doc.status === 'pending' || doc.status === 'pendiente' ? 'Pendiente' :
                               doc.status === 'rejected' || doc.status === 'rechazado' ? 'Rechazado' : doc.status}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`text-xs font-medium px-2 py-1 rounded ${
                              doc.type === 'pdf' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'
                            }`}>
                              {doc.type.toUpperCase()}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-gray-600 text-sm">{doc.size}</span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-gray-600 text-sm">{doc.uploadedAt}</span>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex gap-2">
                              <button 
                                onClick={() => handleViewDocument(doc)}
                                className="p-1.5 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
                                title="Ver documento"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                              </button>
                              <a 
                                href={doc.archivo || doc.preview}
                                download
                                className="p-1.5 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
                                title="Descargar documento"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                              </a>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-1">Carpeta vacía</h3>
                    <p className="text-gray-500 text-sm">Esta carpeta no contiene documentos</p>
                  </div>
                </div>
              )}
            </Card>
          </>
        ) : (
          <Card className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-20 h-20 bg-primary-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Explorador de Documentos</h3>
              <p className="text-gray-500 max-w-sm mx-auto">
                Navega por la estructura de carpetas en el panel izquierdo para ver los documentos de cada cliente.
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
