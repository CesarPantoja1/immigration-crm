import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card, Badge, Button, SplitViewModal } from '../../../components/common'
import { VISA_TYPES, DOCUMENT_CHECKLIST } from '../../../store'

// Nueva estructura: Tipo de Visa → Clientes → Categoría de Documentos → Documentos
const folderStructure = [
  {
    id: 'visa-trabajo',
    name: 'Visa de Trabajo',
    icon: '💼',
    type: 'visa-type',
    color: 'purple',
    expanded: true,
    children: [
      {
        id: 'trabajo-client-1',
        name: 'Ana Martínez',
        type: 'client-folder',
        applicationId: 'SOL-2024-001',
        status: 'pending_review',
        expanded: false,
        children: [
          { id: 't-c1-personal', name: 'Documentos Personales', type: 'folder', docCount: 2, status: 'complete' },
          { id: 't-c1-legal', name: 'Documentos Legales', type: 'folder', docCount: 2, status: 'complete' },
          { id: 't-c1-work', name: 'Documentos Laborales', type: 'folder', docCount: 1, status: 'pending' }
        ]
      },
      {
        id: 'trabajo-client-5',
        name: 'Roberto Méndez',
        type: 'client-folder',
        applicationId: 'SOL-2024-005',
        status: 'approved',
        expanded: false,
        children: [
          { id: 't-c5-personal', name: 'Documentos Personales', type: 'folder', docCount: 2, status: 'complete' },
          { id: 't-c5-legal', name: 'Documentos Legales', type: 'folder', docCount: 2, status: 'complete' },
          { id: 't-c5-work', name: 'Documentos Laborales', type: 'folder', docCount: 2, status: 'complete' }
        ]
      }
    ]
  },
  {
    id: 'visa-estudio',
    name: 'Visa de Estudio',
    icon: '🎓',
    type: 'visa-type',
    color: 'blue',
    expanded: false,
    children: [
      {
        id: 'estudio-client-2',
        name: 'Pedro Sánchez',
        type: 'client-folder',
        applicationId: 'SOL-2024-002',
        status: 'pending_review',
        expanded: false,
        children: [
          { id: 'e-c2-personal', name: 'Documentos Personales', type: 'folder', docCount: 2, status: 'complete' },
          { id: 'e-c2-academic', name: 'Documentos Académicos', type: 'folder', docCount: 1, status: 'pending' },
          { id: 'e-c2-financial', name: 'Documentos Financieros', type: 'folder', docCount: 1, status: 'complete' }
        ]
      },
      {
        id: 'estudio-client-4',
        name: 'Carlos López',
        type: 'client-folder',
        applicationId: 'SOL-2024-004',
        status: 'draft',
        expanded: false,
        children: [
          { id: 'e-c4-personal', name: 'Documentos Personales', type: 'folder', docCount: 2, status: 'incomplete' },
          { id: 'e-c4-academic', name: 'Documentos Académicos', type: 'folder', docCount: 0, status: 'missing' },
          { id: 'e-c4-financial', name: 'Documentos Financieros', type: 'folder', docCount: 1, status: 'pending' }
        ]
      }
    ]
  },
  {
    id: 'visa-vivienda',
    name: 'Visa de Vivienda',
    icon: '🏠',
    type: 'visa-type',
    color: 'green',
    expanded: false,
    children: [
      {
        id: 'vivienda-client-3',
        name: 'Laura Díaz',
        type: 'client-folder',
        applicationId: 'SOL-2024-003',
        status: 'pending_review',
        expanded: false,
        children: [
          { id: 'v-c3-personal', name: 'Documentos Personales', type: 'folder', docCount: 2, status: 'complete' },
          { id: 'v-c3-property', name: 'Documentos de Propiedad', type: 'folder', docCount: 3, status: 'complete' },
          { id: 'v-c3-financial', name: 'Documentos Financieros', type: 'folder', docCount: 1, status: 'pending' }
        ]
      }
    ]
  },
  {
    id: 'templates',
    name: 'Plantillas',
    icon: '📋',
    type: 'folder',
    expanded: false,
    children: [
      { id: 'template-work', name: 'Visa de Trabajo', type: 'folder', docCount: 5 },
      { id: 'template-study', name: 'Visa de Estudio', type: 'folder', docCount: 4 },
      { id: 'template-housing', name: 'Visa de Vivienda', type: 'folder', docCount: 6 }
    ]
  }
]

