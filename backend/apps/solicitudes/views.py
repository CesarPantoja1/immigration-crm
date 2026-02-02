"""
Views para la API de Solicitudes, Documentos y Entrevistas.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
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
from .services import SolicitudService, DocumentoService, EntrevistaService

# Importar servicio de notificaciones
from apps.notificaciones.services import NotificacionService

Usuario = get_user_model()


# =====================================================
# PERMISOS PERSONALIZADOS
# =====================================================

class EsAsesorOAdmin(permissions.BasePermission):
    """Solo permite acceso a asesores y admins."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.rol in ['asesor', 'admin']


# =====================================================
# VISTAS DE SOLICITUDES - CLIENTE
# =====================================================

class MisSolicitudesView(generics.ListAPIView):
    """
    GET /api/solicitudes/mis-solicitudes/
    Lista las solicitudes del usuario autenticado.
    """
    serializer_class = SolicitudListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SolicitudService.listar_solicitudes(self.request.user)


class CrearSolicitudView(generics.CreateAPIView):
    """
    POST /api/solicitudes/nueva/
    Crea una nueva solicitud.
    """
    serializer_class = SolicitudCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        solicitud = serializer.save()
        try:
            NotificacionService.notificar_solicitud_creada(solicitud)
        except Exception as e:
            print(f"Error creando notificación: {e}")


class SolicitudDetailView(generics.RetrieveAPIView):
    """
    GET /api/solicitudes/<id>/
    Obtiene el detalle de una solicitud.
    """
    serializer_class = SolicitudDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SolicitudService.listar_solicitudes(self.request.user)


class EnviarSolicitudView(APIView):
    """
    POST /api/solicitudes/<id>/enviar/
    Envía una solicitud (cambia de borrador a pendiente).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        solicitud = SolicitudService.obtener_solicitud(pk, request.user)
        
        if not solicitud:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        success, error = SolicitudService.enviar_solicitud(solicitud)
        
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            NotificacionService.crear_notificacion_general(
                usuario=request.user,
                titulo='Solicitud enviada correctamente',
                mensaje=f'Tu solicitud de visa {solicitud.get_tipo_visa_display()} está pendiente de revisión.',
                url_accion=f'/solicitudes/{solicitud.id}'
            )
        except Exception:
            pass
        
        return Response({
            'mensaje': 'Solicitud enviada exitosamente',
            'solicitud': SolicitudDetailSerializer(solicitud).data
        })


# =====================================================
# VISTAS DE SOLICITUDES - ASESOR
# =====================================================

class SolicitudesAsignadasView(generics.ListAPIView):
    """
    GET /api/solicitudes/asignadas/
    Lista las solicitudes asignadas al asesor.
    """
    serializer_class = SolicitudDetailSerializer
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def get_queryset(self):
        estado = self.request.query_params.get('estado')
        tipo_visa = self.request.query_params.get('tipo_visa')
        return SolicitudService.listar_solicitudes(self.request.user, estado, tipo_visa)


class SolicitudesPendientesView(generics.ListAPIView):
    """
    GET /api/solicitudes/pendientes/
    Lista solicitudes pendientes de asignación.
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
    Actualiza el estado y notas de una solicitud.
    """
    serializer_class = SolicitudUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def get_queryset(self):
        return SolicitudService.listar_solicitudes(self.request.user)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        
        # Notificaciones según el estado
        try:
            if instance.estado == 'aprobada':
                NotificacionService.notificar_solicitud_aprobada(instance)
            elif instance.estado == 'rechazada':
                motivo = serializer.validated_data.get('observaciones', '')
                NotificacionService.notificar_solicitud_rechazada(instance, motivo)
            elif instance.estado == 'en_revision':
                NotificacionService.notificar_solicitud_en_revision(instance)
            elif instance.estado == 'enviada_embajada':
                NotificacionService.notificar_solicitud_enviada_embajada(instance)
        except Exception as e:
            print(f"Error creando notificación: {e}")


class AsignarAsesorView(APIView):
    """
    POST /api/solicitudes/<id>/asignar/
    Asigna un asesor a una solicitud.
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def post(self, request, pk):
        solicitud = SolicitudService.obtener_solicitud(pk)
        
        if not solicitud:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AsignarAsesorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        success, error = SolicitudService.asignar_asesor(
            solicitud, 
            serializer.validated_data['asesor_id']
        )
        
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            NotificacionService.notificar_solicitud_asignada(solicitud)
        except Exception:
            pass
        
        return Response({
            'mensaje': f'Solicitud asignada a {solicitud.asesor.nombre_completo()}',
            'solicitud': SolicitudDetailSerializer(solicitud).data
        })


# =====================================================
# ESTADÍSTICAS
# =====================================================

