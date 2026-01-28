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
    InfoSalaView,
    EstadoSalaView,
    DebugUserInfoView,
    
    # Recomendaciones
    RecomendacionesListView,
    RecomendacionDetailView,
    GenerarRecomendacionView,
    
    # Recomendaciones con IA
    SubirTranscripcionView,
    GenerarRecomendacionIAView,
    SimulacrosCompletadosAsesorView,
    RecomendacionClienteView,
    RecomendacionDetalleClienteView,
    
    # Feedback y PDF
    SimulacroFeedbackView,
    DescargarPDFRecomendacionView,
    DescargarPDFSimulacroView,
    
    # Configuración de IA
    ConfiguracionIAView,
    TestAPIKeyView,
    
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
    path('simulacros/<int:pk>/sala/', InfoSalaView.as_view(), name='info_sala'),
    path('simulacros/<int:pk>/estado-sala/', EstadoSalaView.as_view(), name='estado_sala'),
    path('simulacros/<int:pk>/iniciar/', IniciarSimulacroView.as_view(), name='iniciar_simulacro'),
    path('simulacros/<int:pk>/finalizar/', FinalizarSimulacroView.as_view(), name='finalizar_simulacro'),
    
    # Recomendaciones
    path('recomendaciones/', RecomendacionesListView.as_view(), name='recomendaciones_list'),
    path('recomendaciones/generar/', GenerarRecomendacionView.as_view(), name='generar_recomendacion'),
    path('recomendaciones/<int:pk>/', RecomendacionDetailView.as_view(), name='recomendacion_detail'),
    
    # Recomendaciones con IA
    path('simulacros/completados/', SimulacrosCompletadosAsesorView.as_view(), name='simulacros_completados'),
    path('simulacros/<int:pk>/subir-transcripcion/', SubirTranscripcionView.as_view(), name='subir_transcripcion'),
    path('simulacros/<int:pk>/generar-recomendacion-ia/', GenerarRecomendacionIAView.as_view(), name='generar_recomendacion_ia'),
    path('simulacros/<int:pk>/mi-recomendacion/', RecomendacionClienteView.as_view(), name='mi_recomendacion'),
    path('simulacros/<int:pk>/feedback/', SimulacroFeedbackView.as_view(), name='simulacro_feedback'),
    path('simulacros/<int:pk>/descargar-pdf/', DescargarPDFSimulacroView.as_view(), name='descargar_pdf_simulacro'),
    path('mis-recomendaciones/', RecomendacionClienteView.as_view(), name='mis_recomendaciones'),
    path('recomendaciones/<int:pk>/detalle-cliente/', RecomendacionDetalleClienteView.as_view(), name='recomendacion_detalle_cliente'),
    path('recomendaciones/<int:pk>/descargar-pdf/', DescargarPDFRecomendacionView.as_view(), name='descargar_pdf'),
    
    # Configuración de IA
    path('configuracion-ia/', ConfiguracionIAView.as_view(), name='configuracion_ia'),
    path('configuracion-ia/test/', TestAPIKeyView.as_view(), name='test_api_key'),
    
    # Práctica Individual
    path('practica/tipos-visa/', TiposVisaPracticaView.as_view(), name='tipos_visa'),
    path('practica/iniciar/', IniciarPracticaView.as_view(), name='iniciar_practica'),
    path('practica/historial/', HistorialPracticaView.as_view(), name='historial_practica'),
    path('practica/estadisticas/', EstadisticasPracticaView.as_view(), name='estadisticas_practica'),
    path('practica/<int:pk>/finalizar/', FinalizarPracticaView.as_view(), name='finalizar_practica'),
    
    # Debug (solo en DEBUG mode)
    path('debug/user/', DebugUserInfoView.as_view(), name='debug_user'),
]
