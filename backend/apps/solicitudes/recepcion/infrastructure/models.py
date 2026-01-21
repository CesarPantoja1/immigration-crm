"""
Modelos de infraestructura para la característica de Recepción de Solicitudes.
"""
from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel


class Solicitud(TimeStampedModel, SoftDeleteModel):
    """
    Modelo de Solicitud Migratoria.
    """
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    solicitante = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name='Solicitante'
    )
    tipo_tramite = models.CharField(
        'Tipo de Trámite',
        max_length=100
    )
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=ESTADOS,
        default='borrador',
        db_index=True
    )
    datos_personales = models.JSONField(
        'Datos Personales',
        default=dict
    )
    documentos_adjuntos = models.JSONField(
        'Documentos Adjuntos',
        default=list
    )
    observaciones = models.TextField(
        'Observaciones',
        blank=True
    )

    class Meta:
        db_table = 'solicitudes'
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Solicitud #{self.id} - {self.solicitante} - {self.estado}"