class EstadisticasClienteView(APIView):
    """GET /api/solicitudes/estadisticas/cliente/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response(SolicitudService.obtener_estadisticas_cliente(request.user))


class EstadisticasAsesorView(APIView):
    """GET /api/solicitudes/estadisticas/asesor/"""
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def get(self, request):
        return Response(SolicitudService.obtener_estadisticas_asesor(request.user))


# =====================================================
# VISTAS DE DOCUMENTOS
# =====================================================

class SubirDocumentoView(APIView):
    """
    POST /api/solicitudes/<id>/documentos/
    Sube un documento a una solicitud.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        solicitud = SolicitudService.obtener_solicitud(pk, request.user)
        
        if not solicitud:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        archivo = request.FILES.get('archivo')
        nombre = request.data.get('nombre', 'Documento')
        
        if not archivo:
            return Response({'error': 'No se ha enviado ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)
        
        documento = DocumentoService.subir_documento(solicitud, archivo, nombre)
        
        try:
            NotificacionService.notificar_documento_subido(documento, solicitud)
        except Exception:
            pass
        
        return Response({
            'mensaje': 'Documento subido exitosamente',
            'documento': DocumentoSerializer(documento, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class ListarDocumentosSolicitudView(generics.ListAPIView):
    """
    GET /api/solicitudes/<id>/documentos/lista/
    Lista documentos de una solicitud.
    """
    serializer_class = DocumentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DocumentoService.listar_documentos(
            self.kwargs.get('pk'),
            self.request.user
        )


class DocumentoDetailView(generics.RetrieveAPIView):
    """GET /api/documentos/<id>/"""
    serializer_class = DocumentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return DocumentoService.obtener_documento(self.kwargs['pk'], self.request.user)


class AprobarDocumentoView(APIView):
    """
    PATCH /api/documentos/<id>/aprobar/

    IDEMPOTENTE: Permite re-aprobar documentos mientras la solicitud
    este en revision (no enviada a embajada).
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]

    def patch(self, request, pk):
        documento = DocumentoService.obtener_documento(pk, request.user)

        if not documento:
            return Response({'error': 'Documento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        success, error = DocumentoService.aprobar_documento(documento, request.user)

        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            NotificacionService.notificar_documento_aprobado(documento, documento.solicitud)
        except Exception:
            pass

        return Response({
            'mensaje': 'Documento aprobado exitosamente',
            'documento': DocumentoSerializer(documento, context={'request': request}).data
        })


class RechazarDocumentoView(APIView):
    """
    PATCH /api/documentos/<id>/rechazar/

    IDEMPOTENTE: Permite re-evaluar documentos mientras la solicitud
    este en revision (no enviada a embajada).
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]

    def patch(self, request, pk):
        documento = DocumentoService.obtener_documento(pk, request.user)

        if not documento:
            return Response({'error': 'Documento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        motivo = request.data.get('motivo_rechazo', '')
        if not motivo:
            return Response({'error': 'Debe proporcionar un motivo de rechazo'}, status=status.HTTP_400_BAD_REQUEST)

        success, error = DocumentoService.rechazar_documento(documento, request.user, motivo)

        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            NotificacionService.notificar_documento_rechazado(documento, documento.solicitud, motivo)
        except Exception:
            pass

        return Response({
            'mensaje': 'Documento rechazado',
            'documento': DocumentoSerializer(documento, context={'request': request}).data
        })


class ResubirDocumentoView(APIView):
    """
    POST /api/documentos/<id>/resubir/

    Permite al CLIENTE resubir un documento que fue rechazado.
    El documento vuelve a estado 'pendiente' para nueva revisión.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        # Solo el cliente dueño de la solicitud puede resubir
        documento = DocumentoService.obtener_documento(pk, request.user)

        if not documento:
            return Response(
                {'error': 'Documento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar que el usuario es el cliente de la solicitud
        if request.user.rol == 'cliente' and documento.solicitud.cliente != request.user:
            return Response(
                {'error': 'No tienes permiso para modificar este documento'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener el nuevo archivo
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response(
                {'error': 'Debe proporcionar un archivo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success, error = DocumentoService.resubir_documento(documento, archivo)

        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        # Notificar al asesor que el documento fue resubido
        try:
            NotificacionService.notificar_documento_subido(documento, documento.solicitud)
        except Exception:
            pass

        return Response({
            'mensaje': 'Documento resubido exitosamente. Pendiente de nueva revisión.',
            'documento': DocumentoSerializer(documento, context={'request': request}).data
        })


# =====================================================
# VISTAS DE ENTREVISTAS
# =====================================================

class EntrevistasListView(APIView):
    """GET /api/entrevistas/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        estado = request.query_params.get('estado')
        entrevistas = EntrevistaService.listar_entrevistas(request.user, estado)
        
        data = [{
            'id': e.id,
            'solicitud_id': e.solicitud_id,
            'solicitud_tipo': e.solicitud.get_tipo_visa_display(),
            'cliente_nombre': e.solicitud.cliente.nombre_completo(),
            'fecha': e.fecha,
            'hora': e.hora,
            'ubicacion': e.ubicacion,
            'estado': e.estado,
            'estado_display': e.get_estado_display(),
            'veces_reprogramada': e.veces_reprogramada,
        } for e in entrevistas]
        
        return Response(data)


class EntrevistaDetailView(APIView):
    """GET /api/entrevistas/<id>/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        entrevista = EntrevistaService.obtener_entrevista(pk, request.user)
        
        if not entrevista:
            return Response({'error': 'Entrevista no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'id': entrevista.id,
            'solicitud_id': entrevista.solicitud_id,
            'solicitud_tipo': entrevista.solicitud.get_tipo_visa_display(),
            'embajada': entrevista.solicitud.embajada,
            'cliente': {
                'id': entrevista.solicitud.cliente.id,
                'nombre': entrevista.solicitud.cliente.nombre_completo(),
                'email': entrevista.solicitud.cliente.email,
            },
            'fecha': entrevista.fecha,
            'hora': entrevista.hora,
            'ubicacion': entrevista.ubicacion,
            'estado': entrevista.estado,
            'estado_display': entrevista.get_estado_display(),
            'veces_reprogramada': entrevista.veces_reprogramada,
            'notas': entrevista.notas,
            'created_at': entrevista.created_at,
        })


class HorariosDisponiblesView(APIView):
    """GET /api/entrevistas/horarios/?fecha=YYYY-MM-DD"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        fecha = request.query_params.get('fecha')
        
        if not fecha:
            return Response({'error': 'Fecha es requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        horarios = EntrevistaService.obtener_horarios_disponibles(fecha)
        return Response({'fecha': fecha, 'horarios': horarios})


class AgendarEntrevistaView(APIView):
    """
    POST /api/entrevistas/agendar/
    
    Agenda una entrevista consular para una solicitud.
    
    FLUJO REQUERIDO:
    1. Asesor aprueba solicitud (revisa documentos)
    2. Asesor envía solicitud a embajada
    3. Asesor registra decisión de embajada (aprobada/rechazada)
    4. Si embajada aprueba -> estado 'aprobada_embajada'
    5. SOLO ENTONCES se puede agendar entrevista
    
    La solicitud DEBE estar en estado 'aprobada_embajada' para poder agendar.
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def post(self, request):
        solicitud_id = request.data.get('solicitud_id')
        fecha = request.data.get('fecha')
        hora = request.data.get('hora')
        ubicacion = request.data.get('ubicacion', '')
        
        if not all([solicitud_id, fecha, hora]):
            return Response({'error': 'solicitud_id, fecha y hora son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        solicitud = SolicitudService.obtener_solicitud(solicitud_id)
        if not solicitud:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        entrevista, error = EntrevistaService.agendar(solicitud, fecha, hora, ubicacion)
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            NotificacionService.notificar_entrevista_agendada(solicitud, fecha, hora)
        except Exception:
            pass
        
        return Response({
            'mensaje': f'Entrevista agendada para el {fecha} a las {hora}',
            'entrevista': {
                'id': entrevista.id,
                'fecha': entrevista.fecha,
                'hora': entrevista.hora,
                'estado': entrevista.estado,
            }
        }, status=status.HTTP_201_CREATED)


class ConfirmarEntrevistaView(APIView):
    """POST /api/entrevistas/<id>/confirmar/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        entrevista = EntrevistaService.obtener_entrevista(pk, request.user)
        
        if not entrevista:
            return Response({'error': 'Entrevista no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        success, error = EntrevistaService.confirmar(entrevista)
        
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'mensaje': 'Entrevista confirmada exitosamente'})


class ReprogramarEntrevistaView(APIView):
    """POST /api/entrevistas/<id>/reprogramar/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        entrevista = EntrevistaService.obtener_entrevista(pk, request.user)
        
        if not entrevista:
            return Response({'error': 'Entrevista no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        nueva_fecha = request.data.get('fecha')
        nueva_hora = request.data.get('hora')
        
        if not nueva_fecha or not nueva_hora:
            return Response({'error': 'Nueva fecha y hora son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        
        success, error = EntrevistaService.reprogramar(entrevista, nueva_fecha, nueva_hora)
        
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'mensaje': 'Entrevista reprogramada exitosamente'})


class VerificarReprogramacionView(APIView):
    """GET /api/entrevistas/<id>/puede-reprogramar/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        entrevista = EntrevistaService.obtener_entrevista(pk, request.user)
        
        if not entrevista:
            return Response({'error': 'Entrevista no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        _, info = EntrevistaService.puede_reprogramar(entrevista)
        return Response(info)


class CancelarEntrevistaView(APIView):
    """POST /api/entrevistas/<id>/cancelar/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        entrevista = EntrevistaService.obtener_entrevista(pk, request.user)
        
        if not entrevista:
            return Response({'error': 'Entrevista no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        motivo = request.data.get('motivo', '')
        success, error = EntrevistaService.cancelar(entrevista, motivo)
        
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'mensaje': 'Cancelación confirmada exitosamente'})


class VerificarCancelacionView(APIView):
    """GET /api/entrevistas/<id>/puede-cancelar/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        entrevista = EntrevistaService.obtener_entrevista(pk, request.user)
        
        if not entrevista:
            return Response({'error': 'Entrevista no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        _, info = EntrevistaService.puede_cancelar(entrevista)
        return Response(info)


class EntrevistasProximasView(APIView):
    """GET /api/entrevistas/proximas/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        dias = int(request.query_params.get('dias', 7))
        entrevistas = EntrevistaService.obtener_proximas(request.user, dias)
        
        data = [{
            'id': e.id,
            'fecha': e.fecha,
            'hora': e.hora,
            'cliente_nombre': e.solicitud.cliente.nombre_completo(),
            'tipo_visa': e.solicitud.get_tipo_visa_display(),
            'estado': e.estado,
        } for e in entrevistas]
        
        return Response(data)


class CalendarioEventosView(APIView):
    """GET /api/entrevistas/calendario/?mes=YYYY-MM o ?fecha_inicio=&fecha_fin="""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from calendar import monthrange
        
        # Soportar tanto mes como fecha_inicio/fecha_fin
        mes = request.query_params.get('mes')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        # Si se pasa mes, calcular fecha_inicio y fecha_fin
        if mes and not (fecha_inicio and fecha_fin):
            try:
                year, month = mes.split('-')
                year, month = int(year), int(month)
                _, last_day = monthrange(year, month)
                fecha_inicio = f"{year}-{month:02d}-01"
                fecha_fin = f"{year}-{month:02d}-{last_day}"
            except (ValueError, AttributeError):
                pass

        entrevistas = EntrevistaService.obtener_eventos_calendario(
            request.user, fecha_inicio, fecha_fin
        )

        eventos = [{
            'id': e.id,
            'title': f"{e.solicitud.cliente.nombre_completo()} - {e.solicitud.get_tipo_visa_display()}",
            'start': f"{e.fecha}T{e.hora}",
            'fecha': str(e.fecha),
            'hora': str(e.hora)[:5],  # HH:MM
            'tipo': 'entrevista',
            'estado': e.estado,
            'ubicacion': e.ubicacion,
            'cliente_nombre': e.solicitud.cliente.nombre_completo(),
            'asesor_nombre': e.solicitud.asesor.nombre_completo() if e.solicitud.asesor else None,
            'tipo_visa': e.solicitud.get_tipo_visa_display(),
            'embajada': e.solicitud.get_embajada_display(),
            'solicitud_id': e.solicitud.id,
        } for e in entrevistas]

        return Response(eventos)


# =====================================================
# DECISION DE EMBAJADA (NUEVO)
# =====================================================

class DecisionEmbajadaView(APIView):
    """
    POST /api/solicitudes/<id>/decision-embajada/

    Registra la decision de la embajada sobre una solicitud.
    Solo asesores y admins pueden registrar esta decision.

    Body:
        decision: 'aprobada' | 'rechazada'
        motivo: string (requerido si decision es 'rechazada')
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]

    def post(self, request, pk):
        solicitud = SolicitudService.obtener_solicitud(pk)

        if not solicitud:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        decision = request.data.get('decision')
        motivo = request.data.get('motivo', '')

        if decision not in ['aprobada', 'rechazada']:
            return Response(
                {'error': 'Decision debe ser "aprobada" o "rechazada"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success, error = SolicitudService.registrar_decision_embajada(
            solicitud, decision, motivo
        )

        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        # Notificar al cliente con notificaciones específicas
        try:
            if decision == 'aprobada':
                NotificacionService.notificar_embajada_aprobada(solicitud)
            else:
                NotificacionService.notificar_embajada_rechazada(solicitud, motivo)
        except Exception as e:
            print(f"Error creando notificación de embajada: {e}")

        return Response({
            'mensaje': f'Decision de embajada registrada: {decision}',
            'solicitud': SolicitudDetailSerializer(solicitud).data
        })
