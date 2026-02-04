# -*- coding: utf-8 -*-
"""
Módulo de lógica de negocio para testing BDD de Agendamiento de Entrevistas.
Sigue el patrón n-capas con Service Layer.

RESPONSABILIDAD:
- Exportar entidades, servicios y constantes para los steps BDD
- Proveer una API limpia y desacoplada de Django/ORM

Estructura:
- constants.py: Constantes del dominio (estados, mensajes, reglas)
- entities.py: Clases que representan modelos (sin ORM)
- services.py: Lógica de negocio (Service Layer)

IMPORTANTE: Este paquete es EXCLUSIVO para BDD, no para runtime.
"""

from .constants import (
    # Estados
    ESTADOS_ENTREVISTA,
    ESTADOS_ENTREVISTA_LEGIBLES,
    MODOS_ASIGNACION,
    MOTIVOS_CANCELACION,
    MOTIVOS_CANCELACION_LEGIBLES,
    # Reglas
    REGLAS_EMBAJADA_DEFAULT,
    REGLA_EMBAJADA_DEFAULT,
    # Mensajes
    MENSAJES,
)

from .entities import (
    # Entidades
    HorarioEntity,
    OpcionHorarioEntity,
    ReglaEmbajadaEntity,
    EntrevistaAgendamientoEntity,
    ResultadoOperacionEntity,
    # Factory functions
    reset_id_counters,
    crear_entrevista_agendamiento,
    crear_horario,
    crear_opcion_horario,
    crear_regla_embajada,
    crear_resultado,
)

from .services import (
    # Excepciones
    AgendamientoException,
    ReprogramacionNoPermitidaException,
    CancelacionNoPermitidaException,
    ModificacionNoPermitidaException,
    HorarioNoDisponibleException,
    # Servicios específicos
    AgendamientoSeleccionService,
    AgendamientoReprogramacionService,
    AgendamientoCancelacionService,
    AgendamientoConfirmacionService,
    AgendamientoProteccionService,
    # Servicio orquestador
    AgendamientoService,
)

__all__ = [
    # Constantes
    'ESTADOS_ENTREVISTA',
    'ESTADOS_ENTREVISTA_LEGIBLES',
    'MODOS_ASIGNACION',
    'MOTIVOS_CANCELACION',
    'MOTIVOS_CANCELACION_LEGIBLES',
    'REGLAS_EMBAJADA_DEFAULT',
    'REGLA_EMBAJADA_DEFAULT',
    'MENSAJES',
    # Entidades
    'HorarioEntity',
    'OpcionHorarioEntity',
    'ReglaEmbajadaEntity',
    'EntrevistaAgendamientoEntity',
    'ResultadoOperacionEntity',
    # Factory functions
    'reset_id_counters',
    'crear_entrevista_agendamiento',
    'crear_horario',
    'crear_opcion_horario',
    'crear_regla_embajada',
    'crear_resultado',
    # Excepciones
    'AgendamientoException',
    'ReprogramacionNoPermitidaException',
    'CancelacionNoPermitidaException',
    'ModificacionNoPermitidaException',
    'HorarioNoDisponibleException',
    # Servicios
    'AgendamientoSeleccionService',
    'AgendamientoReprogramacionService',
    'AgendamientoCancelacionService',
    'AgendamientoConfirmacionService',
    'AgendamientoProteccionService',
    'AgendamientoService',
]
