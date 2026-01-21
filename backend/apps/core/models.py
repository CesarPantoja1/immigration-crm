"""
Modelos base compartidos por todas las apps.
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría temporal.
    """
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now,
        editable=False
    )
    updated_at = models.DateTimeField(
        'Fecha de actualización',
        auto_now=True
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto que proporciona funcionalidad de borrado lógico.
    """
    is_deleted = models.BooleanField(
        'Eliminado',
        default=False,
        db_index=True
    )
    deleted_at = models.DateTimeField(
        'Fecha de eliminación',
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca el registro como eliminado."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaura un registro eliminado."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()
