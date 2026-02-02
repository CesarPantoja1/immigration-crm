"""
URLs de la API de Solicitudes, Documentos y Entrevistas.
"""
from django.urls import path
from .views import (
    # Solicitudes - Cliente
    MisSolicitudesView,
    CrearSolicitudView,
    SolicitudDetailView,
    EnviarSolicitudView,
    EstadisticasClienteView,

    # Solicitudes - Asesor
    SolicitudesAsignadasView,
    SolicitudesPendientesView,
    ActualizarSolicitudView,
    AsignarAsesorView,
    EstadisticasAsesorView,

    # Decision de Embajada (NUEVO)
    DecisionEmbajadaView,

    # Documentos
    SubirDocumentoView,
    ListarDocumentosSolicitudView,
    DocumentoDetailView,
    AprobarDocumentoView,
    RechazarDocumentoView,
    ResubirDocumentoView,

    # Entrevistas
    EntrevistasListView,
    EntrevistaDetailView,
    HorariosDisponiblesView,
    AgendarEntrevistaView,
    ConfirmarEntrevistaView,
    ReprogramarEntrevistaView,
    VerificarReprogramacionView,
    CancelarEntrevistaView,
    VerificarCancelacionView,
    EntrevistasProximasView,
    CalendarioEventosView,
)

app_name = 'solicitudes'

urlpatterns = [
    # ===== SOLICITUDES =====
    # Cliente
    path('solicitudes/mis-solicitudes/', MisSolicitudesView.as_view(), name='mis_solicitudes'),
    path('solicitudes/nueva/', CrearSolicitudView.as_view(), name='crear_solicitud'),
    path('solicitudes/<int:pk>/', SolicitudDetailView.as_view(), name='solicitud_detail'),
    path('solicitudes/<int:pk>/enviar/', EnviarSolicitudView.as_view(), name='enviar_solicitud'),
    path('solicitudes/estadisticas/cliente/', EstadisticasClienteView.as_view(), name='estadisticas_cliente'),
    
    # Asesor
    path('solicitudes/asignadas/', SolicitudesAsignadasView.as_view(), name='solicitudes_asignadas'),
    path('solicitudes/pendientes/', SolicitudesPendientesView.as_view(), name='solicitudes_pendientes'),
    path('solicitudes/<int:pk>/actualizar/', ActualizarSolicitudView.as_view(), name='actualizar_solicitud'),
    path('solicitudes/<int:pk>/asignar/', AsignarAsesorView.as_view(), name='asignar_asesor'),
    path('solicitudes/estadisticas/asesor/', EstadisticasAsesorView.as_view(), name='estadisticas_asesor'),

    # Decision de Embajada (NUEVO - flujo corregido)
    path('solicitudes/<int:pk>/decision-embajada/', DecisionEmbajadaView.as_view(), name='decision_embajada'),
    
    # ===== DOCUMENTOS =====
    path('solicitudes/<int:pk>/documentos/', SubirDocumentoView.as_view(), name='subir_documento'),
    path('solicitudes/<int:pk>/documentos/lista/', ListarDocumentosSolicitudView.as_view(), name='listar_documentos'),
    path('documentos/<int:pk>/', DocumentoDetailView.as_view(), name='documento_detail'),
    path('documentos/<int:pk>/aprobar/', AprobarDocumentoView.as_view(), name='aprobar_documento'),
    path('documentos/<int:pk>/rechazar/', RechazarDocumentoView.as_view(), name='rechazar_documento'),
    path('documentos/<int:pk>/resubir/', ResubirDocumentoView.as_view(), name='resubir_documento'),
    
    # ===== ENTREVISTAS =====
    path('entrevistas/', EntrevistasListView.as_view(), name='entrevistas_list'),
    path('entrevistas/<int:pk>/', EntrevistaDetailView.as_view(), name='entrevista_detail'),
    path('entrevistas/horarios/', HorariosDisponiblesView.as_view(), name='horarios_disponibles'),
    path('entrevistas/agendar/', AgendarEntrevistaView.as_view(), name='agendar_entrevista'),
    path('entrevistas/proximas/', EntrevistasProximasView.as_view(), name='entrevistas_proximas'),
    path('entrevistas/calendario/', CalendarioEventosView.as_view(), name='calendario_eventos'),
    path('entrevistas/<int:pk>/confirmar/', ConfirmarEntrevistaView.as_view(), name='confirmar_entrevista'),
    path('entrevistas/<int:pk>/reprogramar/', ReprogramarEntrevistaView.as_view(), name='reprogramar_entrevista'),
    path('entrevistas/<int:pk>/puede-reprogramar/', VerificarReprogramacionView.as_view(), name='verificar_reprogramacion'),
    path('entrevistas/<int:pk>/cancelar/', CancelarEntrevistaView.as_view(), name='cancelar_entrevista'),
    path('entrevistas/<int:pk>/puede-cancelar/', VerificarCancelacionView.as_view(), name='verificar_cancelacion'),
]
