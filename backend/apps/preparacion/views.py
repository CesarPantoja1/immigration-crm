"""
Views de la app Preparación.
Maneja simulacros, recomendaciones, práctica individual y configuración IA.
"""
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
import io

from .models import Simulacro, Recomendacion, Practica, ConfiguracionIA
from .serializers import (
    SimulacroListSerializer, SimulacroDetailSerializer, SimulacroCompletadoSerializer,
    RecomendacionSerializer, PracticaListSerializer, PracticaDetailSerializer,
    ConfiguracionIASerializer, ConfiguracionIAUpdateSerializer
)
from .services import (
    SimulacroService, RecomendacionService, PracticaService, ConfiguracionIAService
)


# ==============================================================================
# PERMISOS
# ==============================================================================

class EsAsesor(permissions.BasePermission):
    """Verifica que el usuario sea asesor."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'asesor'


class EsCliente(permissions.BasePermission):
    """Verifica que el usuario sea cliente."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'cliente'


# ==============================================================================
# SIMULACROS
# ==============================================================================

class SimulacrosListView(generics.ListAPIView):
    """GET /api/simulacros/ - Lista simulacros según rol del usuario."""
    serializer_class = SimulacroListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        estado = self.request.query_params.get('estado')
        modalidad = self.request.query_params.get('modalidad')
        fecha = self.request.query_params.get('fecha')
        return SimulacroService.listar_simulacros(self.request.user, estado, modalidad, fecha)


class SimulacroDetailView(generics.RetrieveAPIView):
    """GET /api/simulacros/<id>/ - Detalle de simulacro."""
    serializer_class = SimulacroDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return SimulacroService.obtener_simulacro(self.kwargs['pk'], self.request.user)


class DisponibilidadView(APIView):
    """GET /api/simulacros/disponibilidad/ - Verifica disponibilidad del cliente."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        info = SimulacroService.verificar_disponibilidad(request.user)
        return Response(info)


class ContadorSimulacrosView(APIView):
    """GET /api/simulacros/contador/ - Contador de simulacros del cliente."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response(SimulacroService.obtener_contador(request.user))


class SolicitarSimulacroView(APIView):
    """POST /api/simulacros/solicitar/ - Cliente solicita simulacro."""
    permission_classes = [permissions.IsAuthenticated, EsCliente]
    
    def post(self, request):
        from apps.solicitudes.models import Solicitud
        
        solicitud_id = request.data.get('solicitud_id')
        if not solicitud_id:
            return Response({'error': 'Se requiere solicitud_id'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            solicitud = Solicitud.objects.get(pk=solicitud_id, cliente=request.user, is_deleted=False)
        except Solicitud.DoesNotExist:
            return Response({'error': 'Solicitud no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        simulacro, error = SimulacroService.solicitar_simulacro(
            cliente=request.user,
            solicitud=solicitud,
            modalidad=request.data.get('modalidad', 'virtual'),
            fecha_propuesta=request.data.get('fecha_propuesta'),
            hora_propuesta=request.data.get('hora_propuesta'),
            observaciones=request.data.get('observaciones', '')
        )
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'mensaje': 'Simulacro solicitado',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        }, status=status.HTTP_201_CREATED)


class CrearPropuestaView(APIView):
    """POST /api/simulacros/proponer/ - Asesor crea propuesta."""
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request):
        simulacro, error = SimulacroService.crear_propuesta(
            asesor=request.user,
            cliente_id=request.data.get('cliente_id'),
            fecha=request.data.get('fecha'),
            hora=request.data.get('hora'),
            modalidad=request.data.get('modalidad', 'virtual'),
            ubicacion=request.data.get('ubicacion', ''),
            solicitud_id=request.data.get('solicitud_id')
        )
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'mensaje': 'Propuesta creada',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        }, status=status.HTTP_201_CREATED)


