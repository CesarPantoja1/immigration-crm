# -*- coding: utf-8 -*-
"""Módulo de lógica de negocio para testing BDD de Agendamiento de Entrevistas."""

from .constants import (
    ESTADOS_ENTREVISTA,
    ESTADOS_ENTREVISTA_LEGIBLES,
    MODOS_ASIGNACION,
    MOTIVOS_CANCELACION,
    MOTIVOS_CANCELACION_LEGIBLES,
    REGLAS_EMBAJADA_DEFAULT,
    REGLA_EMBAJADA_DEFAULT,
    MENSAJES,
)

from .entities import (
    HorarioEntity,
    OpcionHorarioEntity,
    ReglaEmbajadaEntity,
    EntrevistaAgendamientoEntity,
    ResultadoOperacionEntity,
    reset_id_counters,
    crear_entrevista_agendamiento,
    crear_horario,
    crear_opcion_horario,
    crear_regla_embajada,
    crear_resultado,
)

from .services import (
    AgendamientoException,
    ReprogramacionNoPermitidaException,
    CancelacionNoPermitidaException,
    ModificacionNoPermitidaException,
    HorarioNoDisponibleException,
    AgendamientoSeleccionService,
    AgendamientoReprogramacionService,
    AgendamientoCancelacionService,
    AgendamientoConfirmacionService,
    AgendamientoProteccionService,
    AgendamientoService,
)

__all__ = [
    # Constantes
    'ESTADOS_ENTREVISTA', 'ESTADOS_ENTREVISTA_LEGIBLES', 'MODOS_ASIGNACION',
    'MOTIVOS_CANCELACION', 'MOTIVOS_CANCELACION_LEGIBLES',
    'REGLAS_EMBAJADA_DEFAULT', 'REGLA_EMBAJADA_DEFAULT', 'MENSAJES',
    # Entidades
    'HorarioEntity', 'OpcionHorarioEntity', 'ReglaEmbajadaEntity',
    'EntrevistaAgendamientoEntity', 'ResultadoOperacionEntity',
    # Factory functions
    'reset_id_counters', 'crear_entrevista_agendamiento', 'crear_horario',
    'crear_opcion_horario', 'crear_regla_embajada', 'crear_resultado',
    # Excepciones
    'AgendamientoException', 'ReprogramacionNoPermitidaException',
    'CancelacionNoPermitidaException', 'ModificacionNoPermitidaException',
    'HorarioNoDisponibleException',
    # Servicios
    'AgendamientoSeleccionService', 'AgendamientoReprogramacionService',
    'AgendamientoCancelacionService', 'AgendamientoConfirmacionService',
    'AgendamientoProteccionService', 'AgendamientoService',
]
