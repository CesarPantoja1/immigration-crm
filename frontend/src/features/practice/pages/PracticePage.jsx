import { Link } from 'react-router-dom'
import { Card, Button, Badge } from '../../../components/common'

const visaTypes = [
  {
    id: 'estudio',
    title: 'Visa de Estudio',
    icon: '🎓',
    description: 'Prepárate para preguntas sobre tu programa académico, financiamiento y planes de retorno',
    questions: 25,
    duration: '20 min',
    difficulty: 'Intermedio',
    color: 'from-blue-500 to-blue-600'
  },
  {
    id: 'trabajo',
    title: 'Visa de Trabajo',
    icon: '💼',
    description: 'Practica respuestas sobre tu experiencia laboral, empresa patrocinadora y especialización',
    questions: 30,
    duration: '25 min',
    difficulty: 'Avanzado',
    color: 'from-purple-500 to-purple-600'
  },
  {
    id: 'vivienda',
    title: 'Visa de Vivienda',
    icon: '🏠',
    description: 'Domina preguntas sobre inversión inmobiliaria, fuentes de ingreso y permanencia',
    questions: 20,
    duration: '15 min',
    difficulty: 'Básico',
    color: 'from-green-500 to-green-600'
  },
  {
    id: 'turismo',
    title: 'Visa de Turismo',
    icon: '✈️',
    description: 'Practica el itinerario, lazos con tu país y demostración de solvencia económica',
    questions: 15,
    duration: '12 min',
    difficulty: 'Básico',
    color: 'from-orange-500 to-orange-600'
  }
]

const stats = [
  { value: '500+', label: 'Preguntas reales' },
  { value: '95%', label: 'Tasa de aprobación' },
  { value: '4.8', label: 'Calificación usuarios' }
]

export default function PracticePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-6xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="inline-block px-4 py-1 bg-white/20 rounded-full text-sm font-medium mb-4">
              Práctica Individual
            </span>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Prepárate a tu ritmo
            </h1>
            <p className="text-xl text-primary-100 max-w-2xl mx-auto mb-8">
              Practica con preguntas reales de entrevistas consulares. 
              Sin presión, sin límites, a tu propio ritmo.
            </p>

            {/* Stats */}
            <div className="flex justify-center gap-8 md:gap-16">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold">{stat.value}</div>
                  <div className="text-primary-200 text-sm">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Wave Separator */}
        <div className="relative h-16">
          <svg className="absolute bottom-0 w-full h-16 text-gray-50" viewBox="0 0 1440 54" preserveAspectRatio="none">
            <path fill="currentColor" d="M0 22L48 28.7C96 35.3 192 48.7 288 50C384 51.3 480 40.7 576 35.8C672 31 768 32 864 37.2C960 42.3 1056 51.7 1152 51.8C1248 52 1344 43 1392 38.5L1440 34V54H1392C1344 54 1248 54 1152 54C1056 54 960 54 864 54C768 54 672 54 576 54C480 54 384 54 288 54C192 54 96 54 48 54H0V22Z" />
          </svg>
        </div>
      </div>

      {/* Visa Type Cards */}
      <div className="max-w-6xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">
          Elige tu tipo de visa
        </h2>
        <p className="text-gray-500 text-center mb-8">
          Cada cuestionario está diseñado con preguntas específicas para tu caso
        </p>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {visaTypes.map((visa) => (
            <Link 
              key={visa.id} 
              to={`/practica/${visa.id}`}
              className="group"
            >
              <Card className="h-full hover:shadow-lg transition-all duration-300 group-hover:-translate-y-1 border-2 border-transparent group-hover:border-primary-200">
                {/* Icon */}
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${visa.color} flex items-center justify-center text-3xl mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  {visa.icon}
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {visa.title}
                </h3>
                <p className="text-gray-500 text-sm mb-4 line-clamp-3">
                  {visa.description}
                </p>

                {/* Meta */}
                <div className="flex items-center gap-3 text-sm">
                  <span className="text-gray-400">{visa.questions} preguntas</span>
                  <span className="text-gray-300">•</span>
                  <span className="text-gray-400">{visa.duration}</span>
                </div>

                <div className="mt-4">
                  <Badge 
                    variant={
                      visa.difficulty === 'Básico' ? 'success' :
                      visa.difficulty === 'Intermedio' ? 'warning' : 'danger'
                    }
                    size="sm"
                  >
                    {visa.difficulty}
                  </Badge>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* How it Works */}
      <div className="bg-white py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-12 text-center">
            ¿Cómo funciona?
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-bold text-xl mx-auto mb-4">
                1
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Elige tu categoría</h3>
              <p className="text-gray-500 text-sm">
                Selecciona el tipo de visa para la cual te estás preparando
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-bold text-xl mx-auto mb-4">
                2
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Responde preguntas</h3>
              <p className="text-gray-500 text-sm">
                Practica con preguntas reales de entrevistas consulares
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-bold text-xl mx-auto mb-4">
                3
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Recibe feedback</h3>
              <p className="text-gray-500 text-sm">
                Obtén retroalimentación instantánea y mejora tus respuestas
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gray-50 py-12">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            ¿Listo para tu simulacro real?
          </h2>
          <p className="text-gray-500 mb-6">
            Después de practicar, agenda un simulacro con uno de nuestros asesores expertos
          </p>
          <Link to="/simulacros">
            <Button size="lg">
              Ver mis simulacros
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
