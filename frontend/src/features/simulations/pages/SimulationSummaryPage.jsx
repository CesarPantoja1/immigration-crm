import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Card, Button, Badge } from '../../../components/common'
import { simulacrosService } from '../../../services/simulacrosService'

export default function SimulationSummaryPage() {
  const { id } = useParams()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSimulacro = async () => {
      try {
        const data = await simulacrosService.getSimulacro(id)
        // Transform data to match component format
        const formattedDate = new Date(data.fecha).toLocaleDateString('es-ES', {
          day: 'numeric',
          month: 'long',
          year: 'numeric'
        })
        setSummary({
          id: data.id,
          date: formattedDate,
          startTime: data.hora_inicio || data.hora,
          endTime: data.hora_fin || '',
          duration: data.duracion || '30 minutos',
          advisor: data.asesor?.nombre || data.asesor_nombre || 'Por asignar',
          visaType: data.tipo_visa || 'Visa General',
          modality: data.modalidad === 'virtual' ? 'Virtual' : 'Presencial',
          status: data.estado
        })
      } catch (error) {
        console.error('Error fetching simulacro:', error)
        // Fallback to mock data for demo
        setSummary({
          id: id,
          date: new Date().toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' }),
          startTime: '10:00 AM',
          endTime: '10:28 AM',
          duration: '28 minutos',
          advisor: 'Asesor',
          visaType: 'Visa de Estudio',
          modality: 'Virtual',
          status: 'pending_feedback'
        })
      } finally {
        setLoading(false)
      }
    }
    fetchSimulacro()
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!summary) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Success Card */}
        <Card className="text-center relative overflow-hidden">
          {/* Decorative Background */}
          <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-r from-primary-500 to-primary-600" />
          
          {/* Content */}
          <div className="relative z-10 pt-8">
            {/* Success Icon */}
            <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto shadow-lg mb-6">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>

            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              ¡Simulacro Completado!
            </h1>
            <p className="text-gray-500 mb-8">
              Has finalizado tu simulacro de entrevista exitosamente
            </p>

            {/* Summary Details */}
            <div className="bg-gray-50 rounded-2xl p-6 mb-8">
              <div className="grid grid-cols-2 gap-4 text-left">
                <div>
                  <p className="text-sm text-gray-500">Fecha</p>
                  <p className="font-medium text-gray-900">{summary.date}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Duración</p>
                  <p className="font-medium text-gray-900">{summary.duration}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Horario</p>
                  <p className="font-medium text-gray-900">{summary.startTime} - {summary.endTime}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Asesor</p>
                  <p className="font-medium text-gray-900">{summary.advisor}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Tipo de Visa</p>
                  <p className="font-medium text-gray-900">{summary.visaType}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Modalidad</p>
                  <p className="font-medium text-gray-900">{summary.modality}</p>
                </div>
              </div>
            </div>

            {/* Feedback Status */}
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-8">
              <div className="flex items-center justify-center gap-3">
                <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="text-left">
                  <p className="font-medium text-amber-800">Pendiente de Feedback</p>
                  <p className="text-sm text-amber-700">
                    Recibirás el feedback de tu asesor en las próximas 24 horas
                  </p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button variant="secondary" className="flex-1">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Descargar Resumen
              </Button>
              <Link to="/dashboard" className="flex-1">
                <Button className="w-full">
                  Volver al Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </Card>

        {/* Additional Tips */}
        <div className="mt-6 text-center">
          <p className="text-gray-500 text-sm">
            ¿Quieres seguir preparándote?{' '}
            <Link to="/practica" className="text-primary-600 font-medium hover:text-primary-700">
              Prueba nuestra práctica individual →
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
