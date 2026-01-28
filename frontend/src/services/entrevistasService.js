/**
 * Servicio de Entrevistas
 * Maneja el agendamiento, reprogramación y cancelación de entrevistas
 */
import apiClient from './api'

export const entrevistasService = {
  // =====================================================
  // CONSULTAS
  // =====================================================

  /**
   * Obtiene todas las entrevistas del usuario
   * @param {Object} filters - { estado, fecha_desde, fecha_hasta }
   */
  async getEntrevistas(filters = {}) {
    const params = new URLSearchParams()
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key])
    })
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiClient.get(`/entrevistas/${query}`)
  },

  /**
   * Obtiene el detalle de una entrevista
   * @param {number} id
   */
  async getEntrevista(id) {
    return apiClient.get(`/entrevistas/${id}/`)
  },

  /**
   * Obtiene horarios disponibles para una fecha
   * @param {string} fecha - YYYY-MM-DD
   * @param {string} embajada
   */
  async getHorariosDisponibles(fecha, embajada) {
    return apiClient.get(`/entrevistas/horarios/?fecha=${fecha}&embajada=${embajada}`)
  },

  // =====================================================
  // AGENDAMIENTO (Asesor)
  // =====================================================

  /**
   * Agenda una entrevista para una solicitud
   * @param {number} solicitudId
   * @param {Object} data - { fecha, hora, ubicacion }
   */
  async agendarEntrevista(solicitudId, data) {
    return apiClient.post(`/entrevistas/agendar/`, {
      solicitud_id: solicitudId,
      fecha: data.fecha,
      hora: data.hora,
      ubicacion: data.ubicacion
    })
  },

  /**
   * Envía opciones de fecha al cliente
   * @param {number} solicitudId
   * @param {Array} opciones - [{ fecha, hora }]
   */
  async enviarOpcionesFecha(solicitudId, opciones) {
    return apiClient.post(`/entrevistas/opciones/`, {
      solicitud_id: solicitudId,
      opciones
    })
  },

  // =====================================================
  // CONFIRMACIÓN (Cliente)
  // =====================================================

  /**
   * Confirma una entrevista
   * @param {number} entrevistaId
   */
  async confirmarEntrevista(entrevistaId) {
    return apiClient.post(`/entrevistas/${entrevistaId}/confirmar/`, {})
  },

  /**
   * Selecciona una opción de fecha
   * @param {number} entrevistaId
   * @param {number} opcionIndex
   */
  async seleccionarOpcion(entrevistaId, opcionIndex) {
    return apiClient.post(`/entrevistas/${entrevistaId}/seleccionar/`, {
      opcion: opcionIndex
    })
  },

  // =====================================================
  // REPROGRAMACIÓN
  // =====================================================

  /**
   * Reprograma una entrevista
   * @param {number} entrevistaId
   * @param {Object} data - { fecha, hora, motivo }
   */
  async reprogramarEntrevista(entrevistaId, data) {
    return apiClient.post(`/entrevistas/${entrevistaId}/reprogramar/`, data)
  },

  /**
   * Verifica si se puede reprogramar
   * @param {number} entrevistaId
   */
  async verificarReprogramacion(entrevistaId) {
    return apiClient.get(`/entrevistas/${entrevistaId}/puede-reprogramar/`)
  },

  // =====================================================
  // CANCELACIÓN
  // =====================================================

  /**
   * Cancela una entrevista
   * @param {number} entrevistaId
   * @param {string} motivo
   */
  async cancelarEntrevista(entrevistaId, motivo) {
    return apiClient.post(`/entrevistas/${entrevistaId}/cancelar/`, {
      motivo
    })
  },

  /**
   * Verifica si se puede cancelar (según reglas de embajada)
   * @param {number} entrevistaId
   */
  async verificarCancelacion(entrevistaId) {
    return apiClient.get(`/entrevistas/${entrevistaId}/puede-cancelar/`)
  },

  // =====================================================
  // CALENDARIO
  // =====================================================

  /**
   * Obtiene eventos del calendario
   * @param {string} mes - YYYY-MM
   */
  async getEventosCalendario(mes) {
    return apiClient.get(`/entrevistas/calendario/?mes=${mes}`)
  },

  /**
   * Obtiene eventos del calendario (alias para compatibilidad)
   * @param {string} mes - YYYY-MM
   */
  async getCalendario(mes) {
    return apiClient.get(`/entrevistas/calendario/?mes=${mes}`)
  },

  /**
   * Obtiene entrevistas próximas
   * @param {number} dias - Número de días hacia adelante
   */
  async getEntrevistasProximas(dias = 7) {
    return apiClient.get(`/entrevistas/proximas/?dias=${dias}`)
  },

  // =====================================================
  // ASESOR
  // =====================================================

  /**
   * Obtiene entrevistas asignadas al asesor
   * @param {Object} filters - { estado, fecha_desde, fecha_hasta }
   */
  async getEntrevistasAsesor(filters = {}) {
    const params = new URLSearchParams()
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key])
    })
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiClient.get(`/entrevistas/${query}`)
  },

  // =====================================================
  // EMBAJADA (Datos simulados)
  // =====================================================

  /**
   * Obtiene disponibilidad de citas de la embajada (simulado)
   * @param {string} embajada - 'usa', 'espana', 'canada', 'brasil'
   * @param {string} mes - YYYY-MM
   */
  async getDisponibilidadEmbajada(embajada, mes) {
    const params = new URLSearchParams()
    if (embajada) params.append('embajada', embajada)
    if (mes) params.append('mes', mes)
    return apiClient.get(`/entrevistas/embajada/disponibilidad/?${params.toString()}`)
  },

  /**
   * Simula la confirmación de una cita con la embajada
   * @param {number} solicitudId
   * @param {Object} data - { fecha, hora, embajada }
   */
  async simularCitaEmbajada(solicitudId, data) {
    return apiClient.post(`/entrevistas/embajada/simular-cita/`, {
      solicitud_id: solicitudId,
      fecha: data.fecha,
      hora: data.hora,
      embajada: data.embajada
    })
  }
}

export default entrevistasService
