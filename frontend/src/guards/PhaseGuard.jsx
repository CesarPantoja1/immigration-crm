import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { PHASES, getPhaseByState } from '../store/constants'
import { Card, Button } from '../components/common'

/**
 * PhaseGuard - Guard de verificación de fase de solicitud
 * Bloquea acceso a ciertas secciones hasta que la solicitud 
 * alcance la fase requerida (ej: Simulacros requieren Fase 3)
 */
export default function PhaseGuard({ children, requiredPhase, redirectTo = '/dashboard' }) {
  const { user } = useAuth()
  
  // Obtener el estado actual de la solicitud activa del usuario
  // En producción esto vendría del contexto de aplicación
  const applicationState = user?.activeApplicationState || 'draft'
  const currentPhase = getPhaseByState(applicationState)
  const required = PHASES[requiredPhase.toUpperCase()]

  if (!required) {
    console.warn(`PhaseGuard: Fase desconocida "${requiredPhase}"`)
    return children
  }

  // Verificar si la fase actual es suficiente
  const hasAccess = currentPhase.order >= required.order

  if (!hasAccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="max-w-lg text-center">
          <div className="w-20 h-20 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Sección Bloqueada
          </h2>
          
          <p className="text-gray-500 mb-6">
            Esta sección estará disponible cuando tu solicitud alcance la fase de{' '}
            <span className="font-semibold text-gray-700">{required.name}</span>.
          </p>

          {/* Progress indicator */}
          <div className="bg-gray-50 rounded-xl p-4 mb-6">
            <div className="flex items-center justify-between mb-3">
              {Object.values(PHASES).map((phase, index) => (
                <div key={phase.id} className="flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    currentPhase.order > phase.order
                      ? 'bg-green-500 text-white'
                      : currentPhase.order === phase.order
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-200 text-gray-500'
                  }`}>
                    {currentPhase.order > phase.order ? (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      phase.order
                    )}
                  </div>
                  {index < Object.values(PHASES).length - 1 && (
                    <div className={`w-12 h-1 mx-1 ${
                      currentPhase.order > phase.order ? 'bg-green-500' : 'bg-gray-200'
                    }`} />
                  )}
                </div>
              ))}
            </div>
            <div className="flex justify-between text-xs text-gray-500">
              {Object.values(PHASES).map(phase => (
                <span key={phase.id} className={`${
                  currentPhase.id === phase.id ? 'text-primary-600 font-medium' : ''
                }`}>
                  {phase.name}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 text-left">
            <h4 className="font-medium text-blue-800 mb-2">¿Cómo desbloquear?</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>1. Completa y envía tu solicitud</li>
              <li>2. Espera la aprobación del asesor</li>
              <li>3. Espera el veredicto de la embajada</li>
              <li>4. Una vez aprobada, se desbloqueará la preparación</li>
            </ul>
          </div>

          <Button as="a" href={redirectTo} className="w-full">
            Volver al Dashboard
          </Button>
        </Card>
      </div>
    )
  }

  return children
}
