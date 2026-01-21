"""
Configuración de la app Solicitudes.
"""
from django.apps import AppConfig


class SolicitudesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.solicitudes'
    verbose_name = 'Solicitudes Migratorias'

    def ready(self):
        """
        Importar signals cuando la app esté lista.
        """
        # from .recepcion import signals  # noqa
        # from .agendamiento import signals  # noqa
        pass
