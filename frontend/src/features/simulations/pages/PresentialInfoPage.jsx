import { useParams, useNavigate, Link } from 'react-router-dom'
import { Card, Badge, Button } from '../../../components/common'

// Mock simulation data
const MOCK_SIMULATION = {
  id: 3,
  type: 'presential',
  status: 'confirmed',
  date: '2026-02-05',
  time: '10:00',
  endTime: '10:45',
  advisor: {
    name: 'María González',
    photo: null,
    phone: '+57 300 123 4567'
  },
  location: {
    name: 'Oficina MigraFácil - Sede Norte',
    address: 'Calle Principal #123, Piso 4, Oficina 401',
    city: 'Bogotá',
    mapUrl: 'https://maps.google.com/?q=4.6097,-74.0817',
    lat: 4.6097,
    lng: -74.0817
  },
  instructions: [
    'Llegar 15 minutos antes de la hora programada',
    'Traer documento de identidad original',
    'Traer todos los documentos de tu solicitud de visa (originales y copias)',
    'Vestir de forma formal, similar a como asistirás a la entrevista real',
    'El simulacro durará aproximadamente 45 minutos'
  ],
  documents: [
    { name: 'Pasaporte', required: true },
    { name: 'Carta de oferta laboral', required: true },
    { name: 'Currículum vitae', required: true },
    { name: 'Certificado de antecedentes', required: true }
  ],
  visaType: 'Trabajo',
  applicationId: 'SOL-2024-001'
}

export default function PresentialInfoPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const simulation = MOCK_SIMULATION

  const formatDate = (dateStr) => {
    return new Date(dateStr + 'T00:00').toLocaleDateString('es-ES', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  }

  const handleCancel = () => {
    // Verificar reglas de cancelación
    const simulationDate = new Date(`${simulation.date}T${simulation.time}`)
    const now = new Date()
    const hoursUntil = (simulationDate - now) / (1000 * 60 * 60)

    if (hoursUntil < 24) {
      alert('No puedes cancelar con menos de 24 horas de anticipación.')
      return
    }

    if (confirm('¿Estás seguro de que deseas cancelar este simulacro?')) {
      // TODO: API call
      navigate('/simulacros')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-br from-amber-500 to-amber-600 text-white">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <button
            onClick={() => navigate('/simulacros')}
            className="flex items-center gap-2 text-amber-100 hover:text-white mb-4 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver a simulacros
          </button>

          <div className="flex items-center gap-3 mb-2">
            <span className="text-3xl">🏢</span>
            <h1 className="text-3xl font-bold">Simulacro Presencial</h1>
          </div>
          <p className="text-amber-100">
            {formatDate(simulation.date)} • {simulation.time} - {simulation.endTime}
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-3 gap-6">
          {/* Main Info */}
          <div className="md:col-span-2 space-y-6">
            {/* Location Card */}
            <Card>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Ubicación
              </h2>

              <div className="bg-gray-100 rounded-xl p-4 mb-4">
                <p className="font-medium text-gray-900">{simulation.location.name}</p>
                <p className="text-gray-600 mt-1">{simulation.location.address}</p>
                <p className="text-gray-500 text-sm">{simulation.location.city}</p>
              </div>

              {/* Map placeholder */}
              <div className="bg-gray-200 rounded-xl h-48 flex items-center justify-center mb-4">
                <div className="text-center text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                  <p className="text-sm">Mapa interactivo</p>
                </div>
              </div>

              <a
                href={simulation.location.mapUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 w-full py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-xl transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Abrir en Google Maps
              </a>
            </Card>

            {/* Instructions */}
            <Card>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Instrucciones
              </h2>

              <ul className="space-y-3">
                {simulation.instructions.map((instruction, index) => (
                  <li key={index} className="flex gap-3">
                    <span className="w-6 h-6 bg-amber-100 text-amber-700 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                      {index + 1}
                    </span>
                    <span className="text-gray-700">{instruction}</span>
                  </li>
                ))}
              </ul>
            </Card>

            {/* Documents to bring */}
            <Card>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Documentos a Llevar
              </h2>

              <div className="space-y-2">
                {simulation.documents.map((doc, index) => (
                  <div 
                    key={index}
                    className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl"
                  >
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <span className="text-gray-700 flex-1">{doc.name}</span>
                    {doc.required && (
                      <Badge variant="warning" size="sm">Requerido</Badge>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                <p className="text-amber-800 text-sm">
                  <strong>Importante:</strong> Traer documentos originales y una copia de cada uno.
                </p>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Advisor Info */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-4">Tu Asesor</h3>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-14 h-14 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-xl font-bold">
                  {simulation.advisor.name.charAt(0)}
                </div>
                <div>
                  <p className="font-medium text-gray-900">{simulation.advisor.name}</p>
                  <p className="text-sm text-gray-500">Asesor de Migración</p>
                </div>
              </div>
              <a
                href={`tel:${simulation.advisor.phone}`}
                className="flex items-center justify-center gap-2 w-full py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                {simulation.advisor.phone}
              </a>
            </Card>

            {/* Date & Time Summary */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-4">Resumen</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Fecha</span>
                  <span className="text-gray-900 font-medium">
                    {new Date(simulation.date + 'T00:00').toLocaleDateString('es-ES', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric'
                    })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Hora</span>
                  <span className="text-gray-900 font-medium">{simulation.time}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Duración</span>
                  <span className="text-gray-900 font-medium">~45 min</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Tipo de Visa</span>
                  <span className="text-gray-900 font-medium">{simulation.visaType}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Modalidad</span>
                  <Badge variant="warning" size="sm">Presencial</Badge>
                </div>
              </div>
            </Card>

            {/* Action - Only Cancel allowed for presential */}
            <Card className="bg-red-50 border-red-100">
              <h3 className="font-semibold text-red-800 mb-2">¿Necesitas cancelar?</h3>
              <p className="text-sm text-red-700 mb-4">
                Solo puedes cancelar con más de 24 horas de anticipación.
              </p>
              <Button
                variant="danger"
                className="w-full"
                onClick={handleCancel}
              >
                Cancelar Simulacro
              </Button>
            </Card>

            {/* Add to Calendar */}
            <button className="w-full flex items-center justify-center gap-2 py-3 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 font-medium rounded-xl transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Agregar al calendario
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
