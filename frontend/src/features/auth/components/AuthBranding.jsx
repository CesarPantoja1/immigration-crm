import { Link } from 'react-router-dom'

export default function AuthBranding() {
  return (
    <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 relative overflow-hidden">
      {/* Background Pattern - Reduced opacity */}
      <div className="absolute inset-0">
        {/* Gradient Orbs - More subtle */}
        <div className="absolute top-20 left-20 w-72 h-72 bg-primary-400/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-accent-light/8 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-white/3 rounded-full blur-2xl" />
        
        {/* Grid Pattern - More subtle */}
        <div 
          className="absolute inset-0 opacity-[0.09] bg-repeat"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />
      </div>

      {/* Content - Centered */}
      <div className="relative z-10 flex flex-col items-center justify-center p-12 w-full text-center">
        {/* Logo at top */}
        <Link to="/" className="absolute top-12 left-12 flex items-center space-x-3 group">
          <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20 group-hover:bg-white/20 transition-colors">
            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span className="text-2xl font-bold text-white">MigraFácil</span>
        </Link>

        {/* Main Content - Centered */}
        <div className="max-w-lg space-y-8">
          {/* Floating Icons */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/20 animate-float">
              <span className="text-3xl">🌎</span>
            </div>
            <div className="w-14 h-14 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20 animate-float-delayed">
              <span className="text-2xl">✈️</span>
            </div>
          </div>

          <h1 className="text-5xl xl:text-6xl font-bold text-white leading-tight">
            Tu proceso migratorio,
            <span className="block text-primary-200 mt-2">simplificado.</span>
          </h1>
          
          <p className="text-xl text-primary-100/90 leading-relaxed">
            Gestiona documentos y casos de forma ágil y segura.
          </p>
        </div>

        {/* Footer */}
        <div className="absolute bottom-12 text-primary-200/50 text-sm">
          © 2026 MigraFácil
        </div>
      </div>
    </div>
  )
}
