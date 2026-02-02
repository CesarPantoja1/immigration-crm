// ============================================
// CONSTANTES Y CONFIGURACIÓN - MIGRAFÁCIL CRM
// ============================================

// Fases del proceso de solicitud
export const PHASES = {
  APPROVAL: {
    id: 'approval',
    name: 'Aprobación',
    description: 'Revisión y aprobación de documentos',
    order: 1,
    icon: '📋',
    color: 'blue',
    states: ['draft', 'submitted', 'advisor_review', 'embassy_sent']
  },
  SCHEDULING: {
    id: 'scheduling',
    name: 'Agendamiento',
    description: 'Coordinación de fecha de entrevista',
    order: 2,
    icon: '📅',
    color: 'amber',
    states: ['embassy_approved', 'scheduling', 'interview_scheduled']
  },
  PREPARATION: {
    id: 'preparation',
    name: 'Preparación',
    description: 'Simulacros y práctica para la entrevista',
    order: 3,
    icon: '🎯',
    color: 'green',
    states: ['preparation_unlocked', 'simulation_done', 'interview_completed']
  }
}

// Obtener fase por estado
export const getPhaseByState = (state) => {
  for (const phase of Object.values(PHASES)) {
    if (phase.states.includes(state)) {
      return phase
    }
  }
  return PHASES.APPROVAL
}

// Verificar si una fase está completada
export const isPhaseCompleted = (currentState, targetPhase) => {
  const currentPhase = getPhaseByState(currentState)
  return currentPhase.order > targetPhase.order
}

// Verificar si una fase está activa
export const isPhaseActive = (currentState, targetPhase) => {
  const currentPhase = getPhaseByState(currentState)
  return currentPhase.id === targetPhase.id
}

// Verificar si se puede acceder a simulacros
export const canAccessSimulations = (applicationState) => {
  const phase = getPhaseByState(applicationState)
  return phase.id === 'preparation'
}

// Estados de solicitud con metadatos
// SINCRONIZADO con backend/apps/solicitudes/models.py
export const APPLICATION_STATES = {
  // Fase 1: Aprobación (revisión interna por asesor)
  borrador: {
    label: 'Borrador',
    phase: 'approval',
    color: 'gray',
    description: 'Solicitud en edición'
  },
  draft: {
    label: 'Borrador',
    phase: 'approval',
    color: 'gray',
    description: 'Solicitud en edición'
  },
  pendiente: {
    label: 'Pendiente',
    phase: 'approval',
    color: 'blue',
    description: 'Pendiente de revisión del asesor'
  },
  submitted: {
    label: 'Enviada',
    phase: 'approval',
    color: 'blue',
    description: 'Pendiente de revisión del asesor'
  },
  en_revision: {
    label: 'En Revisión',
    phase: 'approval',
    color: 'amber',
    description: 'El asesor está revisando los documentos'
  },
  advisor_review: {
    label: 'En Revisión',
    phase: 'approval',
    color: 'amber',
    description: 'El asesor está revisando los documentos'
  },
  aprobada: {
    label: 'Aprobada por Asesor',
    phase: 'approval',
    color: 'green',
    description: 'Aprobada, lista para enviar a embajada'
  },
  rechazada: {
    label: 'Rechazada',
    phase: 'approval',
    color: 'red',
    description: 'El asesor ha rechazado la solicitud'
  },
  advisor_rejected: {
    label: 'Requiere Cambios',
    phase: 'approval',
    color: 'red',
    description: 'El asesor ha solicitado correcciones'
  },
  enviada_embajada: {
    label: 'Enviada a Embajada',
    phase: 'approval',
    color: 'purple',
    description: 'Enviada a la embajada, esperando decisión'
  },
  embassy_sent: {
    label: 'Enviada a Embajada',
    phase: 'approval',
    color: 'purple',
    description: 'Esperando respuesta de la embajada'
  },

  // Fase 2: Decisión de Embajada y Agendamiento
  esperando_decision_embajada: {
    label: 'Esperando Decisión',
    phase: 'scheduling',
    color: 'purple',
    description: 'La embajada está evaluando la solicitud'
  },
  aprobada_embajada: {
    label: 'Aprobada por Embajada',
    phase: 'scheduling',
    color: 'green',
    description: 'La embajada ha aprobado - puede agendar entrevista'
  },
  embassy_approved: {
    label: 'Aprobada por Embajada',
    phase: 'scheduling',
    color: 'green',
    description: 'La embajada ha aprobado la solicitud'
  },
  rechazada_embajada: {
    label: 'Rechazada por Embajada',
    phase: 'scheduling',
    color: 'red',
    description: 'La embajada ha rechazado la solicitud'
  },
  embassy_rejected: {
    label: 'Rechazada por Embajada',
    phase: 'scheduling',
    color: 'red',
    description: 'La embajada ha rechazado la solicitud'
  },
  scheduling: {
    label: 'Agendando Entrevista',
    phase: 'scheduling',
    color: 'amber',
    description: 'Coordinando fecha de entrevista'
  },
  entrevista_agendada: {
    label: 'Entrevista Agendada',
    phase: 'scheduling',
    color: 'green',
    description: 'Fecha de entrevista confirmada'
  },
  interview_scheduled: {
    label: 'Entrevista Agendada',
    phase: 'scheduling',
    color: 'green',
    description: 'Fecha de entrevista confirmada'
  },

  // Fase 3: Preparación y Finalización
  preparation_unlocked: {
    label: 'Preparación Habilitada',
    phase: 'preparation',
    color: 'blue',
    description: 'Puedes acceder a simulacros y práctica'
  },
  simulation_done: {
    label: 'Simulacro Completado',
    phase: 'preparation',
    color: 'green',
    description: 'Has completado tu simulacro'
  },
  completada: {
    label: 'Completada',
    phase: 'preparation',
    color: 'green',
    description: 'Proceso finalizado exitosamente'
  },
  interview_completed: {
    label: 'Entrevista Realizada',
    phase: 'preparation',
    color: 'green',
    description: 'Has asistido a la entrevista real'
  }
}

