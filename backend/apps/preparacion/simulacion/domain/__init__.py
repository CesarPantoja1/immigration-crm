"""
Capa de Dominio para Simulación de Entrevistas.
"""

from .value_objects import (
    TipoVisado,
    ModalidadSimulacro,
    EstadoSimulacro,
    NivelDificultad,
    Pregunta,
    RespuestaMigrante,
    HorarioSimulacro,
    ResultadoPractica,
    Transcripcion,
    FeedbackAsesor,
    MAX_SIMULACROS_CON_ASESOR,
    TIPOS_VISADO_DISPONIBLES,
    BANCO_PREGUNTAS,
    obtener_preguntas_por_visado,
)

from .entities import (
    SimulacroConAsesor,
    SesionPracticaIndividual,
    GestorSimulacros,
)

from .services import (
    AgendamientoSimulacroService,
    EjecucionSimulacroService,
    PracticaIndividualService,
    ConsultaSimulacroService,
)

from .repositories import (
    ISimulacroRepository,
    ISesionPracticaRepository,
    IGestorSimulacrosRepository,
    IPreguntaRepository,
)

from .exceptions import (
    SimulacionError,
    LimiteSimulacrosAlcanzadoError,
    SimulacroFueraDeFechaError,
    SimulacroNoEncontradoError,
    SesionPracticaNoActivaError,
    CuestionarioNoDisponibleError,
    TranscripcionInvalidaError,
    EstadoSimulacroInvalidoError,
)

__all__ = [
    # Value Objects
    'TipoVisado',
    'ModalidadSimulacro',
    'EstadoSimulacro',
    'NivelDificultad',
    'Pregunta',
    'RespuestaMigrante',
    'HorarioSimulacro',
    'ResultadoPractica',
    'Transcripcion',
    'FeedbackAsesor',
    'MAX_SIMULACROS_CON_ASESOR',
    'TIPOS_VISADO_DISPONIBLES',
    'BANCO_PREGUNTAS',
    'obtener_preguntas_por_visado',
    
    # Entities
    'SimulacroConAsesor',
    'SesionPracticaIndividual',
    'GestorSimulacros',
    
    # Services
    'AgendamientoSimulacroService',
    'EjecucionSimulacroService',
    'PracticaIndividualService',
    'ConsultaSimulacroService',
    
    # Repositories
    'ISimulacroRepository',
    'ISesionPracticaRepository',
    'IGestorSimulacrosRepository',
    'IPreguntaRepository',
    
    # Exceptions
    'SimulacionError',
    'LimiteSimulacrosAlcanzadoError',
    'SimulacroFueraDeFechaError',
    'SimulacroNoEncontradoError',
    'SesionPracticaNoActivaError',
    'CuestionarioNoDisponibleError',
    'TranscripcionInvalidaError',
    'EstadoSimulacroInvalidoError',
]
