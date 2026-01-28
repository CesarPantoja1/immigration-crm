"""
Tareas asíncronas con Celery para la app de Notificaciones.
Implementa recordatorios programados según especificación Gherkin.

NOTA: Estas tareas están diseñadas para ejecutarse con Celery Beat.
Si Celery no está instalado, las funciones pueden llamarse directamente 
o configurarse con cron jobs.
"""
import logging

logger = logging.getLogger(__name__)

# Intentar importar Celery, si no está disponible, usar decorador dummy
try:
    from celery import shared_task
except ImportError:
    # Decorador dummy para cuando Celery no está instalado
    def shared_task(*args, **kwargs):
        def decorator(func):
            func.delay = lambda *a, **kw: func(*a, **kw)  # Ejecutar síncronamente
            return func
        if args and callable(args[0]):
            return decorator(args[0])
        return decorator
    
    logger.warning("Celery no está instalado. Las tareas se ejecutarán síncronamente.")

from django.utils import timezone
from datetime import timedelta


def _get_entrevista_model():
    """Intenta importar el modelo de Entrevista de forma segura."""
    try:
        from apps.solicitudes.agendamiento.infrastructure.models import EntrevistaModel
        return EntrevistaModel
    except ImportError as e:
        logger.warning(f"No se pudo importar EntrevistaModel: {e}")
        return None


def _get_simulacro_model():
    """Intenta importar el modelo de Simulacro de forma segura."""
    try:
        from apps.preparacion.models import Simulacro
        return Simulacro
    except ImportError as e:
        logger.warning(f"No se pudo importar Simulacro: {e}")
        return None


@shared_task(name='notificaciones.enviar_recordatorios_entrevista')
def enviar_recordatorios_entrevista():
    """
    Tarea programada para enviar recordatorios de entrevista.
    Ejecutar cada hora.
    
    Ventanas de recordatorio:
    - 24 horas antes
    - 2 horas antes
    """
    from apps.notificaciones.services import notificacion_service
    from apps.notificaciones.models import Notificacion
    from datetime import datetime
    
    Entrevista = _get_entrevista_model()
    if not Entrevista:
        logger.error("No se puede ejecutar enviar_recordatorios_entrevista: modelo Entrevista no disponible")
        return "Error: modelo Entrevista no disponible"
    
    ahora = timezone.now()
    enviados = {'24h': 0, '2h': 0}
    
    try:
        # Buscar entrevistas agendadas/confirmadas
        entrevistas = Entrevista.objects.filter(
            estado__in=['AGENDADA', 'CONFIRMADA']
        ).select_related('solicitud')
        
        for entrevista in entrevistas:
            try:
                # Combinar fecha y hora de la entrevista
                if not entrevista.fecha or not entrevista.hora:
                    continue
                    
                fecha_entrevista = timezone.make_aware(
                    datetime.combine(entrevista.fecha, entrevista.hora)
                )
                
                tiempo_restante = fecha_entrevista - ahora
                horas_restantes = tiempo_restante.total_seconds() / 3600
                
                # Obtener el cliente (puede ser 'solicitante' o 'usuario' dependiendo del modelo)
                solicitud = entrevista.solicitud
                cliente = getattr(solicitud, 'solicitante', None) or getattr(solicitud, 'usuario', None)
                
                if not cliente:
                    logger.warning(f"No se pudo obtener el cliente para entrevista {entrevista.id}")
                    continue
                
                # Recordatorio 24 horas antes (entre 23.5 y 24.5 horas)
                if 23.5 <= horas_restantes <= 24.5:
                    # Verificar que no se haya enviado ya
                    ya_enviado = Notificacion.objects.filter(
                        usuario=cliente,
                        tipo='recordatorio_entrevista',
                        datos__horas_restantes=24,
                        created_at__gte=ahora - timedelta(hours=25)
                    ).exists()
                    
                    if not ya_enviado:
                        notificacion_service.notificar_recordatorio_entrevista(
                            solicitud=solicitud,
                            horas_restantes=24,
                            fecha_entrevista=entrevista.fecha,
                            hora_entrevista=entrevista.hora
                        )
                        enviados['24h'] += 1
                        logger.info(f"Recordatorio 24h enviado a {cliente.email} para entrevista {entrevista.id}")
                
                # Recordatorio 2 horas antes (entre 1.5 y 2.5 horas)
                elif 1.5 <= horas_restantes <= 2.5:
                    ya_enviado = Notificacion.objects.filter(
                        usuario=cliente,
                        tipo='recordatorio_entrevista',
                        datos__horas_restantes=2,
                        created_at__gte=ahora - timedelta(hours=3)
                    ).exists()
                    
                    if not ya_enviado:
                        notificacion_service.notificar_recordatorio_entrevista(
                            solicitud=solicitud,
                            horas_restantes=2,
                            fecha_entrevista=entrevista.fecha,
                            hora_entrevista=entrevista.hora
                        )
                        enviados['2h'] += 1
                        logger.info(f"Recordatorio 2h enviado a {cliente.email} para entrevista {entrevista.id}")
                        
            except Exception as e:
                logger.error(f"Error procesando recordatorio para entrevista {entrevista.id}: {e}")
        
    except Exception as e:
        logger.error(f"Error en enviar_recordatorios_entrevista: {e}")
        return f"Error: {e}"
    
    return f"Recordatorios enviados - 24h: {enviados['24h']}, 2h: {enviados['2h']}"


