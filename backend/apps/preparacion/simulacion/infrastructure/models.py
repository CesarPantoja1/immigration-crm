"""
Modelos de infraestructura para la característica de Simulación de Entrevistas.
"""
from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel


class Simulacro(TimeStampedModel, SoftDeleteModel):
    """
    Modelo de Simulacro de Entrevista.
    """
    MODALIDADES = [
        ('virtual', 'Virtual'),
        ('presencial', 'Presencial'),
    ]

    ESTADOS = [
        ('agendado', 'Agendado'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('pendiente_feedback', 'Pendiente de Feedback'),
        ('cancelado', 'Cancelado'),
    ]

    entrevista = models.ForeignKey(
        'solicitudes.Entrevista',
        on_delete=models.PROTECT,
        related_name='simulacros',
        verbose_name='Entrevista'
    )
    asesor = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='simulacros_asignados',
        verbose_name='Asesor'
    )
    fecha_simulacro = models.DateTimeField(
        'Fecha del Simulacro'
    )
    modalidad = models.CharField(
        'Modalidad',
        max_length=20,
        choices=MODALIDADES
    )
    tipo_visado = models.CharField(
        'Tipo de Visado',
        max_length=50,
        help_text='Vivienda, Estudiante, Trabajo, Turismo, etc.'
    )
    estado = models.CharField(
        'Estado',
        max_length=30,
        choices=ESTADOS,
        default='agendado',
        db_index=True
    )
    transcripcion = models.TextField(
        'Transcripción',
        blank=True,
        null=True,
        help_text='Transcripción de preguntas y respuestas del simulacro'
    )
    duracion_minutos = models.IntegerField(
        'Duración en Minutos',
        null=True,
        blank=True
    )
    numero_intento = models.IntegerField(
        'Número de Intento',
        default=1,
        help_text='Máximo 2 simulacros permitidos'
    )

    class Meta:
        db_table = 'simulacros'
        verbose_name = 'Simulacro'
        verbose_name_plural = 'Simulacros'
        ordering = ['-fecha_simulacro']

    def __str__(self):
        return f"Simulacro #{self.id} - {self.tipo_visado} - {self.estado}"


class PreguntaSimulacro(TimeStampedModel):
    """
    Modelo de Pregunta dentro de un Simulacro.
    """
    TIPOS_PREGUNTA = [
        ('motivo_viaje', 'Motivo del Viaje'),
        ('situacion_economica', 'Situación Económica'),
        ('planes_permanencia', 'Planes de Permanencia'),
        ('financiacion_universidad', 'Financiación y Universidad'),
        ('lazos_familiares', 'Lazos Familiares'),
    ]

    simulacro = models.ForeignKey(
        Simulacro,
        on_delete=models.CASCADE,
        related_name='preguntas',
        verbose_name='Simulacro'
    )
    numero_pregunta = models.IntegerField(
        'Número de Pregunta'
    )
    tipo_pregunta = models.CharField(
        'Tipo de Pregunta',
        max_length=50,
        choices=TIPOS_PREGUNTA
    )
    texto_pregunta = models.TextField(
        'Texto de la Pregunta'
    )
    respuesta_migrante = models.TextField(
        'Respuesta del Migrante',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'preguntas_simulacro'
        verbose_name = 'Pregunta de Simulacro'
        verbose_name_plural = 'Preguntas de Simulacro'
        ordering = ['simulacro', 'numero_pregunta']
        unique_together = [['simulacro', 'numero_pregunta']]

    def __str__(self):
        return f"Pregunta {self.numero_pregunta} - {self.tipo_pregunta}"


class CuestionarioPractica(TimeStampedModel):
    """
    Modelo de Cuestionario de Auto-Práctica.
    """
    tipo_visado = models.CharField(
        'Tipo de Visado',
        max_length=50
    )
    titulo = models.CharField(
        'Título',
        max_length=200
    )
    descripcion = models.TextField(
        'Descripción',
        blank=True
    )
    activo = models.BooleanField(
        'Activo',
        default=True,
        db_index=True
    )

    class Meta:
        db_table = 'cuestionarios_practica'
        verbose_name = 'Cuestionario de Práctica'
        verbose_name_plural = 'Cuestionarios de Práctica'

    def __str__(self):
        return f"{self.tipo_visado} - {self.titulo}"


class PreguntaPractica(TimeStampedModel):
    """
    Modelo de Pregunta de Auto-Práctica (con 4 opciones).
    """
    cuestionario = models.ForeignKey(
        CuestionarioPractica,
        on_delete=models.CASCADE,
        related_name='preguntas',
        verbose_name='Cuestionario'
    )
    texto_pregunta = models.TextField(
        'Texto de la Pregunta'
    )
    opcion_a = models.CharField('Opción A', max_length=500)
    opcion_b = models.CharField('Opción B', max_length=500)
    opcion_c = models.CharField('Opción C', max_length=500)
    opcion_d = models.CharField('Opción D', max_length=500)
    respuesta_correcta = models.CharField(
        'Respuesta Correcta',
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    explicacion = models.TextField(
        'Explicación',
        blank=True,
        help_text='Explicación de por qué es la respuesta correcta'
    )

    class Meta:
        db_table = 'preguntas_practica'
        verbose_name = 'Pregunta de Práctica'
        verbose_name_plural = 'Preguntas de Práctica'

    def __str__(self):
        return f"{self.cuestionario.tipo_visado} - {self.texto_pregunta[:50]}..."
