"""
Views para el módulo de Notificaciones.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q

from .models import Notificacion, PreferenciaNotificacion
from .serializers import (
    NotificacionSerializer,
    NotificacionListSerializer,
    PreferenciaNotificacionSerializer,
    CrearNotificacionSerializer,
)


class NotificacionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificacionesListView(generics.ListAPIView):
    """
    GET /api/notificaciones/
    Lista notificaciones del usuario.
    """
    serializer_class = NotificacionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificacionPagination
    
    def get_queryset(self):
        queryset = Notificacion.objects.filter(usuario=self.request.user)
        
        # Filtros
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        leida = self.request.query_params.get('leida')
        if leida is not None:
            queryset = queryset.filter(leida=leida.lower() == 'true')
        
        return queryset.order_by('-created_at')


class NotificacionDetailView(generics.RetrieveAPIView):
    """
    GET /api/notificaciones/<id>/
    Detalle de notificación.
    """
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Marcar como leída al ver el detalle
        instance.marcar_como_leida()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ConteoNoLeidasView(APIView):
    """
    GET /api/notificaciones/no-leidas/count/
    Retorna el conteo de notificaciones no leídas.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        count = Notificacion.objects.filter(
            usuario=request.user,
            leida=False
        ).count()
        
        return Response({'count': count})


class NotificacionesNoLeidasView(generics.ListAPIView):
    """
    GET /api/notificaciones/no-leidas/
    Lista notificaciones no leídas.
    """
    serializer_class = NotificacionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notificacion.objects.filter(
            usuario=self.request.user,
            leida=False
        ).order_by('-created_at')[:10]


class MarcarLeidaView(APIView):
    """
    POST /api/notificaciones/<id>/leer/
    Marca una notificación como leída.
    Asesores pueden marcar notificaciones de sus clientes asignados.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        user = request.user
        
        try:
            # Primero intentar encontrar notificación propia
            notificacion = Notificacion.objects.get(pk=pk, usuario=user)
        except Notificacion.DoesNotExist:
            # Si es asesor, puede marcar notificaciones de sus clientes
            if user.rol in ['asesor', 'admin']:
                from apps.solicitudes.models import Solicitud
                clientes_ids = Solicitud.objects.filter(
                    asesor=user
                ).values_list('cliente_id', flat=True).distinct()
                
                try:
                    notificacion = Notificacion.objects.get(
                        pk=pk,
                        usuario_id__in=clientes_ids
                    )
                except Notificacion.DoesNotExist:
                    return Response(
                        {'error': 'Notificación no encontrada'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {'error': 'Notificación no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        notificacion.marcar_como_leida()
        
        return Response({'mensaje': 'Notificación marcada como leída'})


class MarcarTodasLeidasView(APIView):
    """
    POST /api/notificaciones/leer-todas/
    Marca todas las notificaciones como leídas.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        actualizadas = Notificacion.objects.filter(
            usuario=request.user,
            leida=False
        ).update(
            leida=True,
            fecha_lectura=timezone.now()
        )
        
        return Response({
            'mensaje': f'{actualizadas} notificaciones marcadas como leídas'
        })


class EliminarNotificacionView(APIView):
    """
    DELETE /api/notificaciones/<id>/
    Elimina una notificación.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):
        try:
            notificacion = Notificacion.objects.get(
                pk=pk,
                usuario=request.user
            )
        except Notificacion.DoesNotExist:
            return Response(
                {'error': 'Notificación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notificacion.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class EliminarLeidasView(APIView):
    """
    DELETE /api/notificaciones/eliminar-leidas/
    Elimina todas las notificaciones leídas.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        eliminadas, _ = Notificacion.objects.filter(
            usuario=request.user,
            leida=True
        ).delete()
        
        return Response({
            'mensaje': f'{eliminadas} notificaciones eliminadas'
        })


