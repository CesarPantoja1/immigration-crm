"""
Excepciones de Dominio para Recomendaciones.
"""


class RecomendacionError(Exception):
    """Excepción base para errores de recomendaciones."""
    pass


class SimulacroNoEncontradoError(RecomendacionError):
    """No se encontró el simulacro."""
    
    def __init__(self, simulacro_id: str):
        self.simulacro_id = simulacro_id
        super().__init__(f"Simulacro con ID {simulacro_id} no encontrado")


class TranscripcionNoDisponibleError(RecomendacionError):
    """El simulacro no tiene transcripción disponible."""
    
    def __init__(self, simulacro_id: str):
        self.simulacro_id = simulacro_id
        super().__init__(f"El simulacro {simulacro_id} no tiene transcripción")


class AnalisisNoCompletadoError(RecomendacionError):
    """El análisis de IA no está completado."""
    
    def __init__(self, simulacro_id: str):
        self.simulacro_id = simulacro_id
        super().__init__(f"El análisis del simulacro {simulacro_id} no está completado")


class DocumentoNoGeneradoError(RecomendacionError):
    """El documento de recomendaciones no ha sido generado."""
    
    def __init__(self, simulacro_id: str):
        self.simulacro_id = simulacro_id
        super().__init__(f"No existe documento de recomendaciones para el simulacro {simulacro_id}")


class DocumentoNoPublicadoError(RecomendacionError):
    """El documento no está publicado."""
    
    def __init__(self, simulacro_id: str):
        self.simulacro_id = simulacro_id
        super().__init__(f"El documento del simulacro {simulacro_id} no está publicado")


class FormatoNoSoportadoError(RecomendacionError):
    """El formato de exportación no está soportado."""
    
    def __init__(self, formato: str):
        self.formato = formato
        super().__init__(f"Formato de exportación no soportado: {formato}")


class TrazabilidadIncompletaError(RecomendacionError):
    """Hay recomendaciones sin trazabilidad a preguntas."""
    
    def __init__(self, recomendaciones_sin_trazabilidad: list):
        self.recomendaciones = recomendaciones_sin_trazabilidad
        super().__init__(
            f"Las siguientes recomendaciones no tienen trazabilidad: {recomendaciones_sin_trazabilidad}"
        )
