"""
Interfaces de Repositorios para Simulación.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from .entities import SimulacroConAsesor, SesionPracticaIndividual, GestorSimulacros
from .value_objects import TipoVisado


class ISimulacroRepository(ABC):
    """Interfaz del repositorio de simulacros con asesor."""
    
    @abstractmethod
    def guardar(self, simulacro: SimulacroConAsesor) -> SimulacroConAsesor:
        """Guarda un simulacro."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, simulacro_id: str) -> Optional[SimulacroConAsesor]:
        """Obtiene un simulacro por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_migrante(self, migrante_id: str) -> List[SimulacroConAsesor]:
        """Obtiene todos los simulacros de un migrante."""
        pass
    
    @abstractmethod
    def contar_por_migrante(self, migrante_id: str) -> int:
        """Cuenta los simulacros de un migrante."""
        pass
    
    @abstractmethod
    def obtener_por_asesor(self, asesor_id: str) -> List[SimulacroConAsesor]:
        """Obtiene todos los simulacros de un asesor."""
        pass
    
    @abstractmethod
    def obtener_agendados_para_fecha(self, fecha: date) -> List[SimulacroConAsesor]:
        """Obtiene los simulacros agendados para una fecha específica."""
        pass


class ISesionPracticaRepository(ABC):
    """Interfaz del repositorio de sesiones de práctica individual."""
    
    @abstractmethod
    def guardar(self, sesion: SesionPracticaIndividual) -> SesionPracticaIndividual:
        """Guarda una sesión de práctica."""
        pass
    
    @abstractmethod
    def obtener_por_id(self, sesion_id: str) -> Optional[SesionPracticaIndividual]:
        """Obtiene una sesión por su ID."""
        pass
    
    @abstractmethod
    def obtener_por_migrante(self, migrante_id: str) -> List[SesionPracticaIndividual]:
        """Obtiene todas las sesiones de un migrante."""
        pass
    
    @abstractmethod
    def obtener_activa_por_migrante(self, migrante_id: str) -> Optional[SesionPracticaIndividual]:
        """Obtiene la sesión activa de un migrante si existe."""
        pass


class IGestorSimulacrosRepository(ABC):
    """Interfaz del repositorio del gestor de simulacros."""
    
    @abstractmethod
    def obtener_gestor(self, migrante_id: str) -> Optional[GestorSimulacros]:
        """Obtiene el gestor de simulacros para un migrante."""
        pass
    
    @abstractmethod
    def guardar_gestor(self, gestor: GestorSimulacros) -> GestorSimulacros:
        """Guarda el gestor de simulacros."""
        pass


class IPreguntaRepository(ABC):
    """Interfaz del repositorio de preguntas del banco de preguntas."""
    
    @abstractmethod
    def obtener_por_tipo_visado(self, tipo_visado: TipoVisado) -> List[dict]:
        """Obtiene las preguntas para un tipo de visado."""
        pass
    
    @abstractmethod
    def obtener_pregunta_por_id(self, pregunta_id: str) -> Optional[dict]:
        """Obtiene una pregunta por su ID."""
        pass
