// JavaScript global para el CRM Migratorio

document.addEventListener('DOMContentLoaded', function() {
    console.log('CRM Migratorio - Sistema cargado');

    // Auto-ocultar mensajes después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Agregar funcionalidades globales aquí
});
