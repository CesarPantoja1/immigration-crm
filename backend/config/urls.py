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

    # Apps
    path('usuarios/', include('apps.usuarios.presentation.urls')),
    # path('solicitudes/recepcion/', include('apps.solicitudes.recepcion.presentation.urls')),
    # path('solicitudes/agendamiento/', include('apps.solicitudes.agendamiento.presentation.urls')),
    # path('preparacion/simulacion/', include('apps.preparacion.simulacion.presentation.urls')),
    # path('preparacion/recomendaciones/', include('apps.preparacion.recomendaciones.presentation.urls')),
    # path('notificaciones/seguimiento/', include('apps.notificaciones.seguimiento.presentation.urls')),
    # path('notificaciones/coordinacion/', include('apps.notificaciones.coordinacion.presentation.urls')),

    # API (cuando se implemente)
    # path('api/', include('api.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Personalizar el admin
admin.site.site_header = 'CRM Migratorio - Administración'
admin.site.site_title = 'CRM Migratorio'
admin.site.index_title = 'Panel de Administración'
