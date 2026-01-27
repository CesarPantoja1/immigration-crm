"""
Modelos de infraestructura para la característica de Agendamiento de Entrevistas.
Considera que la embajada es un actor externo que asigna las citas.
"""
from django.db import models
from django.utils import timezone
import uuid


class EntrevistaModel(models.Model):
    """
    Modelo de Entrevista asociada a una Solicitud.
    La embajada asigna la cita (fecha fija u opciones).
    """
    ESTADOS = [
        ('PENDIENTE_ASIGNACION', 'Pendiente de Asignación'),
        ('AGENDADA', 'Agendada'),
        ('OPCIONES_DISPONIBLES', 'Opciones Disponibles'),
        ('CONFIRMADA', 'Confirmada'),
        ('REPROGRAMADA', 'Reprogramada'),
        ('CANCELADA', 'Cancelada'),
        ('COMPLETADA', 'Completada'),
        ('NO_ASISTIO', 'No Asistió'),
    ]
    
    MODOS_ASIGNACION = [
        ('FECHA_FIJA', 'Fecha Fija'),
        ('OPCIONES_ELEGIR', 'Opciones para Elegir'),
    ]
    
    MOTIVOS_CANCELACION = [
        ('SOLICITUD_MIGRANTE', 'Solicitud del Migrante'),
        ('REPROGRAMACION_EMBAJADA', 'Reprogramación de Embajada'),
        ('DOCUMENTOS_INCOMPLETOS', 'Documentos Incompletos'),
        ('EMERGENCIA', 'Emergencia'),
        ('OTRO', 'Otro'),
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
        blank=True
    )
    solicitud = models.ForeignKey(
        'recepcion.SolicitudModel',
        on_delete=models.PROTECT,
        related_name='entrevistas',
        verbose_name='Solicitud'
    )
    embajada = models.CharField(
        'Embajada',
        max_length=100,
        db_index=True
    )
    estado = models.CharField(
        'Estado',
        max_length=30,
        choices=ESTADOS,
        default='PENDIENTE_ASIGNACION',
        db_index=True
    )
    modo_asignacion = models.CharField(
        'Modo de Asignación',
        max_length=20,
        choices=MODOS_ASIGNACION,
        blank=True,
        null=True
    )
    
    # Horario asignado
    fecha = models.DateField(
        'Fecha de Entrevista',
        blank=True,
        null=True
    )
    hora = models.TimeField(
        'Hora de Entrevista',
        blank=True,
        null=True
    )
    ubicacion = models.CharField(
        'Ubicación',
        max_length=255,
        blank=True,
        default=''
    )
    notas = models.TextField(
        'Notas',
        blank=True,
        default=''
    )
    
    # Control de reprogramaciones
    veces_reprogramada = models.IntegerField(
        'Veces Reprogramada',
        default=0
    )
    
    # Cancelación
    cancelada = models.BooleanField(
        'Cancelada',
        default=False
    )
    motivo_cancelacion = models.CharField(
        'Motivo de Cancelación',
        max_length=30,
        choices=MOTIVOS_CANCELACION,
        blank=True,
        null=True
    )
    detalle_cancelacion = models.TextField(
        'Detalle de Cancelación',
        blank=True,
        default=''
    )
    
    # Fechas de auditoría
    fecha_creacion = models.DateTimeField(
        'Fecha de Creación',
        auto_now_add=True
    )
    fecha_actualizacion = models.DateTimeField(
        'Fecha de Actualización',
        auto_now=True
    )
    fecha_confirmacion = models.DateTimeField(
        'Fecha de Confirmación',
        blank=True,
        null=True
    )
    fecha_completada = models.DateTimeField(
        'Fecha Completada',
        blank=True,
        null=True
    )
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código único: ENT-YYYYMMDD-XXXX
            fecha_str = timezone.now().strftime('%Y%m%d')
            ultimo = EntrevistaModel.objects.filter(
                codigo__startswith=f'ENT-{fecha_str}'
            ).count()
            self.codigo = f'ENT-{fecha_str}-{str(ultimo + 1).zfill(4)}'
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'entrevistas'
        verbose_name = 'Entrevista'
        verbose_name_plural = 'Entrevistas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        fecha_str = self.fecha.strftime('%d/%m/%Y') if self.fecha else 'Sin fecha'
        hora_str = self.hora.strftime('%H:%M') if self.hora else ''
        return f"Entrevista {self.codigo} - {fecha_str} {hora_str} - {self.estado}"


