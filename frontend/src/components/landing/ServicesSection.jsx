const services = [
  {
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    title: 'Ingreso de Solicitudes',
    description: 'Proceso simplificado para recibir y gestionar solicitudes migratorias con agendamiento automático de entrevistas.',
    features: ['Recepción de solicitudes', 'Agendamiento de entrevistas'],
    gradient: 'from-primary-400 to-primary-600',
    checkColor: 'text-primary-500',
  },
  {
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    title: 'Preparación para Entrevistas',
    description: 'Simulacros de entrevista potenciados con IA y recomendaciones personalizadas para mejorar tu desempeño.',
    features: ['Simulación de entrevista', 'Generación de recomendaciones'],
    gradient: 'from-accent-light to-accent',
    checkColor: 'text-accent',
    badge: 'IA Incluida',
  },
  {
    icon: (
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
    ),
    title: 'Gestión de Notificaciones',
    description: 'Mantente informado en tiempo real sobre el estado de tu solicitud y coordina tus entrevistas fácilmente.',
    features: ['Seguimiento de solicitudes', 'Coordinación de entrevistas'],
    gradient: 'from-primary-500 to-primary-700',
    checkColor: 'text-primary-500',
  },
]

export default function ServicesSection() {
  return (
    <section id="servicios" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold mb-4">
            NUESTROS SERVICIOS
          </span>
          <h2 className="text-3xl md:text-4xl font-serif font-bold text-gray-900 mb-4">
            Todo lo que necesitas para tu proceso migratorio
          </h2>
          <p className="max-w-2xl mx-auto text-lg text-gray-600">
            Tres capacidades principales diseñadas para hacer tu experiencia migratoria más simple y efectiva.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <div 
              key={index}
              className="group relative bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl border border-gray-100 transition-all duration-300 hover:-translate-y-2"
            >
              {service.badge && (
                <div className="absolute -top-3 -right-3 px-3 py-1 bg-gradient-to-r from-accent-light to-accent text-white text-xs font-bold rounded-full shadow-lg">
                  {service.badge}
                </div>
              )}
              <div className={`w-16 h-16 bg-gradient-to-br ${service.gradient} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                {service.icon}
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">{service.title}</h3>
              <p className="text-gray-600 mb-6">{service.description}</p>
              <ul className="space-y-3 text-sm text-gray-600">
                {service.features.map((feature, idx) => (
                  <li key={idx} className="flex items-center">
                    <svg className={`w-5 h-5 ${service.checkColor} mr-2`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
