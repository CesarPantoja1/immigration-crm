"""
URLs para el módulo de Notificaciones.
"""
from django.urls import path
from .views import (
    NotificacionesListView,
    NotificacionDetailView,
    ConteoNoLeidasView,
    NotificacionesNoLeidasView,
    MarcarLeidaView,
    MarcarTodasLeidasView,
    EliminarNotificacionView,
    EliminarLeidasView,
    TiposNotificacionView,
    PreferenciasView,
)

app_name = 'notificaciones'

urlpatterns = [
    # Lista y detalle
    path('notificaciones/', NotificacionesListView.as_view(), name='list'),
    path('notificaciones/no-leidas/', NotificacionesNoLeidasView.as_view(), name='no_leidas'),
    path('notificaciones/no-leidas/count/', ConteoNoLeidasView.as_view(), name='conteo_no_leidas'),
    path('notificaciones/<int:pk>/', NotificacionDetailView.as_view(), name='detail'),
    
    # Acciones
    path('notificaciones/<int:pk>/leer/', MarcarLeidaView.as_view(), name='marcar_leida'),
    path('notificaciones/leer-todas/', MarcarTodasLeidasView.as_view(), name='marcar_todas_leidas'),
    path('notificaciones/<int:pk>/eliminar/', EliminarNotificacionView.as_view(), name='eliminar'),
    path('notificaciones/eliminar-leidas/', EliminarLeidasView.as_view(), name='eliminar_leidas'),
    
    # Tipos y preferencias
    path('notificaciones/tipos/', TiposNotificacionView.as_view(), name='tipos'),
    path('notificaciones/preferencias/', PreferenciasView.as_view(), name='preferencias'),
]
