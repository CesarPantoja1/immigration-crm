"""
Modelos de infraestructura para la característica de Coordinación.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class Recordatorio(TimeStampedModel):
    """
    Modelo de Recordatorio programado.
    """
    TIPOS_RECORDATORIO = [
        ('entrevista_24h', 'Recordatorio 24h antes de Entrevista'),
        ('entrevista_1h', 'Recordatorio 1h antes de Entrevista'),
        ('simulacro_24h', 'Recordatorio 24h antes de Simulacro'),
        ('simulacro_1h', 'Recordatorio 1h antes de Simulacro'),
        ('documentos_pendientes', 'Documentos Pendientes'),
        ('pago_pendiente', 'Pago Pendiente'),
    ]

    ESTADOS = [
        ('programado', 'Programado'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
        ('fallido', 'Fallido'),
    ]

    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='recordatorios',
        verbose_name='Usuario'
    )
    tipo = models.CharField(
        'Tipo de Recordatorio',
        max_length=50,
        choices=TIPOS_RECORDATORIO
    )
    fecha_programada = models.DateTimeField(
        'Fecha Programada de Envío'
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADOS,
        default='programado',
        db_index=True
    )
    entrevista = models.ForeignKey(
        'solicitudes.Entrevista',
        on_delete=models.CASCADE,
        related_name='recordatorios',
        verbose_name='Entrevista',
        null=True,
        blank=True
    )
    simulacro = models.ForeignKey(
        'preparacion.Simulacro',
        on_delete=models.CASCADE,
        related_name='recordatorios',
        verbose_name='Simulacro',
        null=True,
        blank=True
    )
    mensaje_personalizado = models.TextField(
        'Mensaje Personalizado',
        blank=True
    )
    fecha_envio_real = models.DateTimeField(
        'Fecha de Envío Real',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'recordatorios'
        verbose_name = 'Recordatorio'
        verbose_name_plural = 'Recordatorios'
        ordering = ['fecha_programada']
        indexes = [
            models.Index(fields=['estado', 'fecha_programada']),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.usuario} - {self.fecha_programada}"


class ComunicacionExterna(TimeStampedModel):
    """
    Modelo para registrar comunicaciones con entidades externas (embajadas, etc.).
    """
    TIPOS_COMUNICACION = [
        ('consulta_horarios', 'Consulta de Horarios'),
        ('confirmacion_cita', 'Confirmación de Cita'),
        ('cancelacion_cita', 'Cancelación de Cita'),
        ('reprogramacion_cita', 'Reprogramación de Cita'),
        ('solicitud_informacion', 'Solicitud de Información'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('respondida', 'Respondida'),
        ('fallida', 'Fallida'),
    ]

    entrevista = models.ForeignKey(
        'solicitudes.Entrevista',
        on_delete=models.CASCADE,
        related_name='comunicaciones_externas',
        verbose_name='Entrevista'
    )
    tipo = models.CharField(
        'Tipo de Comunicación',
        max_length=50,
        choices=TIPOS_COMUNICACION
    )
    entidad_destino = models.CharField(
        'Entidad Destino',
        max_length=200,
        help_text='Ej: Embajada de USA'
    )
    mensaje_enviado = models.TextField(
        'Mensaje Enviado',
        blank=True
    )
    respuesta_recibida = models.TextField(
        'Respuesta Recibida',
        blank=True
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
    fecha_respuesta = models.DateTimeField(
        'Fecha de Respuesta',
        null=True,
        blank=True
    )
    datos_adjuntos = models.JSONField(
        'Datos Adjuntos',
        default=dict
    )

    class Meta:
        db_table = 'comunicaciones_externas'
        verbose_name = 'Comunicación Externa'
        verbose_name_plural = 'Comunicaciones Externas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tipo} - {self.entidad_destino} - {self.estado}"
