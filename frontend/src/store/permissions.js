// ============================================
// PERMISOS Y ROLES - MIGRAFÁCIL CRM
// ============================================

export const ROLES = {
  CLIENT: 'client',
  ADVISOR: 'advisor',
  ADMIN: 'admin'
}

export const PERMISSIONS = {
  // Solicitudes
  CREATE_APPLICATION: ['client'],
  VIEW_OWN_APPLICATIONS: ['client'],
  VIEW_ALL_APPLICATIONS: ['advisor', 'admin'],
  REVIEW_APPLICATION: ['advisor', 'admin'],
  SEND_TO_EMBASSY: ['advisor', 'admin'],
  
  // Documentos
  UPLOAD_DOCUMENTS: ['client'],
  VIEW_OWN_DOCUMENTS: ['client'],
  VIEW_ALL_DOCUMENTS: ['advisor', 'admin'],
  APPROVE_DOCUMENTS: ['advisor', 'admin'],
  REJECT_DOCUMENTS: ['advisor', 'admin'],
  
  // Simulacros
  REQUEST_SIMULATION: ['client'],
  VIEW_OWN_SIMULATIONS: ['client'],
  VIEW_ALL_SIMULATIONS: ['advisor', 'admin'],
  CONDUCT_SIMULATION: ['advisor'],
  PROVIDE_FEEDBACK: ['advisor'],
  
  // Práctica
  ACCESS_PRACTICE: ['client'],
  
  // Notificaciones
  VIEW_NOTIFICATIONS: ['client', 'advisor', 'admin'],
  SEND_NOTIFICATIONS: ['advisor', 'admin'],
  
  // Calendario
  VIEW_OWN_CALENDAR: ['client'],
  VIEW_ALL_CALENDARS: ['advisor', 'admin'],
  SCHEDULE_EVENTS: ['advisor', 'admin'],
  
  // Embajada
  COMMUNICATE_EMBASSY: ['advisor', 'admin'],
  UPDATE_EMBASSY_RESPONSE: ['advisor', 'admin']
}

// Verificar si un rol tiene permiso
export const hasPermission = (role, permission) => {
  const allowedRoles = PERMISSIONS[permission]
  return allowedRoles ? allowedRoles.includes(role) : false
}

// Obtener todos los permisos de un rol
export const getPermissionsForRole = (role) => {
  return Object.entries(PERMISSIONS)
    .filter(([_, roles]) => roles.includes(role))
    .map(([permission]) => permission)
}

// Rutas por rol
export const ROUTES_BY_ROLE = {
  [ROLES.CLIENT]: {
    dashboard: '/dashboard',
    inbox: '/inbox',
    applications: '/solicitudes',
    newApplication: '/nueva-solicitud',
    simulations: '/simulacros',
    practice: '/practica',
    calendar: '/calendario',
    profile: '/perfil'
  },
  [ROLES.ADVISOR]: {
    dashboard: '/asesor',
    inbox: '/asesor/inbox',
    applications: '/asesor/solicitudes',
    documents: '/asesor/documentos',
    simulations: '/asesor/simulacros',
    calendar: '/asesor/calendario',
    profile: '/asesor/perfil'
  },
  [ROLES.ADMIN]: {
    dashboard: '/admin',
    users: '/admin/usuarios',
    advisors: '/admin/asesores',
    applications: '/admin/solicitudes',
    reports: '/admin/reportes',
    settings: '/admin/configuracion',
    profile: '/admin/perfil'
  }
}

// Obtener rutas para un rol específico
export const getRoutesForRole = (role) => {
  return ROUTES_BY_ROLE[role] || {}
}

// Verificar si una ruta es accesible para un rol
export const isRouteAccessible = (role, path) => {
  const routes = ROUTES_BY_ROLE[role]
  if (!routes) return false
  return Object.values(routes).some(route => path.startsWith(route))
}

export default {
  ROLES,
  PERMISSIONS,
  ROUTES_BY_ROLE,
  hasPermission,
  getPermissionsForRole,
  getRoutesForRole,
  isRouteAccessible
}
