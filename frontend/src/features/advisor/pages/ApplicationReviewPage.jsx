import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Badge, Button, Modal, SplitViewModal } from '../../../components/common'
import { DOCUMENT_CHECKLIST } from '../../../store'
import { solicitudesService } from '../../../services/solicitudesService'

// Default empty application data
const defaultApplicationData = {
  id: '',
  client: {
    name: '',
    email: '',
    phone: '',
    nationality: ''
  },
  visaType: '',
  embassy: '',
  submittedAt: '',
  status: 'pending_review',
  documents: []
}

export default function ApplicationReviewPage() {
  const { id: rawId } = useParams()
  // Extraer el ID numérico si viene en formato SOL-X
  const id = rawId?.startsWith('SOL-') ? rawId.replace('SOL-', '') : rawId
  const navigate = useNavigate()
  const [applicationData, setApplicationData] = useState(defaultApplicationData)
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [showViewer, setShowViewer] = useState(false)
  const [showSplitView, setShowSplitView] = useState(false)
  const [currentDocIndex, setCurrentDocIndex] = useState(0)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [rejectReason, setRejectReason] = useState('')
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [rejectingDocId, setRejectingDocId] = useState(null)

  useEffect(() => {
    const fetchApplicationData = async () => {
      try {
        setLoading(true)
        const data = await solicitudesService.getSolicitud(id)
        
        // Helper para construir URL absoluta
        const buildAbsoluteUrl = (url) => {
          if (!url) return null
          if (url.startsWith('http')) return url
          const baseUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000'
          return `${baseUrl}${url}`
        }
        
        const formattedData = {
          id: data.id || data.numero || id,
          client: {
            name: data.cliente?.nombre || data.cliente_nombre || 'Cliente',
            email: data.cliente?.email || '',
            phone: data.cliente?.telefono || '',
            nationality: data.cliente?.nacionalidad || ''
          },
          visaType: data.tipo_visa_nombre || data.tipo_visa || 'Visa',
          embassy: data.embajada_nombre || data.embajada || 'Embajada',
          submittedAt: data.fecha_creacion ? new Date(data.fecha_creacion).toLocaleDateString('es-ES', {
            day: 'numeric', month: 'long', year: 'numeric'
          }) : '',
          status: data.estado || 'pending_review',
          documents: (data.documentos_adjuntos || data.documentos || []).map((doc, i) => {
            // Mapear estados del backend a valores del frontend
            const mapEstado = (estado) => {
              switch(estado) {
                case 'aprobado': return 'approved'
                case 'rechazado': return 'rejected'
                case 'pendiente': 
                default: return 'pending'
              }
            }
            return {
              id: doc.id || i + 1,
              name: doc.nombre || doc.name || 'Documento',
              filename: doc.archivo || doc.filename || '',
              status: mapEstado(doc.estado),
              uploadedAt: doc.fecha_subida || doc.created_at || '',
              size: doc.tamano || '',
              type: doc.archivo?.endsWith('.pdf') ? 'pdf' : (doc.tipo || 'pdf'),
              preview: buildAbsoluteUrl(doc.archivo_url || doc.archivo || doc.url)
            }
          })
        }
        
        setApplicationData(formattedData)
        setDocuments(formattedData.documents)
      } catch (error) {
        console.error('Error fetching application:', error)
        // Keep default empty data on error
      } finally {
        setLoading(false)
      }
    }
    fetchApplicationData()
  }, [id])

  const currentDoc = documents[currentDocIndex]
  const pendingDocuments = documents.filter(d => d.status === 'pending')

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!showViewer) return
      if (e.key === 'ArrowLeft') navigateDoc(-1)
      if (e.key === 'ArrowRight') navigateDoc(1)
      if (e.key === 'Escape') setShowViewer(false)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [showViewer, currentDocIndex])

  const navigateDoc = (direction) => {
    const newIndex = currentDocIndex + direction
    if (newIndex >= 0 && newIndex < documents.length) {
      setCurrentDocIndex(newIndex)
    }
  }

  const openViewer = (index) => {
    setCurrentDocIndex(index)
    setShowViewer(true)
  }

  const openSplitViewReview = () => {
    // Abrir SplitView con el primer documento pendiente
    const firstPendingIndex = documents.findIndex(d => d.status === 'pending')
    if (firstPendingIndex !== -1) {
      setCurrentDocIndex(firstPendingIndex)
      setShowSplitView(true)
    }
  }

  const handleSplitViewApprove = async (docId, reviewData) => {
    try {
      await solicitudesService.aprobarDocumento(docId)
      setDocuments(prev => prev.map(doc =>
        doc.id === docId ? { ...doc, status: 'approved', reviewData } : doc
      ))
    } catch (error) {
      console.error('Error aprobando documento:', error)
    }
  }

  const handleSplitViewReject = async (docId, reviewData) => {
    try {
      const motivo = reviewData?.observations || 'Documento rechazado'
      await solicitudesService.rechazarDocumento(docId, motivo)
      setDocuments(prev => prev.map(doc =>
        doc.id === docId ? { ...doc, status: 'rejected', reviewData } : doc
      ))
    } catch (error) {
      console.error('Error rechazando documento:', error)
    }
  }

  const handleDocumentAction = async (docId, action) => {
    try {
      if (action === 'approved') {
        await solicitudesService.aprobarDocumento(docId)
      } else if (action === 'rejected') {
        // No hacer nada aquí, se maneja en el modal de rechazo
        return
      }
      
      setDocuments(prev => prev.map(doc =>
        doc.id === docId ? { ...doc, status: action } : doc
      ))
      
      // Auto navigate to next pending in viewer
      if (showViewer && action === 'approved') {
        const nextPending = documents.findIndex((d, i) => i > currentDocIndex && d.status === 'pending')
        if (nextPending !== -1) {
          setCurrentDocIndex(nextPending)
        }
      }
    } catch (error) {
      console.error('Error actualizando documento:', error)
    }
  }

  const handleRejectWithReason = async () => {
    if (!rejectingDocId || !rejectReason.trim()) return
    
    try {
      await solicitudesService.rechazarDocumento(rejectingDocId, rejectReason)
      setDocuments(prev => prev.map(doc =>
        doc.id === rejectingDocId ? { ...doc, status: 'rejected', rejectReason } : doc
      ))
      setShowRejectModal(false)
      setRejectReason('')
      setRejectingDocId(null)
      
      // Auto navigate to next pending in viewer
      if (showViewer) {
        const nextPending = documents.findIndex((d, i) => i > currentDocIndex && d.status === 'pending')
        if (nextPending !== -1) {
          setCurrentDocIndex(nextPending)
        }
      }
    } catch (error) {
      console.error('Error rechazando documento:', error)
    }
  }

  const openRejectModal = (docId) => {
    setRejectingDocId(docId)
    setShowRejectModal(true)
  }

  const allDocumentsReviewed = documents.every(doc => doc.status !== 'pending')
  const hasRejectedDocs = documents.some(doc => doc.status === 'rejected')

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved':
        return <Badge variant="success" size="sm">Aprobado</Badge>
      case 'rejected':
        return <Badge variant="danger" size="sm">Rechazado</Badge>
      default:
        return <Badge variant="warning" size="sm">Pendiente</Badge>
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return (
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )
      case 'rejected':
        return (
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        )
      default:
        return (
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center">
            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 8v4m0 4h.01" />
            </svg>
          </div>
        )
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate('/asesor/solicitudes')}
            className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver a solicitudes
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Revisión de Solicitud</h1>
          <p className="text-gray-500">{applicationData.id}</p>
        </div>

        {allDocumentsReviewed && (
          <div className="flex gap-3">
            {hasRejectedDocs ? (
              <Button 
                variant="danger" 
                onClick={async () => {
                  try {
                    await solicitudesService.actualizarSolicitud(id, { 
                      estado: 'pendiente',
                      notas_asesor: 'Documentos rechazados. Por favor corrija y vuelva a enviar.'
                    })
                    navigate('/asesor/solicitudes')
                  } catch (error) {
                    console.error('Error:', error)
                  }
                }}
              >
                Devolver al Cliente
              </Button>
            ) : (
              <Button onClick={() => setShowApproveModal(true)}>
                Aprobar Solicitud
              </Button>
            )}
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Client Info */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Información del Cliente</h2>

          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-2xl font-bold">
              {applicationData.client.name.charAt(0)}
            </div>
            <div>
              <p className="font-semibold text-gray-900">{applicationData.client.name}</p>
              <p className="text-sm text-gray-500">{applicationData.client.nationality}</p>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="text-gray-700">{applicationData.client.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Teléfono</p>
              <p className="text-gray-700">{applicationData.client.phone}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Tipo de Visa</p>
              <p className="text-gray-700">{applicationData.visaType}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Embajada</p>
              <p className="text-gray-700">{applicationData.embassy}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Fecha de Solicitud</p>
              <p className="text-gray-700">{applicationData.submittedAt}</p>
            </div>
          </div>
        </Card>

        {/* Documents Review */}
        <div className="lg:col-span-2">
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Documentos a Revisar</h2>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-500">
                  {documents.filter(d => d.status !== 'pending').length} de {documents.length} revisados
                </span>
                {pendingDocuments.length > 0 && (
                  <button
                    onClick={openSplitViewReview}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    Iniciar Revisión ({pendingDocuments.length})
                  </button>
                )}
                <button
                  onClick={() => openViewer(0)}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Ver Galería
                </button>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
              <div
                className="h-full bg-primary-600 rounded-full transition-all duration-500"
                style={{
                  width: `${(documents.filter(d => d.status !== 'pending').length / documents.length) * 100}%`
                }}
              />
            </div>

            {/* Document Gallery Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {documents.map((doc, index) => (
                <button
                  key={doc.id}
                  onClick={() => openViewer(index)}
                  className="group relative aspect-[3/4] rounded-xl overflow-hidden bg-gray-100 border-2 border-gray-200 hover:border-primary-400 transition-all hover:shadow-lg"
                >
                  {/* Preview Image or PDF Icon */}
                  {doc.type === 'pdf' || doc.preview?.endsWith('.pdf') ? (
                    <div className="w-full h-full bg-red-50 flex items-center justify-center">
                      <svg className="w-16 h-16 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M10.92,12.31C10.68,11.54 10.15,9.08 11.55,9.04C12.95,9 12.03,12.16 12.03,12.16C12.42,13.65 14.05,14.72 14.05,14.72C14.55,14.57 17.4,14.24 17,15.72C16.57,17.2 13.5,15.81 13.5,15.81C11.55,15.95 10.09,16.47 10.09,16.47C8.96,18.58 7.64,19.5 7.1,18.61C6.43,17.5 9.23,16.07 9.23,16.07C10.68,13.7 10.92,12.31 10.92,12.31Z" />
                      </svg>
                    </div>
                  ) : (
                    <img
                      src={doc.preview}
                      alt={doc.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  )}

                  {/* Overlay with info */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />

                  {/* Status Icon */}
                  {getStatusIcon(doc.status)}

                  {/* Document Name */}
                  <div className="absolute bottom-0 left-0 right-0 p-2">
                    <p className="text-xs font-medium text-white truncate">{doc.name}</p>
                    <p className="text-xs text-gray-300">{doc.size}</p>
                  </div>

                  {/* Hover View Icon */}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </Card>

          {/* Summary */}
          {allDocumentsReviewed && (
            <Card className="mt-6">
              <h3 className="font-semibold text-gray-900 mb-4">Resumen de Revisión</h3>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-gray-50 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-gray-900">{documents.length}</div>
                  <div className="text-sm text-gray-500">Total</div>
                </div>
                <div className="bg-green-50 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {documents.filter(d => d.status === 'approved').length}
                  </div>
                  <div className="text-sm text-gray-500">Aprobados</div>
                </div>
                <div className="bg-red-50 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {documents.filter(d => d.status === 'rejected').length}
                  </div>
                  <div className="text-sm text-gray-500">Rechazados</div>
                </div>
              </div>

              {hasRejectedDocs && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                  <p className="text-amber-800 text-sm">
                    <strong>Nota:</strong> Al devolver la solicitud, el cliente recibirá una notificación
                    con los motivos de rechazo de cada documento y podrá volver a subirlos.
                  </p>
                </div>
              )}
            </Card>
          )}
        </div>
      </div>

      {/* Full Screen Document Viewer */}
      {showViewer && (
        <div className="fixed inset-0 z-50 bg-black/95 flex flex-col">
          {/* Viewer Header */}
          <div className="flex items-center justify-between px-6 py-4 bg-black/50">
            <div className="flex items-center gap-4">
              <h3 className="text-white font-semibold text-lg">{currentDoc?.name}</h3>
              {getStatusBadge(currentDoc?.status)}
            </div>
            <div className="flex items-center gap-4">
              <span className="text-gray-400 text-sm">
                {currentDocIndex + 1} / {documents.length}
              </span>
              <button
                onClick={() => setShowViewer(false)}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Main Viewer Area */}
          <div className="flex-1 flex items-center justify-center relative px-20">
            {/* Left Arrow */}
            <button
              onClick={() => navigateDoc(-1)}
              disabled={currentDocIndex === 0}
              className="absolute left-4 p-3 bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed rounded-full transition-colors"
            >
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            {/* Document Preview */}
            <div className="w-full max-w-4xl h-[70vh] rounded-xl overflow-hidden shadow-2xl bg-white">
              {currentDoc?.type === 'pdf' || currentDoc?.preview?.endsWith('.pdf') ? (
                <iframe
                  src={`${currentDoc?.preview}#toolbar=1&view=FitH`}
                  className="w-full h-full"
                  title={currentDoc?.name}
                />
              ) : (
                <img
                  src={currentDoc?.preview}
                  alt={currentDoc?.name}
                  className="max-w-full max-h-[70vh] object-contain"
                />
              )}
            </div>

            {/* Right Arrow */}
            <button
              onClick={() => navigateDoc(1)}
              disabled={currentDocIndex === documents.length - 1}
              className="absolute right-4 p-3 bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:cursor-not-allowed rounded-full transition-colors"
            >
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          {/* Action Buttons (only for pending) */}
          {currentDoc?.status === 'pending' && (
            <div className="flex justify-center gap-4 py-4">
              <button
                onClick={() => handleDocumentAction(currentDoc.id, 'approved')}
                className="flex items-center gap-2 px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl font-medium transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Aprobar Documento
              </button>
              <button
                onClick={() => openRejectModal(currentDoc.id)}
                className="flex items-center gap-2 px-8 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Rechazar Documento
              </button>
            </div>
          )}

          {/* Thumbnail Strip */}
          <div className="bg-black/50 px-6 py-4">
            <div className="flex justify-center gap-2 overflow-x-auto">
              {documents.map((doc, index) => (
                <button
                  key={doc.id}
                  onClick={() => setCurrentDocIndex(index)}
                  className={`relative flex-shrink-0 w-16 h-20 rounded-lg overflow-hidden border-2 transition-all ${
                    index === currentDocIndex 
                      ? 'border-primary-500 ring-2 ring-primary-500/50' 
                      : 'border-transparent hover:border-white/50'
                  }`}
                >
                  {doc.type === 'pdf' || doc.preview?.endsWith('.pdf') ? (
                    <div className="w-full h-full bg-red-50 flex items-center justify-center">
                      <svg className="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 24 24">
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
                  {/* Mini status indicator */}
                  {doc.status !== 'pending' && (
                    <div className={`absolute inset-0 ${
                      doc.status === 'approved' ? 'bg-green-500/30' : 'bg-red-500/30'
                    }`}>
                      <div className={`absolute top-1 right-1 w-3 h-3 rounded-full ${
                        doc.status === 'approved' ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      <Modal
        isOpen={showRejectModal}
        onClose={() => {
          setShowRejectModal(false)
          setRejectingDocId(null)
          setRejectReason('')
        }}
        title={`Rechazar: ${documents.find(d => d.id === rejectingDocId)?.name}`}
        size="md"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Indica el motivo del rechazo. Esta información será visible para el cliente.
          </p>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Motivo del rechazo
            </label>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
              rows={4}
              placeholder="Ej: El documento está ilegible, se requiere una nueva copia con mejor resolución..."
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              variant="secondary"
              className="flex-1"
              onClick={() => {
                setShowRejectModal(false)
                setRejectingDocId(null)
                setRejectReason('')
              }}
            >
              Cancelar
            </Button>
            <Button
              variant="danger"
              className="flex-1"
              onClick={handleRejectWithReason}
              disabled={!rejectReason.trim()}
            >
              Confirmar Rechazo
            </Button>
          </div>
        </div>
      </Modal>

      {/* Approve Modal */}
      <Modal
        isOpen={showApproveModal}
        onClose={() => setShowApproveModal(false)}
        title="Aprobar Solicitud"
        size="md"
      >
        <div className="space-y-4">
          <div className="bg-green-50 rounded-xl p-4 flex items-start gap-3">
            <svg className="w-6 h-6 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="font-medium text-green-800">Todos los documentos aprobados</p>
              <p className="text-sm text-green-700">
                {documents.length} documentos han sido revisados y aprobados.
              </p>
            </div>
          </div>

          <p className="text-gray-600">
            Al aprobar esta solicitud, podrás enviarla a la embajada para su revisión final.
          </p>

          <div className="flex gap-3 pt-4">
            <Button
              variant="secondary"
              className="flex-1"
              onClick={() => setShowApproveModal(false)}
            >
              Cancelar
            </Button>
            <Button
              className="flex-1"
              onClick={async () => {
                try {
                  // First transition to en_revision if not already
                  if (applicationData?.status === 'pendiente') {
                    await solicitudesService.actualizarSolicitud(id, { estado: 'en_revision' })
                  }
                  // Then approve
                  await solicitudesService.actualizarSolicitud(id, { estado: 'aprobada' })
                  setShowApproveModal(false)
                  navigate('/asesor/solicitudes')
                } catch (error) {
                  console.error('Error al aprobar:', error)
                }
              }}
            >
              Confirmar Aprobación
            </Button>
          </div>
        </div>
      </Modal>

      {/* Split View Modal para revisión de documentos */}
      <SplitViewModal
        isOpen={showSplitView}
        onClose={() => setShowSplitView(false)}
        documents={documents}
        initialIndex={documents.findIndex(d => d.status === 'pending')}
        onApprove={handleSplitViewApprove}
        onReject={handleSplitViewReject}
      />
    </div>
  )
}
