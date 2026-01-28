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
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
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
    Lista las solicitudes asignadas al asesor con documentos.
    """
    serializer_class = SolicitudDetailSerializer
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Solicitud.objects.filter(is_deleted=False).prefetch_related('documentos_adjuntos')
        
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


class EnviarSolicitudView(APIView):
    """
    POST /api/solicitudes/<id>/enviar/
    Envía/confirma una solicitud (cambia de borrador a pendiente).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            solicitud = Solicitud.objects.get(pk=pk, cliente=request.user, is_deleted=False)
        except Solicitud.DoesNotExist:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if solicitud.estado not in ['borrador', 'pendiente']:
            return Response(
                {'error': 'La solicitud ya ha sido enviada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitud.estado = 'pendiente'
        solicitud.save()
        
        return Response({
            'mensaje': 'Solicitud enviada exitosamente',
            'solicitud': SolicitudDetailSerializer(solicitud).data
        })


class SubirDocumentoView(APIView):
    """
    POST /api/solicitudes/<id>/documentos/
    Sube un documento a una solicitud.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            solicitud = Solicitud.objects.get(pk=pk, cliente=request.user, is_deleted=False)
        except Solicitud.DoesNotExist:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        archivo = request.FILES.get('archivo')
        nombre = request.data.get('nombre', 'Documento')
        
        if not archivo:
            return Response(
                {'error': 'No se ha enviado ningún archivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        documento = Documento.objects.create(
            solicitud=solicitud,
            nombre=nombre,
            archivo=archivo,
            estado='pendiente'
        )
        
        return Response({
            'mensaje': 'Documento subido exitosamente',
            'documento': DocumentoSerializer(documento, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


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


# =====================================================
# VISTAS DE DOCUMENTOS
# =====================================================

class DocumentoDetailView(generics.RetrieveAPIView):
    """
    GET /api/documentos/<id>/
    Obtiene el detalle de un documento.
    """
    serializer_class = DocumentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.rol == 'cliente':
            return Documento.objects.filter(solicitud__cliente=user)
        elif user.rol == 'asesor':
            return Documento.objects.filter(solicitud__asesor=user)
        return Documento.objects.all()


class AprobarDocumentoView(APIView):
    """
    PATCH /api/documentos/<id>/aprobar/
    Aprueba un documento (asesor).
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def patch(self, request, pk):
        try:
            documento = Documento.objects.get(pk=pk)
            
            # Verificar que el asesor tenga permiso
            user = request.user
            if user.rol == 'asesor' and documento.solicitud.asesor != user:
                return Response(
                    {'error': 'No tienes permiso para aprobar este documento'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            documento.estado = 'aprobado'
            documento.revisado_por = user
            documento.fecha_revision = timezone.now()
            documento.motivo_rechazo = ''
            documento.save()
            
            return Response({
                'mensaje': 'Documento aprobado exitosamente',
                'documento': DocumentoSerializer(documento, context={'request': request}).data
            })
        except Documento.DoesNotExist:
            return Response(
                {'error': 'Documento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class RechazarDocumentoView(APIView):
    """
    PATCH /api/documentos/<id>/rechazar/
    Rechaza un documento (asesor).
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def patch(self, request, pk):
        try:
            documento = Documento.objects.get(pk=pk)
            
            # Verificar que el asesor tenga permiso
            user = request.user
            if user.rol == 'asesor' and documento.solicitud.asesor != user:
                return Response(
                    {'error': 'No tienes permiso para rechazar este documento'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            motivo = request.data.get('motivo_rechazo', '')
            if not motivo:
                return Response(
                    {'error': 'Debe proporcionar un motivo de rechazo'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            documento.estado = 'rechazado'
            documento.revisado_por = user
            documento.fecha_revision = timezone.now()
            documento.motivo_rechazo = motivo
            documento.save()
            
            return Response({
                'mensaje': 'Documento rechazado',
                'documento': DocumentoSerializer(documento, context={'request': request}).data
            })
        except Documento.DoesNotExist:
            return Response(
                {'error': 'Documento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class ListarDocumentosSolicitudView(generics.ListAPIView):
    """
    GET /api/solicitudes/<id>/documentos/
    Lista todos los documentos de una solicitud.
    """
    serializer_class = DocumentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        solicitud_id = self.kwargs.get('pk')
        user = self.request.user
        
        queryset = Documento.objects.filter(solicitud_id=solicitud_id)
        
        if user.rol == 'cliente':
            queryset = queryset.filter(solicitud__cliente=user)
        elif user.rol == 'asesor':
            queryset = queryset.filter(solicitud__asesor=user)
        
        return queryset
