"""
URLs de la API de Solicitudes.
"""
from django.urls import path
from .views import (
    # Cliente
    MisSolicitudesView,
    CrearSolicitudView,
    SolicitudDetailView,
    EstadisticasClienteView,
    
    # Asesor
    SolicitudesAsignadasView,
    SolicitudesPendientesView,
    ActualizarSolicitudView,
    AsignarAsesorView,
    EstadisticasAsesorView,
)

app_name = 'solicitudes'

urlpatterns = [
    # Cliente
    path('solicitudes/mis-solicitudes/', MisSolicitudesView.as_view(), name='mis_solicitudes'),
    path('solicitudes/nueva/', CrearSolicitudView.as_view(), name='crear_solicitud'),
    path('solicitudes/<int:pk>/', SolicitudDetailView.as_view(), name='solicitud_detail'),
    path('solicitudes/estadisticas/cliente/', EstadisticasClienteView.as_view(), name='estadisticas_cliente'),
    
    # Asesor
    path('solicitudes/asignadas/', SolicitudesAsignadasView.as_view(), name='solicitudes_asignadas'),
    path('solicitudes/pendientes/', SolicitudesPendientesView.as_view(), name='solicitudes_pendientes'),
    path('solicitudes/<int:pk>/actualizar/', ActualizarSolicitudView.as_view(), name='actualizar_solicitud'),
    path('solicitudes/<int:pk>/asignar/', AsignarAsesorView.as_view(), name='asignar_asesor'),
    path('solicitudes/estadisticas/asesor/', EstadisticasAsesorView.as_view(), name='estadisticas_asesor'),
]
