"""
Modelos para el módulo de Notificaciones.
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class TipoNotificacion(models.Model):
    """
    Catálogo de tipos de notificación.
    """
    codigo = models.CharField('Código', max_length=50, unique=True)
    nombre = models.CharField('Nombre', max_length=100)
    proposito = models.TextField('Propósito')
    icono = models.CharField('Icono', max_length=50, default='bell')
    color = models.CharField('Color', max_length=20, default='blue')
    
    class Meta:
        db_table = 'tipos_notificacion'
        verbose_name = 'Tipo de Notificación'
        verbose_name_plural = 'Tipos de Notificación'
    
    def __str__(self):
        return self.nombre


class Notificacion(TimeStampedModel):
    """
    Modelo de Notificación.
    """
    
    TIPOS = [
        # Solicitudes
        ('solicitud_creada', 'Solicitud Creada'),
        ('solicitud_asignada', 'Solicitud Asignada'),
        ('solicitud_aprobada', 'Solicitud Aprobada'),
        ('solicitud_rechazada', 'Solicitud Rechazada'),
        ('solicitud_enviada', 'Solicitud Enviada a Embajada'),
        ('solicitud_en_revision', 'Solicitud en Revisión'),
        
        # Contratos
        ('contrato_generado', 'Contrato Generado'),
        ('contrato_pendiente', 'Contrato Pendiente de Firma'),
        ('contrato_firmado', 'Contrato Firmado'),
        ('contrato_aprobado', 'Contrato Aprobado'),
        
        # Documentos
        ('documento_subido', 'Documento Subido'),
        ('documento_aprobado', 'Documento Aprobado'),
        ('documento_rechazado', 'Documento Rechazado'),
        
        # Entrevistas
        ('entrevista_agendada', 'Entrevista Agendada'),
        ('entrevista_reprogramada', 'Entrevista Reprogramada'),
        ('entrevista_cancelada', 'Entrevista Cancelada'),
        ('recordatorio_entrevista', 'Recordatorio de Entrevista'),
        
        # Preparación y Simulacros
        ('preparacion_recomendada', 'Preparación Recomendada'),
        ('simulacro_propuesto', 'Simulacro Propuesto'),
        ('simulacro_confirmado', 'Simulacro Confirmado'),
        ('simulacion_completada', 'Simulación Completada'),
        ('recomendaciones_listas', 'Recomendaciones Listas'),
        
        # General
        ('general', 'General'),
        ('mensaje', 'Mensaje'),
    ]
    
    # Destinatario
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Usuario'
    )
    
    # Tipo y contenido
    tipo = models.CharField(
        'Tipo',
        max_length=50,
        choices=TIPOS,
        default='general',
        db_index=True
    )
    titulo = models.CharField('Título', max_length=200)
    mensaje = models.TextField('Mensaje')
    detalle = models.TextField('Detalle', blank=True)
    
    # Datos adicionales (JSON para flexibilidad)
    datos = models.JSONField('Datos Adicionales', default=dict)
    
    # Relaciones opcionales
    solicitud = models.ForeignKey(
        'solicitudes.Solicitud',
        on_delete=models.CASCADE,
        related_name='notificaciones',
        null=True,
        blank=True,
        verbose_name='Solicitud'
    )
    
    # Estado
    leida = models.BooleanField('Leída', default=False)
    fecha_lectura = models.DateTimeField('Fecha de Lectura', null=True, blank=True)
    
    # URL de acción
    url_accion = models.CharField('URL de Acción', max_length=500, blank=True)
    
    class Meta:
        db_table = 'notificaciones'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['usuario', 'tipo']),
        ]
    
    def __str__(self):
        return f"{self.tipo} - {self.usuario}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída."""
        from django.utils import timezone
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save()


class ConfiguracionRecordatorio(models.Model):
    """
    Configuración de ventanas de recordatorio.
    """
    tipo = models.CharField('Tipo', max_length=50)  # entrevista, simulacro, etc.
    ventana_horas = models.PositiveIntegerField('Ventana (horas)')
    mensaje_template = models.TextField('Template del Mensaje')
    activo = models.BooleanField('Activo', default=True)
    
    class Meta:
        db_table = 'configuracion_recordatorios'
        verbose_name = 'Configuración de Recordatorio'
        verbose_name_plural = 'Configuraciones de Recordatorio'
    
    def __str__(self):
        return f"{self.tipo} - {self.ventana_horas}h"


class PreferenciaNotificacion(models.Model):
    """
    Preferencias de notificación por usuario.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferencias_notificacion',
        verbose_name='Usuario'
    )
    
    # Preferencias por tipo
    email_entrevistas = models.BooleanField('Email Entrevistas', default=True)
    email_documentos = models.BooleanField('Email Documentos', default=True)
    email_simulacros = models.BooleanField('Email Simulacros', default=True)
    email_recordatorios = models.BooleanField('Email Recordatorios', default=True)
    
    # Push notifications (futuro)
    push_habilitado = models.BooleanField('Push Habilitado', default=False)
    
    class Meta:
        db_table = 'preferencias_notificacion'
        verbose_name = 'Preferencia de Notificación'
        verbose_name_plural = 'Preferencias de Notificación'
    
    def __str__(self):
        return f"Preferencias - {self.usuario}"
