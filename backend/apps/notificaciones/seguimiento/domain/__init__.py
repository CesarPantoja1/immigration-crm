"""
Dominio de Seguimiento de Solicitudes.

Este módulo proporciona funcionalidades para el seguimiento
del estado y progreso de las solicitudes migratorias.
"""
from .value_objects import (
    TipoEvento,
    EstadoSolicitudSeguimiento,
    NivelAlerta,
    TipoAlerta,
    EventoHistorial,
    ProgresoSolicitud,
    Alerta,
    PasoSiguiente,
    ResumenSolicitud,
    ValidacionDocumento,
)

from .entities import (
    TimelineSolicitud,
    SeguimientoSolicitud,
    PortafolioMigrante,
)

from .services import (
    ResultadoConsulta,
    ConsultaSolicitudService,
    PortafolioService,
    AlertaService,
    ProgresoService,
    PrivacidadService,
    ExpectativasService,
)

from .repositories import (
    ISeguimientoRepository,
    IPortafolioRepository,
    ITimelineRepository,
    IAlertaRepository,
)

__all__ = [
    # Value Objects
    'TipoEvento',
    'EstadoSolicitudSeguimiento',
    'NivelAlerta',
    'TipoAlerta',
    'EventoHistorial',
    'ProgresoSolicitud',
    'Alerta',
    'PasoSiguiente',
    'ResumenSolicitud',
    'ValidacionDocumento',
    
    # Entities
    'TimelineSolicitud',
    'SeguimientoSolicitud',
    'PortafolioMigrante',
    
    # Services
    'ResultadoConsulta',
    'ConsultaSolicitudService',
    'PortafolioService',
    'AlertaService',
    'ProgresoService',
    'PrivacidadService',
    'ExpectativasService',
    
    # Repositories
    'ISeguimientoRepository',
    'IPortafolioRepository',
    'ITimelineRepository',
    'IAlertaRepository',
]
