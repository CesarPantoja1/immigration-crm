/**
 * MigraFácil - Auth Service
 * Servicio de autenticación
 */

import api from './api.js';

class AuthService {
    /**
     * Registra un nuevo usuario
     */
    async register(userData) {
        const response = await api.post('/auth/register/', userData, { includeAuth: false });
        
        if (response.tokens) {
            api.saveTokens(response.tokens.access, response.tokens.refresh);
            localStorage.setItem('user', JSON.stringify(response.user));
        }
        
        return response;
    }

    /**
     * Inicia sesión
     */
    async login(email, password) {
        const response = await api.post('/auth/login/', { email, password }, { includeAuth: false });
        
        if (response.access) {
            api.saveTokens(response.access, response.refresh);
            localStorage.setItem('user', JSON.stringify(response.user));
        }
        
        return response;
    }

    /**
     * Cierra sesión
     */
    async logout() {
        try {
            const refreshToken = api.getRefreshToken();
            if (refreshToken) {
                await api.post('/auth/logout/', { refresh: refreshToken });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            api.clearTokens();
            window.location.href = '/pages/auth/login.html';
        }
    }

    /**
     * Obtiene el usuario actual del localStorage
     */
    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }

    /**
     * Verifica si el usuario está autenticado
     */
    isAuthenticated() {
        return !!api.getAccessToken();
    }

    /**
     * Obtiene el perfil del usuario desde el servidor
     */
    async getProfile() {
        return api.get('/auth/profile/');
    }

    /**
     * Actualiza el perfil del usuario
     */
    async updateProfile(data) {
        const response = await api.patch('/auth/profile/', data);
        localStorage.setItem('user', JSON.stringify(response));
        return response;
    }

    /**
     * Cambia la contraseña
     */
    async changePassword(currentPassword, newPassword, confirmPassword) {
        return api.post('/auth/change-password/', {
            password_actual: currentPassword,
            password_nueva: newPassword,
            password_confirm: confirmPassword,
        });
    }

    /**
     * Redirige al usuario según su rol
     */
    redirectByRole(user = null) {
        const currentUser = user || this.getCurrentUser();
        if (!currentUser) {
            window.location.href = '/pages/auth/login.html';
            return;
        }

        switch (currentUser.rol) {
            case 'admin':
            case 'agente':
                window.location.href = '/pages/asesor/dashboard.html';
                break;
            case 'cliente':
            default:
                window.location.href = '/pages/migrante/dashboard.html';
                break;
        }
    }
}

const authService = new AuthService();
export default authService;
