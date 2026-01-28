"""
URLs para el módulo de Agendamiento de Entrevistas.
"""
from django.urls import path
from .views import (
    EntrevistasListView,
    EntrevistaDetailView,
    HorariosDisponiblesView,
    AgendarEntrevistaView,
    ConfirmarEntrevistaView,
    ReprogramarEntrevistaView,
    VerificarReprogramacionView,
    CancelarEntrevistaView,
    VerificarCancelacionView,
    CalendarioEventosView,
    EntrevistasProximasView,
    DisponibilidadEmbajadaFakerView,
    SimularCitaEmbajadaView,
)

urlpatterns = [
    path('entrevistas/', EntrevistasListView.as_view(), name='entrevistas-list'),
    path('entrevistas/<int:pk>/', EntrevistaDetailView.as_view(), name='entrevista-detail'),
    path('entrevistas/horarios/', HorariosDisponiblesView.as_view(), name='horarios-disponibles'),
    path('entrevistas/agendar/', AgendarEntrevistaView.as_view(), name='agendar-entrevista'),
    path('entrevistas/calendario/', CalendarioEventosView.as_view(), name='calendario-eventos'),
    path('entrevistas/proximas/', EntrevistasProximasView.as_view(), name='entrevistas-proximas'),
    path('entrevistas/embajada/disponibilidad/', DisponibilidadEmbajadaFakerView.as_view(), name='embajada-disponibilidad'),
    path('entrevistas/embajada/simular-cita/', SimularCitaEmbajadaView.as_view(), name='embajada-simular-cita'),
    path('entrevistas/<int:pk>/confirmar/', ConfirmarEntrevistaView.as_view(), name='confirmar-entrevista'),
    path('entrevistas/<int:pk>/reprogramar/', ReprogramarEntrevistaView.as_view(), name='reprogramar-entrevista'),
    path('entrevistas/<int:pk>/puede-reprogramar/', VerificarReprogramacionView.as_view(), name='verificar-reprogramacion'),
    path('entrevistas/<int:pk>/cancelar/', CancelarEntrevistaView.as_view(), name='cancelar-entrevista'),
    path('entrevistas/<int:pk>/puede-cancelar/', VerificarCancelacionView.as_view(), name='verificar-cancelacion'),
]
