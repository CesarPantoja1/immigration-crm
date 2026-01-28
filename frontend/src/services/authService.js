/**
 * Servicio de Autenticación
 * Maneja login, registro, logout y gestión de perfil
 */
import apiClient from './api'

export const authService = {
  /**
   * Registra un nuevo usuario
   * @param {Object} userData - { email, password, password_confirm, first_name, last_name, telefono }
   */
  async register(userData) {
    const response = await apiClient.post('/auth/registro/', userData, {
      includeAuth: false
    })
    
    // Guardar tokens y usuario
    if (response.tokens) {
      apiClient.setTokens(response.tokens)
      localStorage.setItem('migrafacil_user', JSON.stringify(response.usuario))
    }
    
    return response
  },

  /**
   * Inicia sesión
   * @param {string} email
   * @param {string} password
   */
  async login(email, password) {
    const response = await apiClient.post('/auth/login/', { email, password }, {
      includeAuth: false
    })
    
    // Guardar tokens y usuario
    if (response.tokens) {
      apiClient.setTokens(response.tokens)
      localStorage.setItem('migrafacil_user', JSON.stringify(response.usuario))
    }
    
    return response
  },

  /**
   * Cierra sesión
   */
  async logout() {
    try {
      const refreshToken = apiClient.getRefreshToken()
      if (refreshToken) {
        await apiClient.post('/auth/logout/', { refresh: refreshToken })
      }
    } catch (error) {
      // Ignorar errores de logout
      console.warn('Error durante logout:', error)
    } finally {
      apiClient.clearTokens()
    }
  },

  /**
   * Obtiene el perfil del usuario actual
   */
  async getProfile() {
    return apiClient.get('/auth/perfil/')
  },

  /**
   * Actualiza el perfil del usuario
   * @param {Object} profileData - { first_name, last_name, telefono, foto_perfil }
   */
  async updateProfile(profileData) {
    // Si hay foto, usar FormData
    if (profileData.foto_perfil instanceof File) {
      const formData = new FormData()
      Object.keys(profileData).forEach(key => {
        formData.append(key, profileData[key])
      })
      return apiClient.patch('/auth/perfil/', formData, { contentType: null })
    }
    
    return apiClient.patch('/auth/perfil/', profileData)
  },

  /**
   * Cambia la contraseña del usuario
   * @param {string} passwordActual
   * @param {string} passwordNuevo
   * @param {string} passwordConfirm
   */
  async changePassword(passwordActual, passwordNuevo, passwordConfirm) {
    return apiClient.post('/auth/cambiar-password/', {
      password_actual: passwordActual,
      password_nuevo: passwordNuevo,
      password_confirm: passwordConfirm
    })
  },

  /**
   * Refresca el token de acceso
   */
  async refreshToken() {
    return apiClient.refreshAccessToken()
  },

  /**
   * Verifica si hay una sesión activa
   */
  async verifySession() {
    try {
      const user = await this.getProfile()
      localStorage.setItem('migrafacil_user', JSON.stringify(user))
      return { isValid: true, user }
    } catch (error) {
      return { isValid: false, user: null }
    }
  },

  /**
   * Obtiene el usuario guardado en localStorage
   */
  getStoredUser() {
    const userData = localStorage.getItem('migrafacil_user')
    return userData ? JSON.parse(userData) : null
  },

  /**
   * Verifica si hay tokens guardados
   */
  hasTokens() {
    return !!apiClient.getAccessToken()
  },

  /**
   * Limpia los tokens guardados
   */
  clearTokens() {
    apiClient.clearTokens()
  },

  /**
   * Obtiene el token de acceso
   */
  getAccessToken() {
    return apiClient.getAccessToken()
  }
}

export default authService
