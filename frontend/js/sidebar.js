// js/sidebar.js
function inyectarSidebar() {
    // Detectamos el nombre del archivo actual (ej: "solicitudes.html")
    const currentPath = window.location.pathname.split("/").pop() || "index.html";

    const sidebarHTML = `
    <aside class="w-72 bg-white border-r border-gray-100 flex flex-col p-6 shrink-0 h-full">
        <nav class="flex-grow space-y-2">
            <a href="asesor-dashboard.html" class="sidebar-item ${currentPath === 'asesor-dashboard.html' ? 'active shadow-md text-white' : 'text-gray-400 hover:bg-primary-50 hover:text-primary-600'} flex items-center justify-between p-3 rounded-xl transition-all">
                <div class="flex items-center space-x-3 text-sm font-medium">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
                    <span>Dashboard</span>
                </div>
            </a>
            <a href="calendario.html" class="sidebar-item ${currentPath === 'calendario.html' ? 'active shadow-md text-white' : 'text-gray-400 hover:bg-primary-50 hover:text-primary-600'} flex items-center justify-between p-3 rounded-xl transition-all">
                <div class="flex items-center space-x-3 text-sm font-medium">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    <span>Calendario</span>
                </div>
            </a>
            <a href="solicitudes.html" class="sidebar-item ${currentPath === 'solicitudes.html' ? 'active shadow-md text-white' : 'text-gray-400 hover:bg-primary-50 hover:text-primary-600'} flex items-center justify-between p-3 rounded-xl transition-all">
                <div class="flex items-center space-x-3 text-sm font-medium">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    <span>Solicitudes</span>
                </div>
            </a>
            
            <a href="solicitudes.html" class="sidebar-item ${currentPath === 'solicitudes.html' ? 'active shadow-md text-white' : 'text-gray-400 hover:bg-primary-50 hover:text-primary-600'} flex items-center justify-between p-3 rounded-xl transition-all">
                <div class="flex items-center space-x-3 text-sm font-medium">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    <span>Documentos</span>
                </div>
            </a>
            <a href="login.html" class="sidebar-item text-gray-400 hover:bg-red-50 hover:text-red-600 flex items-center justify-between p-3 rounded-xl transition-all">
                <div class="flex items-center space-x-3 text-sm font-medium">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                    <span>Cerrar Sesión</span>
                </div>
            </a>
        </nav>
    </aside>
    `;

    const container = document.getElementById('sidebar-container');
    if (container) {
        container.innerHTML = sidebarHTML;
    }
}

document.addEventListener('DOMContentLoaded', inyectarSidebar);