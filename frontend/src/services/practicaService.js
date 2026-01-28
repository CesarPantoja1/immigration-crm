/**
 * Servicio de Práctica Individual
 * Maneja los cuestionarios de práctica por tipo de visa
 */
import apiClient from './api'

export const practicaService = {
  // =====================================================
  // CUESTIONARIOS
  // =====================================================

  /**
   * Obtiene los tipos de visa disponibles para práctica
   */
  async getTiposVisa() {
    return apiClient.get('/practica/tipos-visa/')
  },

  /**
   * Obtiene un cuestionario por tipo de visa
   * @param {string} tipoVisa - estudio, trabajo, vivienda
   */
  async getCuestionario(tipoVisa) {
    return apiClient.get(`/practica/cuestionario/${tipoVisa}/`)
  },

  /**
   * Inicia un cuestionario
   * @param {string} tipoVisa
   */
  async iniciarCuestionario(tipoVisa) {
    return apiClient.post(`/practica/iniciar/`, { tipo_visa: tipoVisa })
  },

  /**
   * Envía respuesta a una pregunta
   * @param {number} cuestionarioId
   * @param {number} preguntaId
   * @param {string} respuesta
   */
  async responderPregunta(cuestionarioId, preguntaId, respuesta) {
    return apiClient.post(`/practica/${cuestionarioId}/responder/`, {
      pregunta_id: preguntaId,
      respuesta
    })
  },

  /**
   * Finaliza un cuestionario
   * @param {number} cuestionarioId
   * @param {Array} respuestas - [{ pregunta_id, respuesta }]
   */
  async finalizarCuestionario(cuestionarioId, respuestas) {
    return apiClient.post(`/practica/${cuestionarioId}/finalizar/`, {
      respuestas
    })
  },

  // =====================================================
  // RESULTADOS
  // =====================================================

  /**
   * Obtiene el resultado de un cuestionario
   * @param {number} cuestionarioId
   */
  async getResultado(cuestionarioId) {
    return apiClient.get(`/practica/${cuestionarioId}/resultado/`)
  },

  /**
   * Obtiene las respuestas incorrectas
   * @param {number} cuestionarioId
   */
  async getRespuestasIncorrectas(cuestionarioId) {
    return apiClient.get(`/practica/${cuestionarioId}/incorrectas/`)
  },

  /**
   * Obtiene el historial de prácticas del usuario
   */
  async getHistorial() {
    return apiClient.get('/practica/historial/')
  },

  /**
   * Obtiene estadísticas de práctica
   */
  async getEstadisticas() {
    return apiClient.get('/practica/estadisticas/')
  }
}

export default practicaService
