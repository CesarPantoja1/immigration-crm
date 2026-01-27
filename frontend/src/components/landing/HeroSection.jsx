import { useState } from 'react'

export default function HeroSection() {
  const [email, setEmail] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    // TODO: Handle email submission
    console.log('Email submitted:', email)
  }

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-blue-50">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-200 rounded-full opacity-30 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent-light rounded-full opacity-20 blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="text-center">
          {/* Decorative icons */}
          <div className="flex justify-center items-center space-x-4 mb-8">
            <div className="hero-icon w-16 h-16 bg-white rounded-2xl shadow-lg flex items-center justify-center transform hover:scale-110 transition-transform">
              <span className="text-3xl">📋</span>
            </div>
            <div className="hero-icon w-20 h-20 bg-white rounded-2xl shadow-xl flex items-center justify-center transform hover:scale-110 transition-transform">
              <span className="text-4xl">🌎</span>
            </div>
            <div className="hero-icon w-16 h-16 bg-white rounded-2xl shadow-lg flex items-center justify-center transform hover:scale-110 transition-transform">
              <span className="text-3xl">✈️</span>
            </div>
            <div className="hero-icon w-20 h-20 bg-white rounded-2xl shadow-xl flex items-center justify-center transform hover:scale-110 transition-transform">
              <span className="text-4xl">🎯</span>
            </div>
          </div>

          {/* Main Headline */}
          <h1 className="font-serif text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Tu Proceso Migratorio
            <span className="block bg-gradient-to-r from-primary-500 to-accent-dark bg-clip-text text-transparent">
              Simplificado y Automatizado
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-lg md:text-xl text-gray-600 mb-10">
            Gestiona tu solicitud migratoria de forma ágil y confiable. Prepárate para entrevistas con IA y mantente informado en cada etapa del proceso.
          </p>

          {/* Search/CTA Bar */}
          <form onSubmit={handleSubmit} className="max-w-xl mx-auto mb-8">
            <div className="flex flex-col sm:flex-row items-center gap-4 p-2 bg-white rounded-full shadow-xl border border-gray-100">
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Ingresa tu correo electrónico..." 
                className="flex-1 w-full px-6 py-3 bg-transparent text-gray-700 placeholder-gray-400 focus:outline-none"
              />
              <button 
                type="submit"
                className="w-full sm:w-auto px-8 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-full hover:shadow-lg hover:shadow-primary-500/30 transform hover:scale-105 transition-all duration-300"
              >
                Comenzar Gratis
              </button>
            </div>
          </form>

          <p className="text-primary-600 font-medium mb-8">
            ✨ Sin costo inicial • Asesoría personalizada
          </p>

          {/* Feature Pills */}
          <div className="flex flex-wrap justify-center gap-4">
            <a href="#solicitudes" className="group inline-flex items-center px-6 py-3 bg-white border-2 border-primary-100 rounded-full shadow-md hover:shadow-xl hover:border-primary-300 transition-all duration-300">
              <span className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-3 group-hover:bg-primary-200 transition-colors">
                📝
              </span>
              <span className="font-medium text-gray-700">Ingreso de Solicitudes</span>
            </a>
            <a href="#preparacion" className="group inline-flex items-center px-6 py-3 bg-white border-2 border-primary-100 rounded-full shadow-md hover:shadow-xl hover:border-primary-300 transition-all duration-300">
              <span className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-3 group-hover:bg-primary-200 transition-colors">
                🎯
              </span>
              <span className="font-medium text-gray-700">Preparación con IA</span>
            </a>
            <a href="#seguimiento" className="group inline-flex items-center px-6 py-3 bg-white border-2 border-primary-100 rounded-full shadow-md hover:shadow-xl hover:border-primary-300 transition-all duration-300">
              <span className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-3 group-hover:bg-primary-200 transition-colors">
                🔔
              </span>
              <span className="font-medium text-gray-700">Seguimiento en Tiempo Real</span>
            </a>
          </div>
        </div>
      </div>

      {/* Wave divider */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="white"/>
        </svg>
      </div>
    </section>
  )
}
