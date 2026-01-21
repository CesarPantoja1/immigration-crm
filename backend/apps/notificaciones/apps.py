"""
Configuración de la app Notificaciones.
"""
from django.apps import AppConfig


class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notificaciones'
    verbose_name = 'Gestión de Notificaciones'

    def ready(self):
        """
        Importar signals cuando la app esté lista.
        """
        from . import tasks  # noqa: F401
        # from .seguimiento import signals  # noqa
        # from .coordinacion import signals  # noqa