class TiposNotificacionView(APIView):
    """
    GET /api/notificaciones/tipos/
    Lista los tipos de notificación.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        tipos = [
            {'codigo': 'entrevista_agendada', 'nombre': 'Entrevista Agendada', 'icono': 'calendar', 'color': 'blue'},
            {'codigo': 'entrevista_reprogramada', 'nombre': 'Entrevista Reprogramada', 'icono': 'calendar', 'color': 'yellow'},
            {'codigo': 'entrevista_cancelada', 'nombre': 'Entrevista Cancelada', 'icono': 'calendar', 'color': 'red'},
            {'codigo': 'recordatorio_entrevista', 'nombre': 'Recordatorio', 'icono': 'bell', 'color': 'orange'},
            {'codigo': 'documento_aprobado', 'nombre': 'Documento Aprobado', 'icono': 'check', 'color': 'green'},
            {'codigo': 'documento_rechazado', 'nombre': 'Documento Rechazado', 'icono': 'x', 'color': 'red'},
            {'codigo': 'solicitud_aprobada', 'nombre': 'Solicitud Aprobada', 'icono': 'check', 'color': 'green'},
            {'codigo': 'simulacro_propuesto', 'nombre': 'Simulacro Propuesto', 'icono': 'video', 'color': 'purple'},
            {'codigo': 'recomendaciones_listas', 'nombre': 'Recomendaciones', 'icono': 'document', 'color': 'blue'},
        ]
        return Response(tipos)


class PreferenciasView(APIView):
    """
    GET/PATCH /api/notificaciones/preferencias/
    Obtiene o actualiza preferencias de notificación.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        preferencias, _ = PreferenciaNotificacion.objects.get_or_create(
            usuario=request.user
        )
        serializer = PreferenciaNotificacionSerializer(preferencias)
        return Response(serializer.data)
    
    def patch(self, request):
        preferencias, _ = PreferenciaNotificacion.objects.get_or_create(
            usuario=request.user
        )
        serializer = PreferenciaNotificacionSerializer(
            preferencias,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


class CrearNotificacionView(APIView):
    """
    POST /api/notificaciones/crear/
    Permite a asesores/admins crear notificaciones para clientes.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Solo asesores y admins pueden crear notificaciones
        if request.user.rol not in ['asesor', 'admin']:
            return Response(
                {'error': 'No tienes permisos para crear notificaciones'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CrearNotificacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notificacion = serializer.save()
        
        return Response(
            NotificacionSerializer(notificacion).data,
            status=status.HTTP_201_CREATED
        )


class NotificacionesAsesorView(generics.ListAPIView):
    """
    GET /api/notificaciones/asesor/
    Lista notificaciones relevantes para el asesor:
    - Sus propias notificaciones
    - Notificaciones de sus clientes asignados (para seguimiento)
    """
    serializer_class = NotificacionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificacionPagination
    
    def get_queryset(self):
        user = self.request.user
        
        if user.rol not in ['asesor', 'admin']:
            return Notificacion.objects.none()
        
        # Obtener IDs de clientes asignados al asesor
        from apps.solicitudes.models import Solicitud
        clientes_ids = Solicitud.objects.filter(
            asesor=user
        ).values_list('cliente_id', flat=True).distinct()
        
        # Notificaciones propias + de clientes asignados
        queryset = Notificacion.objects.filter(
            Q(usuario=user) | Q(usuario_id__in=clientes_ids)
        )
        
        # Filtros opcionales
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        leida = self.request.query_params.get('leida')
        if leida is not None:
            queryset = queryset.filter(leida=leida.lower() == 'true')
        
        solo_propias = self.request.query_params.get('solo_propias')
        if solo_propias and solo_propias.lower() == 'true':
            queryset = queryset.filter(usuario=user)
        
        return queryset.order_by('-created_at')


# =====================================================
# FUNCIONES HELPER PARA CREAR NOTIFICACIONES
# =====================================================

def crear_notificacion(usuario, tipo, titulo, mensaje, solicitud=None, datos=None, url_accion=''):
    """
    Crea una notificación para un usuario.
    """
    return Notificacion.objects.create(
        usuario=usuario,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        solicitud=solicitud,
        datos=datos or {},
        url_accion=url_accion
    )


def notificar_entrevista_agendada(solicitud, fecha, hora):
    """Notifica al cliente que su entrevista fue agendada."""
    return crear_notificacion(
        usuario=solicitud.cliente,
        tipo='entrevista_agendada',
        titulo='Entrevista Agendada',
        mensaje=f'Tu entrevista ha sido agendada para el {fecha} a las {hora}',
        solicitud=solicitud,
        datos={'fecha': str(fecha), 'hora': str(hora)},
        url_accion=f'/solicitudes/{solicitud.id}'
    )


def notificar_documento_aprobado(documento):
    """Notifica al cliente que su documento fue aprobado."""
    return crear_notificacion(
        usuario=documento.solicitud.cliente,
        tipo='documento_aprobado',
        titulo='Documento Aprobado',
        mensaje=f'Tu documento "{documento.nombre}" ha sido aprobado',
        solicitud=documento.solicitud,
        url_accion=f'/solicitudes/{documento.solicitud_id}'
    )


def notificar_documento_rechazado(documento, motivo):
    """Notifica al cliente que su documento fue rechazado."""
    return crear_notificacion(
        usuario=documento.solicitud.cliente,
        tipo='documento_rechazado',
        titulo='Documento Rechazado',
        mensaje=f'Tu documento "{documento.nombre}" requiere correcciones',
        solicitud=documento.solicitud,
        datos={'motivo': motivo},
        url_accion=f'/solicitudes/{documento.solicitud_id}'
    )


def notificar_simulacro_propuesto(simulacro):
    """Notifica al cliente que tiene una propuesta de simulacro."""
    return crear_notificacion(
        usuario=simulacro.cliente,
        tipo='simulacro_propuesto',
        titulo='Nueva Propuesta de Simulacro',
        mensaje=f'Tienes una propuesta de simulacro para el {simulacro.fecha}',
        datos={
            'simulacro_id': simulacro.id,
            'fecha': str(simulacro.fecha),
            'hora': str(simulacro.hora),
            'modalidad': simulacro.modalidad
        },
        url_accion='/simulacros'
    )


def notificar_recomendaciones_listas(recomendacion):
    """Notifica al cliente que sus recomendaciones están listas."""
    return crear_notificacion(
        usuario=recomendacion.simulacro.cliente,
        tipo='recomendaciones_listas',
        titulo='Recomendaciones Disponibles',
        mensaje='Tus recomendaciones de simulacro están listas para revisar',
        datos={'recomendacion_id': recomendacion.id},
        url_accion=f'/simulacros/{recomendacion.simulacro_id}/resumen'
    )
