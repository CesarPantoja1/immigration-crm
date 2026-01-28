// ============================================
// TIPOS DE VISA - MIGRAFÁCIL CRM
// ============================================
// ❌ TURISMO ELIMINADO (deprecated)

export const VISA_TYPES = {
  TRABAJO: {
    id: 'trabajo',
    name: 'Visa de Trabajo',
    icon: '💼',
    color: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-600',
    description: 'Para profesionales con oferta laboral en el extranjero',
    requiredDocs: [
      { id: 'pasaporte', name: 'Pasaporte vigente', required: true },
      { id: 'foto', name: 'Fotografía 2x2', required: true },
      { id: 'antecedentes', name: 'Certificado de Antecedentes Penales', required: true },
      { id: 'oferta_laboral', name: 'Carta de Oferta Laboral', required: true },
      { id: 'cv', name: 'Currículum Vitae', required: false },
      { id: 'titulos', name: 'Títulos profesionales', required: false }
    ],
    practiceQuestions: 30,
    practiceDuration: '25 min',
    difficulty: 'Avanzado'
  },

  ESTUDIO: {
    id: 'estudio',
    name: 'Visa de Estudio',
    icon: '🎓',
    color: 'from-blue-500 to-blue-600',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-600',
    description: 'Para estudiantes aceptados en instituciones educativas',
    requiredDocs: [
      { id: 'pasaporte', name: 'Pasaporte vigente', required: true },
      { id: 'foto', name: 'Fotografía 2x2', required: true },
      { id: 'antecedentes', name: 'Certificado de Antecedentes Penales', required: true },
      { id: 'carta_aceptacion', name: 'Carta de Aceptación Universitaria', required: true },
      { id: 'solvencia', name: 'Demostración de Solvencia Económica', required: true },
      { id: 'plan_estudios', name: 'Plan de estudios', required: false }
    ],
    practiceQuestions: 25,
    practiceDuration: '20 min',
    difficulty: 'Intermedio'
  },

  VIVIENDA: {
    id: 'vivienda',
    name: 'Visa de Vivienda',
    icon: '🏠',
    color: 'from-green-500 to-green-600',
    bgColor: 'bg-green-100',
    textColor: 'text-green-600',
    description: 'Para inversores inmobiliarios y propietarios',
    requiredDocs: [
      { id: 'pasaporte', name: 'Pasaporte vigente', required: true },
      { id: 'foto', name: 'Fotografía 2x2', required: true },
      { id: 'antecedentes', name: 'Certificado de Antecedentes Penales', required: true },
      { id: 'titulo_propiedad', name: 'Título de Propiedad', required: true },
      { id: 'avaluo', name: 'Avalúo de la propiedad', required: true },
      { id: 'extractos', name: 'Extractos bancarios', required: false }
    ],
    practiceQuestions: 20,
    practiceDuration: '15 min',
    difficulty: 'Básico'
  }
}

// Array de tipos de visa para iterar
export const VISA_TYPES_ARRAY = Object.values(VISA_TYPES)

// Obtener tipo de visa por ID
export const getVisaTypeById = (id) => {
  return VISA_TYPES_ARRAY.find(visa => visa.id === id) || null
}

// Obtener documentos requeridos por tipo de visa
export const getRequiredDocuments = (visaTypeId) => {
  const visaType = getVisaTypeById(visaTypeId)
  return visaType ? visaType.requiredDocs.filter(doc => doc.required) : []
}

// Obtener todos los documentos por tipo de visa
export const getAllDocuments = (visaTypeId) => {
  const visaType = getVisaTypeById(visaTypeId)
  return visaType ? visaType.requiredDocs : []
}

// Verificar si todos los documentos requeridos están completos
export const areRequiredDocsComplete = (visaTypeId, uploadedDocs) => {
  const required = getRequiredDocuments(visaTypeId)
  return required.every(doc => uploadedDocs.includes(doc.id))
}

export default VISA_TYPES
