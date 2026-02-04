"""
Business Logic para Simulación de Entrevistas.
Espeja la arquitectura de apps/preparacion/ para testing BDD.
"""
from .constants import (
    TipoVisado,
    ModalidadSimulacro,
    EstadoSimulacro,
    NivelDificultad,
    BANCO_PREGUNTAS,
)

from .entities import (
    HorarioSimulacro,
    Pregunta,
    RespuestaMigrante,
    ResultadoPractica,
    Transcripcion,
    FeedbackAsesor,
    PreguntaIncorrecta,
)

from .services import (
    SesionPracticaIndividual,
    SimulacroConAsesor,
    GestorSimulacros,
)

__all__ = [
    # Constants
    'TipoVisado',
    'ModalidadSimulacro',
    'EstadoSimulacro',
    'NivelDificultad',
    'BANCO_PREGUNTAS',
    # Entities
    'HorarioSimulacro',
    'Pregunta',
    'RespuestaMigrante',
    'ResultadoPractica',
    'Transcripcion',
    'FeedbackAsesor',
    'PreguntaIncorrecta',
    # Services
    'SesionPracticaIndividual',
    'SimulacroConAsesor',
    'GestorSimulacros',
]
