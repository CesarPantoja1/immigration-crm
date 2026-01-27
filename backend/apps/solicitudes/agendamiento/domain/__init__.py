"""
Dominio de Agendamiento de Entrevistas.

Este módulo maneja el agendamiento de entrevistas consulares,
considerando que la embajada es un actor externo que asigna las citas.
"""
from .value_objects import (
    EstadoEntrevista,
    ModoAsignacion,
    MotivoCancelacion,
    HorarioEntrevista,
    OpcionHorario,
    ReglaEmbajada,
    NotificacionEmbajada,
    REGLAS_EMBAJADAS,
    obtener_regla_embajada,
)

from .entities import (
    Entrevista,
    RespuestaEmbajada,
    GestorEntrevistas,
)

from .repositories import (
    IEntrevistaRepository,
    IRespuestaEmbajadaRepository,
    IGestorEntrevistasRepository,
)

from .services import (
    ResultadoOperacion,
    AsignacionEntrevistaService,
    ReprogramacionService,
    CancelacionService,
    ConfirmacionService,
    NotificacionEntrevistaService,
    ValidacionEntrevistaService,
    ProcesamientoRespuestaEmbajadaService,
)

from .exceptions import (
    AgendamientoException,
    EntrevistaNoEncontradaException,
    EntrevistaYaAgendadaException,
    ReprogramacionNoPermitidaException,
    CancelacionNoPermitidaException,
    OpcionNoDisponibleException,
    SolicitudNoAprobadaException,
    EntrevistaNoConfirmableException,
    FechaInvalidaException,
)

__all__ = [
    # Value Objects
    'EstadoEntrevista',
    'ModoAsignacion',
    'MotivoCancelacion',
    'HorarioEntrevista',
    'OpcionHorario',
    'ReglaEmbajada',
    'NotificacionEmbajada',
    'REGLAS_EMBAJADAS',
    'obtener_regla_embajada',
    
    # Entities
    'Entrevista',
    'RespuestaEmbajada',
    'GestorEntrevistas',
    
    # Repositories
    'IEntrevistaRepository',
    'IRespuestaEmbajadaRepository',
    'IGestorEntrevistasRepository',
    
    # Services
    'ResultadoOperacion',
    'AsignacionEntrevistaService',
    'ReprogramacionService',
    'CancelacionService',
    'ConfirmacionService',
    'NotificacionEntrevistaService',
    'ValidacionEntrevistaService',
    'ProcesamientoRespuestaEmbajadaService',
    
    # Exceptions
    'AgendamientoException',
    'EntrevistaNoEncontradaException',
    'EntrevistaYaAgendadaException',
    'ReprogramacionNoPermitidaException',
    'CancelacionNoPermitidaException',
    'OpcionNoDisponibleException',
    'SolicitudNoAprobadaException',
    'EntrevistaNoConfirmableException',
    'FechaInvalidaException',
]
