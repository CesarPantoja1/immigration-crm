"""
Modelos de infraestructura para la característica de Recepción de Solicitudes.
Django ORM Models que persisten las entidades de dominio.
"""
import uuid
from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel


class ChecklistDocumentosModel(models.Model):
    """
    Modelo para almacenar checklists de documentos por tipo de visa.
    """
    TIPOS_VISA = [
        ('VIVIENDA', 'Vivienda'),
        ('TRABAJO', 'Trabajo'),
        ('ESTUDIO', 'Estudio'),
        ('TURISMO', 'Turismo'),
    ]
    
    tipo_visa = models.CharField(
        'Tipo de Visa',
        max_length=20,
        choices=TIPOS_VISA,
        unique=True,
        db_index=True
    )
    documentos_obligatorios = models.JSONField(
        'Documentos Obligatorios',
        default=list,
        help_text='Lista de nombres de documentos obligatorios'
    )
    activo = models.BooleanField(
        'Activo',
        default=True
    )
    
    class Meta:
        db_table = 'checklists_documentos'
        verbose_name = 'Checklist de Documentos'
        verbose_name_plural = 'Checklists de Documentos'
    
    def __str__(self):
        return f"Checklist {self.tipo_visa} - {len(self.documentos_obligatorios)} docs"
    
    def total_documentos(self) -> int:
        """Retorna el total de documentos obligatorios."""
        return len(self.documentos_obligatorios)


class EmbajadaModel(models.Model):
    """
    Modelo para almacenar información de embajadas.
    """
    nombre = models.CharField(
        'Nombre',
        max_length=100,
        unique=True,
        db_index=True
    )
    codigo = models.CharField(
        'Código',
        max_length=20,
        unique=True
    )
    pais = models.CharField(
        'País',
        max_length=100
    )
    direccion = models.TextField(
        'Dirección',
        blank=True
    )
    telefono = models.CharField(
        'Teléfono',
        max_length=50,
        blank=True
    )
    email = models.EmailField(
        'Email',
        blank=True
    )
    activa = models.BooleanField(
        'Activa',
        default=True
    )
    
    class Meta:
        db_table = 'embajadas'
        verbose_name = 'Embajada'
        verbose_name_plural = 'Embajadas'
    
    def __str__(self):
        return self.nombre


