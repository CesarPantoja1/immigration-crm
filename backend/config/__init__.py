"""
Configuración principal del proyecto.
"""
# Esto asegura que Celery sea importado cuando Django se inicia
from .celery import app as celery_app

__all__ = ('celery_app',)
