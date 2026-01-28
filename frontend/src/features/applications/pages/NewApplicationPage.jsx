import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, Badge, Button } from '../../../components/common'
import { solicitudesService } from '../../../services'

const VISA_TYPES = [
  {
    id: 'vivienda',
    name: 'Visa de Vivienda',
    description: 'Para establecer residencia permanente',
    icon: '🏠',
    documents: ['Pasaporte', 'Foto', 'Antecedentes Penales', 'Escrituras de Propiedad'],
    color: 'purple'
  },
  {
    id: 'trabajo',
    name: 'Visa de Trabajo',
    description: 'Para trabajar en el exterior',
    icon: '💼',
    documents: ['Pasaporte', 'Foto', 'Antecedentes Penales', 'Contrato de Trabajo'],
    color: 'green'
  },
  {
    id: 'estudio',
    name: 'Visa de Estudio',
    description: 'Para estudiar en instituciones extranjeras',
    icon: '📚',
    documents: ['Pasaporte', 'Foto', 'Antecedentes Penales', 'Certificado de Matrícula'],
    color: 'blue'
  }
]

const EMBASSIES = [
  { id: 'usa', name: 'Estados Unidos', flag: '🇺🇸' },
  { id: 'brasil', name: 'Brasil', flag: '🇧🇷' },
  { id: 'canada', name: 'Canadá', flag: '🇨🇦' },
  { id: 'espana', name: 'España', flag: '🇪🇸' }
]

