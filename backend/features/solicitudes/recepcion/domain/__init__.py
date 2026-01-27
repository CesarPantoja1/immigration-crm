"""
Capa de Dominio para Recepción de Solicitudes.
Contiene la lógica de negocio pura, independiente de frameworks.
"""
from .value_objects import (
    TipoVisa,
    TipoEmbajada,
    EstadoSolicitud,
    EstadoDocumento,
    EstadoEnvio,
    TipoNotificacion,
    ChecklistDocumentos,
    ResultadoRevision,
    DatosPersonales
)

from .entities import (
    Documento,
    SolicitudVisa,
    Migrante,
    Asesor,
    AgenciaMigracion
)

from .repositories import (
    ISolicitudRepository,
    IDocumentoRepository,
    IMigranteRepository,
    IChecklistRepository
)

from .services import (
    ValidacionDocumentoService,
    RevisionSolicitudService,
    EnvioEmbajadaService,
    NotificacionService,
    VencimientoDocumentoService,
    ProgresoSolicitudService
)

from .exceptions import (
    DomainException,
    SolicitudException,
    SolicitudNoEncontradaException,
    SolicitudYaExisteException,
    SolicitudEstadoInvalidoException,
    DocumentoException,
    DocumentoNoEncontradoException,
    DocumentoInvalidoException,
    DocumentoNoRecargableException,
    MotivoRechazoInvalidoException,
    ChecklistException,
    ChecklistNoEncontradoException,
    DocumentosFaltantesException,
    EnvioException,
    EnvioNoPermitidoException,
    SolicitudYaEnviadaException,
    MigranteException,
    MigranteNoEncontradoException,
    AccesoDenegadoException
)

__all__ = [
    # Value Objects
    'TipoVisa',
    'TipoEmbajada',
    'EstadoSolicitud',
    'EstadoDocumento',
    'EstadoEnvio',
    'TipoNotificacion',
    'ChecklistDocumentos',
    'ResultadoRevision',
    'DatosPersonales',
    
    # Entities
    'Documento',
    'SolicitudVisa',
    'Migrante',
    'Asesor',
    'AgenciaMigracion',
    
    # Repositories
    'ISolicitudRepository',
    'IDocumentoRepository',
    'IMigranteRepository',
    'IChecklistRepository',
    
    # Services
    'ValidacionDocumentoService',
    'RevisionSolicitudService',
    'EnvioEmbajadaService',
    'NotificacionService',
    'VencimientoDocumentoService',
    'ProgresoSolicitudService',
    
    # Exceptions
    'DomainException',
    'SolicitudException',
    'SolicitudNoEncontradaException',
    'SolicitudYaExisteException',
    'SolicitudEstadoInvalidoException',
    'DocumentoException',
    'DocumentoNoEncontradoException',
    'DocumentoInvalidoException',
    'DocumentoNoRecargableException',
    'MotivoRechazoInvalidoException',
    'ChecklistException',
    'ChecklistNoEncontradoException',
    'DocumentosFaltantesException',
    'EnvioException',
    'EnvioNoPermitidoException',
    'SolicitudYaEnviadaException',
    'MigranteException',
    'MigranteNoEncontradoException',
    'AccesoDenegadoException',
]
