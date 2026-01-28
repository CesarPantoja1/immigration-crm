/**
 * Servicio de Solicitudes
 * Maneja todas las operaciones CRUD de solicitudes de visa
 */
import apiClient from './api'

export const solicitudesService = {
  // =====================================================
  // CLIENTE
  // =====================================================

  /**
   * Obtiene las solicitudes del cliente actual
   * @param {Object} filters - { estado, tipo_visa }
   */
  async getMisSolicitudes(filters = {}) {
    const params = new URLSearchParams()
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key])
    })
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiClient.get(`/solicitudes/mis-solicitudes/${query}`)
  },

  /**
   * Alias para getMisSolicitudes (compatibilidad)
   */
  async getAll(filters = {}) {
    return this.getMisSolicitudes(filters)
  },

  /**
   * Crea una nueva solicitud
   * @param {Object} solicitudData - { tipo_visa, embajada, datos_personales, observaciones }
   */
  async crearSolicitud(solicitudData) {
    return apiClient.post('/solicitudes/nueva/', solicitudData)
  },

  /**
   * Alias para crearSolicitud (compatibilidad)
   */
  async create(solicitudData) {
    return this.crearSolicitud(solicitudData)
  },

  /**
   * Envía/confirma una solicitud
   * @param {number} solicitudId
   */
  async submit(solicitudId) {
    return apiClient.post(`/solicitudes/${solicitudId}/enviar/`, {})
  },

  /**
   * Obtiene el detalle de una solicitud
   * @param {number} id
   */
  async getSolicitud(id) {
    return apiClient.get(`/solicitudes/${id}/`)
  },

  /**
   * Obtiene estadísticas del cliente
   */
  async getEstadisticasCliente() {
    return apiClient.get('/solicitudes/estadisticas/cliente/')
  },

  // =====================================================
  // ASESOR
  // =====================================================

  /**
   * Obtiene las solicitudes asignadas al asesor
   * @param {Object} filters - { estado, tipo_visa }
   */
  async getSolicitudesAsignadas(filters = {}) {
    const params = new URLSearchParams()
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key])
    })
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiClient.get(`/solicitudes/asignadas/${query}`)
  },

  /**
   * Obtiene solicitudes pendientes de asignación
   */
  async getSolicitudesPendientes() {
    return apiClient.get('/solicitudes/pendientes/')
  },

  /**
   * Actualiza una solicitud (asesor)
   * @param {number} id
   * @param {Object} data - { estado, notas_asesor, observaciones }
   */
  async actualizarSolicitud(id, data) {
    return apiClient.patch(`/solicitudes/${id}/actualizar/`, data)
  },

  /**
   * Asigna un asesor a una solicitud
   * @param {number} solicitudId
   * @param {number} asesorId
   */
  async asignarAsesor(solicitudId, asesorId) {
    return apiClient.post(`/solicitudes/${solicitudId}/asignar/`, {
      asesor_id: asesorId
    })
  },

  /**
   * Obtiene estadísticas del asesor
   */
  async getEstadisticasAsesor() {
    return apiClient.get('/solicitudes/estadisticas/asesor/')
  },

  // =====================================================
  // DOCUMENTOS
  // =====================================================

  /**
   * Sube un documento a una solicitud
   * @param {number} solicitudId
   * @param {Object} documentoData - { nombre, archivo }
   */
  async subirDocumento(solicitudId, documentoData) {
    const formData = new FormData()
    formData.append('nombre', documentoData.nombre)
    formData.append('archivo', documentoData.archivo)
    
    return apiClient.post(`/solicitudes/${solicitudId}/documentos/`, formData, {
      contentType: null
    })
  },

  /**
   * Sube un documento (alias para compatibilidad)
   * @param {number} solicitudId
   * @param {File} file
   * @param {string} docName
   */
  async uploadDocument(solicitudId, file, docName) {
    return this.subirDocumento(solicitudId, {
      nombre: docName,
      archivo: file
    })
  },

  /**
   * Aprueba un documento
   * @param {number} documentoId
   */
  async aprobarDocumento(documentoId) {
    return apiClient.patch(`/documentos/${documentoId}/aprobar/`, {})
  },

  /**
   * Rechaza un documento
   * @param {number} documentoId
   * @param {string} motivo
   */
  async rechazarDocumento(documentoId, motivo) {
    return apiClient.patch(`/documentos/${documentoId}/rechazar/`, {
      motivo_rechazo: motivo
    })
  },

  // =====================================================
  // HISTORIAL
  // =====================================================

  /**
   * Obtiene el historial de una solicitud
   * @param {number} solicitudId
   */
  async getHistorial(solicitudId) {
    return apiClient.get(`/solicitudes/${solicitudId}/historial/`)
  }
}

export default solicitudesService
