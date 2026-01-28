import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button, Card } from '../../../components/common'

// Mock questions database
const questionsDB = {
  estudio: [
    {
      id: 1,
      question: '¿Por qué eligió esta universidad en particular?',
      options: [
        'Por su prestigio y reconocimiento internacional en mi área de estudio',
        'Porque es la más barata',
        'Mi familia me obligó a elegirla',
        'No tengo una razón específica'
      ],
      correctAnswer: 0,
      explanation: 'Es importante demostrar que has investigado la institución y tienes razones académicas sólidas para tu elección.'
    },
    {
      id: 2,
      question: '¿Cómo financiará sus estudios?',
      options: [
        'No lo he pensado todavía',
        'Trabajaré ilegalmente durante mis estudios',
        'Tengo ahorros personales, apoyo familiar y/o una beca documentada',
        'Pediré dinero prestado cuando llegue'
      ],
      correctAnswer: 2,
      explanation: 'Debes demostrar solvencia económica con documentos que respalden tu capacidad de financiar tus estudios.'
    },
    {
      id: 3,
      question: '¿Cuáles son sus planes después de graduarse?',
      options: [
        'Quedarme a vivir permanentemente en el país',
        'Regresar a mi país para aplicar mis conocimientos y contribuir a su desarrollo',
        'Buscar cualquier trabajo que me permita quedarme',
        'No tengo planes definidos'
      ],
      correctAnswer: 1,
      explanation: 'Para una visa de estudiante, es fundamental demostrar la intención de regresar a tu país de origen.'
    },
    {
      id: 4,
      question: '¿Ha visitado este país anteriormente?',
      options: [
        'No, nunca he viajado al extranjero',
        'Sí, visité como turista y regresé a tiempo según mi visa',
        'Sí, pero me quedé más tiempo del permitido',
        'Prefiero no responder'
      ],
      correctAnswer: 1,
      explanation: 'El historial de viajes y cumplimiento de visas previas demuestra tu confiabilidad.'
    },
    {
      id: 5,
      question: '¿Qué carrera estudiará y por qué?',
      options: [
        'Cualquier cosa que me den visa',
        'Una carrera que me permita trabajar inmediatamente',
        'Una especialización en mi campo que no está disponible en mi país',
        'No estoy seguro todavía'
      ],
      correctAnswer: 2,
      explanation: 'Demuestra que tu elección académica tiene un propósito claro y beneficios para tu desarrollo profesional.'
    }
  ],
  trabajo: [
    {
      id: 1,
      question: '¿Puede describir sus responsabilidades en el puesto ofrecido?',
      options: [
        'No estoy seguro, solo quiero el trabajo',
        'Haré lo que me pidan',
        'Mi rol incluye [responsabilidades específicas] que requieren mis habilidades en [área de expertise]',
        'Es un trabajo como cualquier otro'
      ],
      correctAnswer: 2,
      explanation: 'Demuestra conocimiento detallado del puesto y cómo tus habilidades específicas son necesarias.'
    },
    {
      id: 2,
      question: '¿Por qué la empresa no contrató a alguien local?',
      options: [
        'No sé, pregúntele a ellos',
        'Porque soy más barato',
        'Mi combinación única de habilidades y experiencia en [especialización] es difícil de encontrar localmente',
        'Porque tengo contactos en la empresa'
      ],
      correctAnswer: 2,
      explanation: 'Justifica por qué la empresa necesita específicamente tus habilidades únicas.'
    },
    {
      id: 3,
      question: '¿Cuánto tiempo planea quedarse?',
      options: [
        'Para siempre',
        'El tiempo que dure mi contrato de trabajo, inicialmente X años',
        'No lo he pensado',
        'Hasta que encuentre algo mejor'
      ],
      correctAnswer: 1,
      explanation: 'Sé específico sobre la duración de tu contrato y tus planes profesionales.'
    }
  ],
  vivienda: [
    {
      id: 1,
      question: '¿Cuál es la fuente de sus ingresos para esta inversión?',
      options: [
        'Préstamos de varias fuentes',
        'Ahorros acumulados durante X años de trabajo en [industria/profesión]',
        'Prefiero no decirlo',
        'Herencia de origen desconocido'
      ],
      correctAnswer: 1,
      explanation: 'Es crucial demostrar el origen legítimo y documentado de tus fondos.'
    },
    {
      id: 2,
      question: '¿Por qué eligió invertir en este país?',
      options: [
        'Para escapar de mi país',
        'La estabilidad económica, el mercado inmobiliario y las oportunidades de inversión',
        'No tenía otra opción',
        'Para obtener la ciudadanía fácilmente'
      ],
      correctAnswer: 1,
      explanation: 'Demuestra que has investigado las ventajas económicas y legales de la inversión.'
    }
  ]
}

