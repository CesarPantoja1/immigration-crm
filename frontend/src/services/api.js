/**
 * Configuración base de la API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

/**
 * Cliente HTTP base con manejo de autenticación
 */
class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL
  }

  /**
   * Obtiene el token de acceso del localStorage
   */
  getAccessToken() {
    const tokens = localStorage.getItem('migrafacil_tokens')
    if (tokens) {
      const parsed = JSON.parse(tokens)
      return parsed.access
    }
    return null
  }

  /**
   * Obtiene el refresh token del localStorage
   */
  getRefreshToken() {
    const tokens = localStorage.getItem('migrafacil_tokens')
    if (tokens) {
      const parsed = JSON.parse(tokens)
      return parsed.refresh
    }
    return null
  }

  /**
   * Guarda los tokens en localStorage
   */
  setTokens(tokens) {
    localStorage.setItem('migrafacil_tokens', JSON.stringify(tokens))
  }

  /**
   * Elimina los tokens del localStorage
   */
  clearTokens() {
    localStorage.removeItem('migrafacil_tokens')
    localStorage.removeItem('migrafacil_user')
  }

  /**
   * Construye los headers de la petición
   */
  buildHeaders(includeAuth = true, contentType = 'application/json') {
    const headers = {}
    
    if (contentType) {
      headers['Content-Type'] = contentType
    }

    if (includeAuth) {
      const token = this.getAccessToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    return headers
  }

  /**
   * Intenta refrescar el token de acceso
   */
  async refreshAccessToken() {
    const refreshToken = this.getRefreshToken()
    if (!refreshToken) {
      throw new Error('No hay refresh token disponible')
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      })

      if (!response.ok) {
        throw new Error('Error al refrescar token')
      }

      const data = await response.json()
      this.setTokens({
        access: data.access,
        refresh: refreshToken
      })

      return data.access
    } catch (error) {
      this.clearTokens()
      throw error
    }
  }

  /**
   * Realiza una petición HTTP
   */
  async request(endpoint, options = {}) {
    const {
      method = 'GET',
      body = null,
      includeAuth = true,
      contentType = 'application/json',
      retryOnUnauthorized = true
    } = options

    const url = `${this.baseURL}${endpoint}`
    const headers = this.buildHeaders(includeAuth, contentType)

    const fetchOptions = {
      method,
      headers
    }

    if (body) {
      if (body instanceof FormData) {
        delete fetchOptions.headers['Content-Type'] // FormData maneja su propio Content-Type
        fetchOptions.body = body
      } else if (contentType === 'application/json') {
        fetchOptions.body = JSON.stringify(body)
      } else {
        fetchOptions.body = body
      }
    }

    try {
      let response = await fetch(url, fetchOptions)

      // Si recibimos 401, intentar refrescar el token
      if (response.status === 401 && retryOnUnauthorized && includeAuth) {
        try {
          await this.refreshAccessToken()
          // Reintentar la petición con el nuevo token
          fetchOptions.headers = this.buildHeaders(true, contentType)
          response = await fetch(url, fetchOptions)
        } catch (refreshError) {
          // Si falla el refresh, limpiar tokens y lanzar error
          this.clearTokens()
          window.location.href = '/login'
          throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.')
        }
      }

      // Parsear respuesta
      const data = await this.parseResponse(response)

      if (!response.ok) {
        const error = new Error(data.error || data.detail || 'Error en la petición')
        error.status = response.status
        error.data = data
        throw error
      }

      return data
    } catch (error) {
      if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
        throw new Error('No se pudo conectar con el servidor. Verifica tu conexión.')
      }
      throw error
    }
  }

  /**
   * Parsea la respuesta según el Content-Type
   */
  async parseResponse(response) {
    const contentType = response.headers.get('Content-Type')
    
    if (contentType && contentType.includes('application/json')) {
      return response.json()
    }
    
    return response.text()
  }

  // Métodos de conveniencia
  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' })
  }

  post(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', body })
  }

  put(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'PUT', body })
  }

  patch(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'PATCH', body })
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' })
  }
}

// Exportar instancia única
export const apiClient = new ApiClient()
export default apiClient
