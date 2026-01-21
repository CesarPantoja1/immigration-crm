"""
Event Bus usando Django Signals.
Este módulo centraliza los eventos del dominio que se propagan entre apps.
"""
from django.dispatch import Signal

# Eventos de Solicitudes
solicitud_creada = Signal()
solicitud_aprobada = Signal()
solicitud_rechazada = Signal()

# Eventos de Entrevistas
entrevista_agendada = Signal()
entrevista_reprogramada = Signal()
entrevista_cancelada = Signal()
entrevista_completada = Signal()

# Eventos de Simulación
simulacro_iniciado = Signal()
simulacro_completado = Signal()

# Eventos de Recomendaciones
recomendaciones_generadas = Signal()

# Eventos de Notificaciones
notificacion_enviada = Signal()
notificacion_fallida = Signal()
