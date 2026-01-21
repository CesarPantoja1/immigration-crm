"""
Configuración de Behave para BDD.
Este archivo configura el entorno de pruebas antes y después de cada escenario.
"""
import os
import django
from django.conf import settings

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
