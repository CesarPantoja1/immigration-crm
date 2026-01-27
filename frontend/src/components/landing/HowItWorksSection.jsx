const steps = [
  {
    number: 1,
    emoji: '📝',
    title: 'Ingresa tu Solicitud',
    titleColor: 'text-primary-600',
    gradient: 'from-primary-500 to-primary-600',
    description: [
      'Completa tu información personal y los datos de tu trámite migratorio. Nuestro sistema guiará cada paso.',
      'Sube los documentos requeridos de forma segura y organizada.',
      'Recibe confirmación inmediata y tu número de seguimiento único.',
    ],
  },
  {
    number: 2,
    emoji: '✨',
    title: 'Prepárate con IA',
    titleColor: 'text-accent',
    gradient: 'from-accent-light to-accent',
    description: [
      'Practica con simulacros de entrevista diseñados específicamente para tu tipo de visa.',
      'La IA analiza tus respuestas y genera recomendaciones personalizadas.',
      'Recibe feedback inmediato para mejorar tu desempeño.',
    ],
  },
  {
    number: 3,
    emoji: '🎉',
    title: 'Sigue tu Proceso',
    titleColor: 'text-primary-700',
    gradient: 'from-primary-600 to-primary-700',
    description: [
      'Recibe notificaciones en tiempo real sobre cada actualización de tu caso.',
      'Coordina tus entrevistas desde la plataforma.',
      'Mantén todo organizado en un solo lugar hasta obtener tu resultado.',
    ],
  },
]

export default function HowItWorksSection() {
  return (
    <section id="como-funciona" className="py-20 bg-gradient-to-br from-gray-50 to-primary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold mb-4">
            PROCESO SIMPLE
          </span>
          <h2 className="text-3xl md:text-4xl font-serif font-bold text-gray-900 mb-4">
            ¿Cómo funciona?
          </h2>
          <p className="max-w-2xl mx-auto text-lg text-gray-600">
            MigraFácil utiliza tecnología avanzada para guiarte en cada paso de tu proceso migratorio.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step) => (
            <div 
              key={step.number}
              className="relative bg-white rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <div className={`absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br ${step.gradient} rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg`}>
                {step.number}
              </div>
              <div className="text-4xl mb-4 mt-4">{step.emoji}</div>
              <h3 className={`text-xl font-bold ${step.titleColor} mb-4`}>{step.title}</h3>
              <div className="text-gray-600 leading-relaxed space-y-4">
                {step.description.map((text, idx) => (
                  <p key={idx}>{text}</p>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
