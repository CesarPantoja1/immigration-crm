"""
Configuración de la app Core.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        """
        Importar signals cuando la app esté lista.
        """
        from . import events  # noqa
