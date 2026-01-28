"""
Steps relacionados con autenticación y usuarios.
"""
import os
import sys

# Agregar el directorio backend al path para importar los módulos
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from behave import given, when, then
from apps.usuarios.infrastructure.models import UsuarioModel


@given('que existe un usuario "{username}" con rol "{rol}"')
def step_crear_usuario(context, username, rol):
    """Crea un usuario de prueba."""
    # Aquí se creará el usuario cuando se implemente el modelo
    context.usuario = None


@given('que el usuario "{username}" ha iniciado sesión')
def step_usuario_autenticado(context, username):
    """Simula un usuario autenticado."""
    context.usuario_autenticado = username
