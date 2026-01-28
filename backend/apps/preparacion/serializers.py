"""
Serializers para el módulo de Preparación (Simulacros).
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Simulacro, Recomendacion, Practica

Usuario = get_user_model()


class SimulacroListSerializer(serializers.ModelSerializer):
    """Serializer para listar simulacros."""
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    modalidad_display = serializers.CharField(source='get_modalidad_display', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    asesor_nombre = serializers.SerializerMethodField()
    puede_cancelar = serializers.SerializerMethodField()
    puede_ingresar = serializers.SerializerMethodField()
    
    class Meta:
        model = Simulacro
        fields = [
            'id', 'fecha', 'hora', 'modalidad', 'modalidad_display',
            'estado', 'estado_display', 'cliente_nombre', 'asesor_nombre',
            'ubicacion', 'puede_cancelar', 'puede_ingresar', 'created_at'
        ]
    
    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre_completo() if obj.cliente else None
    
    def get_asesor_nombre(self, obj):
        return obj.asesor.nombre_completo() if obj.asesor else None
    
    def get_puede_cancelar(self, obj):
        return obj.puede_cancelar()
    
    def get_puede_ingresar(self, obj):
        return obj.puede_ingresar_sala()


class SimulacroDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de simulacro."""
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    modalidad_display = serializers.CharField(source='get_modalidad_display', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    asesor_nombre = serializers.SerializerMethodField()
    tiene_recomendacion = serializers.SerializerMethodField()
    
    class Meta:
        model = Simulacro
        fields = [
            'id', 'fecha', 'hora', 'modalidad', 'modalidad_display',
            'estado', 'estado_display', 'cliente', 'cliente_nombre',
            'asesor', 'asesor_nombre', 'solicitud', 'ubicacion',
            'fecha_propuesta', 'hora_propuesta', 'fecha_inicio', 'fecha_fin',
            'duracion_minutos', 'grabacion_activa', 'notas',
            'tiene_recomendacion', 'created_at', 'updated_at'
        ]
    
    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre_completo() if obj.cliente else None
    
    def get_asesor_nombre(self, obj):
        return obj.asesor.nombre_completo() if obj.asesor else None
    
    def get_tiene_recomendacion(self, obj):
        return hasattr(obj, 'recomendacion')


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
