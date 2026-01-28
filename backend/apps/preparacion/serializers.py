"""
Serializers para el módulo de Preparación (Simulacros).
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Simulacro, Recomendacion, Practica, ConfiguracionIA

Usuario = get_user_model()


class SimulacroListSerializer(serializers.ModelSerializer):
    """Serializer para listar simulacros."""
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    modalidad_display = serializers.CharField(source='get_modalidad_display', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    asesor_nombre = serializers.SerializerMethodField()
    puede_cancelar = serializers.SerializerMethodField()
    puede_ingresar = serializers.SerializerMethodField()
    fecha_propuesta = serializers.SerializerMethodField()
    hora_propuesta = serializers.SerializerMethodField()
    solicitud_tipo = serializers.SerializerMethodField()
    solicitud_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Simulacro
        fields = [
            'id', 'fecha', 'hora', 'modalidad', 'modalidad_display',
            'estado', 'estado_display', 'cliente_nombre', 'asesor_nombre',
            'ubicacion', 'puede_cancelar', 'puede_ingresar', 'created_at',
            'fecha_propuesta', 'hora_propuesta', 'solicitud_tipo', 'solicitud_id'
        ]
    
    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre_completo() if obj.cliente else None
    
    def get_asesor_nombre(self, obj):
        return obj.asesor.nombre_completo() if obj.asesor else None
    
    def get_puede_cancelar(self, obj):
        return obj.puede_cancelar()
    
    def get_puede_ingresar(self, obj):
        return obj.puede_ingresar_sala()
    
    def get_fecha_propuesta(self, obj):
        # Devolver fecha_propuesta si existe, sino fecha
        return str(obj.fecha_propuesta) if obj.fecha_propuesta else str(obj.fecha)
    
    def get_hora_propuesta(self, obj):
        # Devolver hora_propuesta si existe, sino hora
        return str(obj.hora_propuesta) if obj.hora_propuesta else str(obj.hora)
    
    def get_solicitud_tipo(self, obj):
        if obj.solicitud:
            return obj.solicitud.get_tipo_visa_display()
        return 'Visa'
    
    def get_solicitud_id(self, obj):
        return obj.solicitud_id if obj.solicitud_id else None


class SimulacroDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de simulacro."""
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    modalidad_display = serializers.CharField(source='get_modalidad_display', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    asesor_nombre = serializers.SerializerMethodField()
    tiene_recomendacion = serializers.SerializerMethodField()
    tiene_recomendaciones = serializers.SerializerMethodField()  # Alias
    solicitud_tipo = serializers.SerializerMethodField()
    recomendacion = serializers.SerializerMethodField()
    transcripcion_texto = serializers.CharField(read_only=True)
    
    class Meta:
        model = Simulacro
        fields = [
            'id', 'fecha', 'hora', 'modalidad', 'modalidad_display',
            'estado', 'estado_display', 'cliente', 'cliente_nombre',
            'asesor', 'asesor_nombre', 'solicitud', 'solicitud_tipo', 'ubicacion',
            'fecha_propuesta', 'hora_propuesta', 'fecha_inicio', 'fecha_fin',
            'duracion_minutos', 'grabacion_activa', 'notas',
            'tiene_recomendacion', 'tiene_recomendaciones', 'recomendacion',
            'transcripcion_texto', 'created_at', 'updated_at'
        ]
    
    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre_completo() if obj.cliente else None
    
    def get_asesor_nombre(self, obj):
        return obj.asesor.nombre_completo() if obj.asesor else None
    
    def get_tiene_recomendacion(self, obj):
        return hasattr(obj, 'recomendacion')
    
    def get_tiene_recomendaciones(self, obj):
        return hasattr(obj, 'recomendacion')
    
    def get_solicitud_tipo(self, obj):
        if obj.solicitud:
            return obj.solicitud.get_tipo_visa_display()
        return 'Visa'
    
    def get_recomendacion(self, obj):
        """Incluye la recomendación completa si existe."""
        if hasattr(obj, 'recomendacion'):
            rec = obj.recomendacion
            return {
                'id': rec.id,
                'nivel_preparacion': rec.nivel_preparacion,
                'claridad': rec.claridad,
                'coherencia': rec.coherencia,
                'seguridad': rec.seguridad,
                'pertinencia': rec.pertinencia,
                'fortalezas': rec.fortalezas or [],
                'puntos_mejora': rec.puntos_mejora or [],
                'recomendaciones': rec.recomendaciones or [],
                'resumen_ejecutivo': rec.resumen_ejecutivo,
                'accion_sugerida': rec.accion_sugerida,
                'estado_feedback': rec.estado_feedback,
                'publicada': rec.publicada,
                'fecha_publicacion': rec.fecha_publicacion,
                'analisis_raw': rec.analisis_raw
            }
        return None


class SimulacroCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear propuesta de simulacro."""
    cliente_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Simulacro
        fields = ['cliente_id', 'fecha', 'hora', 'modalidad', 'ubicacion', 'solicitud']
    
    def create(self, validated_data):
        cliente_id = validated_data.pop('cliente_id')
        cliente = Usuario.objects.get(id=cliente_id, rol='cliente')
        
        request = self.context.get('request')
        asesor = request.user if request.user.rol == 'asesor' else None
        
        simulacro = Simulacro.objects.create(
            cliente=cliente,
            asesor=asesor,
            estado='pendiente_respuesta',
            **validated_data
        )
        
        # Notificar al cliente sobre la propuesta
        try:
            from apps.notificaciones.services import notificacion_service
            notificacion_service.notificar_simulacro_propuesto(simulacro, propuesto_por='asesor')
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error creando notificación: {e}")
        
        return simulacro


class RecomendacionSerializer(serializers.ModelSerializer):
    """Serializer para recomendaciones."""
    nivel_preparacion_display = serializers.CharField(
        source='get_nivel_preparacion_display', read_only=True
    )
    simulacro_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Recomendacion
        fields = [
            'id', 'simulacro', 'simulacro_info',
            'claridad', 'coherencia', 'seguridad', 'pertinencia',
            'nivel_preparacion', 'nivel_preparacion_display',
            'fortalezas', 'puntos_mejora', 'recomendaciones',
            'accion_sugerida', 'publicada', 'fecha_generacion'
        ]
    
    def get_simulacro_info(self, obj):
        return {
            'id': obj.simulacro.id,
            'fecha': obj.simulacro.fecha,
            'modalidad': obj.simulacro.modalidad
        }


class PracticaListSerializer(serializers.ModelSerializer):
    """Serializer para listar prácticas."""
    tipo_visa_display = serializers.CharField(source='get_tipo_visa_display', read_only=True)
    calificacion_display = serializers.CharField(source='get_calificacion_display', read_only=True)
    
    class Meta:
        model = Practica
        fields = [
            'id', 'tipo_visa', 'tipo_visa_display',
            'total_preguntas', 'respuestas_correctas', 'porcentaje',
            'calificacion', 'calificacion_display', 'completado',
            'fecha_completado', 'created_at'
        ]


class PracticaDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de práctica."""
    tipo_visa_display = serializers.CharField(source='get_tipo_visa_display', read_only=True)
    calificacion_display = serializers.CharField(source='get_calificacion_display', read_only=True)
    
    class Meta:
        model = Practica
        fields = [
            'id', 'tipo_visa', 'tipo_visa_display',
            'total_preguntas', 'respuestas_correctas', 'porcentaje',
            'calificacion', 'calificacion_display', 'respuestas',
            'completado', 'fecha_completado', 'created_at'
        ]


class SimulacroCompletadoSerializer(serializers.ModelSerializer):
    """Serializer para simulacros completados (para asesor)."""
    cliente_nombre = serializers.SerializerMethodField()
    tiene_transcripcion = serializers.SerializerMethodField()
    tiene_recomendacion = serializers.SerializerMethodField()
    estado_feedback = serializers.SerializerMethodField()
    solicitud_tipo = serializers.SerializerMethodField()
    solicitud_id = serializers.SerializerMethodField()
    recomendacion_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Simulacro
        fields = [
            'id', 'fecha', 'hora', 'cliente_nombre', 'solicitud_tipo', 'solicitud_id',
            'tiene_transcripcion', 'tiene_recomendacion', 'estado_feedback',
            'analisis_ia_completado', 'fecha_fin', 'created_at', 'recomendacion_id'
        ]
    
    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre_completo() if obj.cliente else None
    
    def get_tiene_transcripcion(self, obj):
        return bool(obj.transcripcion_texto or obj.transcripcion_archivo)
    
    def get_tiene_recomendacion(self, obj):
        return hasattr(obj, 'recomendacion')
    
    def get_estado_feedback(self, obj):
        if hasattr(obj, 'recomendacion'):
            return obj.recomendacion.estado_feedback
        return 'pendiente'
    
    def get_solicitud_tipo(self, obj):
        if obj.solicitud:
            return obj.solicitud.get_tipo_visa_display()
        return 'Visa'
    
    def get_solicitud_id(self, obj):
        return obj.solicitud_id if obj.solicitud_id else None
    
    def get_recomendacion_id(self, obj):
        if hasattr(obj, 'recomendacion'):
            return obj.recomendacion.id
        return None


class RecomendacionIASerializer(serializers.ModelSerializer):
    """Serializer para recomendaciones con IA (vista completa)."""
    nivel_preparacion_display = serializers.CharField(
        source='get_nivel_preparacion_display', read_only=True
    )
    simulacro_info = serializers.SerializerMethodField()
    indicadores = serializers.SerializerMethodField()
    
    class Meta:
        model = Recomendacion
        fields = [
            'id', 'simulacro', 'simulacro_info',
            'indicadores', 'claridad', 'coherencia', 'seguridad', 'pertinencia',
            'nivel_preparacion', 'nivel_preparacion_display',
            'fortalezas', 'puntos_mejora', 'recomendaciones',
            'accion_sugerida', 'resumen_ejecutivo', 'estado_feedback',
            'documento_pdf', 'error_mensaje',
            'publicada', 'fecha_generacion', 'fecha_publicacion'
        ]
    
    def get_simulacro_info(self, obj):
        return {
            'id': obj.simulacro.id,
            'fecha': obj.simulacro.fecha,
            'modalidad': obj.simulacro.modalidad,
            'cliente_nombre': obj.simulacro.cliente.nombre_completo() if obj.simulacro.cliente else None
        }
    
    def get_indicadores(self, obj):
        return {
            'claridad': obj.claridad,
            'coherencia': obj.coherencia,
            'seguridad': obj.seguridad,
            'pertinencia': obj.pertinencia
        }


class RecomendacionClienteSerializer(serializers.ModelSerializer):
    """Serializer para que el cliente vea sus recomendaciones."""
    nivel_preparacion_display = serializers.CharField(
        source='get_nivel_preparacion_display', read_only=True
    )
    indicadores = serializers.SerializerMethodField()
    fecha_simulacro = serializers.SerializerMethodField()
    asesor_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Recomendacion
        fields = [
            'id', 'fecha_simulacro', 'asesor_nombre',
            'indicadores', 'nivel_preparacion', 'nivel_preparacion_display',
            'fortalezas', 'puntos_mejora', 'recomendaciones',
            'accion_sugerida', 'resumen_ejecutivo', 'documento_pdf',
            'publicada', 'fecha_publicacion'
        ]
    
    def get_indicadores(self, obj):
        return {
            'claridad': {'valor': obj.claridad, 'descripcion': self._get_descripcion_indicador(obj.claridad)},
            'coherencia': {'valor': obj.coherencia, 'descripcion': self._get_descripcion_indicador(obj.coherencia)},
            'seguridad': {'valor': obj.seguridad, 'descripcion': self._get_descripcion_indicador(obj.seguridad)},
            'pertinencia': {'valor': obj.pertinencia, 'descripcion': self._get_descripcion_indicador(obj.pertinencia)}
        }
    
    def _get_descripcion_indicador(self, valor):
        descripciones = {
            'bajo': 'Necesita mejorar',
            'medio': 'Aceptable',
            'alto': 'Excelente'
        }
        return descripciones.get(valor, 'No evaluado')
    
    def get_fecha_simulacro(self, obj):
        return obj.simulacro.fecha if obj.simulacro else None
    
    def get_asesor_nombre(self, obj):
        if obj.simulacro and obj.simulacro.asesor:
            return obj.simulacro.asesor.nombre_completo()
        return None


class ConfiguracionIASerializer(serializers.ModelSerializer):
    """Serializer para configuración de IA del asesor."""
    modelo_display = serializers.CharField(source='get_modelo_display', read_only=True)
    api_key_masked = serializers.SerializerMethodField()
    
    class Meta:
        model = ConfiguracionIA
        fields = [
            'id', 'api_key', 'api_key_masked', 'modelo', 'modelo_display',
            'activo', 'total_analisis', 'ultimo_uso', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'api_key': {'write_only': True},
            'total_analisis': {'read_only': True},
            'ultimo_uso': {'read_only': True},
        }
    
    def get_api_key_masked(self, obj):
        """Devuelve la API key enmascarada para mostrar."""
        if obj.api_key:
            # Mostrar solo los primeros 8 y últimos 4 caracteres
            key = obj.api_key
            if len(key) > 12:
                return f"{key[:8]}...{key[-4:]}"
            return "***configurada***"
        return None
    
    def create(self, validated_data):
        """Crea o actualiza la configuración del asesor."""
        request = self.context.get('request')
        asesor = request.user
        
        # Si ya existe, actualizar
        config, created = ConfiguracionIA.objects.update_or_create(
            asesor=asesor,
            defaults=validated_data
        )
        return config


class ConfiguracionIAUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar configuración de IA."""
    
    class Meta:
        model = ConfiguracionIA
        fields = ['api_key', 'modelo', 'activo']
    
    def validate_api_key(self, value):
        """Valida que la API key tenga un formato válido."""
        if value and len(value) < 20:
            raise serializers.ValidationError("La API key parece ser demasiado corta")
        return value
