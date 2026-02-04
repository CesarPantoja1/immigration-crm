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
)

from .services import (
    NotificacionService,
    SolicitudService,
    SeguimientoService,
    BuzonNotificacionesService,
)

__all__ = [
    # Constantes
    'ESTADOS_SOLICITUD',
    'TIPOS_VISA',
    'EMBAJADAS',
    'ESTADOS_DOCUMENTO',
    'TIPOS_NOTIFICACION',
    # Entidades
    'UsuarioEntity',
    'DocumentoEntity',
    'SolicitudEntity',
    'NotificacionEntity',
    'crear_usuario',
    'crear_solicitud',
    'crear_documento',
    'crear_notificacion',
    'reset_id_counters',
    # Servicios
    'NotificacionService',
    'SolicitudService',
    'SeguimientoService',
    'BuzonNotificacionesService',
]
