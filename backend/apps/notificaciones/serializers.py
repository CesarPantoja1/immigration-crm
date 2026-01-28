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
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje', 'detalle',
            'datos', 'solicitud_id', 'leida', 'fecha_lectura',
            'url_accion', 'tiempo_transcurrido', 'created_at'
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


class NotificacionListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listar notificaciones."""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje',
            'leida', 'url_accion', 'tiempo_transcurrido', 'created_at'
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