class SolicitudModel(TimeStampedModel, SoftDeleteModel):
    """
    Modelo de Solicitud de Visa - Agregado raíz.
    """
    TIPOS_VISA = [
        ('VIVIENDA', 'Vivienda'),
        ('TRABAJO', 'Trabajo'),
        ('ESTUDIO', 'Estudio'),
        ('TURISMO', 'Turismo'),
    ]
    
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADO', 'Aprobado'),
        ('DESAPROBADO', 'Desaprobado'),
        ('REQUIERE_CORRECCIONES', 'Requiere Correcciones'),
        ('ENVIADO_EMBAJADA', 'Enviado a Embajada'),
        ('APROBADO_EMBAJADA', 'Aprobado por Embajada'),
        ('RECHAZADO_EMBAJADA', 'Rechazado por Embajada'),
    ]
    
    ESTADOS_ENVIO = [
        ('PENDIENTE', 'Pendiente'),
        ('ENVIADO', 'Enviado'),
        ('RECIBIDO', 'Recibido'),
        ('ERROR', 'Error'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    codigo = models.CharField(
        'Código',
        max_length=20,
        unique=True,
        db_index=True,
        blank=True,
        null=True
    )
    migrante = models.ForeignKey(
        'usuarios.UsuarioModel',
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name='Migrante'
    )
    tipo_visa = models.CharField(
        'Tipo de Visa',
        max_length=20,
        choices=TIPOS_VISA
    )
    embajada = models.ForeignKey(
        EmbajadaModel,
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name='Embajada',
        null=True,
        blank=True
    )
    embajada_nombre = models.CharField(
        'Nombre Embajada',
        max_length=100,
        blank=True,
        help_text='Nombre de embajada si no hay FK'
    )
    estado = models.CharField(
        'Estado',
        max_length=30,
        choices=ESTADOS,
        default='BORRADOR',
        db_index=True
    )
    estado_envio = models.CharField(
        'Estado de Envío',
        max_length=20,
        choices=ESTADOS_ENVIO,
        default='PENDIENTE'
    )
    datos_personales = models.JSONField(
        'Datos Personales',
        default=dict,
        blank=True
    )
    notas = models.TextField(
        'Notas',
        blank=True
    )
    fecha_envio = models.DateTimeField(
        'Fecha de Envío',
        null=True,
        blank=True
    )
    asesor_revisor = models.ForeignKey(
        'usuarios.UsuarioModel',
        on_delete=models.SET_NULL,
        related_name='solicitudes_revisadas',
        verbose_name='Asesor Revisor',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'solicitudes'
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['migrante', 'estado']),
            models.Index(fields=['tipo_visa', 'estado']),
        ]

    def __str__(self):
        return f"Solicitud {self.codigo or self.id} - {self.tipo_visa} - {self.estado}"
    
    def save(self, *args, **kwargs):
        """Genera código único si no existe."""
        if not self.codigo:
            # Generar código: SOL-YYYY-NNNNN
            from datetime import datetime
            year = datetime.now().year
            count = SolicitudModel.objects.filter(
                created_at__year=year
            ).count() + 1
            self.codigo = f"SOL-{year}-{count:05d}"
        super().save(*args, **kwargs)


class DocumentoModel(TimeStampedModel):
    """
    Modelo de Documento adjunto a una solicitud.
    """
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADO', 'Aprobado'),
        ('DESAPROBADO', 'Desaprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    solicitud = models.ForeignKey(
        SolicitudModel,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Solicitud'
    )
    nombre = models.CharField(
        'Nombre del Documento',
        max_length=100
    )
    archivo = models.FileField(
        'Archivo',
        upload_to='documentos/%Y/%m/',
        null=True,
        blank=True
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE',
        db_index=True
    )
    version = models.IntegerField(
        'Versión',
        default=1
    )
    motivo_rechazo = models.TextField(
        'Motivo de Rechazo',
        blank=True,
        null=True
    )
    fecha_revision = models.DateTimeField(
        'Fecha de Revisión',
        null=True,
        blank=True
    )
    revisor = models.ForeignKey(
        'usuarios.UsuarioModel',
        on_delete=models.SET_NULL,
        related_name='documentos_revisados',
        verbose_name='Revisor',
        null=True,
        blank=True
    )
    fecha_vencimiento = models.DateField(
        'Fecha de Vencimiento',
        null=True,
        blank=True,
        help_text='Fecha de vencimiento del documento (pasaporte, antecedentes, etc.)'
    )
    
    class Meta:
        db_table = 'documentos'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['solicitud', 'nombre', '-version']
        unique_together = [['solicitud', 'nombre', 'version']]
    
    def __str__(self):
        return f"{self.nombre} v{self.version} - {self.estado}"
    
    def esta_aprobado(self) -> bool:
        """Verifica si el documento está aprobado."""
        return self.estado == 'APROBADO'
    
    def esta_rechazado(self) -> bool:
        """Verifica si el documento está rechazado."""
        return self.estado in ['DESAPROBADO', 'RECHAZADO']


class EventoSolicitudModel(TimeStampedModel):
    """
    Modelo para registrar eventos/timeline de una solicitud.
    """
    TIPOS_EVENTO = [
        ('SOLICITUD_CREADA', 'Solicitud Creada'),
        ('DOCUMENTO_CARGADO', 'Documento Cargado'),
        ('DOCUMENTO_APROBADO', 'Documento Aprobado'),
        ('DOCUMENTO_RECHAZADO', 'Documento Rechazado'),
        ('SOLICITUD_EN_REVISION', 'Solicitud en Revisión'),
        ('SOLICITUD_APROBADA', 'Solicitud Aprobada'),
        ('SOLICITUD_RECHAZADA', 'Solicitud Rechazada'),
        ('SOLICITUD_ENVIADA', 'Solicitud Enviada a Embajada'),
        ('ENTREVISTA_AGENDADA', 'Entrevista Agendada'),
        ('VISA_APROBADA', 'Visa Aprobada'),
        ('VISA_RECHAZADA', 'Visa Rechazada'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    solicitud = models.ForeignKey(
        SolicitudModel,
        on_delete=models.CASCADE,
        related_name='eventos',
        verbose_name='Solicitud'
    )
    tipo = models.CharField(
        'Tipo de Evento',
        max_length=50,
        choices=TIPOS_EVENTO,
        db_index=True
    )
    descripcion = models.TextField(
        'Descripción'
    )
    datos_adicionales = models.JSONField(
        'Datos Adicionales',
        default=dict,
        blank=True
    )
    usuario_responsable = models.ForeignKey(
        'usuarios.UsuarioModel',
        on_delete=models.SET_NULL,
        related_name='eventos_generados',
        verbose_name='Usuario Responsable',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'eventos_solicitud'
        verbose_name = 'Evento de Solicitud'
        verbose_name_plural = 'Eventos de Solicitudes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['solicitud', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.tipo} - {self.solicitud.codigo}"