export default function NewApplicationPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [selectedVisa, setSelectedVisa] = useState(null)
  const [selectedEmbassy, setSelectedEmbassy] = useState(null)
  const [files, setFiles] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleFileChange = (docName, file) => {
    setFiles(prev => ({ ...prev, [docName]: file }))
  }

  const handleSubmit = async () => {
    try {
      setIsSubmitting(true)
      setError(null)
      
      // Create application via API
      const solicitudData = {
        tipo_visa: selectedVisa,
        embajada: selectedEmbassy,
        estado: 'borrador'
      }
      
      const result = await solicitudesService.create(solicitudData)
      
      // Upload documents if any
      for (const [docName, file] of Object.entries(files)) {
        if (file) {
          await solicitudesService.uploadDocument(result.id, file, docName)
        }
      }
      
      // Submit application
      await solicitudesService.submit(result.id)
      
      navigate('/solicitudes')
    } catch (err) {
      console.error('Error creating application:', err)
      setError('Error al crear la solicitud. Por favor intenta de nuevo.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const currentVisaType = VISA_TYPES.find(v => v.id === selectedVisa)
  const allFilesUploaded = currentVisaType?.documents.every(doc => files[doc])

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link to="/solicitudes" className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-4">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Volver a solicitudes
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Nueva Solicitud de Visa</h1>
        <p className="text-gray-500 mt-2">Completa los pasos para registrar tu solicitud</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between relative">
          <div className="absolute left-0 right-0 top-1/2 h-0.5 bg-gray-200 -z-10" />
          {['Tipo de Visa', 'Embajada', 'Documentos', 'Confirmación'].map((label, i) => (
            <div key={label} className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm ${
                step > i + 1 ? 'bg-green-500 text-white' :
                step === i + 1 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'
              }`}>
                {step > i + 1 ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : i + 1}
              </div>
              <span className={`text-sm mt-2 ${step === i + 1 ? 'text-primary-600 font-medium' : 'text-gray-500'}`}>
                {label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Step 1: Visa Type */}
      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Selecciona el tipo de visa</h2>
          <div className="grid gap-4">
            {VISA_TYPES.map((visa) => (
              <Card
                key={visa.id}
                hover
                onClick={() => setSelectedVisa(visa.id)}
                className={`cursor-pointer transition-all ${
                  selectedVisa === visa.id 
                    ? 'ring-2 ring-primary-500 border-primary-500' 
                    : ''
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-14 h-14 rounded-xl flex items-center justify-center text-2xl ${
                    visa.color === 'purple' ? 'bg-purple-100' :
                    visa.color === 'green' ? 'bg-green-100' : 'bg-blue-100'
                  }`}>
                    {visa.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{visa.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">{visa.description}</p>
                    <div className="flex flex-wrap gap-2 mt-3">
                      {visa.documents.map(doc => (
                        <Badge key={doc} variant="default" size="sm">{doc}</Badge>
                      ))}
                    </div>
                  </div>
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                    selectedVisa === visa.id 
                      ? 'border-primary-500 bg-primary-500' 
                      : 'border-gray-300'
                  }`}>
                    {selectedVisa === visa.id && (
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
          <div className="flex justify-end mt-8">
            <Button onClick={() => setStep(2)} disabled={!selectedVisa}>
              Continuar
            </Button>
          </div>
        </div>
      )}

      {/* Step 2: Embassy */}
      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Selecciona la embajada</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {EMBASSIES.map((embassy) => (
              <Card
                key={embassy.id}
                hover
                onClick={() => setSelectedEmbassy(embassy.id)}
                className={`cursor-pointer transition-all ${
                  selectedEmbassy === embassy.id 
                    ? 'ring-2 ring-primary-500 border-primary-500' 
                    : ''
                }`}
              >
                <div className="flex items-center gap-4">
                  <span className="text-4xl">{embassy.flag}</span>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">Embajada de {embassy.name}</h3>
                  </div>
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                    selectedEmbassy === embassy.id 
                      ? 'border-primary-500 bg-primary-500' 
                      : 'border-gray-300'
                  }`}>
                    {selectedEmbassy === embassy.id && (
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
          <div className="flex justify-between mt-8">
            <Button variant="secondary" onClick={() => setStep(1)}>
              Atrás
            </Button>
            <Button onClick={() => setStep(3)} disabled={!selectedEmbassy}>
              Continuar
            </Button>
          </div>
        </div>
      )}

      {/* Step 3: Documents */}
      {step === 3 && currentVisaType && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Sube tus documentos</h2>
            <p className="text-gray-500">Todos los documentos deben estar en formato PDF</p>
          </div>

          <div className="space-y-4">
            {currentVisaType.documents.map((docName) => (
              <Card key={docName}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      files[docName] ? 'bg-green-100' : 'bg-gray-100'
                    }`}>
                      {files[docName] ? (
                        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{docName}</p>
                      {files[docName] ? (
                        <p className="text-sm text-green-600">{files[docName].name}</p>
                      ) : (
                        <p className="text-sm text-gray-500">PDF requerido</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {files[docName] && (
                      <button
                        onClick={() => handleFileChange(docName, null)}
                        className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    )}
                    <label className="px-4 py-2 bg-primary-50 text-primary-600 font-medium rounded-lg cursor-pointer hover:bg-primary-100 transition-colors">
                      {files[docName] ? 'Cambiar' : 'Subir'}
                      <input
                        type="file"
                        accept=".pdf"
                        className="hidden"
                        onChange={(e) => handleFileChange(docName, e.target.files[0])}
                      />
                    </label>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          <div className="flex justify-between mt-8">
            <Button variant="secondary" onClick={() => setStep(2)}>
              Atrás
            </Button>
            <Button onClick={() => setStep(4)} disabled={!allFilesUploaded}>
              Continuar
            </Button>
          </div>
        </div>
      )}

      {/* Step 4: Confirmation */}
      {step === 4 && currentVisaType && (
        <div className="space-y-6">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Confirma tu solicitud</h2>
            <p className="text-gray-500 mt-2">Revisa los detalles antes de enviar</p>
          </div>

          <Card>
            <div className="space-y-4">
              <div className="flex justify-between py-3 border-b border-gray-100">
                <span className="text-gray-500">Tipo de Visa</span>
                <span className="font-medium text-gray-900">{currentVisaType.name}</span>
              </div>
              <div className="flex justify-between py-3 border-b border-gray-100">
                <span className="text-gray-500">Embajada</span>
                <span className="font-medium text-gray-900">
                  {EMBASSIES.find(e => e.id === selectedEmbassy)?.name}
                </span>
              </div>
              <div className="py-3">
                <span className="text-gray-500 block mb-3">Documentos adjuntos</span>
                <div className="space-y-2">
                  {currentVisaType.documents.map(doc => (
                    <div key={doc} className="flex items-center gap-2 text-sm">
                      <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-gray-700">{doc}</span>
                      <span className="text-gray-400">({files[doc]?.name})</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>

          <div className="flex justify-between mt-8">
            <Button variant="secondary" onClick={() => setStep(3)}>
              Atrás
            </Button>
            <Button onClick={handleSubmit} loading={isSubmitting}>
              Enviar Solicitud
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