// Estados de documento (sincronizado con backend)
export const DOCUMENT_STATES = {
  pendiente: {
    label: 'Pendiente',
    color: 'amber',
    bgColor: 'bg-amber-100',
    textColor: 'text-amber-600',
    description: 'Documento pendiente de revisión'
  },
  en_revision: {
    label: 'En Revisión',
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-600',
    description: 'El asesor está revisando el documento'
  },
  aprobado: {
    label: 'Aprobado',
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-600',
    description: 'Documento aprobado'
  },
  rechazado: {
    label: 'Rechazado',
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-600',
    description: 'Documento rechazado - requiere corrección'
  }
}

// Tipos de notificación
export const NOTIFICATION_TYPES = {
  APPLICATION_UPDATE: {
    id: 'application_update',
    icon: '📋',
    color: 'blue'
  },
  DOCUMENT_REVIEW: {
    id: 'document_review',
    icon: '📄',
    color: 'amber'
  },
  SIMULATION_SCHEDULED: {
    id: 'simulation_scheduled',
    icon: '📹',
    color: 'purple'
  },
  SIMULATION_REMINDER: {
    id: 'simulation_reminder',
    icon: '⏰',
    color: 'amber'
  },
  EMBASSY_RESPONSE: {
    id: 'embassy_response',
    icon: '🏛️',
    color: 'green'
  },
  INTERVIEW_SCHEDULED: {
    id: 'interview_scheduled',
    icon: '📅',
    color: 'red'
  },
  FEEDBACK_RECEIVED: {
    id: 'feedback_received',
    icon: '💬',
    color: 'blue'
  }
}

// Modalidades de simulacro
export const SIMULATION_MODALITIES = {
  VIRTUAL: {
    id: 'virtual',
    name: 'Virtual',
    icon: '📹',
    description: 'Videollamada con el asesor'
  },
  PRESENTIAL: {
    id: 'presential',
    name: 'Presencial',
    icon: '🏢',
    description: 'Reunión en oficina'
  }
}

// Reglas de cancelación de simulacros
export const CANCELLATION_RULES = {
  NO_CANCEL: {
    hoursLimit: 24,
    canCancel: false,
    penalty: true,
    message: 'No puedes cancelar con menos de 24 horas de anticipación.'
  },
  WITH_PENALTY: {
    hoursLimit: 72,
    canCancel: true,
    penalty: true,
    message: 'Si cancelas ahora, contará como un intento utilizado (entre 24-72 horas de anticipación).'
  },
  FREE_CANCEL: {
    hoursLimit: Infinity,
    canCancel: true,
    penalty: false,
    message: 'Puedes cancelar sin penalización (más de 72 horas de anticipación).'
  }
}

// Obtener regla de cancelación
export const getCancellationRule = (hoursUntil) => {
  if (hoursUntil < 24) return CANCELLATION_RULES.NO_CANCEL
  if (hoursUntil < 72) return CANCELLATION_RULES.WITH_PENALTY
  return CANCELLATION_RULES.FREE_CANCEL
}

// Checklist de evaluación de documentos
export const DOCUMENT_CHECKLIST = [
  { id: 'legibility', label: 'Documento legible', required: true },
  { id: 'validity', label: 'Documento vigente', required: true },
  { id: 'authenticity', label: 'Documento auténtico', required: true },
  { id: 'correct_info', label: 'Información correcta', required: true },
  { id: 'complete', label: 'Documento completo', required: true }
]

// Checklist de desempeño en simulacro (Asesor)
export const PERFORMANCE_CHECKLIST = [
  { id: 'punctuality', label: 'Puntualidad', category: 'basic' },
  { id: 'presentation', label: 'Presentación personal', category: 'basic' },
  { id: 'documents_ready', label: 'Documentos preparados', category: 'basic' },
  { id: 'clear_communication', label: 'Comunicación clara', category: 'communication' },
  { id: 'confidence', label: 'Confianza', category: 'communication' },
  { id: 'eye_contact', label: 'Contacto visual', category: 'communication' },
  { id: 'question_handling', label: 'Manejo de preguntas', category: 'interview' },
  { id: 'consistent_answers', label: 'Respuestas consistentes', category: 'interview' },
  { id: 'knowledge', label: 'Conocimiento del proceso', category: 'interview' }
]

export default {
  PHASES,
  APPLICATION_STATES,
  NOTIFICATION_TYPES,
  SIMULATION_MODALITIES,
  CANCELLATION_RULES,
  DOCUMENT_CHECKLIST,
  PERFORMANCE_CHECKLIST
}
