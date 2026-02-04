# -*- coding: utf-8 -*-
"""
Constantes del dominio para testing BDD.
Alineadas con los valores reales de apps/solicitudes/models.py y apps/notificaciones/models.py

IMPORTANTE: Estos valores deben mantenerse sincronizados con el código de producción.
"""

# ESTADOS DE SOLICITUD

ESTADOS_SOLICITUD = [
    'borrador',
    'pendiente',
    'en_revision',
    'aprobada',
    'rechazada',
    'enviada_embajada',
    'esperando_decision_embajada',
    'aprobada_embajada',
    'rechazada_embajada',
    'entrevista_agendada',
    'completada',
]

# TIPOS DE VISA

TIPOS_VISA = ['vivienda', 'trabajo', 'estudio']

# EMBAJADAS

EMBAJADAS = ['usa', 'brasil', 'canada', 'espana']


# ESTADOS DE DOCUMENTO

ESTADOS_DOCUMENTO = ['pendiente', 'aprobado', 'rechazado']

# TIPOS DE NOTIFICACIÓN

TIPOS_NOTIFICACION = [
    'solicitud_creada', 'solicitud_asignada', 'solicitud_aprobada',
    'solicitud_rechazada', 'solicitud_enviada', 'solicitud_en_revision',
    'contrato_generado', 'contrato_pendiente', 'contrato_firmado', 'contrato_aprobado',
    'documento_subido', 'documento_aprobado', 'documento_rechazado',
    'entrevista_agendada', 'entrevista_reprogramada', 'entrevista_cancelada',
    'recordatorio_entrevista', 'preparacion_recomendada', 'simulacro_propuesto',
    'simulacro_confirmado', 'simulacion_completada', 'recomendaciones_listas',
    'general', 'mensaje',
]

# ============================================================
# CONSTANTES PARA ALERTAS DE ENTREVISTA (BDD)
# ============================================================

# ESTADOS DE ENTREVISTA
ESTADOS_ENTREVISTA = ['programada', 'reprogramada', 'cancelada', 'completada']

# ESTADOS DE SIMULACRO
ESTADOS_SIMULACRO = ['pendiente', 'propuesto', 'confirmado', 'en_progreso', 'completado']

# ESTADOS DE RECOMENDACIONES
ESTADOS_RECOMENDACIONES = ['borrador', 'publicado']

# VENTANAS DE RECORDATORIO (en horas)
VENTANAS_RECORDATORIO = {
    '24h': 24,
    '2h': 2,
}

# VENTANAS DE PREPARACIÓN (en días)
VENTANAS_PREPARACION = {
    '7d': 7,
}

# Mapeo de tipos de alerta a nombres legibles (para feature de Alertas)
TIPOS_ALERTA_ENTREVISTA = {
    'entrevista_agendada': 'Entrevista agendada',
    'entrevista_reprogramada': 'Entrevista reprogramada',
    'entrevista_cancelada': 'Entrevista cancelada',
    'recordatorio_entrevista': 'Recordatorio entrevista',
    'preparacion_recomendada': 'Preparación recomendada',
    'simulacion_completada': 'Simulación completada',
    'recomendaciones_listas': 'Recomendaciones listas',
}

