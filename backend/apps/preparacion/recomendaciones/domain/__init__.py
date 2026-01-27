"""
Capa de Dominio para Generación de Recomendaciones.
"""

from .value_objects import (
    NivelIndicador,
    NivelPreparacion,
    NivelImpacto,
    CategoriaRecomendacion,
    TipoPregunta,
    EstadoSimulacro,
    FormatoDocumento,
    IndicadorDesempeno,
    PuntoMejora,
    Fortaleza,
    RecomendacionAccionable,
    PreguntaSimulacro,
    MetadatosDocumento,
    AccionSugerida,
    calcular_nivel_preparacion,
    SECCIONES_DOCUMENTO,
    NIVEL_A_PUNTOS,
)

from .entities import (
    TranscripcionSimulacro,
    AnalisisIA,
    DocumentoRecomendaciones,
    SimulacroParaRecomendaciones,
)

from .services import (
    AnalisisIAService,
    GeneracionDocumentoService,
    NivelPreparacionService,
    TrazabilidadService,
    ClasificacionImpactoService,
    ConsultaDocumentoService,
)

from .repositories import (
    ISimulacroRecomendacionRepository,
    IDocumentoRecomendacionesRepository,
    IAnalisisIARepository,
    ITranscripcionRepository,
)

from .exceptions import (
    RecomendacionError,
    SimulacroNoEncontradoError,
    TranscripcionNoDisponibleError,
    AnalisisNoCompletadoError,
    DocumentoNoGeneradoError,
    DocumentoNoPublicadoError,
    FormatoNoSoportadoError,
    TrazabilidadIncompletaError,
)

__all__ = [
    # Value Objects
    'NivelIndicador',
    'NivelPreparacion',
    'NivelImpacto',
    'CategoriaRecomendacion',
    'TipoPregunta',
    'EstadoSimulacro',
    'FormatoDocumento',
    'IndicadorDesempeno',
    'PuntoMejora',
    'Fortaleza',
    'RecomendacionAccionable',
    'PreguntaSimulacro',
    'MetadatosDocumento',
    'AccionSugerida',
    'calcular_nivel_preparacion',
    'SECCIONES_DOCUMENTO',
    'NIVEL_A_PUNTOS',
    
    # Entities
    'TranscripcionSimulacro',
    'AnalisisIA',
    'DocumentoRecomendaciones',
    'SimulacroParaRecomendaciones',
    
    # Services
    'AnalisisIAService',
    'GeneracionDocumentoService',
    'NivelPreparacionService',
    'TrazabilidadService',
    'ClasificacionImpactoService',
    'ConsultaDocumentoService',
    
    # Repositories
    'ISimulacroRecomendacionRepository',
    'IDocumentoRecomendacionesRepository',
    'IAnalisisIARepository',
    'ITranscripcionRepository',
    
    # Exceptions
    'RecomendacionError',
    'SimulacroNoEncontradoError',
    'TranscripcionNoDisponibleError',
    'AnalisisNoCompletadoError',
    'DocumentoNoGeneradoError',
    'DocumentoNoPublicadoError',
    'FormatoNoSoportadoError',
    'TrazabilidadIncompletaError',
]
