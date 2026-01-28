"""
URLs para el módulo de Preparación (Simulacros).
"""
from django.urls import path
from .views import (
    # Simulacros
    SimulacrosListView,
    SimulacroDetailView,
    CrearPropuestaView,
    DisponibilidadView,
    ContadorSimulacrosView,
    SolicitarSimulacroView,
    AceptarPropuestaView,
    ContrapropuestaView,
    CancelarSimulacroView,
    IngresarSalaView,
    IniciarSimulacroView,
    FinalizarSimulacroView,
    PropuestasPendientesView,
    
    # Recomendaciones
    RecomendacionesListView,
    RecomendacionDetailView,
    GenerarRecomendacionView,
    
    # Práctica
    TiposVisaPracticaView,
    IniciarPracticaView,
    FinalizarPracticaView,
    HistorialPracticaView,
    EstadisticasPracticaView,
)

app_name = 'preparacion'

urlpatterns = [
    # Simulacros
    path('simulacros/', SimulacrosListView.as_view(), name='simulacros_list'),
    path('simulacros/disponibilidad/', DisponibilidadView.as_view(), name='disponibilidad'),
    path('simulacros/contador/', ContadorSimulacrosView.as_view(), name='contador'),
    path('simulacros/propuesta/', CrearPropuestaView.as_view(), name='crear_propuesta'),
    path('simulacros/propuestas/', PropuestasPendientesView.as_view(), name='propuestas_pendientes'),
    path('simulacros/solicitar/', SolicitarSimulacroView.as_view(), name='solicitar_simulacro'),
    path('simulacros/<int:pk>/', SimulacroDetailView.as_view(), name='simulacro_detail'),
    path('simulacros/<int:pk>/aceptar/', AceptarPropuestaView.as_view(), name='aceptar_propuesta'),
    path('simulacros/<int:pk>/contrapropuesta/', ContrapropuestaView.as_view(), name='contrapropuesta'),
    path('simulacros/<int:pk>/cancelar/', CancelarSimulacroView.as_view(), name='cancelar_simulacro'),
    path('simulacros/<int:pk>/sala-espera/', IngresarSalaView.as_view(), name='sala_espera'),
    path('simulacros/<int:pk>/iniciar/', IniciarSimulacroView.as_view(), name='iniciar_simulacro'),
    path('simulacros/<int:pk>/finalizar/', FinalizarSimulacroView.as_view(), name='finalizar_simulacro'),
    
    # Recomendaciones
    path('recomendaciones/', RecomendacionesListView.as_view(), name='recomendaciones_list'),
    path('recomendaciones/generar/', GenerarRecomendacionView.as_view(), name='generar_recomendacion'),
    path('recomendaciones/<int:pk>/', RecomendacionDetailView.as_view(), name='recomendacion_detail'),
    
    # Práctica Individual
    path('practica/tipos-visa/', TiposVisaPracticaView.as_view(), name='tipos_visa'),
    path('practica/iniciar/', IniciarPracticaView.as_view(), name='iniciar_practica'),
    path('practica/historial/', HistorialPracticaView.as_view(), name='historial_practica'),
    path('practica/estadisticas/', EstadisticasPracticaView.as_view(), name='estadisticas_practica'),
    path('practica/<int:pk>/finalizar/', FinalizarPracticaView.as_view(), name='finalizar_practica'),
]
