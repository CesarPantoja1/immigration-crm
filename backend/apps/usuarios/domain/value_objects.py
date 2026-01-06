"""
Value Objects (DDD)
Objetos sin identidad, inmutables, definidos por sus atributos
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class NombreCompleto:
    """Value Object para nombre completo"""
    nombre: str
    apellido: str
    
    def __str__(self) -> str:
        return f"{self.nombre} {self.apellido}"
    
    def __post_init__(self):
        if not self.nombre or not self.apellido:
            raise ValueError("Nombre y apellido son requeridos")


@dataclass(frozen=True)
class Rol:
    """Value Object para rol de usuario"""
    valor: str
    
    ADMIN = 'admin'
    AGENTE = 'agente'
    CLIENTE = 'cliente'
    
    def __post_init__(self):
        roles_validos = [self.ADMIN, self.AGENTE, self.CLIENTE]
        if self.valor not in roles_validos:
            raise ValueError(f"Rol debe ser uno de: {roles_validos}")
    
    def es_admin(self) -> bool:
        return self.valor == self.ADMIN
