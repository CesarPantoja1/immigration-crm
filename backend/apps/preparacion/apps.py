"""
Configuración de la app Preparación.
"""
from django.apps import AppConfig


class PreparacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.preparacion'
    verbose_name = 'Preparación de Entrevistas'

    def ready(self):
        """
        Importar signals cuando la app esté lista.
        """
        # from .simulacion import signals  # noqa
        # from .recomendaciones import signals  # noqa
        pass
