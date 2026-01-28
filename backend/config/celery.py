"""
Configuración de Celery para tareas asíncronas.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Establecer el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('crm_migratorio')

# Usar la configuración de Django para Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en todas las apps instaladas
app.autodiscover_tasks()

# Configuración de tareas programadas (Celery Beat)
app.conf.beat_schedule = {
    # Recordatorios de entrevista - cada hora
    'enviar-recordatorios-entrevista': {
        'task': 'notificaciones.enviar_recordatorios_entrevista',
        'schedule': crontab(minute=0),  # Cada hora en punto
    },
    
    # Recomendaciones de preparación - diariamente a las 9am
    'enviar-recomendaciones-preparacion': {
        'task': 'notificaciones.enviar_recomendaciones_preparacion',
        'schedule': crontab(hour=9, minute=0),  # Diariamente a las 9:00
    },
    
    # Limpieza de notificaciones antiguas - semanalmente (domingo 3am)
    'limpiar-notificaciones-antiguas': {
        'task': 'notificaciones.limpiar_notificaciones_antiguas',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Domingo 3:00
        'kwargs': {'dias': 90}
    },
}


@app.task(bind=True)
def debug_task(self):
    """Tarea de debug para verificar que Celery funciona."""
    print(f'Request: {self.request!r}')