export default function QuizPage() {
  const { visaType } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [showExplanation, setShowExplanation] = useState(false)
  const [answers, setAnswers] = useState([])
  const [isComplete, setIsComplete] = useState(false)
  const [questions, setQuestions] = useState([])
  const [practicaId, setPracticaId] = useState(null)

  // Map frontend visa types to backend (solo 3 tipos)
  const tipoVisaMap = {
    'estudio': 'estudio',
    'trabajo': 'trabajo',
    'vivienda': 'vivienda'
  }

  useEffect(() => {
    const iniciarPractica = async () => {
      try {
        setLoading(true)
        const { practicaService } = await import('../../../services')
        const tipoVisa = tipoVisaMap[visaType] || visaType
        
        const data = await practicaService.iniciar(tipoVisa)
        
        setPracticaId(data.practica_id)
        // Transform API questions to component format
        const transformedQuestions = data.preguntas.map(p => ({
          id: p.id,
          question: p.pregunta,
          options: p.opciones,
          correctAnswer: p.respuesta_correcta,
          explanation: p.explicacion || 'Esta es la respuesta correcta para una entrevista de visa.'
        }))
        
        setQuestions(transformedQuestions)
      } catch (error) {
        console.error('Error starting practice:', error)
        // Fallback to local questions if API fails
        setQuestions(questionsDB[visaType] || [])
      } finally {
        setLoading(false)
      }
    }

    iniciarPractica()
  }, [visaType])

  const question = questions[currentQuestion]
  const progress = questions.length > 0 ? ((currentQuestion) / questions.length) * 100 : 0

  const handleSelectAnswer = (index) => {
    if (showExplanation) return
    setSelectedAnswer(index)
  }

  const handleConfirm = () => {
    if (selectedAnswer === null) return
    setShowExplanation(true)
    setAnswers(prev => [...prev, {
      questionId: question.id,
      selected: selectedAnswer,
      correct: question.correctAnswer,
      isCorrect: selectedAnswer === question.correctAnswer
    }])
  }

  const handleNext = async () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1)
      setSelectedAnswer(null)
      setShowExplanation(false)
    } else {
      // Send results to API
      if (practicaId) {
        try {
          const { practicaService } = await import('../../../services')
          const respuestas = answers.map(a => ({
            pregunta_id: a.questionId,
            respuesta_seleccionada: a.selected
          }))
          await practicaService.enviarRespuestas(practicaId, respuestas)
        } catch (error) {
          console.error('Error saving practice results:', error)
        }
      }
      setIsComplete(true)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Cargando preguntas...</p>
        </div>
      </div>
    )
  }

  if (!questions.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="text-center max-w-md">
          <div className="text-6xl mb-4">❓</div>
          <h1 className="text-xl font-bold text-gray-900 mb-2">Categoría no encontrada</h1>
          <p className="text-gray-500 mb-6">No hay preguntas disponibles para esta categoría</p>
          <Button onClick={() => navigate('/practica')}>Volver a práctica</Button>
        </Card>
      </div>
    )
  }

  if (isComplete) {
    const correctCount = answers.filter(a => a.isCorrect).length
    const percentage = Math.round((correctCount / questions.length) * 100)
    
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="text-center max-w-lg w-full">
          {/* Result Icon */}
          <div className={`w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6 ${
            percentage >= 80 ? 'bg-green-100' : percentage >= 60 ? 'bg-yellow-100' : 'bg-red-100'
          }`}>
            <span className="text-5xl">
              {percentage >= 80 ? '🎉' : percentage >= 60 ? '💪' : '📚'}
            </span>
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {percentage >= 80 ? '¡Excelente!' : percentage >= 60 ? '¡Buen trabajo!' : '¡Sigue practicando!'}
          </h1>
          <p className="text-gray-500 mb-8">
            Has completado el cuestionario de práctica
          </p>

          {/* Score Circle */}
          <div className="relative w-40 h-40 mx-auto mb-8">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="#e5e7eb"
                strokeWidth="12"
                fill="none"
              />
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke={percentage >= 80 ? '#22c55e' : percentage >= 60 ? '#eab308' : '#ef4444'}
                strokeWidth="12"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 70 * percentage / 100} ${2 * Math.PI * 70}`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-bold text-gray-900">{percentage}%</span>
              <span className="text-sm text-gray-500">de aciertos</span>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-2xl font-bold text-gray-900">{questions.length}</div>
              <div className="text-xs text-gray-500">Preguntas</div>
            </div>
            <div className="bg-green-50 rounded-xl p-4">
              <div className="text-2xl font-bold text-green-600">{correctCount}</div>
              <div className="text-xs text-gray-500">Correctas</div>
            </div>
            <div className="bg-red-50 rounded-xl p-4">
              <div className="text-2xl font-bold text-red-600">{questions.length - correctCount}</div>
              <div className="text-xs text-gray-500">Incorrectas</div>
            </div>
          </div>

          {/* Feedback Message */}
          <div className={`p-4 rounded-xl mb-6 ${
            percentage >= 80 ? 'bg-green-50 border border-green-200' : 
            percentage >= 60 ? 'bg-yellow-50 border border-yellow-200' : 
            'bg-red-50 border border-red-200'
          }`}>
            <p className={`text-sm ${
              percentage >= 80 ? 'text-green-800' : 
              percentage >= 60 ? 'text-yellow-800' : 
              'text-red-800'
            }`}>
              {percentage >= 80 
                ? '¡Estás muy bien preparado para tu entrevista! Considera agendar un simulacro real.'
                : percentage >= 60 
                ? 'Vas por buen camino. Repasa las preguntas que fallaste y vuelve a intentarlo.'
                : 'Te recomendamos estudiar más sobre este tipo de visa antes de tu entrevista.'}
            </p>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button 
              variant="secondary" 
              className="flex-1"
              onClick={() => {
                setCurrentQuestion(0)
                setSelectedAnswer(null)
                setShowExplanation(false)
                setAnswers([])
                setIsComplete(false)
              }}
            >
              Reintentar
            </Button>
            <Button 
              className="flex-1"
              onClick={() => navigate('/practica')}
            >
              Volver a categorías
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <button 
            onClick={() => navigate('/practica')}
            className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver
          </button>

          {/* Progress Bar */}
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Pregunta {currentQuestion + 1} de {questions.length}
            </span>
            <span className="text-sm text-gray-500">
              {Math.round(progress)}% completado
            </span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary-600 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <Card className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            {question.question}
          </h2>

          {/* Options */}
          <div className="space-y-3">
            {question.options.map((option, index) => {
              let optionClass = 'border-2 border-gray-200 hover:border-primary-300 hover:bg-primary-50'
              
              if (showExplanation) {
                if (index === question.correctAnswer) {
                  optionClass = 'border-2 border-green-500 bg-green-50'
                } else if (index === selectedAnswer && index !== question.correctAnswer) {
                  optionClass = 'border-2 border-red-500 bg-red-50'
                } else {
                  optionClass = 'border-2 border-gray-200 opacity-50'
                }
              } else if (selectedAnswer === index) {
                optionClass = 'border-2 border-primary-500 bg-primary-50'
              }

              return (
                <button
                  key={index}
                  onClick={() => handleSelectAnswer(index)}
                  disabled={showExplanation}
                  className={`w-full p-4 rounded-xl text-left transition-all ${optionClass}`}
                >
                  <div className="flex items-start gap-3">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 ${
                      showExplanation && index === question.correctAnswer
                        ? 'bg-green-500 text-white'
                        : showExplanation && index === selectedAnswer && index !== question.correctAnswer
                        ? 'bg-red-500 text-white'
                        : selectedAnswer === index
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {String.fromCharCode(65 + index)}
                    </span>
                    <span className="text-gray-700">{option}</span>
                  </div>
                </button>
              )
            })}
          </div>
        </Card>

        {/* Explanation */}
        {showExplanation && (
          <Card className="mb-6 bg-blue-50 border border-blue-200">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="font-medium text-blue-900 mb-1">Explicación</h3>
                <p className="text-blue-800 text-sm">{question.explanation}</p>
              </div>
            </div>
          </Card>
        )}

        {/* Action Button */}
        <div className="flex justify-end">
          {!showExplanation ? (
            <Button 
              onClick={handleConfirm}
              disabled={selectedAnswer === null}
            >
              Confirmar respuesta
            </Button>
          ) : (
            <Button onClick={handleNext}>
              {currentQuestion < questions.length - 1 ? 'Siguiente pregunta' : 'Ver resultados'}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
