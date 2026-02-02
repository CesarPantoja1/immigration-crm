"""
Serializers para el módulo de Notificaciones.

ARQUITECTURA DE NAVEGACIÓN CONTEXTUAL (Deep Linking):
======================================================
El backend es responsable de calcular la ruta de navegación (action_url)
basándose en el tipo de notificación y los datos asociados.

El frontend NO debe contener lógica de "si es tipo X, ir a Y".
El frontend debe ser "tonto" y simplemente navegar a donde el backend indica.

Campos calculados:
- action_url: Ruta completa para navegación (ej: '/simulacros/42')
- action_type: Tipo de acción ('navigate', 'modal', 'external', 'none')
- target_resource: Objeto con type e id del recurso destino
- is_actionable: Boolean indicando si requiere acción del usuario
"""
from rest_framework import serializers
from .models import Notificacion, PreferenciaNotificacion, TipoNotificacion


# =============================================================================
# MAPEO DE RUTAS POR TIPO DE NOTIFICACIÓN
# =============================================================================
# Centraliza toda la lógica de navegación en el backend.
# El frontend simplemente usa action_url sin interpretarlo.

ROUTE_MAP = {
    # Simulacros - Navegación a detalle de simulacro
    'simulacro_propuesto': {
        'route_template': '/simulacros/{simulacro_id}',
        'route_template_asesor': '/asesor/simulacros/{simulacro_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/simulacros'
    },
    'simulacro_confirmado': {
        'route_template': '/simulacros/{simulacro_id}',
        'route_template_asesor': '/asesor/simulacros/{simulacro_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/simulacros'
    },
    'simulacion_completada': {
        'route_template': '/simulacros/{simulacro_id}/resumen',
        'route_template_asesor': '/asesor/simulacros/{simulacro_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/simulacros'
    },
    'recomendaciones_listas': {
        'route_template': '/simulacros/{simulacro_id}/resumen',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/simulacros'
    },
    
    # Solicitudes - Navegación a detalle de solicitud
    'solicitud_aprobada': {
        'route_template': '/solicitudes/{solicitud_id}',
        'route_template_asesor': '/asesor/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/solicitudes'
    },
    'solicitud_rechazada': {
        'route_template': '/solicitudes/{solicitud_id}',
        'route_template_asesor': '/asesor/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/solicitudes'
    },
    'solicitud_creada': {
        'route_template': '/solicitudes/{solicitud_id}',
        'route_template_asesor': '/asesor/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': False,
        'fallback': '/solicitudes'
    },
    'solicitud_enviada': {
        'route_template': '/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': False,
        'fallback': '/solicitudes'
    },
    
    # Embajada
    'embajada_aprobada': {
        'route_template': '/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/solicitudes'
    },
    'embajada_rechazada': {
        'route_template': '/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/solicitudes'
    },
    
    # Documentos - Solo los que requieren acción
    'documento_rechazado': {
        'route_template': '/solicitudes/{solicitud_id}/documentos',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/solicitudes'
    },
    'documento_aprobado': {
        'route_template': '/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': False,
        'fallback': '/solicitudes'
    },
    
    # Contratos
    'contrato_generado': {
        'route_template': '/solicitudes/{solicitud_id}/contrato',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/solicitudes'
    },
    'contrato_pendiente': {
        'route_template': '/solicitudes/{solicitud_id}/contrato',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/solicitudes'
    },
    'contrato_firmado': {
        'route_template': '/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': False,
        'fallback': '/solicitudes'
    },
    'contrato_aprobado': {
        'route_template': '/solicitudes/{solicitud_id}/documentos',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/solicitudes'
    },
    
    # Entrevistas
    'entrevista_agendada': {
        'route_template': '/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/calendario'
    },
    'entrevista_reprogramada': {
        'route_template': '/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/calendario'
    },
    'entrevista_cancelada': {
        'route_template': '/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/solicitudes'
    },
    'recordatorio_entrevista': {
        'route_template': '/solicitudes/{solicitud_id}',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/calendario'
    },
    
    # Preparación
    'preparacion_recomendada': {
        'route_template': '/simulacros',
        'action_type': 'navigate',
        'is_actionable': True,
        'fallback': '/simulacros'
    },
    
    # General - Sin navegación específica
    'general': {
        'route_template': None,
        'action_type': 'none',
        'is_actionable': False,
        'fallback': '/dashboard'
    },
    'mensaje': {
        'route_template': None,
        'action_type': 'none',
        'is_actionable': False,
        'fallback': '/inbox'
    },
}


