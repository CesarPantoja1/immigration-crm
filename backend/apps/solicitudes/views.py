"""
Views para la API de Solicitudes.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Solicitud, Documento, Entrevista
from .serializers import (
    SolicitudListSerializer,
    SolicitudDetailSerializer,
    SolicitudCreateSerializer,
    SolicitudUpdateSerializer,
    DocumentoSerializer,
    EntrevistaSerializer,
    AsignarAsesorSerializer,
)

Usuario = get_user_model()


# =====================================================
# PERMISOS PERSONALIZADOS
# =====================================================

class EsClienteOAsesor(permissions.BasePermission):
    """Permite acceso a clientes y asesores."""
    
    def has_permission(self, request, view):
        return request.user.rol in ['cliente', 'asesor', 'admin']


class EsAsesorOAdmin(permissions.BasePermission):
    """Solo permite acceso a asesores y admins."""
    
    def has_permission(self, request, view):
        return request.user.rol in ['asesor', 'admin']


# =====================================================
# VISTAS DE CLIENTE
# =====================================================

class MisSolicitudesView(generics.ListAPIView):
    """
    GET /api/solicitudes/mis-solicitudes/
    Lista las solicitudes del cliente autenticado.
    """
    serializer_class = SolicitudListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.rol == 'cliente':
            return Solicitud.objects.filter(cliente=user, is_deleted=False)
        elif user.rol == 'asesor':
            return Solicitud.objects.filter(asesor=user, is_deleted=False)
        else:
            return Solicitud.objects.filter(is_deleted=False)


class CrearSolicitudView(generics.CreateAPIView):
    """
    POST /api/solicitudes/nueva/
    Crea una nueva solicitud (solo clientes).
    """
    serializer_class = SolicitudCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()


class SolicitudDetailView(generics.RetrieveAPIView):
    """
    GET /api/solicitudes/<id>/
    Obtiene el detalle de una solicitud.
    """
    serializer_class = SolicitudDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.rol == 'cliente':
            return Solicitud.objects.filter(cliente=user, is_deleted=False)
        elif user.rol == 'asesor':
            return Solicitud.objects.filter(
                Q(asesor=user) | Q(asesor__isnull=True),
                is_deleted=False
            )
        else:
            return Solicitud.objects.filter(is_deleted=False)


# =====================================================
# VISTAS DE ASESOR
# =====================================================

class SolicitudesAsignadasView(generics.ListAPIView):
    """
    GET /api/solicitudes/asignadas/
    Lista las solicitudes asignadas al asesor.
    """
    serializer_class = SolicitudListSerializer
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Solicitud.objects.filter(is_deleted=False)
        
        if user.rol == 'asesor':
            queryset = queryset.filter(asesor=user)
        
        # Filtros opcionales
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        tipo_visa = self.request.query_params.get('tipo_visa')
        if tipo_visa:
            queryset = queryset.filter(tipo_visa=tipo_visa)
        
        return queryset


class SolicitudesPendientesView(generics.ListAPIView):
    """
    GET /api/solicitudes/pendientes/
    Lista solicitudes pendientes de asignación (admin).
    """
    serializer_class = SolicitudListSerializer
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def get_queryset(self):
        return Solicitud.objects.filter(
            asesor__isnull=True,
            estado='pendiente',
            is_deleted=False
        )


class ActualizarSolicitudView(generics.UpdateAPIView):
    """
    PATCH /api/solicitudes/<id>/actualizar/
    Actualiza el estado y notas de una solicitud (asesor).
    """
    serializer_class = SolicitudUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.rol == 'asesor':
            return Solicitud.objects.filter(asesor=user, is_deleted=False)
        return Solicitud.objects.filter(is_deleted=False)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        
        # Registrar fecha de revisión si se actualiza
        if instance.estado in ['aprobada', 'rechazada']:
            instance.fecha_revision = timezone.now()
            instance.save()


class AsignarAsesorView(APIView):
    """
    POST /api/solicitudes/<id>/asignar/
    Asigna un asesor a una solicitud.
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def post(self, request, pk):
        try:
            solicitud = Solicitud.objects.get(pk=pk, is_deleted=False)
        except Solicitud.DoesNotExist:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not solicitud.puede_ser_asignada():
            return Response(
                {'error': 'La solicitud ya tiene un asesor asignado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AsignarAsesorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        asesor = Usuario.objects.get(id=serializer.validated_data['asesor_id'])
        solicitud.asignar_asesor(asesor)
        
        return Response({
            'mensaje': f'Solicitud asignada a {asesor.nombre_completo()}',
            'solicitud': SolicitudDetailSerializer(solicitud).data
        })


# =====================================================
# ESTADÍSTICAS Y DASHBOARD
# =====================================================

class EstadisticasClienteView(APIView):
    """
    GET /api/solicitudes/estadisticas/cliente/
    Estadísticas del dashboard del cliente.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        solicitudes = Solicitud.objects.filter(cliente=user, is_deleted=False)
        
        return Response({
            'total_solicitudes': solicitudes.count(),
            'en_proceso': solicitudes.filter(
                estado__in=['pendiente', 'en_revision', 'aprobada']
            ).count(),
            'aprobadas': solicitudes.filter(estado='aprobada').count(),
            'completadas': solicitudes.filter(estado='completada').count(),
            'rechazadas': solicitudes.filter(estado='rechazada').count(),
            'con_entrevista': solicitudes.filter(
                estado='entrevista_agendada'
            ).count(),
        })


class EstadisticasAsesorView(APIView):
    """
    GET /api/solicitudes/estadisticas/asesor/
    Estadísticas del dashboard del asesor.
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def get(self, request):
        user = request.user
        hoy = timezone.now().date()
        
        if user.rol == 'asesor':
            solicitudes = Solicitud.objects.filter(asesor=user, is_deleted=False)
        else:
            solicitudes = Solicitud.objects.filter(is_deleted=False)
        
        return Response({
            'total_asignadas': solicitudes.count(),
            'asignadas_hoy': solicitudes.filter(
                fecha_asignacion__date=hoy
            ).count(),
            'pendientes_revision': solicitudes.filter(
                estado='pendiente'
            ).count(),
            'en_revision': solicitudes.filter(estado='en_revision').count(),
            'aprobadas': solicitudes.filter(estado='aprobada').count(),
            'enviadas_embajada': solicitudes.filter(
                estado='enviada_embajada'
            ).count(),
            'limite_diario': user.limite_solicitudes_diarias if user.rol == 'asesor' else None,
            'disponibilidad': user.limite_solicitudes_diarias - solicitudes.filter(
                fecha_asignacion__date=hoy
            ).count() if user.rol == 'asesor' else None,
        })
