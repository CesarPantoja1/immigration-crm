"""
URLs de la API de Usuarios y Autenticación.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegistroView,
    LoginView,
    LogoutView,
    PerfilView,
    CambiarPasswordView,
    UsuarioListView,
    AsesoresListView,
    UsuarioDetailView,
    # Admin views
    CrearAsesorView,
    AdminAsesoresListView,
    AdminAsesorDetailView,
    ToggleAsesorEstadoView,
    AdminEstadisticasView,
)

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Perfil
    path('auth/perfil/', PerfilView.as_view(), name='perfil'),
    path('auth/cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),

    # Gestión de usuarios
    path('usuarios/', UsuarioListView.as_view(), name='usuarios_list'),
    path('usuarios/asesores/', AsesoresListView.as_view(), name='asesores_list'),
    path('usuarios/<int:pk>/', UsuarioDetailView.as_view(), name='usuario_detail'),
    
    # Administración
    path('admin/estadisticas/', AdminEstadisticasView.as_view(), name='admin_estadisticas'),
    path('admin/asesores/', AdminAsesoresListView.as_view(), name='admin_asesores_list'),
    path('admin/asesores/crear/', CrearAsesorView.as_view(), name='admin_crear_asesor'),
    path('admin/asesores/<int:pk>/', AdminAsesorDetailView.as_view(), name='admin_asesor_detail'),
    path('admin/asesores/<int:pk>/toggle-estado/', ToggleAsesorEstadoView.as_view(), name='admin_toggle_asesor'),
]
