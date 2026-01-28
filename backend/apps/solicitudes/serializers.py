"""
Serializers para la API de Solicitudes.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q, F, Count
from .models import Solicitud, Documento, Entrevista

Usuario = get_user_model()


class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para documentos."""
    archivo_url = serializers.SerializerMethodField()
    fecha_subida = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Documento
        fields = [
            'id', 'nombre', 'archivo', 'archivo_url', 'estado',
            'motivo_rechazo', 'fecha_revision', 'created_at', 'fecha_subida'
        ]
        read_only_fields = ['id', 'created_at', 'fecha_revision', 'fecha_subida']
    
    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            # Fallback: construir URL manualmente si no hay request
            from django.conf import settings
            base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            return f"{base_url}{obj.archivo.url}"
        return None


class EntrevistaSerializer(serializers.ModelSerializer):
    """Serializer para entrevistas."""
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Entrevista
        fields = [
            'id', 'fecha', 'hora', 'ubicacion', 'estado',
            'estado_display', 'notas', 'veces_reprogramada', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'veces_reprogramada']


class SolicitudListSerializer(serializers.ModelSerializer):
    """Serializer para listar solicitudes (versión resumida)."""
    tipo_visa_display = serializers.CharField(source='get_tipo_visa_display', read_only=True)
    embajada_display = serializers.CharField(source='get_embajada_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    asesor_nombre = serializers.SerializerMethodField()
    tiene_entrevista = serializers.SerializerMethodField()
    documentos_count = serializers.SerializerMethodField()
    documentos_aprobados = serializers.SerializerMethodField()
    
    class Meta:
        model = Solicitud
        fields = [
            'id', 'tipo_visa', 'tipo_visa_display', 'embajada', 'embajada_display',
            'estado', 'estado_display', 'cliente_nombre', 'asesor_nombre',
            'tiene_entrevista', 'documentos_count', 'documentos_aprobados',
            'created_at', 'updated_at'
        ]
    
    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre_completo() if obj.cliente else None
    
    def get_asesor_nombre(self, obj):
        return obj.asesor.nombre_completo() if obj.asesor else None
    
    def get_tiene_entrevista(self, obj):
        return hasattr(obj, 'entrevista')
    
    def get_documentos_count(self, obj):
        return obj.documentos_adjuntos.count()
    
    def get_documentos_aprobados(self, obj):
        return obj.documentos_adjuntos.filter(estado='aprobado').count()


class SolicitudDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle completo de solicitud."""
    tipo_visa_display = serializers.CharField(source='get_tipo_visa_display', read_only=True)
    embajada_display = serializers.CharField(source='get_embajada_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    asesor_nombre = serializers.SerializerMethodField()
    documentos_adjuntos = serializers.SerializerMethodField()
    entrevista = EntrevistaSerializer(read_only=True)
    
    class Meta:
        model = Solicitud
        fields = [
            'id', 'tipo_visa', 'tipo_visa_display', 'embajada', 'embajada_display',
            'estado', 'estado_display', 'cliente', 'cliente_nombre',
            'asesor', 'asesor_nombre', 'datos_personales', 'documentos',
            'observaciones', 'notas_asesor', 'documentos_adjuntos', 'entrevista',
            'fecha_asignacion', 'fecha_revision', 'fecha_envio_embajada',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'cliente', 'created_at', 'updated_at',
            'fecha_asignacion', 'fecha_revision', 'fecha_envio_embajada'
        ]
    
    def get_cliente_nombre(self, obj):
        return obj.cliente.nombre_completo() if obj.cliente else None
    
    def get_asesor_nombre(self, obj):
        return obj.asesor.nombre_completo() if obj.asesor else None
    
    def get_documentos_adjuntos(self, obj):
        """Serializa los documentos pasando el contexto con request."""
        documentos = obj.documentos_adjuntos.all()
        return DocumentoSerializer(documentos, many=True, context=self.context).data


class SolicitudCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear solicitudes (cliente)."""
    
    class Meta:
        model = Solicitud
        fields = [
            'id', 'tipo_visa', 'embajada', 'datos_personales', 'observaciones', 'estado'
        ]
        read_only_fields = ['id', 'estado']
    
    def create(self, validated_data):
        # El cliente se obtiene del request
        request = self.context.get('request')
        validated_data['cliente'] = request.user
        validated_data['estado'] = 'pendiente'
        
        solicitud = Solicitud.objects.create(**validated_data)
        
        # Asignar automáticamente a un asesor disponible
        self._asignar_asesor(solicitud)
        
        return solicitud
    
    def _asignar_asesor(self, solicitud):
        """Asigna la solicitud al asesor con menos carga."""
        from django.utils import timezone
        
        hoy = timezone.now().date()
        
        # Obtener asesores con su carga de trabajo de hoy
        asesor = Usuario.objects.filter(
            rol='asesor',
            is_active=True
        ).annotate(
            solicitudes_hoy=Count(
                'solicitudes_asignadas',
                filter=Q(
                    solicitudes_asignadas__fecha_asignacion__date=hoy
                )
            )
        ).filter(
            solicitudes_hoy__lt=F('limite_solicitudes_diarias')
        ).order_by('solicitudes_hoy').first()
        
        if asesor:
            solicitud.asignar_asesor(asesor)


class SolicitudUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar solicitudes (asesor)."""
    
    class Meta:
        model = Solicitud
        fields = [
            'estado', 'notas_asesor', 'observaciones'
        ]
    
    def validate_estado(self, value):
        instance = self.instance
        
        # Validar transiciones de estado permitidas
        transiciones_validas = {
            'pendiente': ['en_revision', 'rechazada'],
            'en_revision': ['aprobada', 'rechazada'],
            'aprobada': ['enviada_embajada'],
            'enviada_embajada': ['entrevista_agendada'],
            'entrevista_agendada': ['completada'],
        }
        
        if instance:
            estados_permitidos = transiciones_validas.get(instance.estado, [])
            if value not in estados_permitidos and value != instance.estado:
                raise serializers.ValidationError(
                    f"No se puede cambiar de '{instance.estado}' a '{value}'"
                )
        
        return value


class AsignarAsesorSerializer(serializers.Serializer):
    """Serializer para asignar asesor manualmente."""
    asesor_id = serializers.IntegerField(required=True)
    
    def validate_asesor_id(self, value):
        try:
            asesor = Usuario.objects.get(id=value, rol='asesor', is_active=True)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Asesor no encontrado o no disponible")
        
        # Verificar límite diario
        from django.utils import timezone
        from django.db.models import Count
        
        hoy = timezone.now().date()
        solicitudes_hoy = asesor.solicitudes_asignadas.filter(
            fecha_asignacion__date=hoy
        ).count()
        
        if solicitudes_hoy >= asesor.limite_solicitudes_diarias:
            raise serializers.ValidationError(
                "El asesor ha alcanzado el límite diario de solicitudes"
            )
        
        return value
