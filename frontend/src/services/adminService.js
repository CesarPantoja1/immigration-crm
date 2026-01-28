/**
 * Servicio para la administración del sistema
 */
import apiClient from './api'

const adminService = {
  /**
   * Obtiene estadísticas del sistema
   */
  async getEstadisticas() {
    return apiClient.get('/admin/estadisticas/')
  },

  /**
   * Obtiene lista de todos los asesores
   * @param {Object} params - Parámetros de filtro (activo, busqueda)
   */
  async getAsesores(params = {}) {
    const queryParams = new URLSearchParams()
    if (params.activo !== undefined) queryParams.append('activo', params.activo)
    if (params.busqueda) queryParams.append('busqueda', params.busqueda)
    
    const query = queryParams.toString()
    return apiClient.get(`/admin/asesores/${query ? '?' + query : ''}`)
  },

  /**
   * Obtiene detalle de un asesor
   * @param {number} id 
   */
  async getAsesor(id) {
    return apiClient.get(`/admin/asesores/${id}/`)
  },

  /**
   * Crea un nuevo asesor
   * @param {Object} data - Datos del asesor
   */
  async crearAsesor(data) {
    return apiClient.post('/admin/asesores/crear/', data)
  },

  /**
   * Actualiza un asesor
   * @param {number} id 
   * @param {Object} data 
   */
  async actualizarAsesor(id, data) {
    return apiClient.patch(`/admin/asesores/${id}/`, data)
  },

  /**
   * Activa/desactiva un asesor
   * @param {number} id 
   */
  async toggleEstadoAsesor(id) {
    return apiClient.post(`/admin/asesores/${id}/toggle-estado/`)
  },

  /**
   * Desactiva un asesor (soft delete)
   * @param {number} id 
   */
  async desactivarAsesor(id) {
    return apiClient.delete(`/admin/asesores/${id}/`)
  },

  /**
   * Obtiene lista de todos los usuarios
   * @param {Object} params - Parámetros de filtro
   */
  async getUsuarios(params = {}) {
    const queryParams = new URLSearchParams()
    if (params.rol) queryParams.append('rol', params.rol)
    if (params.activo !== undefined) queryParams.append('activo', params.activo)
    
    const query = queryParams.toString()
    return apiClient.get(`/usuarios/${query ? '?' + query : ''}`)
  },
}

export default adminService
