# -*- coding: utf-8 -*-
"""
Constantes del dominio para testing BDD de Agendamiento de Entrevistas.

RESPONSABILIDAD:
- Definir valores válidos para estados, tipos y configuraciones
- Servir como fuente de verdad para validaciones en testing
- Alineadas con apps/solicitudes/models.py (pero sin depender de Django)

LÓGICA EXTRAÍDA DE:
- EstadoEntrevista (Enum) → ESTADOS_ENTREVISTA
- ModoAsignacion (Enum) → MODOS_ASIGNACION
- MotivoCancelacion (Enum) → MOTIVOS_CANCELACION
- REGLAS_EMBAJADA (dict) → REGLAS_EMBAJADA_DEFAULT

IMPORTANTE: Estos valores deben mantenerse sincronizados con el código de producción.
"""

# ============================================================
# ESTADOS DE ENTREVISTA
# ============================================================

ESTADOS_ENTREVISTA = [
    'pendiente',
    'agendada',
    'confirmada',
    'reprogramada',
    'cancelada',
    'completada',
]

# Mapeo de nombres legibles a estados internos
ESTADOS_ENTREVISTA_LEGIBLES = {
    'Pendiente': 'pendiente',
    'Programada': 'agendada',  # "Programada" en feature = "agendada" internamente
    'Agendada': 'agendada',
    'Confirmada': 'confirmada',
    'Reprogramada': 'reprogramada',
    'Cancelada': 'cancelada',
    'Completada': 'completada',
}

# ============================================================
# MODOS DE ASIGNACIÓN
# ============================================================

MODOS_ASIGNACION = [
    'automatico',
    'manual',
]

# ============================================================
# MOTIVOS DE CANCELACIÓN
# ============================================================

MOTIVOS_CANCELACION = [
    'solicitud_migrante',
    'emergencia',
    'reprogramacion_embajada',
]

# Mapeo de motivos legibles
MOTIVOS_CANCELACION_LEGIBLES = {
    'Solicitud del migrante': 'solicitud_migrante',
    'Emergencia': 'emergencia',
    'Reprogramación de embajada': 'reprogramacion_embajada',
}

# ============================================================
# REGLAS POR EMBAJADA
# ============================================================

# Configuración por defecto de reglas de cada embajada
REGLAS_EMBAJADA_DEFAULT = {
    'USA': {
        'max_reprogramaciones': 2,
        'horas_minimas_cancelacion': 48,
    },
    'CANADA': {
        'max_reprogramaciones': 2,
        'horas_minimas_cancelacion': 72,
    },
    'ESPAÑA': {
        'max_reprogramaciones': 3,
        'horas_minimas_cancelacion': 24,
    },
    'España': {  # Variante con acento minúscula
        'max_reprogramaciones': 3,
        'horas_minimas_cancelacion': 48,
    },
    'Canadá': {  # Variante con acento
        'max_reprogramaciones': 2,
        'horas_minimas_cancelacion': 72,
    },
}

# Valores por defecto para embajadas no configuradas
REGLA_EMBAJADA_DEFAULT = {
    'max_reprogramaciones': 2,
    'horas_minimas_cancelacion': 48,
}

# ============================================================
# MENSAJES DEL SISTEMA
# ============================================================

MENSAJES = {
    # Agendamiento
    'agendamiento_exitoso': 'Entrevista agendada para el {fecha_legible} a las {hora}',

    # Reprogramación
    'reprogramacion_exitosa': 'Entrevista reprogramada exitosamente',
    'reprogramacion_ultima': 'Esta es su última reprogramación disponible',
    'reprogramacion_permitida': 'Esta es su última reprogramación permitida',
    'reprogramacion_rechazada': 'Error: ha alcanzado el límite máximo de reprogramaciones permitidas',
    'reprogramacion_no_permitida': 'No es posible reprogramar. Límite alcanzado ({max} reprogramaciones)',

    # Cancelación
    'cancelacion_exitosa': 'Cancelación confirmada exitosamente',
    'cancelacion_rechazada': 'Error: no es posible cancelar la entrevista debido a que no se cumple el tiempo mínimo de anticipación',
    'cancelacion_no_permitida': 'No es posible cancelar. Mínimo {horas}h de anticipación requeridas',

    # Modificación
    'modificacion_rechazada': 'No es posible modificar directamente. Use el proceso de reprogramación',
}