@shared_task(name='notificaciones.enviar_recomendaciones_preparacion')
def enviar_recomendaciones_preparacion():
    """
    Tarea programada para enviar recomendaciones de preparación.
    Ejecutar diariamente.
    
    Envía notificación si:
    - La entrevista es en 7 días o menos
    - El cliente NO tiene simulacro confirmado
    """
    from apps.notificaciones.services import notificacion_service
    from apps.notificaciones.models import Notificacion
    
    Entrevista = _get_entrevista_model()
    Simulacro = _get_simulacro_model()
    
    if not Entrevista:
        logger.error("No se puede ejecutar enviar_recomendaciones_preparacion: modelo Entrevista no disponible")
        return "Error: modelo Entrevista no disponible"
    
    ahora = timezone.now()
    hoy = ahora.date()
    en_7_dias = hoy + timedelta(days=7)
    enviados = 0
    
    try:
        # Buscar entrevistas en los próximos 7 días
        entrevistas = Entrevista.objects.filter(
            estado__in=['AGENDADA', 'CONFIRMADA'],
            fecha__gte=hoy,
            fecha__lte=en_7_dias
        ).select_related('solicitud')
        
        for entrevista in entrevistas:
            try:
                solicitud = entrevista.solicitud
                cliente = getattr(solicitud, 'solicitante', None) or getattr(solicitud, 'usuario', None)
                
                if not cliente:
                    continue
                    
                dias_restantes = (entrevista.fecha - hoy).days
                
                # Verificar si tiene simulacro confirmado
                tiene_simulacro = False
                if Simulacro:
                    tiene_simulacro = Simulacro.objects.filter(
                        cliente=cliente,
                        estado__in=['confirmado', 'en_sala_espera', 'en_progreso', 'completado']
                    ).exists()
                
                if tiene_simulacro:
                    continue
                
                # Verificar que no se haya enviado ya esta semana
                ya_enviado = Notificacion.objects.filter(
                    usuario=cliente,
                    tipo='preparacion_recomendada',
                    created_at__gte=ahora - timedelta(days=7)
                ).exists()
                
                if not ya_enviado:
                    notificacion_service.notificar_preparacion_recomendada(
                        solicitud=solicitud,
                        dias_para_entrevista=dias_restantes
                    )
                    enviados += 1
                    logger.info(f"Recomendación de preparación enviada a {cliente.email}")
                    
            except Exception as e:
                logger.error(f"Error procesando recomendación para entrevista {entrevista.id}: {e}")
        
    except Exception as e:
        logger.error(f"Error en enviar_recomendaciones_preparacion: {e}")
        return f"Error: {e}"
    
    return f"Recomendaciones de preparación enviadas: {enviados}"


@shared_task(name='notificaciones.limpiar_notificaciones_antiguas')
def limpiar_notificaciones_antiguas(dias=90):
    """
    Limpia notificaciones leídas con más de X días de antigüedad.
    Ejecutar semanalmente.
    """
    from apps.notificaciones.models import Notificacion
    
    fecha_limite = timezone.now() - timedelta(days=dias)
    
    try:
        eliminadas = Notificacion.objects.filter(
            leida=True,
            created_at__lt=fecha_limite
        ).delete()[0]
        
        logger.info(f"Notificaciones antiguas eliminadas: {eliminadas}")
        return f"Notificaciones eliminadas: {eliminadas}"
    except Exception as e:
        logger.error(f"Error limpiando notificaciones: {e}")
        return f"Error: {e}"


# =====================================================
# TAREAS SÍNCRONAS (para llamar desde signals/views)
# =====================================================

@shared_task(name='notificaciones.notificar_simulacro_completado')
def notificar_simulacro_completado(simulacro_id):
    """
    Notifica al asesor cuando un simulacro es completado.
    Se llama desde el endpoint de finalizar simulacro.
    """
    from apps.notificaciones.services import notificacion_service
    
    Simulacro = _get_simulacro_model()
    if not Simulacro:
        return f"Error: modelo Simulacro no disponible"
    
    try:
        simulacro = Simulacro.objects.select_related('cliente', 'asesor').get(pk=simulacro_id)
        notificacion_service.notificar_simulacion_completada(simulacro)
        logger.info(f"Notificación de simulacro completado enviada para simulacro {simulacro_id}")
        return f"Notificación enviada para simulacro {simulacro_id}"
    except Simulacro.DoesNotExist:
        logger.error(f"Simulacro {simulacro_id} no encontrado")
        return f"Error: Simulacro {simulacro_id} no encontrado"
    except Exception as e:
        logger.error(f"Error notificando simulacro completado: {e}")
        return f"Error: {e}"


@shared_task(name='notificaciones.notificar_recomendaciones_publicadas')
def notificar_recomendaciones_publicadas(simulacro_id):
    """
    Notifica al cliente cuando las recomendaciones están listas.
    Se llama cuando el asesor publica las recomendaciones.
    """
    from apps.notificaciones.services import notificacion_service
    
    Simulacro = _get_simulacro_model()
    if not Simulacro:
        return f"Error: modelo Simulacro no disponible"
    
    try:
        simulacro = Simulacro.objects.select_related('cliente', 'asesor').get(pk=simulacro_id)
        notificacion_service.notificar_recomendaciones_listas(simulacro)
        logger.info(f"Notificación de recomendaciones enviada para simulacro {simulacro_id}")
        return f"Notificación enviada para simulacro {simulacro_id}"
    except Simulacro.DoesNotExist:
        logger.error(f"Simulacro {simulacro_id} no encontrado")
        return f"Error: Simulacro {simulacro_id} no encontrado"
    except Exception as e:
        logger.error(f"Error notificando recomendaciones: {e}")
        return f"Error: {e}"
