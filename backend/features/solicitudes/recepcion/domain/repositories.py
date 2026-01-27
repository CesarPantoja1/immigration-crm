"""
Interfaces de Repositorios para Recepción de Solicitudes.
Define los contratos (puertos) que deben implementar los adaptadores.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import SolicitudVisa, Documento, Migrante


class ISolicitudRepository(ABC):
    """Interfaz del repositorio de solicitudes de visa."""
    
    @abstractmethod
    def save(self, solicitud: SolicitudVisa) -> SolicitudVisa:
        """Guarda o actualiza una solicitud."""
        pass
    
    @abstractmethod
    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudVisa]:
        """Encuentra una solicitud por su ID."""
        pass
    
    @abstractmethod
    def find_by_migrante(self, migrante_id: str) -> List[SolicitudVisa]:
        """Encuentra todas las solicitudes de un migrante."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[SolicitudVisa]:
        """Retorna todas las solicitudes."""
        pass
    
    @abstractmethod
    def find_by_estado(self, estado: str) -> List[SolicitudVisa]:
        """Encuentra solicitudes por estado."""
        pass
    
    @abstractmethod
    def delete(self, solicitud_id: str) -> bool:
        """Elimina una solicitud."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Cuenta el total de solicitudes."""
        pass


class IDocumentoRepository(ABC):
    """Interfaz del repositorio de documentos."""
    
    @abstractmethod
    def save(self, documento: Documento, solicitud_id: str) -> Documento:
        """Guarda o actualiza un documento."""
        pass
    
    @abstractmethod
    def find_by_id(self, documento_id: str) -> Optional[Documento]:
        """Encuentra un documento por su ID."""
        pass
    
    @abstractmethod
    def find_by_solicitud(self, solicitud_id: str) -> List[Documento]:
        """Encuentra todos los documentos de una solicitud."""
        pass
    
    @abstractmethod
    def find_by_estado(self, estado: str) -> List[Documento]:
        """Encuentra documentos por estado."""
        pass
    
    @abstractmethod
    def delete(self, documento_id: str) -> bool:
        """Elimina un documento."""
        pass


class IMigranteRepository(ABC):
    """Interfaz del repositorio de migrantes."""
    
    @abstractmethod
    def save(self, migrante: Migrante) -> Migrante:
        """Guarda o actualiza un migrante."""
        pass
    
    @abstractmethod
    def find_by_id(self, migrante_id: str) -> Optional[Migrante]:
        """Encuentra un migrante por su ID."""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Migrante]:
        """Encuentra un migrante por su email."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Migrante]:
        """Retorna todos los migrantes."""
        pass
    
    @abstractmethod
    def delete(self, migrante_id: str) -> bool:
        """Elimina un migrante."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Cuenta el total de migrantes."""
        pass


class IChecklistRepository(ABC):
    """Interfaz del repositorio de checklists."""
    
    @abstractmethod
    def find_by_tipo_visa(self, tipo_visa: str) -> Optional[List[str]]:
        """Encuentra el checklist de documentos por tipo de visa."""
        pass
    
    @abstractmethod
    def save(self, tipo_visa: str, documentos: List[str]) -> None:
        """Guarda un checklist de documentos."""
        pass
