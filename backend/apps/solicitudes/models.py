"""
Modelos de la app Solicitudes.
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel, SoftDeleteModel


class Solicitud(TimeStampedModel, SoftDeleteModel):
    """
    Modelo de Solicitud de Visa.
    Representa una solicitud de trámite migratorio.
    """
    
    TIPOS_VISA = [
        ('vivienda', 'Visa de Vivienda'),
        ('trabajo', 'Visa de Trabajo'),
        ('estudio', 'Visa de Estudio'),
        ('turismo', 'Visa de Turismo'),
    ]
    
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente de Revisión'),
        ('en_revision', 'En Revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('enviada_embajada', 'Enviada a Embajada'),
        ('entrevista_agendada', 'Entrevista Agendada'),
        ('completada', 'Completada'),
    ]
    
    EMBAJADAS = [
        ('usa', 'Estados Unidos'),
        ('brasil', 'Brasil'),
        ('canada', 'Canadá'),
        ('espana', 'España'),
    ]
    
    # Relaciones
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='solicitudes_como_cliente',
        limit_choices_to={'rol': 'cliente'},
        verbose_name='Cliente'
    )
    asesor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='solicitudes_asignadas',
        limit_choices_to={'rol': 'asesor'},
        null=True,
        blank=True,
        verbose_name='Asesor Asignado'
    )
    
    # Datos de la solicitud
    tipo_visa = models.CharField(
        'Tipo de Visa',
        max_length=20,
        choices=TIPOS_VISA
    )
    embajada = models.CharField(
        'Embajada',
        max_length=20,
        choices=EMBAJADAS
    )
    estado = models.CharField(
        'Estado',
        max_length=30,
        choices=ESTADOS,
        default='borrador',
        db_index=True
    )
    
    # Datos personales del solicitante
    datos_personales = models.JSONField(
        'Datos Personales',
        default=dict,
        help_text='Nombre, pasaporte, nacionalidad, etc.'
    )
    
    # Documentos adjuntos
    documentos = models.JSONField(
        'Documentos',
        default=list,
        help_text='Lista de documentos adjuntos'
    )
    
    # Observaciones y notas
    observaciones = models.TextField(
        'Observaciones',
        blank=True
    )
    notas_asesor = models.TextField(
        'Notas del Asesor',
        blank=True
    )
    
    # Fechas importantes
    fecha_asignacion = models.DateTimeField(
        'Fecha de Asignación',
        null=True,
        blank=True
    )
    fecha_revision = models.DateTimeField(
        'Fecha de Revisión',
        null=True,
        blank=True
    )
    fecha_envio_embajada = models.DateTimeField(
        'Fecha de Envío a Embajada',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'solicitudes'
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Solicitud #{self.id} - {self.get_tipo_visa_display()} - {self.cliente}"
    
    def puede_ser_asignada(self) -> bool:
        """Verifica si la solicitud puede ser asignada a un asesor."""
        return self.estado in ['pendiente', 'borrador'] and self.asesor is None
    
    def asignar_asesor(self, asesor):
        """Asigna un asesor a la solicitud."""
        from django.utils import timezone
        self.asesor = asesor
        self.estado = 'pendiente'
        self.fecha_asignacion = timezone.now()
        self.save()


class Documento(TimeStampedModel):
    """
    Modelo de Documento adjunto a una solicitud.
    """
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='documentos_adjuntos',
        verbose_name='Solicitud'
    )
    nombre = models.CharField('Nombre', max_length=100)
    archivo = models.FileField(
        'Archivo',
        upload_to='solicitudes/documentos/%Y/%m/'
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADOS,
        default='pendiente'
    )
    motivo_rechazo = models.TextField(
        'Motivo de Rechazo',
        blank=True
    )
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Revisado por'
    )
    fecha_revision = models.DateTimeField(
        'Fecha de Revisión',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'documentos_solicitud'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
    
    def __str__(self):
        return f"{self.nombre} - {self.solicitud_id}"


class Entrevista(TimeStampedModel):
    """
    Modelo de Entrevista agendada.
    """
    
    ESTADOS = [
        ('pendiente', 'Pendiente de Agendar'),
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('reprogramada', 'Reprogramada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    solicitud = models.OneToOneField(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='entrevista',
        verbose_name='Solicitud'
    )
    fecha = models.DateField('Fecha de Entrevista')
    hora = models.TimeField('Hora de Entrevista')
    ubicacion = models.CharField(
        'Ubicación',
        max_length=200,
        blank=True
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADOS,
        default='agendada'
    )
    notas = models.TextField('Notas', blank=True)
    veces_reprogramada = models.PositiveIntegerField(
        'Veces Reprogramada',
        default=0
    )
    motivo_cancelacion = models.TextField(
        'Motivo de Cancelación',
        blank=True
    )
    
    class Meta:
        db_table = 'entrevistas'
        verbose_name = 'Entrevista'
        verbose_name_plural = 'Entrevistas'
        ordering = ['fecha', 'hora']
    
    def __str__(self):
        return f"Entrevista - {self.solicitud} - {self.fecha}"
