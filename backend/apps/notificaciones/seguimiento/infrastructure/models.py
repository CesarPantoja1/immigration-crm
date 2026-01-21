"""
Modelos de infraestructura para la característica de Seguimiento de Solicitudes.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class EstadoSolicitud(TimeStampedModel):
    """
    Modelo para registrar el historial de estados de una solicitud.
    """
    solicitud = models.ForeignKey(
        'solicitudes.Solicitud',
        on_delete=models.CASCADE,
        related_name='historial_estados',
        verbose_name='Solicitud'
    )
    estado_anterior = models.CharField(
        'Estado Anterior',
        max_length=50,
        null=True,
        blank=True
    )
    estado_nuevo = models.CharField(
        'Estado Nuevo',
        max_length=50
    )
    observacion = models.TextField(
        'Observación',
        blank=True
    )
    usuario_responsable = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cambios_estado_realizados',
        verbose_name='Usuario Responsable'
    )

    class Meta:
        db_table = 'historial_estados_solicitud'
        verbose_name = 'Estado de Solicitud'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.solicitud} - {self.estado_anterior} → {self.estado_nuevo}"


class Notificacion(TimeStampedModel):
    """
    Modelo de Notificación enviada a un usuario.
    """
    TIPOS_NOTIFICACION = [
        ('solicitud_aprobada', 'Solicitud Aprobada'),
        ('solicitud_rechazada', 'Solicitud Rechazada'),
        ('entrevista_agendada', 'Entrevista Agendada'),
        ('entrevista_reprogramada', 'Entrevista Reprogramada'),
        ('recordatorio_entrevista', 'Recordatorio de Entrevista'),
        ('simulacro_agendado', 'Simulacro Agendado'),
        ('recomendaciones_disponibles', 'Recomendaciones Disponibles'),
    ]

    CANALES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Notificación Push'),
        ('sistema', 'Notificación del Sistema'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('fallida', 'Fallida'),
        ('leida', 'Leída'),
    ]

    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Usuario'
    )
    tipo = models.CharField(
        'Tipo de Notificación',
        max_length=50,
        choices=TIPOS_NOTIFICACION,
        db_index=True
    )
    canal = models.CharField(
        'Canal',
        max_length=20,
        choices=CANALES,
        default='sistema'
    )
    titulo = models.CharField(
        'Título',
        max_length=200
    )
    mensaje = models.TextField(
        'Mensaje'
    )
    datos_adicionales = models.JSONField(
        'Datos Adicionales',
        default=dict,
        help_text='Información contextual de la notificación'
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADOS,
        default='pendiente',
        db_index=True
    )
    fecha_envio = models.DateTimeField(
        'Fecha de Envío',
        null=True,
        blank=True
    )
    fecha_lectura = models.DateTimeField(
        'Fecha de Lectura',
        null=True,
        blank=True
    )
    error_envio = models.TextField(
        'Error de Envío',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'notificaciones'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario', 'estado']),
            models.Index(fields=['tipo', 'estado']),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.usuario} - {self.estado}"

    def marcar_como_leida(self):
        """Marca la notificación como leída."""
        from django.utils import timezone
        self.estado = 'leida'
        self.fecha_lectura = timezone.now()
        self.save()
