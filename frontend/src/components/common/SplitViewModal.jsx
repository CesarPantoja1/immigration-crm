import { useState, useEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Button from './Button'
import Badge from './Badge'
import { DOCUMENT_CHECKLIST } from '../../store/constants'

/**
 * SplitViewModal - Modal de pantalla dividida para revisión de documentos
 * Izquierda: Visor de documento
 * Derecha: Herramientas de evaluación (Checklist + Observaciones)
 */
export default function SplitViewModal({
  isOpen,
  onClose,
  documents = [],
  initialIndex = 0,
  onApprove,
  onReject
}) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex)
  const [checklist, setChecklist] = useState({})
  const [observations, setObservations] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [zoom, setZoom] = useState(100)

  const currentDoc = documents[currentIndex]
  const allChecked = DOCUMENT_CHECKLIST.every(item => checklist[item.id])

  // Reset state when document changes
  useEffect(() => {
    setChecklist({})
    setObservations('')
    setZoom(100)
  }, [currentIndex])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return
      if (e.key === 'ArrowLeft') navigateDoc(-1)
      if (e.key === 'ArrowRight') navigateDoc(1)
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, currentIndex])

  const navigateDoc = useCallback((direction) => {
    const newIndex = currentIndex + direction
    if (newIndex >= 0 && newIndex < documents.length) {
      setCurrentIndex(newIndex)
    }
  }, [currentIndex, documents.length])

  const handleCheckChange = (itemId) => {
    setChecklist(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }))
  }

  const handleApprove = async () => {
    if (!allChecked) return
    setIsSubmitting(true)
    try {
      await onApprove?.(currentDoc.id, { checklist, observations })
      // Auto-navigate to next pending document
      const nextPending = documents.findIndex((d, i) => i > currentIndex && d.status === 'pending')
      if (nextPending !== -1) {
        setCurrentIndex(nextPending)
      } else {
        onClose()
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleReject = async () => {
    if (!observations.trim()) {
      alert('Las observaciones son obligatorias al rechazar un documento')
      return
    }
    setIsSubmitting(true)
    try {
      await onReject?.(currentDoc.id, { checklist, observations })
      // Auto-navigate to next pending document
      const nextPending = documents.findIndex((d, i) => i > currentIndex && d.status === 'pending')
      if (nextPending !== -1) {
        setCurrentIndex(nextPending)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

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

  if (!isOpen) return null

  return createPortal(
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-2xl shadow-2xl w-full max-w-7xl h-[90vh] flex flex-col overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center gap-4">
              <h2 className="text-xl font-bold text-gray-900">Revisión de Documento</h2>
              <span className="text-sm text-gray-500">
                {currentIndex + 1} de {documents.length}
              </span>
            </div>

            {/* Document Navigation */}
            <div className="flex items-center gap-2">
              {documents.map((doc, index) => (
                <button
                  key={doc.id}
                  onClick={() => setCurrentIndex(index)}
                  className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-medium transition-all ${
                    index === currentIndex
                      ? 'bg-primary-500 text-white'
                      : doc.status === 'approved'
                        ? 'bg-green-100 text-green-700'
                        : doc.status === 'rejected'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>

            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content - Split View */}
          <div className="flex-1 flex overflow-hidden">
            {/* Left Panel - Document Viewer */}
            <div className="flex-1 bg-gray-900 flex flex-col">
              {/* Document Header */}
              <div className="flex items-center justify-between px-4 py-3 bg-gray-800">
                <div className="flex items-center gap-3">
                  <span className="text-white font-medium">{currentDoc?.name}</span>
                  {getStatusBadge(currentDoc?.status)}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setZoom(z => Math.max(50, z - 25))}
                    className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                    </svg>
                  </button>
                  <span className="text-gray-400 text-sm w-12 text-center">{zoom}%</span>
                  <button
                    onClick={() => setZoom(z => Math.min(200, z + 25))}
                    className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Document Preview */}
              <div className="flex-1 overflow-auto flex items-center justify-center p-4">
                {currentDoc?.preview ? (
                  <img
                    src={currentDoc.preview}
                    alt={currentDoc.name}
                    className="max-w-full max-h-full object-contain rounded-lg shadow-lg transition-transform"
                    style={{ transform: `scale(${zoom / 100})` }}
                  />
                ) : (
                  <div className="text-gray-400 text-center">
                    <svg className="w-24 h-24 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p>Vista previa no disponible</p>
                  </div>
                )}
              </div>

              {/* Navigation Arrows */}
              <div className="absolute left-4 top-1/2 -translate-y-1/2 z-10">
                <button
                  onClick={() => navigateDoc(-1)}
                  disabled={currentIndex === 0}
                  className="p-2 bg-black/50 hover:bg-black/70 text-white rounded-full disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
              </div>
              <div className="absolute right-[400px] top-1/2 -translate-y-1/2 z-10">
                <button
                  onClick={() => navigateDoc(1)}
                  disabled={currentIndex === documents.length - 1}
                  className="p-2 bg-black/50 hover:bg-black/70 text-white rounded-full disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Right Panel - Evaluation Tools */}
            <div className="w-[400px] border-l border-gray-200 flex flex-col bg-white">
              <div className="flex-1 overflow-y-auto p-6">
                {/* Document Info */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{currentDoc?.name}</h3>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>{currentDoc?.filename}</span>
                    <span>{currentDoc?.size}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    Subido: {currentDoc?.uploadedAt}
                  </p>
                </div>

                {/* Checklist */}
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    Lista de Verificación
                  </h4>
                  <div className="space-y-2">
                    {DOCUMENT_CHECKLIST.map(item => (
                      <label
                        key={item.id}
                        className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all ${
                          checklist[item.id]
                            ? 'bg-green-50 border-green-200'
                            : 'bg-gray-50 border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={checklist[item.id] || false}
                          onChange={() => handleCheckChange(item.id)}
                          className="w-5 h-5 rounded border-gray-300 text-green-600 focus:ring-green-500"
                        />
                        <span className={`text-sm ${checklist[item.id] ? 'text-green-700' : 'text-gray-700'}`}>
                          {item.label}
                        </span>
                        {item.required && (
                          <span className="text-xs text-red-500 ml-auto">*</span>
                        )}
                      </label>
                    ))}
                  </div>
                </div>

                {/* Observations */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Observaciones
                    <span className="text-xs text-red-500">(obligatorio si rechaza)</span>
                  </h4>
                  <textarea
                    value={observations}
                    onChange={(e) => setObservations(e.target.value)}
                    placeholder="Ingrese observaciones sobre el documento..."
                    className="w-full h-32 px-4 py-3 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="p-6 border-t border-gray-200 bg-gray-50">
                {!allChecked && (
                  <p className="text-xs text-amber-600 mb-3 flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Complete todos los ítems del checklist para aprobar
                  </p>
                )}
                <div className="flex gap-3">
                  <Button
                    variant="danger"
                    className="flex-1"
                    onClick={handleReject}
                    disabled={isSubmitting || currentDoc?.status !== 'pending'}
                  >
                    {isSubmitting ? 'Procesando...' : 'Rechazar'}
                  </Button>
                  <Button
                    className="flex-1"
                    onClick={handleApprove}
                    disabled={!allChecked || isSubmitting || currentDoc?.status !== 'pending'}
                  >
                    {isSubmitting ? 'Procesando...' : 'Aprobar'}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>,
    document.body
  )
}
