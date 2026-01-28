import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../../contexts/AuthContext'
import { Card, Badge, StatCard } from '../../../components/common'
import { 
  solicitudesService, 
  simulacrosService, 
  practicaService,
  entrevistasService 
} from '../../../services'

export default function ClientDashboard() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    pendingApplications: 0,
    approvedDocuments: 0,
    upcomingSimulations: 0,
    practiceScore: 0
  })
  const [disponibilidad, setDisponibilidad] = useState({ disponibles: 2, usados: 0 })
  const [recentApplications, setRecentApplications] = useState([])
  const [upcomingSimulations, setUpcomingSimulations] = useState([])

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        
        // Fetch all data in parallel
        const [solicitudesResponse, simulacrosResponse, disponibilidadData, practicaResponse] = await Promise.all([
          solicitudesService.getAll({ limit: 5 }).catch(() => ({ results: [] })),
          simulacrosService.getMisSimulacros().catch(() => []),
          simulacrosService.getDisponibilidad().catch(() => ({ disponibles: 2, usados: 0 })),
          practicaService.getHistorial({ limit: 1 }).catch(() => [])
        ])

        // Handle both array and object with results
        const solicitudes = Array.isArray(solicitudesResponse) 
          ? solicitudesResponse 
          : (solicitudesResponse?.results || [])
        
        const simulacrosData = Array.isArray(simulacrosResponse) 
          ? simulacrosResponse 
          : (simulacrosResponse?.results || [])
        
        const practicaData = Array.isArray(practicaResponse) 
          ? practicaResponse 
          : (practicaResponse?.results || [])

        // Process solicitudes
        setRecentApplications(solicitudes.slice(0, 2).map(s => ({
          id: `SOL-${s.id}`,
          rawId: s.id,
          type: s.tipo_visa,
          embassy: s.embajada,
          status: s.estado,
          date: s.created_at?.split('T')[0]
        })))

        // Count pending applications
        const pending = solicitudes.filter(s => 
          ['borrador', 'pendiente', 'en_revision'].includes(s.estado)
        ).length

        // Count approved documents
        const approvedDocs = solicitudes.reduce((acc, s) => {
          const docs = s.documentos_adjuntos || []
          return acc + docs.filter(d => d.estado === 'aprobado').length
        }, 0)

        // Process simulacros
        const proximos = simulacrosData.filter(s => 
          ['propuesto', 'confirmado'].includes(s.estado)
        )
        setUpcomingSimulations(proximos.slice(0, 1).map(s => ({
          id: s.id,
          date: s.fecha_propuesta,
          time: s.hora_propuesta,
          advisor: s.asesor_nombre || 'Asesor asignado',
          modality: 'Virtual',
          visaType: s.solicitud_tipo || 'Entrevista'
        })))

        // Get disponibilidad - normalizar respuesta
        const disponibilidadNormalizada = {
          disponibles: disponibilidadData?.simulacros_disponibles ?? disponibilidadData?.disponibles ?? 2,
          usados: disponibilidadData?.simulacros_realizados ?? disponibilidadData?.usados ?? 0
        }
        setDisponibilidad(disponibilidadNormalizada)

        // Get last practice score
        const lastPractice = practicaData[0]
        const practiceScore = lastPractice?.porcentaje_aciertos || 0

        setStats({
          pendingApplications: pending,
          approvedDocuments: approvedDocs,
          upcomingSimulations: proximos.length,
          practiceScore: Math.round(practiceScore)
        })

      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const simulationsUsed = disponibilidad.usados
  const simulationsTotal = disponibilidad.usados + disponibilidad.disponibles

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Cargando tu dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-3xl p-8 text-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              ¡Hola, {user?.name?.split(' ')[0]}! 👋
            </h1>
            <p className="text-primary-100 text-lg">
              Bienvenido de vuelta. Aquí está el resumen de tu proceso migratorio.
            </p>
          </div>
          <Link
            to="/nueva-solicitud"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-primary-600 font-semibold rounded-xl hover:bg-primary-50 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nueva Solicitud
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Solicitudes Pendientes"
          value={stats.pendingApplications}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
          color="amber"
        />
        <StatCard
          title="Documentos Aprobados"
          value={stats.approvedDocuments}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          color="green"
        />
        <StatCard
          title="Próximo Simulacro"
          value={stats.upcomingSimulations}
          subtitle="En 2 días"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          }
          color="primary"
        />
        <StatCard
          title="Práctica Individual"
          value={`${stats.practiceScore}%`}
          subtitle="Último resultado"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
          color="blue"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Applications */}
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Solicitudes Recientes</h2>
            <Link to="/solicitudes" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              Ver todas →
            </Link>
          </div>
          
          <div className="space-y-4">
            {recentApplications.map((app) => (
              <div key={app.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    app.type === 'study' ? 'bg-blue-100' :
                    app.type === 'work' ? 'bg-green-100' : 'bg-purple-100'
                  }`}>
                    {app.type === 'study' && (
                      <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                    )}
                    {app.type === 'work' && (
                      <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    )}
                    {app.type === 'residence' && (
                      <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                      </svg>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{app.id}</p>
                    <p className="text-sm text-gray-500">
                      {app.type === 'study' ? 'Visa de Estudio' : 
                       app.type === 'work' ? 'Visa de Trabajo' : 'Visa de Vivienda'} 
                      {' • '} Embajada {app.embassy === 'USA' ? 'Estados Unidos' : 'Brasil'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Badge 
                    variant={app.status === 'pending' ? 'warning' : app.status === 'reviewing' ? 'info' : 'success'}
                    dot
                  >
                    {app.status === 'pending' ? 'Pendiente' : 
                     app.status === 'reviewing' ? 'En revisión' : 'Aprobada'}
                  </Badge>
                  <Link 
                    to={`/solicitudes/${app.rawId}`}
                    className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Simulation Indicator & Upcoming */}
        <div className="space-y-6">
          {/* Simulation Counter */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-4">Simulacros Disponibles</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Utilizados</span>
                <span className="font-semibold">{simulationsUsed} de {simulationsTotal}</span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all ${
                    simulationsUsed === 0 ? 'bg-green-500' :
                    simulationsUsed === 1 ? 'bg-amber-500 w-1/2' : 'bg-red-500 w-full'
                  }`}
                  style={{ width: `${(simulationsUsed / simulationsTotal) * 100}%` }}
                />
              </div>
              <p className={`text-sm ${
                simulationsUsed < simulationsTotal ? 'text-gray-600' : 'text-red-600'
              }`}>
                {simulationsUsed < simulationsTotal 
                  ? `Puedes solicitar hasta ${simulationsTotal} simulacros en total`
                  : 'Has alcanzado el límite de simulacros por proceso'}
              </p>
              <Link
                to="/simulacros"
                className={`block w-full py-2.5 text-center font-medium rounded-xl transition-colors ${
                  simulationsUsed < simulationsTotal
                    ? 'bg-primary-600 text-white hover:bg-primary-700'
                    : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                }`}
              >
                {simulationsUsed < simulationsTotal ? 'Ver Simulacros' : 'Límite Alcanzado'}
              </Link>
            </div>
          </Card>

          {/* Upcoming Simulation */}
          {upcomingSimulations.length > 0 && (
            <Card className="border-l-4 border-l-primary-500">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">Próximo Simulacro</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {upcomingSimulations[0].date} • {upcomingSimulations[0].time}
                  </p>
                  <p className="text-sm text-gray-500">
                    Con {upcomingSimulations[0].advisor}
                  </p>
                  <div className="flex items-center gap-2 mt-3">
                    <Badge variant="primary">{upcomingSimulations[0].modality}</Badge>
                    <Badge variant="info">{upcomingSimulations[0].visaType}</Badge>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Quick Actions */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
            <div className="space-y-3">
              <Link
                to="/practica"
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Práctica Individual</p>
                  <p className="text-xs text-gray-500">Prepárate para tu entrevista</p>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
              
              <Link
                to="/nueva-solicitud"
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Nueva Solicitud</p>
                  <p className="text-xs text-gray-500">Registra una nueva visa</p>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
