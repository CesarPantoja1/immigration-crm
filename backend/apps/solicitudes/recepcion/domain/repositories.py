"""
Interfaces de Repositorios para Recepción de Solicitudes.
Definen contratos que la infraestructura debe implementar.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import SolicitudVisa, Documento, Migrante
from .value_objects import TipoVisa, ChecklistDocumentos


class ISolicitudRepository(ABC):
    """Interfaz para el repositorio de solicitudes."""
    
    @abstractmethod
    def guardar(self, solicitud: SolicitudVisa) -> SolicitudVisa:
        """Guarda una solicitud."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, id_solicitud: str) -> Optional[SolicitudVisa]:
        """Obtiene una solicitud por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_migrante(self, id_migrante: str) -> List[SolicitudVisa]:
        """Obtiene las solicitudes de un migrante."""
        pass
    
    @abstractmethod
    def obtener_por_estado(self, estado: str) -> List[SolicitudVisa]:
        """Obtiene solicitudes por estado."""
        pass
    
    @abstractmethod
    def actualizar(self, solicitud: SolicitudVisa) -> SolicitudVisa:
        """Actualiza una solicitud existente."""
        pass
    
    @abstractmethod
    def eliminar(self, id_solicitud: str) -> bool:
        """Elimina una solicitud."""
        pass


class IDocumentoRepository(ABC):
    """Interfaz para el repositorio de documentos."""
    
    @abstractmethod
    def guardar(self, documento: Documento, id_solicitud: str) -> Documento:
        """Guarda un documento asociado a una solicitud."""
        pass
    
    @abstractmethod
    def obtener_por_solicitud(self, id_solicitud: str) -> List[Documento]:
        """Obtiene los documentos de una solicitud."""
        pass
    
    @abstractmethod
    def actualizar(self, documento: Documento) -> Documento:
        """Actualiza un documento existente."""
        pass


class IMigranteRepository(ABC):
    """Interfaz para el repositorio de migrantes."""
    
    @abstractmethod
    def obtener_por_id(self, id_migrante: str) -> Optional[Migrante]:
        """Obtiene un migrante por su ID."""
        pass
    
    @abstractmethod
    def guardar(self, migrante: Migrante) -> Migrante:
        """Guarda un migrante."""
        pass


class IChecklistRepository(ABC):
    """Interfaz para el repositorio de checklists."""
    
    @abstractmethod
    def obtener_por_tipo_visa(self, tipo_visa: TipoVisa) -> Optional[ChecklistDocumentos]:
        """Obtiene el checklist para un tipo de visa."""
        pass
    
    @abstractmethod
    def guardar(self, checklist: ChecklistDocumentos) -> ChecklistDocumentos:
        """Guarda un checklist."""
        pass
