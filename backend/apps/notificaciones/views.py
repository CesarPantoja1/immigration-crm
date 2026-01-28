"""
Views para el módulo de Notificaciones.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone

from .models import Notificacion, PreferenciaNotificacion
from .serializers import (
    NotificacionSerializer,
    NotificacionListSerializer,
    PreferenciaNotificacionSerializer,
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
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
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
