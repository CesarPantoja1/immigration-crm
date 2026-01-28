import { SIMULATION_MODALITIES } from '../../store/constants'

/**
 * ModalityFilter - Filtro de modalidad (Virtual/Presencial) para simulacros
 */
export default function ModalityFilter({ value, onChange, counts = {} }) {
  const options = [
    { id: 'all', label: 'Todos', icon: null },
    ...Object.values(SIMULATION_MODALITIES).map(m => ({
      id: m.id,
      label: m.name,
      icon: m.icon
    }))
  ]

  return (
    <div className="inline-flex items-center gap-1 p-1 bg-gray-100 rounded-xl">
      {options.map(option => (
        <button
          key={option.id}
          onClick={() => onChange(option.id)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            value === option.id
              ? 'bg-white text-primary-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          {option.icon && <span>{option.icon}</span>}
          <span>{option.label}</span>
          {counts[option.id] !== undefined && (
            <span className={`ml-1 px-1.5 py-0.5 rounded-full text-xs ${
              value === option.id
                ? 'bg-primary-100 text-primary-600'
                : 'bg-gray-200 text-gray-500'
            }`}>
              {counts[option.id]}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}

/**
 * ModalityBadge - Badge de modalidad
 */
export function ModalityBadge({ modality, size = 'default' }) {
  const mod = SIMULATION_MODALITIES[modality?.toUpperCase()] || SIMULATION_MODALITIES.VIRTUAL
  
  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    default: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5'
  }

  const colors = {
    virtual: 'bg-purple-100 text-purple-700',
    presential: 'bg-amber-100 text-amber-700'
  }

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ${sizes[size]} ${colors[mod.id]}`}>
      <span>{mod.icon}</span>
      <span>{mod.name}</span>
    </span>
  )
}
