import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
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

export default function AdvisorFeedbackViewPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [loading, setLoading] = useState(true)
  const [simulacro, setSimulacro] = useState(null)
  const [recomendacion, setRecomendacion] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Obtener el simulacro (ahora incluye la recomendación embebida)
        const simData = await simulacrosService.getSimulacro(id)
        setSimulacro(simData)
        
        // La recomendación ahora viene embebida en el simulacro
        if (simData?.recomendacion) {
          setRecomendacion(simData.recomendacion)
        }
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('No se pudo cargar la información del feedback')
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
  }, [id])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Cargando feedback...</p>
        </div>
      </div>
    )
  }

  if (error || !simulacro) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <Card className="text-center py-12">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">{error || 'Simulacro no encontrado'}</h2>
          <p className="text-gray-500 mb-6">
            No se pudo cargar la información del simulacro.
          </p>
          <Button onClick={() => navigate('/asesor/simulacros')}>
            Volver a Simulacros
          </Button>
        </Card>
      </div>
    )
  }

  if (!recomendacion) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <Card className="text-center py-12">
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Sin feedback aún</h2>
          <p className="text-gray-500 mb-6">
            Este simulacro aún no tiene feedback generado.
          </p>
          <div className="flex gap-4 justify-center">
            <Button variant="secondary" onClick={() => navigate('/asesor/simulacros')}>
              Volver
            </Button>
            <Button onClick={() => navigate(`/asesor/simulacros/${id}/presencial`)}>
              Agregar Feedback
            </Button>
          </div>
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
  const resumenEjecutivo = recomendacion?.resumen_ejecutivo || ''
  const esGeneradoPorIA = recomendacion?.analisis_raw?.tipo !== 'manual'

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button 
            onClick={() => navigate('/asesor/simulacros')}
            className="text-primary-600 hover:text-primary-700 flex items-center gap-2 mb-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Volver a Simulacros
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Feedback del Simulacro</h1>
          <p className="text-gray-500">
            Cliente: {simulacro.cliente_nombre || simulacro.cliente?.nombre || 'Cliente'} • 
            {simulacro.fecha && ` ${new Date(simulacro.fecha).toLocaleDateString('es-ES', {
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })}`}
          </p>
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
              {nivelPreparacion === 'alto' ? 'Excelente preparación' : 
               nivelPreparacion === 'medio' ? 'Buen progreso' : 
               'Requiere más práctica'}
            </h2>
            <p className="text-primary-100">{accionSugerida}</p>
          </div>
        </div>
      </Card>

      {/* Indicadores */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Indicadores de Desempeño</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(indicadores).map(([key, value]) => (
            <div key={key} className={`p-4 rounded-xl border ${INDICADOR_COLORS[value]}`}>
              <p className="text-sm font-medium capitalize">{key}</p>
              <p className="text-lg font-bold">{INDICADOR_LABELS[value]}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Fuente del feedback */}
      <div className="flex items-center gap-2">
        {esGeneradoPorIA ? (
          <Badge variant="info" className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Generado con IA (Gemini)
          </Badge>
        ) : (
          <Badge variant="secondary" className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Feedback manual del asesor
          </Badge>
        )}
      </div>

      {/* Comentarios del Asesor / Resumen */}
      {resumenEjecutivo && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💬 Comentarios del Asesor</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-700 whitespace-pre-wrap">{resumenEjecutivo}</p>
          </div>
        </Card>
      )}

      {/* Fortalezas */}
      {fortalezas.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💪 Fortalezas Identificadas</h3>
          <div className="space-y-3">
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
        </Card>
      )}

      {/* Puntos de Mejora */}
      {puntosMejora.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 Puntos de Mejora</h3>
          <div className="space-y-3">
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
        </Card>
      )}

      {/* Recomendaciones */}
      {recomendaciones.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Recomendaciones</h3>
          <div className="space-y-4">
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
        </Card>
      )}

      {/* Transcripción (si está disponible) */}
      {simulacro.transcripcion_texto && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📝 Transcripción</h3>
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
              {simulacro.transcripcion_texto}
            </pre>
          </div>
        </Card>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <Button variant="secondary" onClick={() => navigate('/asesor/simulacros')}>
          Volver a Simulacros
        </Button>
      </div>
    </div>
  )
}
