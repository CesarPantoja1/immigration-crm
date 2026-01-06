"""
Entidades de Dominio (DDD)
Objetos con identidad que encapsulan lógica de negocio
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuario:
    """Entidad Usuario - Agregado raíz"""
    id: Optional[int]
    nombre: str
    apellido: str
    rol: str
    
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario"""
        return f"{self.nombre} {self.apellido}"
    
    def es_administrador(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.rol == 'admin'
    
    def cambiar_rol(self, nuevo_rol: str) -> None:
        """Cambia el rol del usuario con validación"""
        roles_validos = ['admin', 'agente', 'cliente']
        if nuevo_rol not in roles_validos:
            raise ValueError(f"Rol inválido. Debe ser uno de: {roles_validos}")
        self.rol = nuevo_rol
