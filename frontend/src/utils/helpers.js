/**
 * MigraFácil - Utility Functions
 * Funciones de utilidad compartidas
 */

/**
 * Valida un email
 */
export function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Valida la fortaleza de una contraseña
 * @returns {Object} { score, label, color }
 */
export function validatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score += 25;
    if (password.length >= 12) score += 15;
    if (/[a-z]/.test(password)) score += 15;
    if (/[A-Z]/.test(password)) score += 15;
    if (/[0-9]/.test(password)) score += 15;
    if (/[^a-zA-Z0-9]/.test(password)) score += 15;

    if (score < 40) {
        return { score, percent: 33, label: 'Débil', color: 'error' };
    } else if (score < 70) {
        return { score, percent: 66, label: 'Media', color: 'warning' };
    } else {
        return { score, percent: 100, label: 'Fuerte', color: 'success' };
    }
}

/**
 * Formatea una fecha
 */
export function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        ...options
    };
    
    return new Date(date).toLocaleDateString('es-MX', defaultOptions);
}

/**
 * Formatea una fecha relativa (hace X tiempo)
 */
export function formatRelativeTime(date) {
    const now = new Date();
    const past = new Date(date);
    const diffMs = now - past;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) return 'Hace un momento';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours}h`;
    if (diffDays < 7) return `Hace ${diffDays}d`;
    
    return formatDate(date, { month: 'short', day: 'numeric' });
}

/**
 * Trunca un texto
 */
export function truncate(text, length = 100) {
    if (text.length <= length) return text;
    return text.substring(0, length).trim() + '...';
}

/**
 * Obtiene las iniciales de un nombre
 */
export function getInitials(name) {
    if (!name) return '';
    return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
}

/**
 * Debounce function
 */
export function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Genera un ID único
 */
export function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Deep clone de un objeto
 */
export function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Capitaliza la primera letra
 */
export function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Parsea query params de la URL
 */
export function getQueryParams() {
    const params = new URLSearchParams(window.location.search);
    const result = {};
    for (const [key, value] of params) {
        result[key] = value;
    }
    return result;
}

/**
 * Formatea un número como moneda
 */
export function formatCurrency(amount, currency = 'MXN') {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Formatea un número con separadores de miles
 */
export function formatNumber(num) {
    return new Intl.NumberFormat('es-MX').format(num);
}

/**
 * Copia texto al portapapeles
 */
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch {
        return false;
    }
}

/**
 * Espera un tiempo determinado
 */
export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Verifica si estamos en desarrollo
 */
export function isDev() {
    return window.location.hostname === 'localhost' || 
           window.location.hostname === '127.0.0.1';
}
