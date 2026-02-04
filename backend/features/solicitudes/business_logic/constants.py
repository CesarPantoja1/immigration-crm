# -*- coding: utf-8 -*-
"""Constantes del dominio para testing BDD de Agendamiento de Entrevistas."""

ESTADOS_ENTREVISTA = [
    'pendiente',
    'agendada',
    'confirmada',
    'reprogramada',
    'cancelada',
    'completada',
]

ESTADOS_ENTREVISTA_LEGIBLES = {
    'Pendiente': 'pendiente',
    'Programada': 'agendada',
    'Agendada': 'agendada',
    'Confirmada': 'confirmada',
    'Reprogramada': 'reprogramada',
    'Cancelada': 'cancelada',
    'Completada': 'completada',
}

MODOS_ASIGNACION = ['automatico', 'manual']

MOTIVOS_CANCELACION = [
    'solicitud_migrante',
    'emergencia',
    'reprogramacion_embajada',
]

MOTIVOS_CANCELACION_LEGIBLES = {
    'Solicitud del migrante': 'solicitud_migrante',
    'Emergencia': 'emergencia',
    'Reprogramación de embajada': 'reprogramacion_embajada',
}

REGLAS_EMBAJADA_DEFAULT = {
    'USA': {'max_reprogramaciones': 2, 'horas_minimas_cancelacion': 48},
    'CANADA': {'max_reprogramaciones': 2, 'horas_minimas_cancelacion': 72},
    'ESPAÑA': {'max_reprogramaciones': 3, 'horas_minimas_cancelacion': 24},
    'España': {'max_reprogramaciones': 3, 'horas_minimas_cancelacion': 48},
    'Canadá': {'max_reprogramaciones': 2, 'horas_minimas_cancelacion': 72},
}

REGLA_EMBAJADA_DEFAULT = {'max_reprogramaciones': 2, 'horas_minimas_cancelacion': 48}

MENSAJES = {
    'agendamiento_exitoso': 'Entrevista agendada para el {fecha_legible} a las {hora}',
    'reprogramacion_exitosa': 'Entrevista reprogramada exitosamente',
    'reprogramacion_ultima': 'Esta es su última reprogramación disponible',
    'reprogramacion_permitida': 'Esta es su última reprogramación permitida',
    'reprogramacion_rechazada': 'Error: ha alcanzado el límite máximo de reprogramaciones permitidas',
    'reprogramacion_no_permitida': 'No es posible reprogramar. Límite alcanzado ({max} reprogramaciones)',
    'cancelacion_exitosa': 'Cancelación confirmada exitosamente',
    'cancelacion_rechazada': 'Error: no es posible cancelar la entrevista debido a que no se cumple el tiempo mínimo de anticipación',
    'cancelacion_no_permitida': 'No es posible cancelar. Mínimo {horas}h de anticipación requeridas',
    'modificacion_rechazada': 'No es posible modificar directamente. Use el proceso de reprogramación',
}
