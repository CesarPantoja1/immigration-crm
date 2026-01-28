/**
 * Servicio de Recomendaciones
 * Maneja las recomendaciones generadas por IA basadas en simulacros
 */
import apiClient from './api'

export const recomendacionesService = {
  // =====================================================
  // CONSULTAS
  // =====================================================

  /**
   * Obtiene las recomendaciones de un simulacro
   * @param {number} simulacroId
   */
  async getRecomendaciones(simulacroId) {
    return apiClient.get(`/recomendaciones/simulacro/${simulacroId}/`)
  },

  /**
   * Obtiene todas las recomendaciones del usuario
   */
  async getMisRecomendaciones() {
    return apiClient.get('/recomendaciones/')
  },

  /**
   * Obtiene el detalle de una recomendación
   * @param {number} id
   */
  async getRecomendacion(id) {
    return apiClient.get(`/recomendaciones/${id}/`)
  },

  // =====================================================
  // GENERACIÓN (Asesor)
  // =====================================================

  /**
   * Solicita generar recomendaciones para un simulacro
   * @param {number} simulacroId
   */
  async generarRecomendaciones(simulacroId) {
    return apiClient.post(`/recomendaciones/generar/`, {
      simulacro_id: simulacroId
    })
  },

  /**
   * Verifica el estado de generación
   * @param {number} simulacroId
   */
  async getEstadoGeneracion(simulacroId) {
    return apiClient.get(`/recomendaciones/estado/${simulacroId}/`)
  },

  // =====================================================
  // INDICADORES DE DESEMPEÑO
  // =====================================================

  /**
   * Obtiene los indicadores de un simulacro
   * @param {number} simulacroId
   */
  async getIndicadores(simulacroId) {
    return apiClient.get(`/recomendaciones/indicadores/${simulacroId}/`)
  },

  /**
   * Guarda los indicadores de desempeño (Asesor)
   * @param {number} simulacroId
   * @param {Object} indicadores - { claridad, coherencia, seguridad, pertinencia }
   */
  async guardarIndicadores(simulacroId, indicadores) {
    return apiClient.post(`/recomendaciones/indicadores/`, {
      simulacro_id: simulacroId,
      ...indicadores
    })
  },

  // =====================================================
  // DESCARGA
  // =====================================================

  /**
   * Descarga el documento de recomendaciones en PDF
   * @param {number} recomendacionId
   */
  async descargarPDF(recomendacionId) {
    const response = await fetch(
      `${apiClient.baseURL}/recomendaciones/${recomendacionId}/pdf/`,
      {
        headers: {
          'Authorization': `Bearer ${apiClient.getAccessToken()}`
        }
      }
    )
    
    if (!response.ok) {
      throw new Error('Error al descargar PDF')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `recomendaciones-${recomendacionId}.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }
}

export default recomendacionesService