class AceptarPropuestaView(APIView):
    """POST /api/simulacros/<id>/aceptar/ - Cliente acepta propuesta."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        success, error = SimulacroService.aceptar_propuesta(simulacro)
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'mensaje': 'Simulacro confirmado',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class ContrapropuestaView(APIView):
    """POST /api/simulacros/<id>/contrapropuesta/ - Cliente sugiere otra fecha."""
    permission_classes = [permissions.IsAuthenticated, EsCliente]
    
    def post(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        success, error = SimulacroService.contrapropuesta(
            simulacro,
            fecha=request.data.get('fecha'),
            hora=request.data.get('hora')
        )
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'mensaje': 'Contrapropuesta enviada',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class CancelarSimulacroView(APIView):
    """POST /api/simulacros/<id>/cancelar/ - Cancela simulacro."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        success, error = SimulacroService.cancelar(simulacro, request.data.get('motivo', ''))
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'mensaje': 'Simulacro cancelado',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class IngresarSalaView(APIView):
    """POST /api/simulacros/<id>/sala-espera/ - Ingresa a sala de espera."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # En DEBUG permitir siempre
        if not settings.DEBUG:
            estados_permitidos = ['confirmado', 'en_sala_espera']
            if simulacro.estado not in estados_permitidos:
                return Response({
                    'error': f'El simulacro no está en estado permitido. Estado actual: {simulacro.estado}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not simulacro.puede_ingresar_sala():
                fecha_simulacro = datetime.combine(simulacro.fecha, simulacro.hora)
                fecha_simulacro = timezone.make_aware(fecha_simulacro)
                tiempo_restante = fecha_simulacro - timezone.now()
                
                if tiempo_restante.total_seconds() > 0:
                    minutos = int(tiempo_restante.total_seconds() / 60)
                    return Response({
                        'error': f'Podrás ingresar 15 minutos antes. Faltan {minutos} minutos.',
                        'tiempo_restante_minutos': minutos
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        if simulacro.estado == 'confirmado':
            simulacro.estado = 'en_sala_espera'
            simulacro.save()
        
        fecha_simulacro = datetime.combine(simulacro.fecha, simulacro.hora)
        fecha_simulacro = timezone.make_aware(fecha_simulacro)
        tiempo_restante = int((fecha_simulacro - timezone.now()).total_seconds() / 60)
        
        return Response({
            'mensaje': 'Has ingresado a la sala de espera',
            'tiempo_restante_minutos': max(0, tiempo_restante),
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class IniciarSimulacroView(APIView):
    """POST /api/simulacros/<id>/iniciar/ - Asesor inicia simulacro."""
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        if simulacro.estado == 'en_progreso':
            return Response({
                'mensaje': 'Simulacro ya está en progreso',
                'simulacro': SimulacroDetailSerializer(simulacro).data
            })
        
        estados_permitidos = ['en_sala_espera']
        if settings.DEBUG:
            estados_permitidos = ['confirmado', 'en_sala_espera']
        
        if simulacro.estado not in estados_permitidos:
            return Response({
                'error': f'El simulacro no está listo para iniciar. Estado actual: {simulacro.estado}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success, error = SimulacroService.iniciar(simulacro)
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        simulacro.grabacion_activa = True
        simulacro.save()
        
        return Response({
            'mensaje': 'Simulacro iniciado',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class FinalizarSimulacroView(APIView):
    """POST /api/simulacros/<id>/finalizar/ - Asesor finaliza simulacro."""
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        success, error = SimulacroService.finalizar(simulacro)
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        simulacro.grabacion_activa = False
        simulacro.notas = request.data.get('notas', '')
        simulacro.save()
        
        # Notificar
        try:
            from apps.notificaciones.services import notificacion_service
            notificacion_service.notificar_simulacion_completada(simulacro)
        except Exception:
            pass
        
        return Response({
            'mensaje': 'Simulacro completado',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class InfoSalaView(APIView):
    """GET /api/simulacros/<id>/sala/ - Info de sala Jitsi."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        import hashlib
        
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        estados_permitidos = ['confirmado', 'en_sala_espera', 'en_progreso']
        if simulacro.estado not in estados_permitidos:
            return Response({
                'error': f'El simulacro no está disponible (estado: {simulacro.estado})'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar nombre de sala Jitsi
        sala_base = f"migrafacil-simulacro-{simulacro.id}-{simulacro.created_at.isoformat()}"
        sala_hash = hashlib.sha256(sala_base.encode()).hexdigest()[:16]
        room_name = f"MigraFacilSimulacro{simulacro.id}Session{sala_hash}"
        
        jitsi_domain = "meet.jit.si"
        user = request.user
        
        # Info del otro participante
        if user.rol == 'cliente':
            otro = {'nombre': simulacro.asesor.nombre_completo() if simulacro.asesor else 'Asesor', 'rol': 'asesor'}
        else:
            otro = {'nombre': simulacro.cliente.nombre_completo() if simulacro.cliente else 'Cliente', 'rol': 'cliente'}
        
        return Response({
            'simulacro_id': simulacro.id,
            'room_name': room_name,
            'jitsi_domain': jitsi_domain,
            'jitsi_url': f"https://{jitsi_domain}/{room_name}",
            'estado': simulacro.estado,
            'modalidad': simulacro.modalidad,
            'fecha': simulacro.fecha,
            'hora': str(simulacro.hora) if simulacro.hora else None,
            'otro_participante': otro,
            'mi_rol': user.rol,
            'mi_nombre': user.nombre_completo(),
            'puede_iniciar': user.rol == 'asesor' and simulacro.estado in ['confirmado', 'en_sala_espera'],
            'en_progreso': simulacro.estado == 'en_progreso',
            'fecha_inicio': simulacro.fecha_inicio,
        })


class EstadoSalaView(APIView):
    """GET /api/simulacros/<id>/estado-sala/ - Estado actual para polling."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'simulacro_id': simulacro.id,
            'estado': simulacro.estado,
            'en_progreso': simulacro.estado == 'en_progreso',
            'en_sala_espera': simulacro.estado == 'en_sala_espera',
            'cliente_en_sala': simulacro.estado in ['en_sala_espera', 'en_progreso'],
            'fecha_inicio': simulacro.fecha_inicio,
            'duracion_actual': int((timezone.now() - simulacro.fecha_inicio).total_seconds()) if simulacro.fecha_inicio else 0
        })


class PropuestasPendientesView(generics.ListAPIView):
    """GET /api/simulacros/propuestas/ - Lista propuestas pendientes.
    
    Para ASESOR: Muestra solicitudes de clientes (estado='solicitado', propuesto_por='cliente')
                 y contrapropuestas pendientes (estado='contrapropuesta')
    Para CLIENTE: Muestra propuestas del asesor (estado='pendiente_respuesta', propuesto_por='asesor')
    """
    serializer_class = SimulacroListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        
        if user.rol == 'asesor':
            # El asesor ve:
            # 1. Solicitudes de clientes (estado='solicitado', propuesto_por='cliente')
            # 2. Contrapropuestas de clientes (estado='contrapropuesta')
            return Simulacro.objects.filter(
                Q(asesor=user, is_deleted=False) &
                (
                    Q(estado='solicitado', propuesto_por='cliente') |
                    Q(estado='contrapropuesta')
                )
            ).order_by('-created_at')
        elif user.rol == 'cliente':
            # El cliente ve propuestas del asesor pendientes de su respuesta
            return Simulacro.objects.filter(
                cliente=user,
                estado='pendiente_respuesta',
                propuesto_por='asesor',
                is_deleted=False
            ).order_by('-created_at')
        else:
            return Simulacro.objects.none()


class SimulacrosCompletadosAsesorView(generics.ListAPIView):
    """GET /api/simulacros/completados/ - Lista simulacros completados (asesor)."""
    serializer_class = SimulacroCompletadoSerializer
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def get_queryset(self):
        return SimulacroService.listar_completados_para_asesor(self.request.user)


# ==============================================================================
# TRANSCRIPCIÓN
# ==============================================================================

class SubirTranscripcionView(APIView):
    """POST /api/simulacros/<id>/transcripcion/ - Sube transcripción."""
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro or simulacro.estado != 'completado':
            return Response({'error': 'Simulacro no encontrado o no completado'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'archivo' not in request.FILES:
            return Response({'error': 'Se requiere un archivo de transcripción (.txt)'}, status=status.HTTP_400_BAD_REQUEST)
        
        archivo = request.FILES['archivo']
        if not archivo.name.endswith('.txt'):
            return Response({'error': 'El archivo debe ser de texto (.txt)'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            contenido = archivo.read().decode('utf-8')
        except UnicodeDecodeError:
            try:
                archivo.seek(0)
                contenido = archivo.read().decode('latin-1')
            except Exception:
                return Response({'error': 'No se pudo leer el archivo'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(contenido.strip()) < 50:
            return Response({'error': 'La transcripción es muy corta (mínimo 50 caracteres)'}, status=status.HTTP_400_BAD_REQUEST)
        
        archivo.seek(0)
        simulacro.transcripcion_archivo = archivo
        simulacro.transcripcion_texto = contenido
        simulacro.save()
        
        return Response({
            'mensaje': 'Transcripción subida exitosamente',
            'simulacro_id': simulacro.id,
            'caracteres': len(contenido),
            'lineas': len(contenido.split('\n'))
        })


# ==============================================================================
# RECOMENDACIONES
# ==============================================================================

class RecomendacionesListView(generics.ListAPIView):
    """GET /api/recomendaciones/ - Lista recomendaciones del cliente."""
    serializer_class = RecomendacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RecomendacionService.listar_para_cliente(self.request.user)


class RecomendacionDetailView(generics.RetrieveAPIView):
    """GET /api/recomendaciones/<id>/ - Detalle de recomendación."""
    serializer_class = RecomendacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return RecomendacionService.obtener_recomendacion(self.kwargs['pk'])


class GenerarRecomendacionView(APIView):
    """POST /api/recomendaciones/generar/ - Genera recomendación manual (asesor)."""
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request):
        simulacro_id = request.data.get('simulacro_id')
        simulacro = SimulacroService.obtener_simulacro(simulacro_id, request.user)
        
        if not simulacro or simulacro.estado != 'completado':
            return Response({'error': 'Simulacro no encontrado o no completado'}, status=status.HTTP_404_NOT_FOUND)
        
        if hasattr(simulacro, 'recomendacion'):
            return Response({'error': 'El simulacro ya tiene recomendaciones'}, status=status.HTTP_400_BAD_REQUEST)
        
        recomendacion = RecomendacionService.crear_o_actualizar(simulacro, request.data)
        recomendacion.publicada = True
        recomendacion.nivel_preparacion = recomendacion.calcular_nivel_preparacion()
        recomendacion.save()
        
        # Notificar
        try:
            from apps.notificaciones.services import notificacion_service
            notificacion_service.notificar_recomendaciones_listas(simulacro)
        except Exception:
            pass
        
        return Response({
            'mensaje': 'Recomendaciones generadas',
            'recomendacion': RecomendacionSerializer(recomendacion).data
        }, status=status.HTTP_201_CREATED)


class GenerarRecomendacionIAView(APIView):
    """POST /api/simulacros/<id>/generar-recomendacion-ia/ - Genera con IA."""
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        
        if not simulacro or simulacro.estado != 'completado':
            return Response({'error': 'Simulacro no encontrado o no completado'}, status=status.HTTP_404_NOT_FOUND)
        
        if not simulacro.transcripcion_texto:
            return Response({
                'error': f'No es posible generar recomendaciones: la transcripción del simulacro SIM-{simulacro.id:03d} no está disponible'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya tiene IA generada
        recomendacion_existente = getattr(simulacro, 'recomendacion', None)
        if recomendacion_existente and recomendacion_existente.analisis_raw and recomendacion_existente.analisis_raw.get('tipo') != 'manual':
            return Response({'error': 'El simulacro ya tiene recomendaciones generadas por IA'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear o reutilizar
        if recomendacion_existente:
            recomendacion = recomendacion_existente
            recomendacion.estado_feedback = 'generando'
            recomendacion.save()
        else:
            recomendacion = Recomendacion.objects.create(simulacro=simulacro, estado_feedback='generando')
        
        tipo_visa = simulacro.solicitud.tipo_visa if simulacro.solicitud else 'general'
        
        try:
            from .ai_service import analizar_simulacro
            resultado = analizar_simulacro(simulacro.transcripcion_texto, tipo_visa, asesor_id=request.user.id)
            
            if not resultado.analisis_completo:
                recomendacion.estado_feedback = 'error'
                recomendacion.error_mensaje = resultado.error or 'Análisis incompleto'
                recomendacion.save()
                
                error_msg = resultado.error or 'Error al procesar'
                if 'API key' in error_msg or 'comunicación' in error_msg.lower():
                    return Response({
                        'error': 'No se ha configurado una API key de IA válida. Por favor, configura tu API key de Gemini.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({'error': f'No es posible generar recomendaciones: {error_msg}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Actualizar recomendación
            recomendacion.claridad = resultado.claridad
            recomendacion.coherencia = resultado.coherencia
            recomendacion.seguridad = resultado.seguridad
            recomendacion.pertinencia = resultado.pertinencia
            recomendacion.nivel_preparacion = resultado.nivel_preparacion
            recomendacion.fortalezas = resultado.fortalezas
            recomendacion.puntos_mejora = resultado.puntos_mejora
            recomendacion.recomendaciones = resultado.recomendaciones
            recomendacion.accion_sugerida = resultado.accion_sugerida
            recomendacion.estado_feedback = 'generado'
            recomendacion.publicada = True
            recomendacion.fecha_publicacion = timezone.now()
            recomendacion.analisis_raw = {
                'claridad': resultado.claridad,
                'coherencia': resultado.coherencia,
                'seguridad': resultado.seguridad,
                'pertinencia': resultado.pertinencia
            }
            recomendacion.save()
            
            simulacro.analisis_ia_completado = True
            simulacro.analisis_ia_fecha = timezone.now()
            simulacro.save()
            
            # Notificar
            try:
                from apps.notificaciones.services import notificacion_service
                notificacion_service.notificar_recomendaciones_listas(simulacro)
            except Exception:
                pass
            
            return Response({
                'mensaje': 'Recomendaciones generadas exitosamente por IA',
                'estado': 'Feedback generado',
                'recomendacion': RecomendacionSerializer(recomendacion).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error en análisis IA: {e}")
            recomendacion.estado_feedback = 'error'
            recomendacion.error_mensaje = str(e)
            recomendacion.save()
            return Response({'error': f'Error al procesar con IA: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecomendacionClienteView(APIView):
    """GET /api/mis-recomendaciones/ o /api/simulacros/<pk>/mi-recomendacion/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk=None):
        user = request.user
        if user.rol != 'cliente':
            return Response({'error': 'Solo los clientes pueden ver sus recomendaciones'}, status=status.HTTP_403_FORBIDDEN)
        
        if pk:
            simulacro = SimulacroService.obtener_simulacro(pk, user)
            if not simulacro:
                return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
            if not hasattr(simulacro, 'recomendacion'):
                return Response({'error': 'Este simulacro aún no tiene recomendaciones'}, status=status.HTTP_404_NOT_FOUND)
            
            rec = simulacro.recomendacion
            return Response({
                'id': rec.id,
                'simulacro_id': simulacro.id,
                'simulacro_fecha': simulacro.fecha,
                'asesor_nombre': simulacro.asesor.get_full_name() if simulacro.asesor else None,
                'fecha_generacion': rec.fecha_generacion,
                'estado_feedback': rec.estado_feedback,
                'nivel_preparacion': rec.nivel_preparacion,
                'claridad': rec.claridad,
                'coherencia': rec.coherencia,
                'seguridad': rec.seguridad,
                'pertinencia': rec.pertinencia,
                'fortalezas': rec.fortalezas,
                'puntos_mejora': rec.puntos_mejora,
                'recomendaciones': rec.recomendaciones,
                'accion_sugerida': rec.accion_sugerida or rec.obtener_accion_sugerida(),
                'resumen_ejecutivo': rec.resumen_ejecutivo,
                'publicada': rec.publicada
            })
        
        # Listar todas las recomendaciones
        simulacros = Simulacro.objects.filter(cliente=user, estado='completado', is_deleted=False).select_related('asesor', 'solicitud')
        
        recomendaciones = []
        for sim in simulacros:
            if hasattr(sim, 'recomendacion') and sim.recomendacion.publicada:
                rec = sim.recomendacion
                recomendaciones.append({
                    'id': rec.id,
                    'simulacro_id': sim.id,
                    'simulacro_fecha': sim.fecha,
                    'asesor_nombre': sim.asesor.get_full_name() if sim.asesor else None,
                    'fecha_generacion': rec.fecha_generacion,
                    'estado_feedback': rec.estado_feedback,
                    'nivel_preparacion': rec.nivel_preparacion,
                    'indicadores': {
                        'claridad': rec.claridad,
                        'coherencia': rec.coherencia,
                        'seguridad': rec.seguridad,
                        'pertinencia': rec.pertinencia
                    },
                    'fortalezas': rec.fortalezas,
                    'puntos_mejora': rec.puntos_mejora,
                    'recomendaciones': rec.recomendaciones,
                    'recomendaciones_por_impacto': rec.organizar_por_impacto(),
                    'accion_sugerida': rec.accion_sugerida or rec.obtener_accion_sugerida(),
                    'resumen_ejecutivo': rec.resumen_ejecutivo
                })
        
        return Response(recomendaciones)


class RecomendacionDetalleClienteView(APIView):
    """GET /api/mis-recomendaciones/<id>/ - Detalle para cliente."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            recomendacion = Recomendacion.objects.select_related(
                'simulacro', 'simulacro__asesor', 'simulacro__solicitud'
            ).get(pk=pk, simulacro__cliente=request.user, publicada=True)
        except Recomendacion.DoesNotExist:
            return Response({'error': 'Recomendación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        sim = recomendacion.simulacro
        
        return Response({
            'id': recomendacion.id,
            'simulacro': {
                'id': sim.id,
                'fecha': sim.fecha,
                'hora': sim.hora,
                'duracion_minutos': sim.duracion_minutos,
                'modalidad': sim.modalidad
            },
            'asesor': {
                'nombre': sim.asesor.get_full_name() if sim.asesor else None,
                'email': sim.asesor.email if sim.asesor else None
            },
            'fecha_generacion': recomendacion.fecha_generacion,
            'estado_feedback': recomendacion.estado_feedback,
            'nivel_preparacion': recomendacion.nivel_preparacion,
            'nivel_preparacion_display': dict(Recomendacion.NIVELES_PREPARACION).get(recomendacion.nivel_preparacion, 'Medio'),
            'indicadores': {
                'claridad': {'valor': recomendacion.claridad, 'label': 'Claridad en respuestas'},
                'coherencia': {'valor': recomendacion.coherencia, 'label': 'Coherencia del discurso'},
                'seguridad': {'valor': recomendacion.seguridad, 'label': 'Seguridad al responder'},
                'pertinencia': {'valor': recomendacion.pertinencia, 'label': 'Pertinencia de la información'}
            },
            'fortalezas': recomendacion.fortalezas,
            'puntos_mejora': recomendacion.puntos_mejora,
            'recomendaciones': recomendacion.recomendaciones,
            'recomendaciones_por_impacto': recomendacion.organizar_por_impacto(),
            'accion_sugerida': recomendacion.accion_sugerida or recomendacion.obtener_accion_sugerida(),
            'resumen_ejecutivo': recomendacion.resumen_ejecutivo
        })


class SimulacroFeedbackView(APIView):
    """POST /api/simulacros/<id>/feedback/ - Feedback manual del asesor."""
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        recomendacion, created = Recomendacion.objects.get_or_create(simulacro=simulacro)
        data = request.data
        
        # Procesar calificación
        calificacion = data.get('overallScore', 3)
        if calificacion >= 4:
            recomendacion.nivel_preparacion = 'alto'
        elif calificacion >= 2:
            recomendacion.nivel_preparacion = 'medio'
        else:
            recomendacion.nivel_preparacion = 'bajo'
        
        # Procesar scores
        scores = data.get('scores', {})
        if scores:
            def score_to_level(avg):
                if avg >= 4: return 'alto'
                elif avg >= 2.5: return 'medio'
                else: return 'bajo'
            
            basic_scores = [v for k, v in scores.items() if k.startswith('basic_')]
            comm_scores = [v for k, v in scores.items() if k.startswith('comm_')]
            interview_scores = [v for k, v in scores.items() if k.startswith('interview_')]
            
            if basic_scores:
                recomendacion.claridad = score_to_level(sum(basic_scores) / len(basic_scores))
            if comm_scores:
                recomendacion.coherencia = score_to_level(sum(comm_scores) / len(comm_scores))
                recomendacion.seguridad = score_to_level(sum(comm_scores) / len(comm_scores))
            if interview_scores:
                recomendacion.pertinencia = score_to_level(sum(interview_scores) / len(interview_scores))
        
        # Checklist
        checklist = data.get('checklist', {})
        fortalezas = []
        puntos_mejora = []
        
        for item_id, completado in checklist.items():
            item_data = {'categoria': 'general', 'descripcion': item_id.replace('_', ' ').title(), 'impacto': 'medio'}
            if completado:
                fortalezas.append(item_data)
            else:
                puntos_mejora.append(item_data)
        
        if fortalezas:
            recomendacion.fortalezas = fortalezas
        if puntos_mejora:
            recomendacion.puntos_mejora = puntos_mejora
        
        # Notas
        notas = data.get('notes', '')
        recomendaciones_texto = data.get('recommendations', '')
        
        if notas or recomendaciones_texto:
            recomendacion.resumen_ejecutivo = f"{notas}\n\n{recomendaciones_texto}".strip()
        
        if recomendaciones_texto:
            recomendacion.recomendaciones = [{
                'categoria': 'general',
                'titulo': 'Recomendaciones del Asesor',
                'descripcion': recomendaciones_texto,
                'impacto': 'alto',
                'accion_concreta': recomendaciones_texto
            }]
        
        recomendacion.accion_sugerida = recomendacion.obtener_accion_sugerida()
        # IMPORTANTE: El feedback manual NO debe marcar como 'generado'
        # Solo la generación con IA debe poner estado_feedback = 'generado'
        # El estado se mantiene como está o se pone 'pendiente' si es nuevo
        if created:
            recomendacion.estado_feedback = 'pendiente'
        recomendacion.publicada = True
        recomendacion.fecha_publicacion = timezone.now()
        recomendacion.analisis_raw = {
            'tipo': 'manual',
            'asesor_id': request.user.id,
            'fecha': timezone.now().isoformat(),
            'data_original': data
        }
        recomendacion.save()
        
        return Response({'mensaje': 'Feedback guardado correctamente', 'recomendacion_id': recomendacion.id})


# ==============================================================================
# PDF EXPORT
# ==============================================================================

class DescargarPDFRecomendacionView(APIView):
    """GET /api/recomendaciones/<id>/descargar-pdf/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            recomendacion = Recomendacion.objects.select_related(
                'simulacro', 'simulacro__cliente', 'simulacro__asesor', 'simulacro__solicitud'
            ).get(pk=pk)
        except Recomendacion.DoesNotExist:
            return Response({'error': 'Recomendación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        simulacro = recomendacion.simulacro
        
        if user.rol == 'cliente' and simulacro.cliente != user:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        elif user.rol == 'asesor' and simulacro.asesor != user:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que la recomendación IA haya sido generada exitosamente
        if recomendacion.estado_feedback != 'generado':
            return Response(
                {'error': 'Este simulacro no tiene recomendaciones generadas. La IA aún no ha procesado este simulacro.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return self._generar_pdf(recomendacion)
    
    def _generar_pdf(self, recomendacion):
        simulacro = recomendacion.simulacro
        
        context = {
            'recomendacion': recomendacion,
            'simulacro': simulacro,
            'cliente': simulacro.cliente,
            'asesor': simulacro.asesor,
            'fecha_generacion': recomendacion.fecha_generacion,
            'nivel_preparacion': dict(Recomendacion.NIVELES_PREPARACION).get(recomendacion.nivel_preparacion, 'Medio'),
            'indicadores': {
                'Claridad en respuestas': recomendacion.claridad,
                'Coherencia del discurso': recomendacion.coherencia,
                'Seguridad al responder': recomendacion.seguridad,
                'Pertinencia de la información': recomendacion.pertinencia,
            },
            'fortalezas': recomendacion.fortalezas,
            'puntos_mejora': recomendacion.puntos_mejora,
            'recomendaciones': recomendacion.recomendaciones,
            'accion_sugerida': recomendacion.accion_sugerida or recomendacion.obtener_accion_sugerida(),
            'resumen_ejecutivo': recomendacion.resumen_ejecutivo,
        }
        
        try:
            from weasyprint import HTML
            html_content = render_to_string('recomendaciones/pdf_recomendacion.html', context)
            pdf_file = io.BytesIO()
            HTML(string=html_content).write_pdf(pdf_file)
            pdf_file.seek(0)
            
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="recomendacion_simulacro_{simulacro.id}.pdf"'
            return response
        except ImportError:
            html_content = render_to_string('recomendaciones/pdf_recomendacion.html', context)
            response = HttpResponse(html_content, content_type='text/html')
            response['Content-Disposition'] = f'inline; filename="recomendacion_simulacro_{simulacro.id}.html"'
            return response


class DescargarPDFSimulacroView(DescargarPDFRecomendacionView):
    """GET /api/simulacros/<id>/descargar-pdf/"""
    
    def get(self, request, pk):
        simulacro = SimulacroService.obtener_simulacro(pk, request.user)
        if not simulacro:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar que exista la recomendación
        if not hasattr(simulacro, 'recomendacion'):
            return Response({'error': 'Este simulacro no tiene recomendaciones'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar que la recomendación IA haya sido generada exitosamente
        if simulacro.recomendacion.estado_feedback != 'generado':
            return Response(
                {'error': 'Este simulacro no tiene recomendaciones generadas. La IA aún no ha procesado este simulacro.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return self._generar_pdf(simulacro.recomendacion)


# ==============================================================================
# PRÁCTICA INDIVIDUAL
# ==============================================================================

# Banco de preguntas por tipo de visa
BANCO_PREGUNTAS = {
    'estudiante': [
        {'id': 1, 'pregunta': '¿Cuál es el propósito principal de tu viaje?', 'respuesta_correcta': 'estudiar'},
        {'id': 2, 'pregunta': '¿En qué institución estudiarás?', 'respuesta_correcta': 'universidad'},
        {'id': 3, 'pregunta': '¿Cómo financiarás tus estudios?', 'respuesta_correcta': 'beca'},
        {'id': 4, 'pregunta': '¿Cuánto tiempo durará tu programa?', 'respuesta_correcta': 'semestres'},
        {'id': 5, 'pregunta': '¿Qué carrera estudiarás?', 'respuesta_correcta': 'carrera'},
        {'id': 6, 'pregunta': '¿Tienes familia en el país de destino?', 'respuesta_correcta': 'no'},
        {'id': 7, 'pregunta': '¿Dónde vivirás durante tus estudios?', 'respuesta_correcta': 'dormitorio'},
        {'id': 8, 'pregunta': '¿Cuáles son tus planes después de graduarte?', 'respuesta_correcta': 'regresar'},
        {'id': 9, 'pregunta': '¿Por qué elegiste este país para estudiar?', 'respuesta_correcta': 'calidad'},
        {'id': 10, 'pregunta': '¿Has viajado antes al extranjero?', 'respuesta_correcta': 'si'},
    ],
    'trabajo': [
        {'id': 1, 'pregunta': '¿Cuál es tu profesión?', 'respuesta_correcta': 'profesion'},
        {'id': 2, 'pregunta': '¿Qué empresa te contrató?', 'respuesta_correcta': 'empresa'},
        {'id': 3, 'pregunta': '¿Cuál será tu puesto?', 'respuesta_correcta': 'puesto'},
        {'id': 4, 'pregunta': '¿Cuánto ganarás?', 'respuesta_correcta': 'salario'},
        {'id': 5, 'pregunta': '¿Cuánto durará tu contrato?', 'respuesta_correcta': 'duracion'},
        {'id': 6, 'pregunta': '¿Tienes experiencia en el área?', 'respuesta_correcta': 'si'},
        {'id': 7, 'pregunta': '¿Por qué te eligieron a ti?', 'respuesta_correcta': 'calificado'},
        {'id': 8, 'pregunta': '¿Tu familia te acompañará?', 'respuesta_correcta': 'no'},
        {'id': 9, 'pregunta': '¿Dónde vivirás?', 'respuesta_correcta': 'ciudad'},
        {'id': 10, 'pregunta': '¿Cuáles son tus planes a largo plazo?', 'respuesta_correcta': 'regresar'},
    ],
    'turismo': [
        {'id': 1, 'pregunta': '¿Cuál es el propósito de tu viaje?', 'respuesta_correcta': 'turismo'},
        {'id': 2, 'pregunta': '¿Cuántos días estarás?', 'respuesta_correcta': 'dias'},
        {'id': 3, 'pregunta': '¿Dónde te hospedarás?', 'respuesta_correcta': 'hotel'},
        {'id': 4, 'pregunta': '¿Cuánto dinero llevas?', 'respuesta_correcta': 'dinero'},
        {'id': 5, 'pregunta': '¿Qué lugares visitarás?', 'respuesta_correcta': 'lugares'},
        {'id': 6, 'pregunta': '¿Viajas solo o acompañado?', 'respuesta_correcta': 'acompanado'},
        {'id': 7, 'pregunta': '¿Tienes trabajo en tu país?', 'respuesta_correcta': 'si'},
        {'id': 8, 'pregunta': '¿A qué te dedicas?', 'respuesta_correcta': 'profesion'},
        {'id': 9, 'pregunta': '¿Tienes propiedades en tu país?', 'respuesta_correcta': 'si'},
        {'id': 10, 'pregunta': '¿Cuándo regresarás?', 'respuesta_correcta': 'fecha'},
    ],
    'vivienda': [
        {'id': 1, 'pregunta': '¿Por qué deseas residir en este país?', 'respuesta_correcta': 'calidad'},
        {'id': 2, 'pregunta': '¿Tienes propiedad en el país?', 'respuesta_correcta': 'si'},
        {'id': 3, 'pregunta': '¿Cuál es el valor de tu propiedad?', 'respuesta_correcta': 'valor'},
        {'id': 4, 'pregunta': '¿Cómo adquiriste la propiedad?', 'respuesta_correcta': 'compra'},
        {'id': 5, 'pregunta': '¿Tienes ingresos suficientes?', 'respuesta_correcta': 'si'},
        {'id': 6, 'pregunta': '¿De dónde provienen tus ingresos?', 'respuesta_correcta': 'inversiones'},
        {'id': 7, 'pregunta': '¿Tu familia te acompañará?', 'respuesta_correcta': 'si'},
        {'id': 8, 'pregunta': '¿Tienes seguro médico?', 'respuesta_correcta': 'si'},
        {'id': 9, 'pregunta': '¿Hablas el idioma local?', 'respuesta_correcta': 'basico'},
        {'id': 10, 'pregunta': '¿Mantienes vínculos con tu país?', 'respuesta_correcta': 'si'},
    ],
}


class TiposVisaPracticaView(APIView):
    """GET /api/practica/tipos-visa/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        tipos = [
            {'codigo': 'estudiante', 'nombre': 'Visa de Estudiante', 'preguntas': 10},
            {'codigo': 'trabajo', 'nombre': 'Visa de Trabajo', 'preguntas': 10},
            {'codigo': 'turismo', 'nombre': 'Visa de Turismo', 'preguntas': 10},
            {'codigo': 'vivienda', 'nombre': 'Visa de Vivienda', 'preguntas': 10},
        ]
        return Response(tipos)


class IniciarPracticaView(APIView):
    """POST /api/practica/iniciar/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        tipo_visa = request.data.get('tipo_visa')
        
        if tipo_visa not in BANCO_PREGUNTAS:
            return Response({'error': 'Tipo de visa no válido'}, status=status.HTTP_400_BAD_REQUEST)
        
        practica = Practica.objects.create(
            cliente=request.user,
            tipo_visa=tipo_visa,
            total_preguntas=len(BANCO_PREGUNTAS[tipo_visa])
        )
        
        preguntas = [{'id': p['id'], 'pregunta': p['pregunta']} for p in BANCO_PREGUNTAS[tipo_visa]]
        
        return Response({
            'practica_id': practica.id,
            'tipo_visa': tipo_visa,
            'preguntas': preguntas
        }, status=status.HTTP_201_CREATED)


class FinalizarPracticaView(APIView):
    """POST /api/practica/<id>/finalizar/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            practica = Practica.objects.get(pk=pk, cliente=request.user, completado=False)
        except Practica.DoesNotExist:
            return Response({'error': 'Práctica no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        respuestas = request.data.get('respuestas', [])
        preguntas = BANCO_PREGUNTAS.get(practica.tipo_visa, [])
        
        correctas = 0
        resultado_detalle = []
        
        for resp in respuestas:
            pregunta_id = resp.get('pregunta_id')
            respuesta_usuario = resp.get('respuesta', '').lower()
            
            pregunta = next((p for p in preguntas if p['id'] == pregunta_id), None)
            if pregunta:
                es_correcta = pregunta['respuesta_correcta'] in respuesta_usuario
                if es_correcta:
                    correctas += 1
                
                resultado_detalle.append({
                    'pregunta_id': pregunta_id,
                    'pregunta': pregunta['pregunta'],
                    'respuesta_usuario': resp.get('respuesta'),
                    'es_correcta': es_correcta,
                    'respuesta_correcta': pregunta['respuesta_correcta']
                })
        
        practica.respuestas = resultado_detalle
        practica.respuestas_correctas = correctas
        practica.completado = True
        practica.fecha_completado = timezone.now()
        practica.calcular_resultado()
        
        mensajes = {
            'excelente': '¡Muy bien! Estás muy preparado',
            'bueno': 'Buen trabajo, repasa las preguntas incorrectas',
            'regular': 'Necesitas practicar más antes del simulacro real',
            'insuficiente': 'Te recomendamos estudiar más este tema'
        }
        
        return Response({
            'practica': PracticaDetailSerializer(practica).data,
            'mensaje': mensajes.get(practica.calificacion, '')
        })


class HistorialPracticaView(generics.ListAPIView):
    """GET /api/practica/historial/"""
    serializer_class = PracticaListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Practica.objects.filter(cliente=self.request.user, completado=True).order_by('-fecha_completado')


class EstadisticasPracticaView(APIView):
    """GET /api/practica/estadisticas/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response(PracticaService.obtener_estadisticas(request.user))


# ==============================================================================
# CONFIGURACIÓN IA
# ==============================================================================

class ConfiguracionIAView(APIView):
    """GET/POST/PUT/DELETE /api/configuracion-ia/"""
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def get(self, request):
        config = ConfiguracionIAService.obtener_configuracion(request.user)
        if config:
            return Response({
                'configurado': True,
                'configuracion': ConfiguracionIASerializer(config).data,
                'modelos_disponibles': dict(ConfiguracionIA.MODELOS_GEMINI)
            })
        return Response({
            'configurado': False,
            'configuracion': None,
            'modelos_disponibles': dict(ConfiguracionIA.MODELOS_GEMINI)
        })
    
    def post(self, request):
        serializer = ConfiguracionIASerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            config = serializer.save()
            return Response({
                'mensaje': 'Configuración guardada exitosamente',
                'configuracion': ConfiguracionIASerializer(config).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        config = ConfiguracionIAService.obtener_configuracion(request.user)
        if not config:
            return Response({'error': 'No tienes configuración de IA'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ConfiguracionIAUpdateSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Configuración actualizada exitosamente',
                'configuracion': ConfiguracionIASerializer(config).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        config = ConfiguracionIAService.obtener_configuracion(request.user)
        if not config:
            return Response({'error': 'No tienes configuración de IA'}, status=status.HTTP_404_NOT_FOUND)
        config.delete()
        return Response({'mensaje': 'Configuración eliminada'})


class TestAPIKeyView(APIView):
    """POST /api/configuracion-ia/test/"""
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request):
        import requests
        
        api_key = request.data.get('api_key')
        modelo = request.data.get('modelo', 'gemini-2.5-flash')
        
        if not api_key:
            return Response({'error': 'Se requiere api_key'}, status=status.HTTP_400_BAD_REQUEST)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": "Responde solo con: OK"}]}],
            "generationConfig": {"maxOutputTokens": 10, "temperature": 0}
        }
        
        try:
            response = requests.post(f"{url}?key={api_key}", json=payload, timeout=10)
            
            if response.status_code == 200:
                return Response({'valida': True, 'mensaje': f'API key válida para el modelo {modelo}', 'modelo': modelo})
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Error desconocido')
                return Response({'valida': False, 'mensaje': f'Error: {error_msg}', 'codigo': response.status_code}, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.Timeout:
            return Response({'valida': False, 'mensaje': 'Tiempo de espera agotado'}, status=status.HTTP_408_REQUEST_TIMEOUT)
        except Exception as e:
            return Response({'valida': False, 'mensaje': f'Error de conexión: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# DEBUG
# ==============================================================================

class DebugUserInfoView(APIView):
    """Endpoint de debug para verificar información del usuario actual."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not settings.DEBUG:
            return Response({'error': 'Solo disponible en modo DEBUG'}, status=403)
        
        user = request.user
        return Response({
            'id': user.id,
            'email': user.email,
            'rol': user.rol,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'es_asesor_check': user.rol == 'asesor',
            'es_admin_check': user.rol == 'admin',
            'es_cliente_check': user.rol == 'cliente',
        })
