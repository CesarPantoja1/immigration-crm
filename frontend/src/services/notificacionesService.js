/**
 * Servicio de Notificaciones
 * Maneja el centro de notificaciones y alertas
 */
import apiClient from './api'

export const notificacionesService = {
  // =====================================================
  // CONSULTAS
  // =====================================================

  /**
   * Obtiene todas las notificaciones del usuario
   * @param {Object} filters - { tipo, leida, page }
   */
  async getNotificaciones(filters = {}) {
    const params = new URLSearchParams()
    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined) params.append(key, filters[key])
    })
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiClient.get(`/notificaciones/${query}`)
  },

  /**
   * Alias para getNotificaciones (compatibilidad)
   */
  async getAll(filters = {}) {
    return this.getNotificaciones(filters)
  },

  /**
   * Obtiene el conteo de notificaciones no leídas
   */
  async getConteoNoLeidas() {
    return apiClient.get('/notificaciones/no-leidas/count/')
  },

  /**
   * Obtiene notificaciones no leídas
   */
  async getNoLeidas() {
    return apiClient.get('/notificaciones/no-leidas/')
  },

  /**
   * Obtiene el detalle de una notificación
   * @param {number} id
   */
  async getNotificacion(id) {
    return apiClient.get(`/notificaciones/${id}/`)
  },

  // =====================================================
  // ACCIONES
  // =====================================================

  /**
   * Marca una notificación como leída
   * @param {number} id
   */
  async marcarComoLeida(id) {
    return apiClient.post(`/notificaciones/${id}/leer/`, {})
  },

  /**
   * Marca todas las notificaciones como leídas
   */
  async marcarTodasComoLeidas() {
    return apiClient.post('/notificaciones/leer-todas/', {})
  },

  /**
   * Elimina una notificación
   * @param {number} id
   */
  async eliminarNotificacion(id) {
    return apiClient.delete(`/notificaciones/${id}/`)
  },

  /**
   * Elimina todas las notificaciones leídas
   */
  async eliminarLeidas() {
    return apiClient.delete('/notificaciones/eliminar-leidas/')
  },

  // =====================================================
  // TIPOS DE NOTIFICACIÓN
  // =====================================================

  /**
   * Obtiene los tipos de notificación disponibles
   */
  async getTipos() {
    return apiClient.get('/notificaciones/tipos/')
  },

  // =====================================================
  // PREFERENCIAS
  // =====================================================

  /**
   * Obtiene las preferencias de notificación del usuario
   */
  async getPreferencias() {
    return apiClient.get('/notificaciones/preferencias/')
  },

  /**
   * Actualiza las preferencias de notificación
   * @param {Object} preferencias
   */
  async actualizarPreferencias(preferencias) {
    return apiClient.patch('/notificaciones/preferencias/', preferencias)
  }
}

export default notificacionesService