const mockDocuments = {
  't-c1-personal': [
    { id: 1, name: 'Pasaporte', type: 'pdf', size: '2.4 MB', uploadedAt: '25/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1544965838-54ef8406f868?w=400' },
    { id: 2, name: 'Foto 2x2', type: 'jpg', size: '1.1 MB', uploadedAt: '25/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400' }
  ],
  't-c1-legal': [
    { id: 3, name: 'Antecedentes Judiciales', type: 'pdf', size: '1.3 MB', uploadedAt: '25/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400' },
    { id: 4, name: 'Certificado de Conducta', type: 'pdf', size: '890 KB', uploadedAt: '25/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1586282391129-76a6df230234?w=400' }
  ],
  't-c1-work': [
    { id: 5, name: 'Carta de Oferta Laboral', type: 'pdf', size: '856 KB', uploadedAt: '25/01/2024', status: 'pending', preview: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=400' }
  ],
  'e-c2-personal': [
    { id: 1, name: 'Pasaporte', type: 'pdf', size: '2.1 MB', uploadedAt: '24/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1544965838-54ef8406f868?w=400' },
    { id: 2, name: 'Foto 2x2', type: 'jpg', size: '980 KB', uploadedAt: '24/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400' }
  ],
  'e-c2-academic': [
    { id: 3, name: 'Carta de Aceptación', type: 'pdf', size: '1.2 MB', uploadedAt: '24/01/2024', status: 'pending', preview: 'https://images.unsplash.com/photo-1586282391129-76a6df230234?w=400' }
  ],
  'e-c2-financial': [
    { id: 4, name: 'Estados Financieros', type: 'pdf', size: '2.8 MB', uploadedAt: '24/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400' }
  ],
  'v-c3-personal': [
    { id: 1, name: 'Pasaporte', type: 'pdf', size: '2.3 MB', uploadedAt: '23/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1544965838-54ef8406f868?w=400' },
    { id: 2, name: 'Foto 2x2', type: 'jpg', size: '1.0 MB', uploadedAt: '23/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400' }
  ],
  'v-c3-property': [
    { id: 3, name: 'Título de Propiedad', type: 'pdf', size: '3.5 MB', uploadedAt: '23/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400' },
    { id: 4, name: 'Contrato de Compra', type: 'pdf', size: '2.1 MB', uploadedAt: '23/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1586282391129-76a6df230234?w=400' },
    { id: 5, name: 'Avalúo', type: 'pdf', size: '1.8 MB', uploadedAt: '23/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400' }
  ],
  'v-c3-financial': [
    { id: 6, name: 'Extractos Bancarios', type: 'pdf', size: '4.2 MB', uploadedAt: '23/01/2024', status: 'pending', preview: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400' }
  ],
  'e-c4-personal': [
    { id: 1, name: 'Pasaporte', type: 'pdf', size: '2.0 MB', uploadedAt: '22/01/2024', status: 'pending', preview: 'https://images.unsplash.com/photo-1544965838-54ef8406f868?w=400' },
    { id: 2, name: 'Foto 2x2', type: 'jpg', size: '890 KB', uploadedAt: '22/01/2024', status: 'pending', preview: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400' }
  ],
  'e-c4-financial': [
    { id: 4, name: 'Solvencia Económica', type: 'pdf', size: '2.5 MB', uploadedAt: '22/01/2024', status: 'pending', preview: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400' }
  ],
  't-c5-personal': [
    { id: 1, name: 'Pasaporte', type: 'pdf', size: '2.4 MB', uploadedAt: '20/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1544965838-54ef8406f868?w=400' },
    { id: 2, name: 'Foto 2x2', type: 'jpg', size: '1.2 MB', uploadedAt: '20/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400' }
  ],
  't-c5-legal': [
    { id: 3, name: 'Antecedentes Judiciales', type: 'pdf', size: '1.1 MB', uploadedAt: '20/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400' },
    { id: 4, name: 'Certificado de Conducta', type: 'pdf', size: '920 KB', uploadedAt: '20/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1586282391129-76a6df230234?w=400' }
  ],
  't-c5-work': [
    { id: 5, name: 'Carta de Oferta Laboral', type: 'pdf', size: '780 KB', uploadedAt: '20/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=400' },
    { id: 6, name: 'Contrato de Trabajo', type: 'pdf', size: '1.3 MB', uploadedAt: '20/01/2024', status: 'approved', preview: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400' }
  ]
}

export default function DocumentExplorerPage() {
  const [expandedFolders, setExpandedFolders] = useState(['visa-trabajo'])
  const [selectedFolder, setSelectedFolder] = useState(null)
  const [selectedPath, setSelectedPath] = useState([])
  const [viewMode, setViewMode] = useState('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [reviewingDocument, setReviewingDocument] = useState(null)
  const [showSplitView, setShowSplitView] = useState(false)

  const documents = selectedFolder ? mockDocuments[selectedFolder] || [] : []

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
        return 'bg-green-100 text-green-600'
      case 'pending':
      case 'pending_review':
        return 'bg-yellow-100 text-yellow-600'
      case 'incomplete':
      case 'missing':
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

  const handleOpenReview = (doc) => {
    setReviewingDocument(doc)
    setShowSplitView(true)
  }

  const handleCloseReview = () => {
    setShowSplitView(false)
    setReviewingDocument(null)
  }

  const handleApprove = (checklist, observations) => {
    console.log('Document approved:', { document: reviewingDocument, checklist, observations })
    // TODO: API call
    handleCloseReview()
  }

  const handleReject = (checklist, observations) => {
    console.log('Document rejected:', { document: reviewingDocument, checklist, observations })
    // TODO: API call
    handleCloseReview()
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

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-6">
      {/* Sidebar - Folder Tree */}
      <div className="w-72 flex-shrink-0">
        <Card className="h-full flex flex-col overflow-hidden">
          <div className="p-4 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Explorador</h2>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
            {folderStructure.map(item => renderFolderItem(item))}
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
                          <img 
                            src={doc.preview} 
                            alt={doc.name}
                            className="w-full h-full object-cover"
                          />
                          {/* Status Badge */}
                          <div className={`absolute top-2 right-2 px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(doc.status)}`}>
                            {doc.status === 'approved' ? 'Aprobado' :
                             doc.status === 'pending' ? 'Pendiente' :
                             doc.status === 'rejected' ? 'Rechazado' : doc.status}
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
                        {/* Realizar Revisión Button */}
                        {doc.status === 'pending' && (
                          <button
                            onClick={() => handleOpenReview(doc)}
                            className="w-full py-2 bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium rounded-lg transition-colors"
                          >
                            Realizar Revisión
                          </button>
                        )}
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
                              <div className="w-10 h-10 rounded-lg overflow-hidden bg-gray-100">
                                <img 
                                  src={doc.preview} 
                                  alt={doc.name}
                                  className="w-full h-full object-cover"
                                />
                              </div>
                              <span className="font-medium text-gray-900">{doc.name}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`text-xs font-medium px-2 py-1 rounded ${getStatusColor(doc.status)}`}>
                              {doc.status === 'approved' ? 'Aprobado' :
                               doc.status === 'pending' ? 'Pendiente' :
                               doc.status === 'rejected' ? 'Rechazado' : doc.status}
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
                              {doc.status === 'pending' ? (
                                <button 
                                  onClick={() => handleOpenReview(doc)}
                                  className="px-3 py-1.5 bg-primary-500 hover:bg-primary-600 text-white text-xs font-medium rounded-lg transition-colors"
                                >
                                  Realizar Revisión
                                </button>
                              ) : (
                                <>
                                  <button className="p-1.5 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                    </svg>
                                  </button>
                                  <button className="p-1.5 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                    </svg>
                                  </button>
                                </>
                              )}
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

      {/* SplitView Modal for Document Review */}
      {showSplitView && reviewingDocument && (
        <SplitViewModal
          isOpen={showSplitView}
          onClose={handleCloseReview}
          document={reviewingDocument}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}
    </div>
  )
}
