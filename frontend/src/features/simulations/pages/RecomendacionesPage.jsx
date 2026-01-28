import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Card, Badge, Button } from '../../../components/common'
import { simulacrosService } from '../../../services/simulacrosService'

const INDICADOR_COLORS = {
  alto: 'bg-green-100 text-green-700 border-green-200',
  medio: 'bg-amber-100 text-amber-700 border-amber-200',
  bajo: 'bg-red-100 text-red-700 border-red-200'
}

const INDICADOR_LABELS = {
  alto: 'Alto',
  medio: 'Medio',
  bajo: 'Bajo'
}

export default function RecomendacionesPage() {
  const [searchParams] = useSearchParams()
  const simulacroId = searchParams.get('simulacro')
  
  const [loading, setLoading] = useState(true)
  const [recomendacion, setRecomendacion] = useState(null)
  const [error, setError] = useState(null)
  const [expandedSection, setExpandedSection] = useState('indicadores')

  useEffect(() => {
    const fetchRecomendacion = async () => {
      try {
        setLoading(true)
        setError(null)
        
        let data
        if (simulacroId) {
          data = await simulacrosService.getMiRecomendacion(simulacroId)
        } else {
          // Si no hay simulacro específico, obtener la última recomendación
          const recomendaciones = await simulacrosService.getMisRecomendaciones()
          data = Array.isArray(recomendaciones) ? recomendaciones[0] : recomendaciones?.results?.[0]
        }
        
        if (!data) {
          setError('No se encontraron recomendaciones')
          return
        }
        
        setRecomendacion(data)
      } catch (err) {
        console.error('Error fetching recomendacion:', err)
        setError('No se pudieron cargar las recomendaciones')
      } finally {
        setLoading(false)
      }
    }
    
    fetchRecomendacion()
  }, [simulacroId])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Cargando recomendaciones...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full text-center py-12">
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">{error}</h2>
          <p className="text-gray-500 mb-6">
            Aún no tienes recomendaciones disponibles. Completa un simulacro para recibir feedback de tu asesor.
          </p>
          <Link to="/simulacros">
            <Button>Ir a Mis Simulacros</Button>
          </Link>
        </Card>
      </div>
    )
  }

  const indicadores = {
    claridad: recomendacion?.claridad || 'medio',
    coherencia: recomendacion?.coherencia || 'medio',
    seguridad: recomendacion?.seguridad || 'medio',
    pertinencia: recomendacion?.pertinencia || 'medio'
  }

  const fortalezas = recomendacion?.fortalezas || []
  const puntosMejora = recomendacion?.puntos_mejora || []
  const recomendaciones = recomendacion?.recomendaciones || []
  const nivelPreparacion = recomendacion?.nivel_preparacion || 'medio'
  const accionSugerida = recomendacion?.accion_sugerida || ''

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <Link to="/simulacros" className="text-primary-600 hover:text-primary-700 flex items-center gap-2 mb-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Volver a Simulacros
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Recomendaciones de tu Simulacro</h1>
            {recomendacion?.simulacro_fecha && (
              <p className="text-gray-500">
                Simulacro del {new Date(recomendacion.simulacro_fecha).toLocaleDateString('es-ES', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric'
                })}
              </p>
            )}
          </div>
          <Badge 
            variant={nivelPreparacion === 'alto' ? 'success' : nivelPreparacion === 'medio' ? 'warning' : 'error'}
            className="text-sm px-3 py-1"
          >
            Nivel: {INDICADOR_LABELS[nivelPreparacion]}
          </Badge>
        </div>

        {/* Nivel de Preparación Card */}
        <Card className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
          <div className="flex items-center gap-4">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
              nivelPreparacion === 'alto' ? 'bg-green-400' : 
              nivelPreparacion === 'medio' ? 'bg-amber-400' : 'bg-red-400'
            }`}>
              {nivelPreparacion === 'alto' ? (
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : nivelPreparacion === 'medio' ? (
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01" />
                </svg>
              ) : (
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01" />
                </svg>
              )}
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold">
                {nivelPreparacion === 'alto' ? '¡Excelente preparación!' : 
                 nivelPreparacion === 'medio' ? 'Buen progreso, sigue adelante' : 
                 'Necesitas más práctica'}
              </h2>
              <p className="text-primary-100">{accionSugerida}</p>
            </div>
          </div>
        </Card>

        {/* Indicadores */}
        <Card>
          <button 
            onClick={() => setExpandedSection(expandedSection === 'indicadores' ? '' : 'indicadores')}
            className="w-full flex items-center justify-between"
          >
            <h3 className="text-lg font-semibold text-gray-900">📊 Indicadores de Desempeño</h3>
            <svg className={`w-5 h-5 text-gray-400 transition-transform ${expandedSection === 'indicadores' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {expandedSection === 'indicadores' && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(indicadores).map(([key, value]) => (
                <div key={key} className={`p-4 rounded-xl border ${INDICADOR_COLORS[value]}`}>
                  <p className="text-sm font-medium capitalize">{key}</p>
                  <p className="text-lg font-bold">{INDICADOR_LABELS[value]}</p>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Fortalezas */}
        {fortalezas.length > 0 && (
          <Card>
            <button 
              onClick={() => setExpandedSection(expandedSection === 'fortalezas' ? '' : 'fortalezas')}
              className="w-full flex items-center justify-between"
            >
              <h3 className="text-lg font-semibold text-gray-900">💪 Fortalezas Identificadas</h3>
              <svg className={`w-5 h-5 text-gray-400 transition-transform ${expandedSection === 'fortalezas' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {expandedSection === 'fortalezas' && (
              <div className="mt-4 space-y-3">
                {fortalezas.map((f, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-green-800">{f.categoria || 'Fortaleza'}</p>
                      <p className="text-sm text-green-700">{f.descripcion}</p>
                      {f.pregunta_relacionada && (
                        <p className="text-xs text-green-600 mt-1">Pregunta: {f.pregunta_relacionada}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* Puntos de Mejora */}
        {puntosMejora.length > 0 && (
          <Card>
            <button 
              onClick={() => setExpandedSection(expandedSection === 'mejora' ? '' : 'mejora')}
              className="w-full flex items-center justify-between"
            >
              <h3 className="text-lg font-semibold text-gray-900">📈 Puntos de Mejora</h3>
              <svg className={`w-5 h-5 text-gray-400 transition-transform ${expandedSection === 'mejora' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {expandedSection === 'mejora' && (
              <div className="mt-4 space-y-3">
                {puntosMejora.map((p, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg">
                    <div className="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-amber-800">{p.categoria || 'Área de mejora'}</p>
                      <p className="text-sm text-amber-700">{p.descripcion}</p>
                      {p.pregunta_relacionada && (
                        <p className="text-xs text-amber-600 mt-1">Pregunta: {p.pregunta_relacionada}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* Recomendaciones */}
        {recomendaciones.length > 0 && (
          <Card>
            <button 
              onClick={() => setExpandedSection(expandedSection === 'recomendaciones' ? '' : 'recomendaciones')}
              className="w-full flex items-center justify-between"
            >
              <h3 className="text-lg font-semibold text-gray-900">💡 Recomendaciones</h3>
              <svg className={`w-5 h-5 text-gray-400 transition-transform ${expandedSection === 'recomendaciones' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {expandedSection === 'recomendaciones' && (
              <div className="mt-4 space-y-4">
                {recomendaciones.map((r, idx) => (
                  <div key={idx} className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 text-blue-600 font-bold">
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold text-blue-900">{r.titulo || r.categoria}</p>
                        <p className="text-sm text-blue-800 mt-1">{r.descripcion}</p>
                        {r.accion_concreta && (
                          <div className="mt-2 p-2 bg-blue-100 rounded text-sm text-blue-700">
                            <span className="font-medium">Acción:</span> {r.accion_concreta}
                          </div>
                        )}
                      </div>
                      {r.impacto && (
                        <Badge variant={r.impacto === 'alto' ? 'error' : r.impacto === 'medio' ? 'warning' : 'info'}>
                          {r.impacto}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Link to="/practica" className="flex-1">
            <Button variant="secondary" className="w-full">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              Practicar más
            </Button>
          </Link>
          <Link to="/simulacros" className="flex-1">
            <Button className="w-full">
              Volver a Simulacros
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