class OpcionHorarioModel(models.Model):
    """
    Modelo para opciones de horario ofrecidas por la embajada.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    entrevista = models.ForeignKey(
        EntrevistaModel,
        on_delete=models.CASCADE,
        related_name='opciones_horario',
        verbose_name='Entrevista'
    )
    fecha = models.DateField('Fecha')
    hora = models.TimeField('Hora')
    disponible = models.BooleanField('Disponible', default=True)
    seleccionada = models.BooleanField('Seleccionada', default=False)
    
    class Meta:
        db_table = 'opciones_horario_entrevista'
        verbose_name = 'Opción de Horario'
        verbose_name_plural = 'Opciones de Horario'
        ordering = ['fecha', 'hora']

    def __str__(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.fecha} {self.hora} - {estado}"


class HistorialHorarioModel(models.Model):
    """
    Modelo para historial de horarios de entrevista (reprogramaciones).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    entrevista = models.ForeignKey(
        EntrevistaModel,
        on_delete=models.CASCADE,
        related_name='historial_horarios',
        verbose_name='Entrevista'
    )
    fecha = models.DateField('Fecha')
    hora = models.TimeField('Hora')
    fecha_registro = models.DateTimeField('Fecha de Registro', auto_now_add=True)
    motivo_cambio = models.CharField('Motivo del Cambio', max_length=255, blank=True)
    
    class Meta:
        db_table = 'historial_horarios_entrevista'
        verbose_name = 'Historial de Horario'
        verbose_name_plural = 'Historial de Horarios'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.entrevista.codigo} - {self.fecha} {self.hora}"


class RespuestaEmbajadaModel(models.Model):
    """
    Modelo para respuestas recibidas de la embajada.
    """
    TIPOS_RESPUESTA = [
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    solicitud = models.ForeignKey(
        'recepcion.SolicitudModel',
        on_delete=models.PROTECT,
        related_name='respuestas_embajada',
        verbose_name='Solicitud'
    )
    tipo_respuesta = models.CharField(
        'Tipo de Respuesta',
        max_length=20,
        choices=TIPOS_RESPUESTA
    )
    fecha_respuesta = models.DateTimeField(
        'Fecha de Respuesta',
        auto_now_add=True
    )
    motivo_rechazo = models.TextField(
        'Motivo de Rechazo',
        blank=True,
        default=''
    )
    puede_apelar = models.BooleanField(
        'Puede Apelar',
        default=False
    )
    mensaje = models.TextField(
        'Mensaje',
        blank=True,
        default=''
    )
    entrevista = models.ForeignKey(
        EntrevistaModel,
        on_delete=models.SET_NULL,
        related_name='respuestas',
        verbose_name='Entrevista Asociada',
        blank=True,
        null=True
    )
    
    class Meta:
        db_table = 'respuestas_embajada'
        verbose_name = 'Respuesta de Embajada'
        verbose_name_plural = 'Respuestas de Embajada'
        ordering = ['-fecha_respuesta']

    def __str__(self):
        return f"Respuesta {self.tipo_respuesta} - {self.solicitud}"


class HorarioDisponibleModel(models.Model):
    """
    Modelo para gestionar horarios disponibles por fecha y embajada.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    fecha = models.DateField('Fecha')
    hora = models.TimeField('Hora')
    embajada = models.CharField('Embajada', max_length=100, db_index=True)
    disponible = models.BooleanField('Disponible', default=True, db_index=True)
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)

    class Meta:
        db_table = 'horarios_disponibles'
        verbose_name = 'Horario Disponible'
        verbose_name_plural = 'Horarios Disponibles'
        ordering = ['fecha', 'hora']
        unique_together = [['fecha', 'hora', 'embajada']]

    def __str__(self):
        return f"{self.fecha} {self.hora} - {'Disponible' if self.disponible else 'Ocupado'}"


class ReglaEmbajadaModel(models.Model):
    """
    Modelo para gestionar reglas específicas de cada embajada.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    embajada = models.CharField(
        'Embajada',
        max_length=100,
        unique=True,
        db_index=True
    )
    max_reprogramaciones = models.IntegerField(
        'Máximo de Reprogramaciones',
        default=2
    )
    horas_minimas_cancelacion = models.IntegerField(
        'Horas Mínimas para Cancelación',
        default=24,
        help_text='Horas mínimas de anticipación para cancelar una entrevista'
    )
    dias_minimos_anticipacion = models.IntegerField(
        'Días Mínimos de Anticipación',
        default=7,
        help_text='Días mínimos de anticipación para programar una entrevista'
    )
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de Actualización', auto_now=True)

    class Meta:
        db_table = 'reglas_embajada'
        verbose_name = 'Regla de Embajada'
        verbose_name_plural = 'Reglas de Embajadas'

    def __str__(self):
        return f"{self.embajada} - {self.max_reprogramaciones} reprog. / {self.horas_minimas_cancelacion}h cancel."
