"""
Configuración de Behave para feature de Agendamiento de Entrevistas.
"""
import os
import sys

# Agregar el directorio backend al path para importar los módulos
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configurar Django para los tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
os.environ.setdefault('DJANGO_ENV', 'testing')

import django
django.setup()


def before_all(context):
    """Se ejecuta una vez antes de todas las pruebas."""
    pass


def before_scenario(context, scenario):
    """Se ejecuta antes de cada escenario."""
    pass


def after_scenario(context, scenario):
    """Se ejecuta después de cada escenario."""
    pass


def after_all(context):
    """Se ejecuta una vez después de todas las pruebas."""
    pass
