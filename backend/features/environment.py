"""
Configuración de Behave para BDD.
Este archivo configura el entorno de pruebas antes y después de cada escenario.
"""
import os
import sys
import django
from django.conf import settings

# Agregar el directorio backend al path para importar los módulos
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configurar Django para los tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
os.environ.setdefault('DJANGO_ENV', 'testing')

# Inicializar Django
django.setup()


def before_all(context):
    """
    Se ejecuta una vez antes de todas las pruebas.
    """
    from django.core.management import call_command

    # Crear tablas de la base de datos
    call_command('migrate', '--run-syncdb', verbosity=0)
    
    # Registrar steps adicionales
    from behave.runner import Context
    
    # Importar steps específicos de cada módulo
    import importlib
    
    step_modules = [
        'features.preparacion.simulacion.steps.simulacion_steps',
        'features.preparacion.recomendaciones.steps.recomendaciones_steps',
        'features.notificaciones.steps.seguimiento_solicitud',
        'features.solicitudes.agendamiento.steps.agendamiento_entrevista',
        'features.solicitudes.recepcion.steps.recepcion_solicitud',
    ]
    
    for module_name in step_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")


def before_scenario(context, scenario):
    """
    Se ejecuta antes de cada escenario.
    """
    # Limpiar la base de datos antes de cada escenario
    from django.core.management import call_command
    call_command('flush', '--no-input', verbosity=0)


def after_scenario(context, scenario):
    """
    Se ejecuta después de cada escenario.
    """
    pass


def after_all(context):
    """
    Se ejecuta una vez después de todas las pruebas.
    """
    pass