def build_action_url(tipo, datos, solicitud_id=None, url_accion=None, usuario=None):
    """
    Construye la URL de acción basada en el tipo y datos de la notificación.
    
    Args:
        tipo: Tipo de notificación (ej: 'simulacro_confirmado')
        datos: Dict con datos adicionales (ej: {'simulacro_id': 42})
        solicitud_id: ID de solicitud asociada (opcional)
        url_accion: URL de acción manual (override)
        usuario: Usuario para determinar si es asesor
    
    Returns:
        str: URL de navegación calculada
    """
    # Si hay url_accion explícita, usarla como override
    if url_accion:
        return url_accion
    
    config = ROUTE_MAP.get(tipo, ROUTE_MAP['general'])
    template = config.get('route_template')
    
    # Determinar si usar template de asesor
    if usuario and hasattr(usuario, 'rol') and usuario.rol == 'asesor':
        template = config.get('route_template_asesor', template)
    
    if not template:
        return config.get('fallback', '/dashboard')
    
    # Construir contexto para el template
    context = {
        'solicitud_id': solicitud_id or datos.get('solicitud_id'),
        'simulacro_id': datos.get('simulacro_id'),
        'documento_id': datos.get('documento_id'),
        'cliente_id': datos.get('cliente_id'),
    }
    
    try:
        # Intentar formatear el template
        url = template.format(**{k: v for k, v in context.items() if v is not None})
        # Verificar que no quedaron placeholders sin resolver
        if '{' in url:
            return config.get('fallback', '/dashboard')
        return url
    except (KeyError, ValueError):
        return config.get('fallback', '/dashboard')


class NotificacionSerializer(serializers.ModelSerializer):
    """
    Serializer completo para notificaciones con navegación contextual.
    
    Incluye campos calculados para Deep Linking:
    - action_url: Ruta de navegación calculada
    - action_type: Tipo de acción (navigate, modal, external, none)
    - target_resource: Recurso destino {type, id}
    - is_actionable: Si requiere acción del usuario
    """
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    solicitud_id = serializers.SerializerMethodField()
    usuario_nombre = serializers.SerializerMethodField()
    
    # Campos de navegación contextual
    action_url = serializers.SerializerMethodField()
    action_type = serializers.SerializerMethodField()
    target_resource = serializers.SerializerMethodField()
    is_actionable = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje', 'detalle',
            'datos', 'solicitud_id', 'leida', 'fecha_lectura',
            'url_accion', 'tiempo_transcurrido', 'created_at',
            'usuario_nombre',
            # Campos de navegación contextual
            'action_url', 'action_type', 'target_resource', 'is_actionable'
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
    
    def get_action_url(self, obj):
        """Calcula la URL de navegación basada en tipo y datos."""
        request = self.context.get('request')
        usuario = request.user if request else None
        return build_action_url(
            tipo=obj.tipo,
            datos=obj.datos or {},
            solicitud_id=obj.solicitud_id,
            url_accion=obj.url_accion,
            usuario=usuario
        )
    
    def get_action_type(self, obj):
        """Retorna el tipo de acción: navigate, modal, external, none."""
        config = ROUTE_MAP.get(obj.tipo, ROUTE_MAP['general'])
        return config.get('action_type', 'none')
    
    def get_target_resource(self, obj):
        """Retorna información del recurso destino."""
        datos = obj.datos or {}
        
        # Determinar tipo de recurso basado en el tipo de notificación
        if obj.tipo.startswith('simulacro') or obj.tipo in ['simulacion_completada', 'recomendaciones_listas']:
            return {
                'type': 'simulacro',
                'id': datos.get('simulacro_id')
            }
        elif obj.tipo.startswith('solicitud') or obj.tipo.startswith('embajada'):
            return {
                'type': 'solicitud',
                'id': obj.solicitud_id or datos.get('solicitud_id')
            }
        elif obj.tipo.startswith('documento'):
            return {
                'type': 'documento',
                'id': datos.get('documento_id'),
                'parent_id': obj.solicitud_id
            }
        elif obj.tipo.startswith('contrato'):
            return {
                'type': 'contrato',
                'id': obj.solicitud_id
            }
        elif obj.tipo.startswith('entrevista') or obj.tipo == 'recordatorio_entrevista':
            return {
                'type': 'entrevista',
                'id': obj.solicitud_id
            }
        else:
            return {
                'type': 'general',
                'id': None
            }
    
    def get_is_actionable(self, obj):
        """Indica si la notificación requiere acción del usuario."""
        config = ROUTE_MAP.get(obj.tipo, ROUTE_MAP['general'])
        return config.get('is_actionable', False)


class NotificacionListSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listar notificaciones.
    Incluye campos de navegación contextual para Deep Linking.
    """
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    usuario_nombre = serializers.SerializerMethodField()
    
    # Campos de navegación contextual
    action_url = serializers.SerializerMethodField()
    action_type = serializers.SerializerMethodField()
    is_actionable = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje',
            'leida', 'url_accion', 'tiempo_transcurrido', 'created_at',
            'usuario_nombre',
            # Campos de navegación contextual
            'action_url', 'action_type', 'is_actionable'
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
    
    def get_action_url(self, obj):
        """Calcula la URL de navegación basada en tipo y datos."""
        request = self.context.get('request')
        usuario = request.user if request else None
        return build_action_url(
            tipo=obj.tipo,
            datos=obj.datos or {},
            solicitud_id=obj.solicitud_id,
            url_accion=obj.url_accion,
            usuario=usuario
        )
    
    def get_action_type(self, obj):
        """Retorna el tipo de acción."""
        config = ROUTE_MAP.get(obj.tipo, ROUTE_MAP['general'])
        return config.get('action_type', 'none')
    
    def get_is_actionable(self, obj):
        """Indica si la notificación requiere acción del usuario."""
        config = ROUTE_MAP.get(obj.tipo, ROUTE_MAP['general'])
        return config.get('is_actionable', False)


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
