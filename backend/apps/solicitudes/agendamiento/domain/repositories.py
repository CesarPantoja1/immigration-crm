"""
Interfaces de Repositorio para Agendamiento.
Define los contratos que deben implementar los adaptadores de infraestructura.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from .entities import Entrevista, RespuestaEmbajada, GestorEntrevistas


class IEntrevistaRepository(ABC):
    """Repositorio de Entrevistas."""
    
    @abstractmethod
    def guardar(self, entrevista: Entrevista) -> Entrevista:
        """Guarda o actualiza una entrevista."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, entrevista_id: str) -> Optional[Entrevista]:
        """Obtiene una entrevista por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_solicitud(self, solicitud_id: str) -> Optional[Entrevista]:
        """Obtiene la entrevista activa de una solicitud."""
        pass
    
    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> Optional[Entrevista]:
        """Obtiene una entrevista por su código."""
        pass
    
    @abstractmethod
    def listar_por_migrante(self, migrante_id: str) -> List[Entrevista]:
        """Lista todas las entrevistas de un migrante."""
        pass
    
    @abstractmethod
    def listar_por_embajada(self, embajada: str) -> List[Entrevista]:
        """Lista todas las entrevistas de una embajada."""
        pass
    
    @abstractmethod
    def listar_por_fecha(self, fecha: date) -> List[Entrevista]:
        """Lista todas las entrevistas de una fecha."""
        pass
    
    @abstractmethod
    def listar_pendientes(self) -> List[Entrevista]:
        """Lista entrevistas pendientes de asignación."""
        pass
    
    @abstractmethod
    def listar_proximas(self, dias: int = 7) -> List[Entrevista]:
        """Lista entrevistas en los próximos X días."""
        pass
    
    @abstractmethod
    def eliminar(self, entrevista_id: str) -> bool:
        """Elimina una entrevista."""
        pass


class IRespuestaEmbajadaRepository(ABC):
    """Repositorio de Respuestas de Embajada."""
    
    @abstractmethod
    def guardar(self, respuesta: RespuestaEmbajada) -> RespuestaEmbajada:
        """Guarda una respuesta de embajada."""
        pass
    
    @abstractmethod
    def obtener_por_solicitud(self, solicitud_id: str) -> List[RespuestaEmbajada]:
        """Obtiene todas las respuestas para una solicitud."""
        pass
    
    @abstractmethod
    def obtener_ultima_respuesta(self, solicitud_id: str) -> Optional[RespuestaEmbajada]:
        """Obtiene la última respuesta de una solicitud."""
        pass


class IGestorEntrevistasRepository(ABC):
    """Repositorio para el agregado GestorEntrevistas."""
    
    @abstractmethod
    def guardar(self, gestor: GestorEntrevistas) -> GestorEntrevistas:
        """Guarda el gestor de entrevistas."""
        pass
    
    @abstractmethod
    def obtener_por_solicitud(self, solicitud_id: str) -> Optional[GestorEntrevistas]:
        """Obtiene el gestor de entrevistas de una solicitud."""
        pass
    
    @abstractmethod
    def crear(self, solicitud_id: str, embajada: str) -> GestorEntrevistas:
        """Crea un nuevo gestor de entrevistas."""
        pass
