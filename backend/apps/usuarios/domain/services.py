"""
Domain Services (DDD)
Lógica de dominio que no pertenece a una entidad específica
"""
from .entities import Usuario


class UsuarioDomainService:
    """Servicios de dominio para Usuario"""
    
    @staticmethod
    def puede_gestionar_usuarios(usuario: Usuario) -> bool:
        """Verifica si un usuario puede gestionar otros usuarios"""
        return usuario.es_administrador()
    
    @staticmethod
    def usuarios_mismo_rol(usuario1: Usuario, usuario2: Usuario) -> bool:
        """Verifica si dos usuarios tienen el mismo rol"""
        return usuario1.rol == usuario2.rol
