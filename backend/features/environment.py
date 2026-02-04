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
        'features.notificaciones.steps.alertas_entrevista',
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
    
    NOTA: Los tests de seguimiento_solicitud.feature usan lógica pura en memoria,
    no requieren limpieza de BD. Esta limpieza es para otros features que sí
    interactúan con la BD real (alertas_entrevista, agendamiento, etc.)
    """
    # Detectar si el feature requiere limpieza de BD
    # Los features con lógica pura no necesitan limpieza
    features_sin_bd = [
        'seguimiento_solicitud.feature',  # Usa business_logic puro
    ]
    
    feature_name = scenario.feature.filename.split('/')[-1].split('\\')[-1]
    
    if feature_name in features_sin_bd:
        # Este feature usa lógica pura, no necesita limpieza de BD
        return
    
    # Limpieza de BD para features que sí la necesitan
    from apps.notificaciones.models import Notificacion, ConfiguracionRecordatorio
    from apps.solicitudes.models import Solicitud, Documento, Cita
    from apps.usuarios.models import Usuario
    
    # Limpiar en orden para evitar conflictos de FK
    Notificacion.objects.all().delete()
    ConfiguracionRecordatorio.objects.all().delete()
    Documento.objects.all().delete()
    Cita.objects.all().delete()
    Solicitud.objects.all().delete()
    Usuario.objects.all().delete()


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
