"""
URLs para la característica de Agendamiento de Entrevistas.
"""
from django.urls import path
from . import views_simple as views  # Usando vistas simplificadas

app_name = 'agendamiento'

urlpatterns = [
    # Asignación de entrevistas
    path('asignar-fecha-fija/', views.asignar_fecha_fija, name='asignar_fecha_fija'),
    path('ofrecer-opciones/', views.ofrecer_opciones, name='ofrecer_opciones'),

    # Operaciones sobre entrevista específica
    path('<str:entrevista_id>/', views.consultar_entrevista, name='consultar_entrevista'),
    path('<str:entrevista_id>/seleccionar-opcion/', views.seleccionar_opcion, name='seleccionar_opcion'),
    path('<str:entrevista_id>/reprogramar/', views.reprogramar_entrevista, name='reprogramar_entrevista'),
    path('<str:entrevista_id>/cancelar/', views.cancelar_entrevista, name='cancelar_entrevista'),
    path('<str:entrevista_id>/confirmar/', views.confirmar_asistencia, name='confirmar_asistencia'),

    # Consultas
    path('solicitud/<str:solicitud_id>/', views.consultar_por_solicitud, name='consultar_por_solicitud'),
    path('listar/', views.listar_entrevistas, name='listar_entrevistas'),
]
