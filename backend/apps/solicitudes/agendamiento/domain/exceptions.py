"""
Excepciones del dominio de Agendamiento.
"""


class AgendamientoException(Exception):
    """Excepción base para el módulo de agendamiento."""
    pass


class EntrevistaNoEncontradaException(AgendamientoException):
    """La entrevista no existe."""
    
    def __init__(self, entrevista_id: str):
        self.entrevista_id = entrevista_id
        super().__init__(f"Entrevista con ID {entrevista_id} no encontrada")


class EntrevistaYaAgendadaException(AgendamientoException):
    """Ya existe una entrevista agendada para esta solicitud."""
    
    def __init__(self, solicitud_id: str):
        self.solicitud_id = solicitud_id
        super().__init__(f"Ya existe una entrevista activa para la solicitud {solicitud_id}")


class ReprogramacionNoPermitidaException(AgendamientoException):
    """No se permite reprogramar la entrevista."""
    
    def __init__(self, mensaje: str = "Ha alcanzado el límite máximo de reprogramaciones"):
        super().__init__(mensaje)


class CancelacionNoPermitidaException(AgendamientoException):
    """No se permite cancelar la entrevista."""
    
    def __init__(self, horas_minimas: int):
        self.horas_minimas = horas_minimas
        super().__init__(
            f"No es posible cancelar la entrevista. "
            f"Se requieren al menos {horas_minimas} horas de anticipación"
        )


class OpcionNoDisponibleException(AgendamientoException):
    """La opción de horario seleccionada no está disponible."""
    
    def __init__(self, opcion_id: str):
        self.opcion_id = opcion_id
        super().__init__(f"La opción de horario {opcion_id} no está disponible")


class SolicitudNoAprobadaException(AgendamientoException):
    """La solicitud no está aprobada para agendar entrevista."""
    
    def __init__(self, solicitud_id: str):
        self.solicitud_id = solicitud_id
        super().__init__(f"La solicitud {solicitud_id} no está aprobada para agendar entrevista")


class EntrevistaNoConfirmableException(AgendamientoException):
    """La entrevista no puede ser confirmada."""
    
    def __init__(self, estado_actual: str):
        self.estado_actual = estado_actual
        super().__init__(f"No se puede confirmar la entrevista en estado {estado_actual}")


class FechaInvalidaException(AgendamientoException):
    """La fecha seleccionada no es válida."""
    
    def __init__(self, mensaje: str = "La fecha seleccionada no es válida"):
        super().__init__(mensaje)
