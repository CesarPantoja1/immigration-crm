# -*- coding: utf-8 -*-
"""
Módulo de lógica de negocio para testing BDD de notificaciones.
Sigue el patrón n-capas con Service Layer alineado con apps/notificaciones.

Estructura:
- constants.py: Constantes del dominio (estados, tipos, embajadas)
- entities.py: Clases que representan modelos (sin ORM)
- services.py: Lógica de negocio (Service Layer)
"""
from .constants import (
    ESTADOS_SOLICITUD,
    TIPOS_VISA,
    EMBAJADAS,
    ESTADOS_DOCUMENTO,
    TIPOS_NOTIFICACION,
    # Constantes para Alertas de Entrevista
    ESTADOS_ENTREVISTA,
    ESTADOS_SIMULACRO,
    ESTADOS_RECOMENDACIONES,
    VENTANAS_RECORDATORIO,
    VENTANAS_PREPARACION,
    TIPOS_ALERTA_ENTREVISTA,
)

from .entities import (
    UsuarioEntity,
    DocumentoEntity,
    SolicitudEntity,
    NotificacionEntity,
    crear_usuario,
    crear_solicitud,
    crear_documento,
    crear_notificacion,
    reset_id_counters,
    # Entidades para Alertas de Entrevista
    EntrevistaEntity,
    SimulacroEntity,
    RecomendacionesEntity,
    CentroNotificacionesEntity,
    crear_entrevista,
    crear_simulacro,
    crear_recomendaciones,
    crear_centro_notificaciones,
)

from .services import (
    NotificacionService,
    SolicitudService,
    SeguimientoService,
    BuzonNotificacionesService,
    # Servicios para Alertas de Entrevista
    EntrevistaAlertasService,
    RecordatorioAlertasService,
    PreparacionAlertasService,
    SimulacroAlertasService,
    AlertasEntrevistaService,
)

__all__ = [
    # Constantes
    'ESTADOS_SOLICITUD',
    'TIPOS_VISA',
    'EMBAJADAS',
    'ESTADOS_DOCUMENTO',
    'TIPOS_NOTIFICACION',
    'ESTADOS_ENTREVISTA',
    'ESTADOS_SIMULACRO',
    'ESTADOS_RECOMENDACIONES',
    'VENTANAS_RECORDATORIO',
    'VENTANAS_PREPARACION',
    'TIPOS_ALERTA_ENTREVISTA',
    # Entidades
    'UsuarioEntity',
    'DocumentoEntity',
    'SolicitudEntity',
    'NotificacionEntity',
    'EntrevistaEntity',
    'SimulacroEntity',
    'RecomendacionesEntity',
    'CentroNotificacionesEntity',
    'crear_usuario',
    'crear_solicitud',
    'crear_documento',
    'crear_notificacion',
    'crear_entrevista',
    'crear_simulacro',
    'crear_recomendaciones',
    'crear_centro_notificaciones',
    'reset_id_counters',
    # Servicios
    'NotificacionService',
    'SolicitudService',
    'SeguimientoService',
    'BuzonNotificacionesService',
    'EntrevistaAlertasService',
    'RecordatorioAlertasService',
    'PreparacionAlertasService',
    'SimulacroAlertasService',
    'AlertasEntrevistaService',
]
