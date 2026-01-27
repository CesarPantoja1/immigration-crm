import { useRef, useState } from 'react'

export default function FileUpload({
  accept = '.pdf',
  maxSize = 10, // MB
  onFileSelect,
  label = 'Arrastra tu documento aquí o haz clic para seleccionar',
  icon = null,
  className = ''
}) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    validateAndSetFile(droppedFile)
  }

  const handleChange = (e) => {
    const selectedFile = e.target.files[0]
    validateAndSetFile(selectedFile)
  }

  const validateAndSetFile = (selectedFile) => {
    setError('')
    
    if (!selectedFile) return

    // Check file type
    const allowedTypes = accept.split(',').map(t => t.trim())
    const fileType = '.' + selectedFile.name.split('.').pop().toLowerCase()
    
    if (!allowedTypes.includes(fileType) && !allowedTypes.includes('*')) {
      setError(`Solo se permiten archivos ${accept}`)
      return
    }

    // Check file size
    const sizeMB = selectedFile.size / (1024 * 1024)
    if (sizeMB > maxSize) {
      setError(`El archivo no puede superar ${maxSize}MB`)
      return
    }

    setFile(selectedFile)
    onFileSelect?.(selectedFile)
  }

  const removeFile = () => {
    setFile(null)
    onFileSelect?.(null)
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className={className}>
      {!file ? (
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all
            ${isDragging 
              ? 'border-primary-500 bg-primary-50' 
              : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            }
            ${error ? 'border-red-300 bg-red-50' : ''}
          `}
        >
          <input
            ref={inputRef}
            type="file"
            accept={accept}
            onChange={handleChange}
            className="hidden"
          />
          
          <div className="flex flex-col items-center">
            {icon || (
              <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-4 ${
                isDragging ? 'bg-primary-100' : 'bg-gray-100'
              }`}>
                <svg className={`w-7 h-7 ${isDragging ? 'text-primary-600' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
            )}
            
            <p className={`text-sm font-medium ${isDragging ? 'text-primary-700' : 'text-gray-700'}`}>
              {label}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              {accept.toUpperCase().replace(/\./g, '')} • Máximo {maxSize}MB
            </p>
          </div>
        </div>
      ) : (
        <div className="border border-gray-200 rounded-2xl p-4 bg-gray-50">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM14 3.5L18.5 8H14V3.5zM12 18c-.6 0-1-.4-1-1v-4h-.5c-.3 0-.5-.2-.5-.5s.2-.5.5-.5H12v-1c0-.6.4-1 1-1s1 .4 1 1v1h1.5c.3 0 .5.2.5.5s-.2.5-.5.5H14v4c0 .6-.4 1-1 1z"/>
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
              <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
            </div>
            <button
              onClick={removeFile}
              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {error && (
        <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </p>
      )}
    </div>
  )
}
