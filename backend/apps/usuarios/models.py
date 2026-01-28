"""
Modelos de la app Usuarios.
Re-exporta desde infrastructure para que Django los encuentre.
"""
from .infrastructure.models import Usuario, UsuarioManager

__all__ = ['Usuario', 'UsuarioManager']
