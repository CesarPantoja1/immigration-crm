"""
Modelos de infraestructura para la característica de Agendamiento de Entrevistas.
"""
from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel


class Entrevista(TimeStampedModel, SoftDeleteModel):
    """
    Modelo de Entrevista asociada a una Solicitud.
    """
    ESTADOS = [
        ('programada', 'Programada'),
        ('reprogramada', 'Reprogramada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    solicitud = models.ForeignKey(
        'recepcion.Solicitud',
        on_delete=models.PROTECT,
        related_name='entrevistas',
        verbose_name='Solicitud'
    )
    fecha = models.DateField(
        'Fecha de Entrevista'
    )
    horario = models.TimeField(
        'Horario de Entrevista'
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADOS,
        default='programada',
        db_index=True
    )
    embajada = models.CharField(
        'Embajada',
        max_length=100
    )
    reprogramaciones = models.IntegerField(
        'Número de Reprogramaciones',
        default=0
    )
    motivo_cancelacion = models.TextField(
        'Motivo de Cancelación',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'entrevistas'
        verbose_name = 'Entrevista'
        verbose_name_plural = 'Entrevistas'
        ordering = ['fecha', 'horario']
        unique_together = [['fecha', 'horario', 'embajada']]

    def __str__(self):
        return f"Entrevista {self.fecha} {self.horario} - {self.estado}"


class HorarioDisponible(TimeStampedModel):
    """
    Modelo para gestionar horarios disponibles por fecha y embajada.
    """
    fecha = models.DateField(
        'Fecha'
    )
    horario = models.TimeField(
        'Horario'
    )
    embajada = models.CharField(
        'Embajada',
        max_length=100
    )
    disponible = models.BooleanField(
        'Disponible',
        default=True,
        db_index=True
    )

    class Meta:
        db_table = 'horarios_disponibles'
        verbose_name = 'Horario Disponible'
        verbose_name_plural = 'Horarios Disponibles'
        ordering = ['fecha', 'horario']
        unique_together = [['fecha', 'horario', 'embajada']]

    def __str__(self):
        return f"{self.fecha} {self.horario} - {'Disponible' if self.disponible else 'Ocupado'}"


class ReglaEmbajada(TimeStampedModel):
    """
    Modelo para gestionar reglas específicas de cada embajada.
    """
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

    class Meta:
        db_table = 'reglas_embajada'
        verbose_name = 'Regla de Embajada'
        verbose_name_plural = 'Reglas de Embajadas'

    def __str__(self):
        return f"{self.embajada} - {self.max_reprogramaciones} reprog. / {self.horas_minimas_cancelacion}h cancel."
