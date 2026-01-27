/**
 * MigraFácil - API Service
 * Servicio centralizado para comunicación con el backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Obtiene el token de acceso del localStorage
     */
    getAccessToken() {
        return localStorage.getItem('access_token');
    }

    /**
     * Obtiene el token de refresh del localStorage
     */
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }

    /**
     * Guarda los tokens en localStorage
     */
    saveTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }

    /**
     * Limpia los tokens del localStorage
     */
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    /**
     * Construye los headers para las peticiones
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth) {
            const token = this.getAccessToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        return headers;
    }

    /**
     * Realiza una petición HTTP
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(options.includeAuth !== false),
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            
            // Si el token expiró, intentar refresh
            if (response.status === 401) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Reintentar la petición original
                    config.headers['Authorization'] = `Bearer ${this.getAccessToken()}`;
                    const retryResponse = await fetch(url, config);
                    return this.handleResponse(retryResponse);
                } else {
                    // Redirect al login
                    this.clearTokens();
                    window.location.href = '/pages/auth/login.html';
                    throw new Error('Sesión expirada');
                }
            }

            return this.handleResponse(response);
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Maneja la respuesta de la API
     */
    async handleResponse(response) {
        const data = await response.json().catch(() => null);
        
        if (!response.ok) {
            const error = new Error(data?.message || data?.detail || 'Error en la petición');
            error.status = response.status;
            error.data = data;
            throw error;
        }

        return data;
    }

    /**
     * Intenta refrescar el token de acceso
     */
    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken }),
            });

            if (response.ok) {
                const data = await response.json();
                this.saveTokens(data.access, data.refresh || refreshToken);
                return true;
            }
            return false;
        } catch {
            return false;
        }
    }

    // ===== Métodos HTTP =====
    
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options,
        });
    }

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Instancia global
const api = new ApiService();

export default api;
export { ApiService };
