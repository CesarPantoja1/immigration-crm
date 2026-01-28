"""
Modelos para el módulo de Preparación (Simulacros).
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel, SoftDeleteModel


class Simulacro(TimeStampedModel, SoftDeleteModel):
    """
    Modelo de Simulacro de Entrevista Consular.
    """
    
    ESTADOS = [
        ('solicitado', 'Solicitado'),
        ('propuesto', 'Propuesto'),
        ('pendiente_respuesta', 'Pendiente de Respuesta'),
        ('contrapropuesta', 'Contrapropuesta Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_sala_espera', 'En Sala de Espera'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('no_asistio', 'No Asistió'),
    ]
    
    MODALIDADES = [
        ('virtual', 'Virtual'),
        ('presencial', 'Presencial'),
    ]
    
    # Relaciones
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='simulacros_como_cliente',
        limit_choices_to={'rol': 'cliente'},
        verbose_name='Cliente'
    )
    asesor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='simulacros_como_asesor',
        limit_choices_to={'rol': 'asesor'},
        null=True,
        blank=True,
        verbose_name='Asesor'
    )
    solicitud = models.ForeignKey(
        'solicitudes.Solicitud',
        on_delete=models.CASCADE,
        related_name='simulacros',
        null=True,
        blank=True,
        verbose_name='Solicitud Asociada'
    )
    
    # Datos del simulacro
    fecha = models.DateField('Fecha')
    hora = models.TimeField('Hora')
    modalidad = models.CharField(
        'Modalidad',
        max_length=20,
        choices=MODALIDADES,
        default='virtual'
    )
    estado = models.CharField(
        'Estado',
        max_length=30,
        choices=ESTADOS,
        default='propuesto',
        db_index=True
    )
    
    # Para contrapropuestas
    fecha_propuesta = models.DateField('Fecha Propuesta', null=True, blank=True)
    hora_propuesta = models.TimeField('Hora Propuesta', null=True, blank=True)
    
    # Datos de la sesión
    fecha_inicio = models.DateTimeField('Inicio de Sesión', null=True, blank=True)
    fecha_fin = models.DateTimeField('Fin de Sesión', null=True, blank=True)
    duracion_minutos = models.PositiveIntegerField('Duración (minutos)', default=0)
    
    # Grabación y transcripción
    grabacion_activa = models.BooleanField('Grabación Activa', default=False)
    url_grabacion = models.URLField('URL Grabación', blank=True)
    transcripcion = models.JSONField('Transcripción', default=list)
    
    # Ubicación para presenciales
    ubicacion = models.CharField('Ubicación', max_length=200, blank=True)
    
    # Notas
    notas = models.TextField('Notas', blank=True)
    motivo_cancelacion = models.TextField('Motivo de Cancelación', blank=True)
    
    class Meta:
        db_table = 'simulacros'
        verbose_name = 'Simulacro'
        verbose_name_plural = 'Simulacros'
        ordering = ['-fecha', '-hora']
    
    def __str__(self):
        return f"Simulacro #{self.id} - {self.cliente} - {self.fecha}"
    
    def puede_cancelar(self, horas_anticipacion=24):
        """Verifica si el simulacro puede ser cancelado."""
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        if self.estado in ['cancelado', 'completado', 'no_asistio']:
            return False
        
        fecha_simulacro = datetime.combine(self.fecha, self.hora)
        fecha_simulacro = timezone.make_aware(fecha_simulacro)
        tiempo_restante = fecha_simulacro - timezone.now()
        
        return tiempo_restante >= timedelta(hours=horas_anticipacion)
    
    def puede_ingresar_sala(self, minutos_anticipacion=15):
        """Verifica si el cliente puede ingresar a la sala de espera."""
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        if self.estado not in ['confirmado']:
            return False
        
        fecha_simulacro = datetime.combine(self.fecha, self.hora)
        fecha_simulacro = timezone.make_aware(fecha_simulacro)
        tiempo_restante = fecha_simulacro - timezone.now()
        
        return timedelta(0) <= tiempo_restante <= timedelta(minutes=minutos_anticipacion)


class Recomendacion(TimeStampedModel):
    """
    Modelo de Recomendaciones generadas por IA.
    """
    
    NIVELES_PREPARACION = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]
    
    NIVELES_IMPACTO = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]
    
    simulacro = models.OneToOneField(
        Simulacro,
        on_delete=models.CASCADE,
        related_name='recomendacion',
        verbose_name='Simulacro'
    )
    
    # Indicadores de desempeño
    claridad = models.CharField('Claridad', max_length=20, default='medio')
    coherencia = models.CharField('Coherencia', max_length=20, default='medio')
    seguridad = models.CharField('Seguridad', max_length=20, default='medio')
    pertinencia = models.CharField('Pertinencia', max_length=20, default='medio')
    
    # Nivel global
    nivel_preparacion = models.CharField(
        'Nivel de Preparación',
        max_length=20,
        choices=NIVELES_PREPARACION,
        default='medio'
    )
    
    # Contenido
    fortalezas = models.JSONField('Fortalezas', default=list)
    puntos_mejora = models.JSONField('Puntos de Mejora', default=list)
    recomendaciones = models.JSONField('Recomendaciones', default=list)
    accion_sugerida = models.TextField('Acción Sugerida', blank=True)
    
    # Estado
    publicada = models.BooleanField('Publicada', default=False)
    fecha_generacion = models.DateTimeField('Fecha de Generación', auto_now_add=True)
    
    class Meta:
        db_table = 'recomendaciones'
        verbose_name = 'Recomendación'
        verbose_name_plural = 'Recomendaciones'
    
    def __str__(self):
        return f"Recomendación - Simulacro #{self.simulacro_id}"
    
    def calcular_nivel_preparacion(self):
        """Calcula el nivel de preparación basado en los indicadores."""
        niveles = {'bajo': 1, 'medio': 2, 'alto': 3}
        indicadores = [self.claridad, self.coherencia, self.seguridad, self.pertinencia]
        promedio = sum(niveles.get(i, 2) for i in indicadores) / len(indicadores)
        
        if promedio >= 2.5:
            return 'alto'
        elif promedio >= 1.5:
            return 'medio'
        return 'bajo'


class Practica(TimeStampedModel):
    """
    Modelo de Práctica Individual (Cuestionarios).
    """
    
    TIPOS_VISA = [
        ('estudio', 'Visa de Estudio'),
        ('trabajo', 'Visa de Trabajo'),
        ('vivienda', 'Visa de Vivienda'),
    ]
    
    CALIFICACIONES = [
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('insuficiente', 'Insuficiente'),
    ]
    
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practicas',
        verbose_name='Cliente'
    )
    
    tipo_visa = models.CharField(
        'Tipo de Visa',
        max_length=20,
        choices=TIPOS_VISA
    )
    
    # Resultados
    total_preguntas = models.PositiveIntegerField('Total Preguntas', default=10)
    respuestas_correctas = models.PositiveIntegerField('Respuestas Correctas', default=0)
    porcentaje = models.PositiveIntegerField('Porcentaje', default=0)
    calificacion = models.CharField(
        'Calificación',
        max_length=20,
        choices=CALIFICACIONES,
        blank=True
    )
    
    # Detalle
    respuestas = models.JSONField('Respuestas', default=list)
    completado = models.BooleanField('Completado', default=False)
    fecha_completado = models.DateTimeField('Fecha Completado', null=True, blank=True)
    
    class Meta:
        db_table = 'practicas'
        verbose_name = 'Práctica'
        verbose_name_plural = 'Prácticas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Práctica {self.tipo_visa} - {self.cliente}"
    
    def calcular_resultado(self):
        """Calcula el porcentaje y calificación."""
        if self.total_preguntas > 0:
            self.porcentaje = int((self.respuestas_correctas / self.total_preguntas) * 100)
        
        if self.porcentaje >= 90:
            self.calificacion = 'excelente'
        elif self.porcentaje >= 70:
            self.calificacion = 'bueno'
        elif self.porcentaje >= 50:
            self.calificacion = 'regular'
        else:
            self.calificacion = 'insuficiente'
        
        self.save()
