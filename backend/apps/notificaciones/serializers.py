"""
Serializers para el módulo de Notificaciones.
"""
from rest_framework import serializers
from .models import Notificacion, PreferenciaNotificacion, TipoNotificacion


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones."""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    solicitud_id = serializers.SerializerMethodField()
    usuario_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje', 'detalle',
            'datos', 'solicitud_id', 'leida', 'fecha_lectura',
            'url_accion', 'tiempo_transcurrido', 'created_at',
            'usuario_nombre'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_tiempo_transcurrido(self, obj):
        """Retorna el tiempo transcurrido en formato legible."""
        from django.utils import timezone
        from datetime import timedelta
        
        ahora = timezone.now()
        diferencia = ahora - obj.created_at
        
        if diferencia < timedelta(minutes=1):
            return 'Hace un momento'
        elif diferencia < timedelta(hours=1):
            minutos = int(diferencia.total_seconds() / 60)
            return f'Hace {minutos} minutos'
        elif diferencia < timedelta(days=1):
            horas = int(diferencia.total_seconds() / 3600)
            return f'Hace {horas} horas'
        elif diferencia < timedelta(days=7):
            dias = diferencia.days
            return f'Hace {dias} días'
        else:
            return obj.created_at.strftime('%d/%m/%Y')
    
    def get_solicitud_id(self, obj):
        return obj.solicitud_id if obj.solicitud else None
    
    def get_usuario_nombre(self, obj):
        return obj.usuario.nombre_completo() if obj.usuario else None


class NotificacionListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listar notificaciones."""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    usuario_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje',
            'leida', 'url_accion', 'tiempo_transcurrido', 'created_at',
            'usuario_nombre'
        ]
    
    def get_tiempo_transcurrido(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        ahora = timezone.now()
        diferencia = ahora - obj.created_at
        
        if diferencia < timedelta(minutes=1):
            return 'Hace un momento'
        elif diferencia < timedelta(hours=1):
            minutos = int(diferencia.total_seconds() / 60)
            return f'Hace {minutos} min'
        elif diferencia < timedelta(days=1):
            horas = int(diferencia.total_seconds() / 3600)
            return f'Hace {horas}h'
        elif diferencia < timedelta(days=7):
            dias = diferencia.days
            return f'Hace {dias}d'
        else:
            return obj.created_at.strftime('%d/%m')
    
    def get_usuario_nombre(self, obj):
        return obj.usuario.nombre_completo() if obj.usuario else None


class PreferenciaNotificacionSerializer(serializers.ModelSerializer):
    """Serializer para preferencias de notificación."""
    
    class Meta:
        model = PreferenciaNotificacion
        fields = [
            'email_entrevistas', 'email_documentos',
            'email_simulacros', 'email_recordatorios',
            'push_habilitado'
        ]


class TipoNotificacionSerializer(serializers.ModelSerializer):
    """Serializer para tipos de notificación."""
    
    class Meta:
        model = TipoNotificacion
        fields = ['codigo', 'nombre', 'proposito', 'icono', 'color']


class CrearNotificacionSerializer(serializers.ModelSerializer):
    """Serializer para crear notificaciones desde el panel de asesor."""
    usuario_id = serializers.IntegerField(write_only=True)
    solicitud_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Notificacion
        fields = [
            'usuario_id', 'tipo', 'titulo', 'mensaje', 'detalle',
            'solicitud_id', 'url_accion', 'datos'
        ]
    
    def create(self, validated_data):
        from apps.usuarios.models import Usuario
        from apps.solicitudes.models import Solicitud
        
        usuario_id = validated_data.pop('usuario_id')
        solicitud_id = validated_data.pop('solicitud_id', None)
        
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({'usuario_id': 'Usuario no encontrado'})
        
        solicitud = None
        if solicitud_id:
            try:
                solicitud = Solicitud.objects.get(pk=solicitud_id)
            except Solicitud.DoesNotExist:
                raise serializers.ValidationError({'solicitud_id': 'Solicitud no encontrada'})
        
        return Notificacion.objects.create(
            usuario=usuario,
            solicitud=solicitud,
            **validated_data
        )
