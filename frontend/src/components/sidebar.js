/**
 * MigraFácil - Sidebar Component
 * Componente de navegación lateral reutilizable
 */

class Sidebar {
    constructor(options = {}) {
        this.container = options.container || document.getElementById('sidebar');
        this.userRole = options.userRole || 'cliente';
        this.currentPath = window.location.pathname;
        
        if (this.container) {
            this.render();
            this.bindEvents();
        }
    }

    getMenuItems() {
        const baseItems = {
            cliente: [
                {
                    section: 'Principal',
                    items: [
                        { icon: 'home', label: 'Inicio', href: '/pages/migrante/dashboard.html' },
                        { icon: 'file-text', label: 'Mis Solicitudes', href: '/pages/migrante/solicitudes.html' },
                        { icon: 'calendar', label: 'Mis Citas', href: '/pages/migrante/citas.html' },
                    ]
                },
                {
                    section: 'Documentos',
                    items: [
                        { icon: 'folder', label: 'Mis Documentos', href: '/pages/migrante/documentos.html' },
                        { icon: 'upload', label: 'Subir Documentos', href: '/pages/migrante/subir-documentos.html' },
                    ]
                },
                {
                    section: 'Preparación',
                    items: [
                        { icon: 'video', label: 'Simulacros', href: '/pages/migrante/simulacros.html' },
                        { icon: 'book-open', label: 'Recursos', href: '/pages/migrante/recursos.html' },
                    ]
                },
                {
                    section: 'Cuenta',
                    items: [
                        { icon: 'settings', label: 'Configuración', href: '/pages/migrante/configuracion.html' },
                        { icon: 'help-circle', label: 'Ayuda', href: '/pages/migrante/ayuda.html' },
                    ]
                }
            ],
            agente: [
                {
                    section: 'Principal',
                    items: [
                        { icon: 'home', label: 'Dashboard', href: '/pages/asesor/dashboard.html' },
                        { icon: 'users', label: 'Clientes', href: '/pages/asesor/clientes.html' },
                        { icon: 'file-text', label: 'Solicitudes', href: '/pages/asesor/solicitudes.html', badge: '24' },
                    ]
                },
                {
                    section: 'Gestión',
                    items: [
                        { icon: 'calendar', label: 'Citas', href: '/pages/asesor/citas.html' },
                        { icon: 'folder', label: 'Documentos', href: '/pages/asesor/documentos.html' },
                        { icon: 'video', label: 'Simulacros', href: '/pages/asesor/simulacros.html' },
                    ]
                },
                {
                    section: 'Reportes',
                    items: [
                        { icon: 'bar-chart-2', label: 'Estadísticas', href: '/pages/asesor/estadisticas.html' },
                        { icon: 'pie-chart', label: 'Reportes', href: '/pages/asesor/reportes.html' },
                    ]
                },
                {
                    section: 'Cuenta',
                    items: [
                        { icon: 'settings', label: 'Configuración', href: '/pages/asesor/configuracion.html' },
                    ]
                }
            ],
            admin: [
                {
                    section: 'Principal',
                    items: [
                        { icon: 'home', label: 'Dashboard', href: '/pages/admin/dashboard.html' },
                        { icon: 'users', label: 'Usuarios', href: '/pages/admin/usuarios.html' },
                        { icon: 'briefcase', label: 'Asesores', href: '/pages/admin/asesores.html' },
                    ]
                },
                {
                    section: 'Sistema',
                    items: [
                        { icon: 'sliders', label: 'Configuración', href: '/pages/admin/configuracion.html' },
                        { icon: 'shield', label: 'Seguridad', href: '/pages/admin/seguridad.html' },
                        { icon: 'activity', label: 'Logs', href: '/pages/admin/logs.html' },
                    ]
                }
            ]
        };

        // Admin tiene acceso a todo
        if (this.userRole === 'admin') {
            return [...baseItems.admin, ...baseItems.agente.slice(1)];
        }

        return baseItems[this.userRole] || baseItems.cliente;
    }

    getIcon(name) {
        const icons = {
            'home': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>',
            'file-text': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>',
            'calendar': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>',
            'folder': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>',
            'upload': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>',
            'video': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>',
            'book-open': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>',
            'settings': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>',
            'help-circle': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>',
            'users': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>',
            'bar-chart-2': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 20V10M12 20V4M6 20v-6"/>',
            'pie-chart': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"/>',
            'briefcase': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>',
            'sliders': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>',
            'shield': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>',
            'activity': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
            'log-out': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>',
        };

        return `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">${icons[name] || ''}</svg>`;
    }

    isActive(href) {
        return this.currentPath.includes(href.replace('.html', ''));
    }

    render() {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const userName = user.nombre || 'Usuario';
        const userRole = user.rol || 'cliente';
        const initials = userName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);

        const menuSections = this.getMenuItems();

        this.container.innerHTML = `
            <aside class="sidebar" id="main-sidebar">
                <div class="sidebar-header">
                    <div class="sidebar-logo">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <span class="sidebar-brand">MigraFácil</span>
                </div>

                <nav class="sidebar-nav">
                    ${menuSections.map(section => `
                        <div class="nav-section">
                            <div class="nav-section-title">${section.section}</div>
                            ${section.items.map(item => `
                                <a href="${item.href}" class="nav-item ${this.isActive(item.href) ? 'active' : ''}">
                                    ${this.getIcon(item.icon)}
                                    <span class="nav-text">${item.label}</span>
                                    ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}
                                </a>
                            `).join('')}
                        </div>
                    `).join('')}
                </nav>

                <div class="sidebar-footer">
                    <div class="sidebar-user">
                        <div class="avatar avatar-md avatar-primary">${initials}</div>
                        <div class="sidebar-user-info">
                            <div class="sidebar-user-name">${userName}</div>
                            <div class="sidebar-user-role">${this.getRoleLabel(userRole)}</div>
                        </div>
                        <button class="btn-icon btn-ghost" id="logout-btn" title="Cerrar sesión">
                            ${this.getIcon('log-out')}
                        </button>
                    </div>
                </div>
            </aside>
        `;
    }

    getRoleLabel(role) {
        const labels = {
            admin: 'Administrador',
            agente: 'Asesor',
            cliente: 'Migrante'
        };
        return labels[role] || role;
    }

    bindEvents() {
        // Logout
        const logoutBtn = this.container.querySelector('#logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                localStorage.clear();
                window.location.href = '/pages/auth/login.html';
            });
        }
    }
}

export default Sidebar;
