"""
Modelos de infraestructura para la característica de Generación de Recomendaciones.
"""
from django.db import models
from apps.core.models import TimeStampedModel


class DocumentoRecomendaciones(TimeStampedModel):
    """
    Modelo de Documento de Recomendaciones generado por IA.
    """
    NIVELES_PREPARACION = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]

    simulacro = models.OneToOneField(
        'simulacion.Simulacro',
        on_delete=models.CASCADE,
        related_name='documento_recomendaciones',
        verbose_name='Simulacro'
    )
    nivel_preparacion = models.CharField(
        'Nivel de Preparación',
        max_length=10,
        choices=NIVELES_PREPARACION
    )
    fortalezas = models.TextField(
        'Fortalezas',
        help_text='Aspectos positivos identificados'
    )
    puntos_mejora = models.TextField(
        'Puntos de Mejora',
        help_text='Aspectos a mejorar'
    )
    recomendaciones_generales = models.TextField(
        'Recomendaciones Generales'
    )
    accion_sugerida = models.CharField(
        'Acción Sugerida',
        max_length=200,
        help_text='Siguiente paso recomendado'
    )
    fecha_generacion = models.DateTimeField(
        'Fecha de Generación',
        auto_now_add=True
    )
    archivo_pdf = models.FileField(
        'Archivo PDF',
        upload_to='recomendaciones/',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'documentos_recomendaciones'
        verbose_name = 'Documento de Recomendaciones'
        verbose_name_plural = 'Documentos de Recomendaciones'
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"Recomendaciones - Simulacro #{self.simulacro.id} - {self.nivel_preparacion}"


class IndicadorDesempeno(TimeStampedModel):
    """
    Modelo de Indicadores de Desempeño evaluados por la IA.
    """
    VALORES_INDICADOR = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]

    documento = models.ForeignKey(
        DocumentoRecomendaciones,
        on_delete=models.CASCADE,
        related_name='indicadores',
        verbose_name='Documento'
    )
    nombre_indicador = models.CharField(
        'Nombre del Indicador',
        max_length=100,
        help_text='Ej: Claridad en respuestas, Coherencia del discurso, etc.'
    )
    valor = models.CharField(
        'Valor',
        max_length=10,
        choices=VALORES_INDICADOR
    )
    observaciones = models.TextField(
        'Observaciones',
        blank=True
    )

    class Meta:
        db_table = 'indicadores_desempeno'
        verbose_name = 'Indicador de Desempeño'
        verbose_name_plural = 'Indicadores de Desempeño'

    def __str__(self):
        return f"{self.nombre_indicador}: {self.valor}"


class RecomendacionEspecifica(TimeStampedModel):
    """
    Modelo de Recomendación Específica asociada a una pregunta.
    """
    CATEGORIAS = [
        ('claridad', 'Claridad'),
        ('coherencia', 'Coherencia'),
        ('seguridad', 'Seguridad'),
        ('pertinencia', 'Pertinencia'),
    ]

    NIVELES_IMPACTO = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]

    documento = models.ForeignKey(
        DocumentoRecomendaciones,
        on_delete=models.CASCADE,
        related_name='recomendaciones_especificas',
        verbose_name='Documento'
    )
    pregunta_origen = models.ForeignKey(
        'simulacion.PreguntaSimulacro',
        on_delete=models.CASCADE,
        related_name='recomendaciones',
        verbose_name='Pregunta Origen',
        null=True,
        blank=True
    )
    categoria = models.CharField(
        'Categoría',
        max_length=20,
        choices=CATEGORIAS
    )
    descripcion = models.TextField(
        'Descripción de la Recomendación'
    )
    impacto = models.CharField(
        'Nivel de Impacto',
        max_length=10,
        choices=NIVELES_IMPACTO,
        default='medio'
    )

    class Meta:
        db_table = 'recomendaciones_especificas'
        verbose_name = 'Recomendación Específica'
        verbose_name_plural = 'Recomendaciones Específicas'
        ordering = ['-impacto', 'categoria']

    def __str__(self):
        return f"{self.categoria} - {self.impacto} - {self.descripcion[:50]}..."
