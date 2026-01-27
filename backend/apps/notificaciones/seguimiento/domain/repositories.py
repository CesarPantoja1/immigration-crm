"""
Interfaces de Repositorio para Seguimiento de Solicitudes.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import SeguimientoSolicitud, PortafolioMigrante, TimelineSolicitud
from .value_objects import EventoHistorial, Alerta


class ISeguimientoRepository(ABC):
    """Repositorio de Seguimiento de Solicitudes."""
    
    @abstractmethod
    def obtener_por_id(self, solicitud_id: str) -> Optional[SeguimientoSolicitud]:
        """Obtiene el seguimiento de una solicitud por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> Optional[SeguimientoSolicitud]:
        """Obtiene el seguimiento de una solicitud por su código."""
        pass
    
    @abstractmethod
    def listar_por_migrante(self, migrante_id: str) -> List[SeguimientoSolicitud]:
        """Lista todas las solicitudes de un migrante."""
        pass
    
    @abstractmethod
    def guardar(self, seguimiento: SeguimientoSolicitud) -> SeguimientoSolicitud:
        """Guarda o actualiza un seguimiento."""
        pass


class IPortafolioRepository(ABC):
    """Repositorio de Portafolio de Migrantes."""
    
    @abstractmethod
    def obtener_por_migrante(self, migrante_id: str) -> Optional[PortafolioMigrante]:
        """Obtiene el portafolio de un migrante."""
        pass
    
    @abstractmethod
    def crear(self, migrante_id: str, migrante_email: str) -> PortafolioMigrante:
        """Crea un nuevo portafolio."""
        pass


class ITimelineRepository(ABC):
    """Repositorio de Timeline de Eventos."""
    
    @abstractmethod
    def obtener_por_solicitud(self, solicitud_id: str) -> Optional[TimelineSolicitud]:
        """Obtiene el timeline de una solicitud."""
        pass
    
    @abstractmethod
    def agregar_evento(
        self,
        solicitud_id: str,
        evento: EventoHistorial
    ) -> EventoHistorial:
        """Agrega un evento al timeline."""
        pass
    
    @abstractmethod
    def listar_eventos(
        self,
        solicitud_id: str,
        cantidad: int = None
    ) -> List[EventoHistorial]:
        """Lista los eventos de una solicitud."""
        pass


class IAlertaRepository(ABC):
    """Repositorio de Alertas."""
    
    @abstractmethod
    def guardar(self, alerta: Alerta) -> Alerta:
        """Guarda una alerta."""
        pass
    
    @abstractmethod
    def listar_por_solicitud(self, solicitud_id: str) -> List[Alerta]:
        """Lista alertas de una solicitud."""
        pass
    
    @abstractmethod
    def listar_por_migrante(self, migrante_id: str) -> List[Alerta]:
        """Lista alertas de un migrante."""
        pass
    
    @abstractmethod
    def listar_urgentes(self, migrante_id: str) -> List[Alerta]:
        """Lista alertas urgentes de un migrante."""
        pass
