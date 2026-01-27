"""
Interfaces de Repositorios para Recomendaciones.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import (
    SimulacroParaRecomendaciones,
    DocumentoRecomendaciones,
    AnalisisIA,
    TranscripcionSimulacro,
)
from .value_objects import EstadoSimulacro


class ISimulacroRecomendacionRepository(ABC):
    """Interfaz del repositorio de simulacros para recomendaciones."""
    
    @abstractmethod
    def guardar(self, simulacro: SimulacroParaRecomendaciones) -> SimulacroParaRecomendaciones:
        """Guarda un simulacro."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, simulacro_id: str) -> Optional[SimulacroParaRecomendaciones]:
        """Obtiene un simulacro por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_migrante(self, migrante_id: str) -> List[SimulacroParaRecomendaciones]:
        """Obtiene todos los simulacros de un migrante."""
        pass
    
    @abstractmethod
    def obtener_pendientes_analisis(self) -> List[SimulacroParaRecomendaciones]:
        """Obtiene simulacros pendientes de análisis."""
        pass


class IDocumentoRecomendacionesRepository(ABC):
    """Interfaz del repositorio de documentos de recomendaciones."""
    
    @abstractmethod
    def guardar(self, documento: DocumentoRecomendaciones) -> DocumentoRecomendaciones:
        """Guarda un documento de recomendaciones."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, documento_id: str) -> Optional[DocumentoRecomendaciones]:
        """Obtiene un documento por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_simulacro(self, simulacro_id: str) -> Optional[DocumentoRecomendaciones]:
        """Obtiene el documento asociado a un simulacro."""
        pass
    
    @abstractmethod
    def obtener_publicados_por_migrante(self, migrante_id: str) -> List[DocumentoRecomendaciones]:
        """Obtiene documentos publicados de un migrante."""
        pass


class IAnalisisIARepository(ABC):
    """Interfaz del repositorio de análisis de IA."""
    
    @abstractmethod
    def guardar(self, analisis: AnalisisIA) -> AnalisisIA:
        """Guarda un análisis de IA."""
        pass
    
    @abstractmethod
    def obtener_por_simulacro(self, simulacro_id: str) -> Optional[AnalisisIA]:
        """Obtiene el análisis de un simulacro."""
        pass


class ITranscripcionRepository(ABC):
    """Interfaz del repositorio de transcripciones."""
    
    @abstractmethod
    def guardar(self, transcripcion: TranscripcionSimulacro) -> TranscripcionSimulacro:
        """Guarda una transcripción."""
        pass
    
    @abstractmethod
    def obtener_por_simulacro(self, simulacro_id: str) -> Optional[TranscripcionSimulacro]:
        """Obtiene la transcripción de un simulacro."""
        pass
