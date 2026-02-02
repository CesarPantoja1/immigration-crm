"""
Steps relacionados con autenticación y usuarios.
Refactorizado para usar la arquitectura Service Layer.

Los datos de usuario se manejan como diccionarios para testing BDD.
No se importa el modelo Django directamente para evitar dependencias.
"""
from behave import given, when, then


@given('que existe un usuario "{username}" con rol "{rol}"')
def step_crear_usuario(context, username, rol):
    """Crea un usuario de prueba como diccionario."""
    # Mapear rol del feature al modelo
    rol_map = {
        'admin': 'admin',
        'administrador': 'admin',
        'asesor': 'asesor',
        'cliente': 'cliente',
        'migrante': 'cliente',
    }
    rol_db = rol_map.get(rol.lower(), 'cliente')
    
    context.usuario = {
        'email': f'{username}@test.com',
        'rol': rol_db,
        'first_name': username,
        'last_name': 'Test'
    }


@given('que el usuario "{username}" ha iniciado sesión')
def step_usuario_autenticado(context, username):
    """Simula un usuario autenticado."""
    context.usuario_autenticado = username
    context.autenticado = True
