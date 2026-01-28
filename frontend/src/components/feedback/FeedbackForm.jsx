import { useState } from 'react'
import { PERFORMANCE_CHECKLIST } from '../../store/constants'

/**
 * FeedbackForm - Formulario de retroalimentación del asesor
 * Usado después de simulacros presenciales
 */
export default function FeedbackForm({ simulation, onSubmit, onCancel }) {
  const [checklist, setChecklist] = useState({})
  const [scores, setScores] = useState({})
  const [notes, setNotes] = useState('')
  const [recommendations, setRecommendations] = useState('')
  const [overallScore, setOverallScore] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const categories = {
    basic: { name: 'Aspectos Básicos', color: 'blue' },
    communication: { name: 'Comunicación', color: 'purple' },
    interview: { name: 'Entrevista', color: 'green' }
  }

  const handleCheckChange = (itemId) => {
    setChecklist(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }))
  }

  const handleScoreChange = (itemId, score) => {
    setScores(prev => ({
      ...prev,
      [itemId]: score
    }))
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      await onSubmit?.({
        simulationId: simulation?.id,
        checklist,
        scores,
        notes,
        recommendations,
        overallScore,
        submittedAt: new Date().toISOString()
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const completedItems = Object.values(checklist).filter(Boolean).length
  const totalItems = PERFORMANCE_CHECKLIST.length
  const progress = (completedItems / totalItems) * 100

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-4 text-white">
        <h2 className="text-xl font-bold">Dashboard de Retroalimentación</h2>
        <p className="text-primary-100 text-sm mt-1">
          Simulacro presencial - {simulation?.clientName || 'Cliente'}
        </p>
      </div>

      {/* Progress */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Progreso de evaluación</span>
          <span className="text-sm font-medium text-gray-900">{completedItems}/{totalItems}</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-primary-500 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="p-6 space-y-8">
        {/* Checklist by Category */}
        {Object.entries(categories).map(([categoryId, category]) => (
          <div key={categoryId}>
            <h3 className={`font-semibold text-gray-900 mb-4 flex items-center gap-2`}>
              <span className={`w-3 h-3 rounded-full bg-${category.color}-500`} />
              {category.name}
            </h3>
            <div className="space-y-3">
              {PERFORMANCE_CHECKLIST.filter(item => item.category === categoryId).map(item => (
                <div 
                  key={item.id}
                  className={`flex items-center justify-between p-4 rounded-xl border-2 transition-all ${
                    checklist[item.id]
                      ? 'bg-green-50 border-green-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <label className="flex items-center gap-3 cursor-pointer flex-1">
                    <input
                      type="checkbox"
                      checked={checklist[item.id] || false}
                      onChange={() => handleCheckChange(item.id)}
                      className="w-5 h-5 rounded border-gray-300 text-green-600 focus:ring-green-500"
                    />
                    <span className={`text-sm ${checklist[item.id] ? 'text-green-700' : 'text-gray-700'}`}>
                      {item.label}
                    </span>
                  </label>

                  {/* Score Selector */}
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map(score => (
                      <button
                        key={score}
                        onClick={() => handleScoreChange(item.id, score)}
                        className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
                          scores[item.id] === score
                            ? 'bg-primary-500 text-white'
                            : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                        }`}
                      >
                        {score}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* Notes */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Notas y Observaciones</h3>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Anote observaciones específicas durante el simulacro..."
            className="w-full h-32 px-4 py-3 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {/* Recommendations */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Recomendaciones para el Cliente</h3>
          <textarea
            value={recommendations}
            onChange={(e) => setRecommendations(e.target.value)}
            placeholder="Escriba las recomendaciones que se enviarán al cliente..."
            className="w-full h-32 px-4 py-3 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {/* Overall Score */}
        <div className="bg-gray-50 rounded-xl p-6">
          <h3 className="font-semibold text-gray-900 mb-4 text-center">Puntuación General</h3>
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(score => (
              <button
                key={score}
                onClick={() => setOverallScore(score)}
                className={`w-10 h-10 rounded-xl text-sm font-bold transition-all ${
                  overallScore === score
                    ? score <= 3 ? 'bg-red-500 text-white' :
                      score <= 6 ? 'bg-amber-500 text-white' :
                      'bg-green-500 text-white'
                    : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                {score}
              </button>
            ))}
          </div>
          <p className="text-center text-sm text-gray-500 mt-3">
            {overallScore === 0 ? 'Seleccione una puntuación del 1 al 10' :
             overallScore <= 3 ? 'Necesita mejorar significativamente' :
             overallScore <= 6 ? 'Desempeño aceptable con áreas de mejora' :
             overallScore <= 8 ? 'Buen desempeño' :
             'Excelente desempeño'}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3">
        <button
          onClick={onCancel}
          className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-100 transition-colors"
        >
          Cancelar
        </button>
        <button
          onClick={handleSubmit}
          disabled={isSubmitting || overallScore === 0}
          className="flex-1 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? 'Enviando...' : 'Subir Retroalimentación'}
        </button>
      </div>
    </div>
  )
}
