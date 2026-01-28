"""
URL Configuration para el CRM Migratorio.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/', include('apps.usuarios.presentation.urls')),
    path('api/', include('apps.solicitudes.urls')),
    path('api/', include('apps.solicitudes.agendamiento.urls')),
    path('api/', include('apps.preparacion.urls')),
    path('api/', include('apps.notificaciones.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Personalizar el admin
admin.site.site_header = 'CRM Migratorio - Administración'
admin.site.site_title = 'CRM Migratorio'
admin.site.index_title = 'Panel de Administración'
