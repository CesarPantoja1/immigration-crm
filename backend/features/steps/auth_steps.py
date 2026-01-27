"""
Steps relacionados con autenticación y usuarios.
"""
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
