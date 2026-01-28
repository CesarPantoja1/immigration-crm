/**
 * Servicio de Simulacros
 * Maneja simulacros de entrevista consular
 */
import apiClient from './api'

export const simulacrosService = {
  // =====================================================
  // CONSULTAS
  // =====================================================

  /**
   * Obtiene los simulacros del usuario
   * @param {Object} filters - { estado, modalidad }
   */
  async getSimulacros(filters = {}) {
    const params = new URLSearchParams()
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key])
    })
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiClient.get(`/simulacros/${query}`)
  },

  /**
   * Obtiene los simulacros del cliente actual (alias para compatibilidad)
   */
  async getMisSimulacros() {
    return apiClient.get('/simulacros/')
  },

  /**
   * Cancela un simulacro (alias para compatibilidad)
   * @param {number} simulacroId
   */
  async cancelar(simulacroId) {
    return apiClient.post(`/simulacros/${simulacroId}/cancelar/`, {})
  },

  /**
   * Obtiene el detalle de un simulacro
   * @param {number} id
   */
  async getSimulacro(id) {
    return apiClient.get(`/simulacros/${id}/`)
  },

  /**
   * Obtiene disponibilidad para nuevo simulacro
   */
  async getDisponibilidad() {
    return apiClient.get('/simulacros/disponibilidad/')
  },

  /**
   * Obtiene el contador de simulacros del cliente
   */
  async getContadorSimulacros() {
    return apiClient.get('/simulacros/contador/')
  },

  /**
   * Solicita un simulacro (cliente)
   * @param {number} solicitudId - ID de la solicitud asociada
   * @param {Object} data - { fecha_propuesta, hora_propuesta, modalidad, observaciones }
   */
  async solicitarSimulacro(solicitudId, data) {
    return apiClient.post('/simulacros/solicitar/', {
      solicitud_id: solicitudId,
      ...data
    })
  },

  // =====================================================
  // PROPUESTAS (Asesor)
  // =====================================================

  /**
   * Crea una propuesta de simulacro
   * @param {Object} data - { cliente_id, fecha, hora, modalidad }
   */
  async crearPropuesta(data) {
    return apiClient.post('/simulacros/propuesta/', data)
  },

  /**
   * Obtiene propuestas pendientes de respuesta
   */
  async getPropuestasPendientes() {
    return apiClient.get('/simulacros/propuestas/')
  },

  // =====================================================
  // RESPUESTAS (Cliente)
  // =====================================================

  /**
   * Acepta una propuesta de simulacro
   * @param {number} simulacroId
   */
  async aceptarPropuesta(simulacroId) {
    return apiClient.post(`/simulacros/${simulacroId}/aceptar/`, {})
  },

  /**
   * Propone fecha alternativa
   * @param {number} simulacroId
   * @param {Object} data - { fecha, hora }
   */
  async proponerFechaAlternativa(simulacroId, data) {
    return apiClient.post(`/simulacros/${simulacroId}/contrapropuesta/`, data)
  },

  /**
   * Rechaza una propuesta
   * @param {number} simulacroId
   * @param {string} motivo
   */
  async rechazarPropuesta(simulacroId, motivo) {
    return apiClient.post(`/simulacros/${simulacroId}/rechazar/`, { motivo })
  },

  // =====================================================
  // SALA DE ESPERA Y SESIÓN
  // =====================================================

  /**
   * Ingresa a la sala de espera
   * @param {number} simulacroId
   */
  async ingresarSalaEspera(simulacroId) {
    return apiClient.post(`/simulacros/${simulacroId}/sala-espera/`, {})
  },

  /**
   * Obtiene información completa de la sala (Jitsi)
   * @param {number} simulacroId
   */
  async getInfoSala(simulacroId) {
    return apiClient.get(`/simulacros/${simulacroId}/sala/`)
  },

  /**
   * Obtiene el estado de la sala de espera
   * @param {number} simulacroId
   */
  async getEstadoSala(simulacroId) {
    return apiClient.get(`/simulacros/${simulacroId}/estado-sala/`)
  },

  /**
   * Inicia el simulacro (Asesor)
   * @param {number} simulacroId
   */
  async iniciarSimulacro(simulacroId) {
    return apiClient.post(`/simulacros/${simulacroId}/iniciar/`, {})
  },

  /**
   * Finaliza el simulacro (Asesor)
   * @param {number} simulacroId
   * @param {Object} data - { duracion_minutos, notas }
   */
  async finalizarSimulacro(simulacroId, data = {}) {
    return apiClient.post(`/simulacros/${simulacroId}/finalizar/`, data)
  },

  // =====================================================
  // TRANSCRIPCIÓN Y GRABACIÓN
  // =====================================================

  /**
   * Guarda la transcripción del simulacro
   * @param {number} simulacroId
   * @param {Array} transcripcion - [{ pregunta, respuesta }]
   */
  async guardarTranscripcion(simulacroId, transcripcion) {
    return apiClient.post(`/simulacros/${simulacroId}/transcripcion/`, {
      transcripcion
    })
  },

  /**
   * Obtiene la transcripción de un simulacro
   * @param {number} simulacroId
   */
  async getTranscripcion(simulacroId) {
    return apiClient.get(`/simulacros/${simulacroId}/transcripcion/`)
  },

  // =====================================================
  // CANCELACIÓN
  // =====================================================

  /**
   * Cancela un simulacro
   * @param {number} simulacroId
   * @param {string} motivo
   */
  async cancelarSimulacro(simulacroId, motivo) {
    return apiClient.post(`/simulacros/${simulacroId}/cancelar/`, { motivo })
  },

  /**
   * Verifica si se puede cancelar
   * @param {number} simulacroId
   */
  async verificarCancelacion(simulacroId) {
    return apiClient.get(`/simulacros/${simulacroId}/puede-cancelar/`)
  },

  // =====================================================
  // SIMULACROS PRESENCIALES
  // =====================================================

  /**
   * Obtiene información para simulacro presencial
   * @param {number} simulacroId
   */
  async getInfoPresencial(simulacroId) {
    return apiClient.get(`/simulacros/${simulacroId}/presencial/`)
  },

  /**
   * Confirma asistencia a simulacro presencial
   * @param {number} simulacroId
   */
  async confirmarAsistencia(simulacroId) {
    return apiClient.post(`/simulacros/${simulacroId}/confirmar-asistencia/`, {})
  },

  // =====================================================
  // FEEDBACK Y COMPLETAR
  // =====================================================

  /**
   * Envía feedback del simulacro (asesor)
   * @param {number} simulacroId
   * @param {Object} feedback - { calificacion, comentarios, areas_mejora }
   */
  async submitFeedback(simulacroId, feedback) {
    return apiClient.post(`/simulacros/${simulacroId}/feedback/`, feedback)
  },

  /**
   * Marca un simulacro como completado (asesor)
   * @param {number} simulacroId
   */
  async completarSimulacro(simulacroId) {
    return apiClient.post(`/simulacros/${simulacroId}/finalizar/`, {})
  },

  // =====================================================
  // RECOMENDACIONES CON IA
  // =====================================================

  /**
   * Obtiene simulacros completados del asesor (para agregar feedback)
   */
  async getSimulacrosCompletados() {
    return apiClient.get('/simulacros/completados/')
  },

  /**
   * Sube un archivo de transcripción (.txt)
   * @param {number} simulacroId
   * @param {File} archivo - Archivo .txt con la transcripción
   */
  async subirTranscripcion(simulacroId, archivo) {
    const formData = new FormData()
    formData.append('archivo', archivo)
    return apiClient.post(`/simulacros/${simulacroId}/subir-transcripcion/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * Genera recomendaciones usando IA (Gemini)
   * @param {number} simulacroId
   */
  async generarRecomendacionIA(simulacroId) {
    return apiClient.post(`/simulacros/${simulacroId}/generar-recomendacion-ia/`, {})
  },

  /**
   * Obtiene la recomendación de un simulacro específico (cliente)
   * @param {number} simulacroId
   */
  async getMiRecomendacion(simulacroId) {
    return apiClient.get(`/simulacros/${simulacroId}/mi-recomendacion/`)
  },

  /**
   * Obtiene todas las recomendaciones del cliente
   */
  async getMisRecomendaciones() {
    return apiClient.get('/mis-recomendaciones/')
  },

  /**
   * Obtiene el detalle de una recomendación
   * @param {number} recomendacionId
   */
  async getDetalleRecomendacion(recomendacionId) {
    return apiClient.get(`/recomendaciones/${recomendacionId}/detalle-cliente/`)
  },

  // =====================================================
  // CONFIGURACIÓN DE IA
  // =====================================================

  /**
   * Obtiene la configuración de IA del asesor
   */
  async getConfiguracionIA() {
    return apiClient.get('/configuracion-ia/')
  },

  /**
   * Guarda la configuración de IA del asesor
   * @param {Object} data - { api_key, modelo }
   */
  async guardarConfiguracionIA(data) {
    return apiClient.post('/configuracion-ia/', data)
  },

  /**
   * Actualiza la configuración de IA del asesor
   * @param {Object} data - { api_key?, modelo?, activo? }
   */
  async actualizarConfiguracionIA(data) {
    return apiClient.put('/configuracion-ia/', data)
  },

  /**
   * Elimina la configuración de IA del asesor
   */
  async eliminarConfiguracionIA() {
    return apiClient.delete('/configuracion-ia/')
  },

  /**
   * Prueba si una API key es válida
   * @param {string} apiKey - API key de Gemini
   * @param {string} modelo - Modelo a probar
   */
  async testAPIKey(apiKey, modelo = 'gemini-2.5-flash') {
    return apiClient.post('/configuracion-ia/test/', { api_key: apiKey, modelo })
  }
}

export default simulacrosService
