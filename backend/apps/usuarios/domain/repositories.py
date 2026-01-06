"""
Repository Interface (DDD)
Define el contrato para el repositorio sin implementación
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Usuario


class IUsuarioRepository(ABC):
    """Interfaz del repositorio de usuarios"""
    
    @abstractmethod
    def save(self, usuario: Usuario) -> Usuario:
        """Guarda un usuario"""
        pass
    
    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Usuario]:
        """Encuentra un usuario por ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Usuario]:
        """Retorna todos los usuarios"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> None:
        """Elimina un usuario"""
        pass
