import { PHASES } from '../../store/constants'

/**
 * PhaseProgressBar - Barra de progreso de fases del proceso
 * Muestra las 3 fases: Aprobación → Agendamiento → Preparación
 */
export default function PhaseProgressBar({ 
  currentPhase, 
  currentState,
  showLabels = true,
  size = 'default' // 'sm', 'default', 'lg'
}) {
  const phases = Object.values(PHASES)
  const currentPhaseData = phases.find(p => p.id === currentPhase) || phases[0]

  const sizes = {
    sm: {
      circle: 'w-6 h-6 text-xs',
      line: 'h-0.5',
      icon: 'w-3 h-3',
      label: 'text-xs'
    },
    default: {
      circle: 'w-10 h-10 text-sm',
      line: 'h-1',
      icon: 'w-4 h-4',
      label: 'text-sm'
    },
    lg: {
      circle: 'w-14 h-14 text-base',
      line: 'h-1.5',
      icon: 'w-5 h-5',
      label: 'text-base'
    }
  }

  const s = sizes[size]

  const getPhaseStatus = (phase) => {
    if (currentPhaseData.order > phase.order) return 'completed'
    if (currentPhaseData.order === phase.order) return 'current'
    return 'pending'
  }

  const getPhaseColors = (status) => {
    switch (status) {
      case 'completed':
        return {
          bg: 'bg-green-500',
          text: 'text-white',
          line: 'bg-green-500',
          label: 'text-green-600'
        }
      case 'current':
        return {
          bg: 'bg-primary-500',
          text: 'text-white',
          line: 'bg-gray-200',
          label: 'text-primary-600 font-medium'
        }
      default:
        return {
          bg: 'bg-gray-200',
          text: 'text-gray-500',
          line: 'bg-gray-200',
          label: 'text-gray-400'
        }
    }
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {phases.map((phase, index) => {
          const status = getPhaseStatus(phase)
          const colors = getPhaseColors(status)
          const isLast = index === phases.length - 1

          return (
            <div key={phase.id} className="flex items-center flex-1">
              {/* Phase Circle */}
              <div className="flex flex-col items-center">
                <div
                  className={`${s.circle} ${colors.bg} ${colors.text} rounded-full flex items-center justify-center font-semibold shadow-sm transition-all`}
                >
                  {status === 'completed' ? (
                    <svg className={s.icon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span>{phase.icon}</span>
                  )}
                </div>
                {showLabels && (
                  <span className={`${s.label} ${colors.label} mt-2 text-center whitespace-nowrap`}>
                    {phase.name}
                  </span>
                )}
              </div>

              {/* Connector Line */}
              {!isLast && (
                <div className={`flex-1 ${s.line} mx-2 ${colors.line} rounded-full transition-all`} />
              )}
            </div>
          )
        })}
      </div>

      {/* Current State Description */}
      {currentState && (
        <div className="mt-4 text-center">
          <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
            currentPhaseData.color === 'blue' ? 'bg-blue-100 text-blue-700' :
            currentPhaseData.color === 'amber' ? 'bg-amber-100 text-amber-700' :
            'bg-green-100 text-green-700'
          }`}>
            <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
            {currentState}
          </span>
        </div>
      )}
    </div>
  )
}

/**
 * PhaseProgressBarCompact - Versión compacta para cards
 */
export function PhaseProgressBarCompact({ currentPhase }) {
  const phases = Object.values(PHASES)
  const currentIndex = phases.findIndex(p => p.id === currentPhase)
  const progress = ((currentIndex + 1) / phases.length) * 100

  return (
    <div className="w-full">
      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
        <span>Progreso</span>
        <span>{Math.round(progress)}%</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="flex justify-between mt-1">
        {phases.map((phase, index) => (
          <div
            key={phase.id}
            className={`w-2 h-2 rounded-full transition-all ${
              index <= currentIndex ? 'bg-primary-500' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  )
}
