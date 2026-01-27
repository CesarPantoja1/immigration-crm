"""
Excepciones de Dominio para Simulación.
"""


class SimulacionError(Exception):
    """Excepción base para errores de simulación."""
    pass


class LimiteSimulacrosAlcanzadoError(SimulacionError):
    """Se ha alcanzado el límite de simulacros con asesor."""
    
    def __init__(self, limite: int = 2):
        self.limite = limite
        super().__init__(f"Error: Límite de {limite} simulacros alcanzado")


class SimulacroFueraDeFechaError(SimulacionError):
    """El simulacro está fuera de la fecha permitida."""
    
    def __init__(self, mensaje: str = "Error: La simulación debe ser antes de la cita real"):
        super().__init__(mensaje)


class SimulacroNoEncontradoError(SimulacionError):
    """No se encontró el simulacro."""
    
    def __init__(self, simulacro_id: str):
        self.simulacro_id = simulacro_id
        super().__init__(f"Simulacro con ID {simulacro_id} no encontrado")


class SesionPracticaNoActivaError(SimulacionError):
    """La sesión de práctica no está activa."""
    
    def __init__(self):
        super().__init__("La sesión de práctica no está activa")


class CuestionarioNoDisponibleError(SimulacionError):
    """No hay cuestionario disponible para el tipo de visado."""
    
    def __init__(self, tipo_visado: str):
        self.tipo_visado = tipo_visado
        super().__init__(f"No hay cuestionario disponible para visado tipo: {tipo_visado}")


class TranscripcionInvalidaError(SimulacionError):
    """La transcripción es inválida o vacía."""
    
    def __init__(self):
        super().__init__("La transcripción no puede estar vacía")


class EstadoSimulacroInvalidoError(SimulacionError):
    """El estado del simulacro no permite la operación."""
    
    def __init__(self, estado_actual: str, operacion: str):
        self.estado_actual = estado_actual
        self.operacion = operacion
        super().__init__(
            f"No se puede realizar '{operacion}' cuando el simulacro está en estado '{estado_actual}'"
        )
