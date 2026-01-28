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
    
    # Transcripción en texto para análisis de IA
    transcripcion_texto = models.TextField('Transcripción Texto', blank=True, help_text='Transcripción en texto plano para análisis de IA')
    transcripcion_archivo = models.FileField('Archivo Transcripción', upload_to='simulacros/transcripciones/', null=True, blank=True)
    analisis_ia_completado = models.BooleanField('Análisis IA Completado', default=False)
    analisis_ia_fecha = models.DateTimeField('Fecha Análisis IA', null=True, blank=True)
    
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
    Según feature: generacion_recomendaciones.feature
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
    
    ESTADOS_FEEDBACK = [
        ('pendiente', 'Pendiente'),
        ('generando', 'Generando'),
        ('generado', 'Feedback generado'),
        ('error', 'Error en generación'),
    ]
    
    simulacro = models.OneToOneField(
        Simulacro,
        on_delete=models.CASCADE,
        related_name='recomendacion',
        verbose_name='Simulacro'
    )
    
    # Estado del feedback
    estado_feedback = models.CharField(
        'Estado Feedback',
        max_length=20,
        choices=ESTADOS_FEEDBACK,
        default='pendiente'
    )
    
    # Indicadores de desempeño (según feature escenario 1 y 3)
    claridad = models.CharField('Claridad en respuestas', max_length=20, default='medio')
    coherencia = models.CharField('Coherencia del discurso', max_length=20, default='medio')
    seguridad = models.CharField('Seguridad al responder', max_length=20, default='medio')
    pertinencia = models.CharField('Pertinencia de la información', max_length=20, default='medio')
    
    # Nivel global (según feature escenario 3)
    nivel_preparacion = models.CharField(
        'Nivel de Preparación',
        max_length=20,
        choices=NIVELES_PREPARACION,
        default='medio'
    )
    
    # Contenido estructurado (según feature escenarios 1, 2, 4, 5)
    # Fortalezas: [{categoria, descripcion, pregunta_relacionada, impacto}]
    fortalezas = models.JSONField('Fortalezas', default=list)
    
    # Puntos de mejora: [{categoria, descripcion, pregunta_relacionada, impacto}]
    puntos_mejora = models.JSONField('Puntos de Mejora', default=list)
    
    # Recomendaciones accionables: [{categoria, titulo, descripcion, pregunta_relacionada, impacto, accion_concreta}]
    recomendaciones = models.JSONField('Recomendaciones', default=list)
    
    # Acción sugerida según nivel (según feature escenario 6)
    accion_sugerida = models.TextField('Acción Sugerida', blank=True)
    
    # Resumen ejecutivo generado por IA
    resumen_ejecutivo = models.TextField('Resumen Ejecutivo', blank=True)
    
    # Estado de publicación
    publicada = models.BooleanField('Publicada', default=False)
    fecha_generacion = models.DateTimeField('Fecha de Generación', auto_now_add=True)
    fecha_publicacion = models.DateTimeField('Fecha de Publicación', null=True, blank=True)
    
    # Documento generado (para descarga PDF - según feature escenario 7)
    documento_pdf = models.FileField('Documento PDF', upload_to='recomendaciones/pdf/', null=True, blank=True)
    
    # Metadata del análisis
    analisis_raw = models.JSONField('Análisis Raw IA', default=dict, help_text='Respuesta completa de la IA')
    error_mensaje = models.TextField('Mensaje de Error', blank=True)
    
    class Meta:
        db_table = 'recomendaciones'
        verbose_name = 'Recomendación'
        verbose_name_plural = 'Recomendaciones'
    
    def __str__(self):
        return f"Recomendación - Simulacro #{self.simulacro_id}"
    
    def calcular_nivel_preparacion(self):
        """
        Calcula el nivel de preparación basado en los indicadores.
        Según feature escenario 3:
        - Alto: mayoría de indicadores altos
        - Medio: indicadores mixtos
        - Bajo: mayoría de indicadores bajos
        """
        niveles = {'bajo': 1, 'medio': 2, 'alto': 3}
        indicadores = [self.claridad, self.coherencia, self.seguridad, self.pertinencia]
        promedio = sum(niveles.get(i.lower(), 2) for i in indicadores) / len(indicadores)
        
        if promedio >= 2.5:
            return 'alto'
        elif promedio >= 1.5:
            return 'medio'
        return 'bajo'
    
    def obtener_accion_sugerida(self):
        """
        Obtiene la acción sugerida según el nivel de preparación.
        Según feature escenario 6.
        """
        acciones = {
            'bajo': 'Realizar un nuevo simulacro con asesor',
            'medio': 'Reforzar los puntos de mejora identificados',
            'alto': 'Mantener el plan actual de preparación'
        }
        return acciones.get(self.nivel_preparacion, acciones['medio'])
    
    def organizar_por_impacto(self):
        """
        Organiza las recomendaciones por nivel de impacto.
        Según feature escenario 5.
        """
        resultado = {'alto': [], 'medio': [], 'bajo': []}
        for rec in self.recomendaciones:
            impacto = rec.get('impacto', 'medio').lower()
            if impacto in resultado:
                resultado[impacto].append(rec)
        return resultado


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


class ConfiguracionIA(TimeStampedModel):
    """
    Configuración de IA para cada asesor.
    Permite a cada asesor usar su propia API key y modelo de Gemini.
    """
    
    MODELOS_GEMINI = [
        ('gemini-2.5-pro', 'Gemini 2.5 Pro (Mayor precisión)'),
        ('gemini-2.5-flash', 'Gemini 2.5 Flash (Más rápido)'),
        ('gemini-2.0-flash', 'Gemini 2.0 Flash'),
        ('gemini-2.5-flash-lite', 'Gemini 2.5 Flash Lite (Económico)'),
    ]
    
    asesor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='configuracion_ia',
        limit_choices_to={'rol__in': ['asesor', 'admin']},
        verbose_name='Asesor'
    )
    
    api_key = models.CharField(
        'API Key de Gemini',
        max_length=100,
        help_text='Tu API key de Google AI Studio'
    )
    
    modelo = models.CharField(
        'Modelo de IA',
        max_length=50,
        choices=MODELOS_GEMINI,
        default='gemini-2.5-flash',
        help_text='Modelo de Gemini a utilizar'
    )
    
    activo = models.BooleanField(
        'Configuración Activa',
        default=True
    )
    
    # Estadísticas de uso
    total_analisis = models.PositiveIntegerField('Total Análisis Realizados', default=0)
    ultimo_uso = models.DateTimeField('Último Uso', null=True, blank=True)
    
    class Meta:
        db_table = 'configuracion_ia'
        verbose_name = 'Configuración de IA'
        verbose_name_plural = 'Configuraciones de IA'
    
    def __str__(self):
        return f"Config IA - {self.asesor} ({self.modelo})"
    
    def incrementar_uso(self):
        """Incrementa el contador de uso y actualiza fecha."""
        from django.utils import timezone
        self.total_analisis += 1
        self.ultimo_uso = timezone.now()
        self.save(update_fields=['total_analisis', 'ultimo_uso'])
    
    def get_api_url(self):
        """Obtiene la URL de la API según el modelo seleccionado."""
        return f"https://generativelanguage.googleapis.com/v1beta/models/{self.modelo}:generateContent"
