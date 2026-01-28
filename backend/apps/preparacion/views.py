"""
Views para el módulo de Preparación (Simulacros).
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

from .models import Simulacro, Recomendacion, Practica
from .serializers import (
    SimulacroListSerializer,
    SimulacroDetailSerializer,
    SimulacroCreateSerializer,
    RecomendacionSerializer,
    PracticaListSerializer,
    PracticaDetailSerializer,
)


# =====================================================
# PERMISOS
# =====================================================

class EsAsesor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.rol == 'asesor'


# =====================================================
# SIMULACROS
# =====================================================

class SimulacrosListView(generics.ListAPIView):
    """
    GET /api/simulacros/
    Lista simulacros del usuario.
    """
    serializer_class = SimulacroListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.rol == 'cliente':
            queryset = Simulacro.objects.filter(cliente=user, is_deleted=False)
        elif user.rol == 'asesor':
            queryset = Simulacro.objects.filter(asesor=user, is_deleted=False)
        else:
            queryset = Simulacro.objects.filter(is_deleted=False)
        
        # Filtros
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        modalidad = self.request.query_params.get('modalidad')
        if modalidad:
            queryset = queryset.filter(modalidad=modalidad)
        
        return queryset.order_by('-fecha', '-hora')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PropuestasPendientesView(generics.ListAPIView):
    """
    GET /api/simulacros/propuestas/
    Lista propuestas pendientes de respuesta.
    """
    serializer_class = SimulacroListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.rol == 'asesor':
            return Simulacro.objects.filter(
                asesor=user,
                estado='pendiente_respuesta',
                is_deleted=False
            ).order_by('-created_at')
        elif user.rol == 'cliente':
            return Simulacro.objects.filter(
                cliente=user,
                estado='pendiente_respuesta',
                is_deleted=False
            ).order_by('-created_at')
        
        return Simulacro.objects.none()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SimulacroDetailView(generics.RetrieveAPIView):
    """
    GET /api/simulacros/<id>/
    Detalle de un simulacro.
    """
    serializer_class = SimulacroDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.rol == 'cliente':
            return Simulacro.objects.filter(cliente=user, is_deleted=False)
        elif user.rol == 'asesor':
            return Simulacro.objects.filter(asesor=user, is_deleted=False)
        return Simulacro.objects.filter(is_deleted=False)


class CrearPropuestaView(generics.CreateAPIView):
    """
    POST /api/simulacros/propuesta/
    Crea una propuesta de simulacro (asesor).
    """
    serializer_class = SimulacroCreateSerializer
    permission_classes = [permissions.IsAuthenticated, EsAsesor]


class DisponibilidadView(APIView):
    """
    GET /api/simulacros/disponibilidad/
    Verifica disponibilidad para nuevo simulacro.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Contar simulacros ACTIVOS del cliente (todos excepto cancelados)
        # Esto incluye: solicitado, propuesto, pendiente_respuesta, confirmado, en_progreso, completado
        simulacros_activos = Simulacro.objects.filter(
            cliente=user,
            is_deleted=False
        ).exclude(
            estado='cancelado'
        ).count()
        
        max_simulacros = 2
        disponibles = max(0, max_simulacros - simulacros_activos)
        
        if disponibles > 0:
            return Response({
                'disponibilidad': 'disponible',
                'simulacros_activos': simulacros_activos,
                'simulacros_disponibles': disponibles,
                'mensaje': f'Tiene {disponibles} simulacro(s) disponible(s)'
            })
        
        return Response({
            'disponibilidad': 'no_disponible',
            'simulacros_activos': simulacros_activos,
            'simulacros_disponibles': 0,
            'mensaje': f'Ha alcanzado el límite de {max_simulacros} simulacros por proceso'
        })


class ContadorSimulacrosView(APIView):
    """
    GET /api/simulacros/contador/
    Contador de simulacros del cliente.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Contar simulacros completados
        completados = Simulacro.objects.filter(
            cliente=user,
            estado='completado',
            is_deleted=False
        ).count()
        
        # Contar simulacros activos (pendientes, confirmados, solicitados, en_progreso)
        activos = Simulacro.objects.filter(
            cliente=user,
            estado__in=['solicitado', 'propuesto', 'pendiente_respuesta', 'confirmado', 'en_progreso'],
            is_deleted=False
        ).count()
        
        # Total de simulacros no cancelados
        total_activos = completados + activos
        
        return Response({
            'completados': completados,
            'activos': activos,
            'total_usados': total_activos,
            'total_permitidos': 2,
            'disponibles': max(0, 2 - total_activos)
        })


class SolicitarSimulacroView(APIView):
    """
    POST /api/simulacros/solicitar/
    Permite al cliente solicitar un simulacro.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Verificar que sea cliente
        if user.rol != 'cliente':
            return Response(
                {'error': 'Solo los clientes pueden solicitar simulacros'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar disponibilidad - contar TODOS los simulacros activos (no cancelados)
        simulacros_activos = Simulacro.objects.filter(
            cliente=user,
            is_deleted=False
        ).exclude(
            estado='cancelado'
        ).count()
        
        if simulacros_activos >= 2:
            return Response(
                {'error': 'Ha alcanzado el límite de 2 simulacros permitidos. Debe cancelar uno existente para solicitar otro.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener datos
        solicitud_id = request.data.get('solicitud_id')
        fecha_propuesta = request.data.get('fecha_propuesta')
        hora_propuesta = request.data.get('hora_propuesta')
        modalidad = request.data.get('modalidad', 'virtual')
        observaciones = request.data.get('observaciones', '')
        
        if not solicitud_id:
            return Response(
                {'error': 'solicitud_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que la solicitud pertenezca al cliente
        from apps.solicitudes.models import Solicitud
        try:
            solicitud = Solicitud.objects.get(pk=solicitud_id, cliente=user, is_deleted=False)
        except Solicitud.DoesNotExist:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Crear simulacro con estado 'solicitado'
        # Usar valores por defecto si no se proporcionan fecha/hora
        from datetime import date, time
        fecha_default = date.today() if not fecha_propuesta else fecha_propuesta
        hora_default = time(9, 0) if not hora_propuesta else hora_propuesta
        
        simulacro = Simulacro.objects.create(
            cliente=user,
            solicitud=solicitud,
            asesor=solicitud.asesor,  # Asignar al asesor de la solicitud
            modalidad=modalidad,
            fecha=fecha_default,
            hora=hora_default,
            fecha_propuesta=fecha_propuesta if fecha_propuesta else None,
            hora_propuesta=hora_propuesta if hora_propuesta else None,
            estado='solicitado',
            notas=f"Solicitud del cliente: {observaciones}" if observaciones else ""
        )
        
        return Response({
            'mensaje': 'Solicitud de simulacro enviada exitosamente',
            'simulacro': {
                'id': simulacro.id,
                'estado': simulacro.estado,
                'modalidad': simulacro.modalidad,
                'fecha': simulacro.fecha,
                'hora': simulacro.hora,
            }
        }, status=status.HTTP_201_CREATED)


class AceptarPropuestaView(APIView):
    """
    POST /api/simulacros/<id>/aceptar/
    Acepta una propuesta de simulacro.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        # Estados que pueden ser aceptados
        estados_aceptables = ['solicitado', 'propuesto', 'pendiente_respuesta']
        
        try:
            # Buscar simulacro donde el usuario sea cliente o asesor
            simulacro = Simulacro.objects.get(
                pk=pk,
                is_deleted=False
            )
            
            # Verificar que el usuario tenga permiso
            user = request.user
            if user.rol == 'cliente' and simulacro.cliente != user:
                return Response(
                    {'error': 'No tienes permiso para este simulacro'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Verificar estado válido
            if simulacro.estado not in estados_aceptables:
                return Response(
                    {'error': f'El simulacro no puede ser aceptado en estado {simulacro.estado}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Simulacro.DoesNotExist:
            return Response(
                {'error': 'Simulacro no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        simulacro.estado = 'confirmado'
        simulacro.save()
        
        return Response({
            'mensaje': 'Simulacro confirmado exitosamente',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class ContrapropuestaView(APIView):
    """
    POST /api/simulacros/<id>/contrapropuesta/
    Propone fecha alternativa.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            simulacro = Simulacro.objects.get(
                pk=pk,
                cliente=request.user,
                estado='pendiente_respuesta',
                is_deleted=False
            )
        except Simulacro.DoesNotExist:
            return Response(
                {'error': 'Simulacro no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        fecha = request.data.get('fecha')
        hora = request.data.get('hora')
        
        if not fecha or not hora:
            return Response(
                {'error': 'Fecha y hora son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        simulacro.fecha_propuesta = fecha
        simulacro.hora_propuesta = hora
        simulacro.estado = 'contrapropuesta'
        simulacro.save()
        
        return Response({
            'mensaje': 'Contrapropuesta enviada',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class CancelarSimulacroView(APIView):
    """
    POST /api/simulacros/<id>/cancelar/
    Cancela un simulacro.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        user = request.user
        
        try:
            if user.rol == 'cliente':
                simulacro = Simulacro.objects.get(pk=pk, cliente=user, is_deleted=False)
            else:
                simulacro = Simulacro.objects.get(pk=pk, asesor=user, is_deleted=False)
        except Simulacro.DoesNotExist:
            return Response(
                {'error': 'Simulacro no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not simulacro.puede_cancelar():
            return Response(
                {'error': 'No puedes cancelar con menos de 24 horas de anticipación'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        simulacro.estado = 'cancelado'
        simulacro.motivo_cancelacion = request.data.get('motivo', '')
        simulacro.save()
        
        return Response({
            'mensaje': 'Simulacro cancelado',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class IngresarSalaView(APIView):
    """
    POST /api/simulacros/<id>/sala-espera/
    Ingresa a la sala de espera.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        from django.conf import settings
        
        try:
            simulacro = Simulacro.objects.get(
                pk=pk,
                cliente=request.user,
                estado='confirmado',
                is_deleted=False
            )
        except Simulacro.DoesNotExist:
            return Response(
                {'error': 'Simulacro no encontrado o no confirmado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # En desarrollo, permitir siempre el acceso
        if not settings.DEBUG and not simulacro.puede_ingresar_sala():
            # Calcular tiempo restante
            fecha_simulacro = datetime.combine(simulacro.fecha, simulacro.hora)
            fecha_simulacro = timezone.make_aware(fecha_simulacro)
            tiempo_restante = fecha_simulacro - timezone.now()
            
            if tiempo_restante.total_seconds() > 0:
                minutos = int(tiempo_restante.total_seconds() / 60)
                return Response({
                    'error': f'Podrás ingresar 15 minutos antes. Faltan {minutos} minutos.',
                    'tiempo_restante_minutos': minutos
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {'error': 'El simulacro ya pasó'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        simulacro.estado = 'en_sala_espera'
        simulacro.save()
        
        # Calcular tiempo para inicio
        fecha_simulacro = datetime.combine(simulacro.fecha, simulacro.hora)
        fecha_simulacro = timezone.make_aware(fecha_simulacro)
        tiempo_restante = int((fecha_simulacro - timezone.now()).total_seconds() / 60)
        
        return Response({
            'mensaje': 'Has ingresado a la sala de espera',
            'tiempo_restante_minutos': max(0, tiempo_restante),
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class IniciarSimulacroView(APIView):
    """
    POST /api/simulacros/<id>/iniciar/
    Inicia el simulacro (asesor).
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request, pk):
        from django.conf import settings
        
        # En DEBUG permitimos iniciar desde confirmado o en_sala_espera
        estados_permitidos = ['en_sala_espera']
        if settings.DEBUG:
            estados_permitidos = ['confirmado', 'en_sala_espera']
        
        try:
            simulacro = Simulacro.objects.get(
                pk=pk,
                asesor=request.user,
                estado__in=estados_permitidos,
                is_deleted=False
            )
        except Simulacro.DoesNotExist:
            return Response(
                {'error': 'Simulacro no encontrado o no está listo para iniciar'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        simulacro.estado = 'en_progreso'
        simulacro.fecha_inicio = timezone.now()
        simulacro.grabacion_activa = True
        simulacro.save()
        
        return Response({
            'mensaje': 'Simulacro iniciado',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class FinalizarSimulacroView(APIView):
    """
    POST /api/simulacros/<id>/finalizar/
    Finaliza el simulacro (asesor).
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request, pk):
        try:
            simulacro = Simulacro.objects.get(
                pk=pk,
                asesor=request.user,
                estado='en_progreso',
                is_deleted=False
            )
        except Simulacro.DoesNotExist:
            return Response(
                {'error': 'Simulacro no encontrado o no en progreso'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        simulacro.estado = 'completado'
        simulacro.fecha_fin = timezone.now()
        simulacro.grabacion_activa = False
        
        # Calcular duración
        if simulacro.fecha_inicio:
            duracion = simulacro.fecha_fin - simulacro.fecha_inicio
            simulacro.duracion_minutos = int(duracion.total_seconds() / 60)
        
        simulacro.notas = request.data.get('notas', '')
        simulacro.save()
        
        return Response({
            'mensaje': 'Simulacro completado',
            'simulacro': SimulacroDetailSerializer(simulacro).data
        })


class InfoSalaView(APIView):
    """
    GET /api/simulacros/<id>/sala/
    Obtiene información de la sala de reunión con URL de Jitsi.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            user = request.user
            # Permitir acceso al cliente o asesor del simulacro
            if user.rol == 'cliente':
                simulacro = Simulacro.objects.get(
                    pk=pk,
                    cliente=user,
                    is_deleted=False
                )
            elif user.rol == 'asesor':
                simulacro = Simulacro.objects.get(
                    pk=pk,
                    asesor=user,
                    is_deleted=False
                )
            else:
                return Response(
                    {'error': 'No autorizado'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Simulacro.DoesNotExist:
            return Response(
                {'error': 'Simulacro no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el simulacro esté en un estado que permita acceso a la sala
        estados_permitidos = ['confirmado', 'en_sala_espera', 'en_progreso']
        if simulacro.estado not in estados_permitidos:
            return Response({
                'error': f'El simulacro no está disponible (estado: {simulacro.estado})',
                'estado_actual': simulacro.estado
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar nombre de sala único para Jitsi
        room_name = f"migrafacil-sim-{simulacro.id}"
        
        # URL de Jitsi Meet (usando el servidor público gratuito)
        jitsi_domain = "meet.jit.si"
        jitsi_url = f"https://{jitsi_domain}/{room_name}"
        
        # Información del otro participante
        if user.rol == 'cliente':
            otro_participante = {
                'nombre': simulacro.asesor.nombre_completo() if simulacro.asesor else 'Asesor',
                'rol': 'asesor'
            }
        else:
            otro_participante = {
                'nombre': simulacro.cliente.nombre_completo() if simulacro.cliente else 'Cliente',
                'rol': 'cliente'
            }
        
        return Response({
            'simulacro_id': simulacro.id,
            'room_name': room_name,
            'jitsi_domain': jitsi_domain,
            'jitsi_url': jitsi_url,
            'estado': simulacro.estado,
            'modalidad': simulacro.modalidad,
            'fecha': simulacro.fecha,
            'hora': str(simulacro.hora) if simulacro.hora else None,
            'otro_participante': otro_participante,
            'mi_rol': user.rol,
            'mi_nombre': user.nombre_completo(),
            'puede_iniciar': user.rol == 'asesor' and simulacro.estado in ['confirmado', 'en_sala_espera'],
            'en_progreso': simulacro.estado == 'en_progreso',
            'fecha_inicio': simulacro.fecha_inicio,
        })


class EstadoSalaView(APIView):
    """
    GET /api/simulacros/<id>/estado-sala/
    Obtiene el estado actual de la sala (para polling).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            user = request.user
            if user.rol == 'cliente':
                simulacro = Simulacro.objects.get(pk=pk, cliente=user, is_deleted=False)
            elif user.rol == 'asesor':
                simulacro = Simulacro.objects.get(pk=pk, asesor=user, is_deleted=False)
            else:
                return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        except Simulacro.DoesNotExist:
            return Response({'error': 'Simulacro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'simulacro_id': simulacro.id,
            'estado': simulacro.estado,
            'en_progreso': simulacro.estado == 'en_progreso',
            'fecha_inicio': simulacro.fecha_inicio,
            'duracion_actual': int((timezone.now() - simulacro.fecha_inicio).total_seconds()) if simulacro.fecha_inicio else 0
        })


# =====================================================
# RECOMENDACIONES
# =====================================================

class RecomendacionesListView(generics.ListAPIView):
    """
    GET /api/recomendaciones/
    Lista recomendaciones del cliente.
    """
    serializer_class = RecomendacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Recomendacion.objects.filter(
            simulacro__cliente=user,
            publicada=True
        ).order_by('-fecha_generacion')


class RecomendacionDetailView(generics.RetrieveAPIView):
    """
    GET /api/recomendaciones/<id>/
    Detalle de recomendación.
    """
    serializer_class = RecomendacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.rol == 'cliente':
            return Recomendacion.objects.filter(
                simulacro__cliente=user,
                publicada=True
            )
        return Recomendacion.objects.all()


class GenerarRecomendacionView(APIView):
    """
    POST /api/recomendaciones/generar/
    Genera recomendaciones para un simulacro (asesor).
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesor]
    
    def post(self, request):
        simulacro_id = request.data.get('simulacro_id')
        
        try:
            simulacro = Simulacro.objects.get(
                pk=simulacro_id,
                asesor=request.user,
                estado='completado',
                is_deleted=False
            )
        except Simulacro.DoesNotExist:
            return Response(
                {'error': 'Simulacro no encontrado o no completado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar si ya tiene recomendación
        if hasattr(simulacro, 'recomendacion'):
            return Response(
                {'error': 'El simulacro ya tiene recomendaciones generadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear recomendación con indicadores del request
        recomendacion = Recomendacion.objects.create(
            simulacro=simulacro,
            claridad=request.data.get('claridad', 'medio'),
            coherencia=request.data.get('coherencia', 'medio'),
            seguridad=request.data.get('seguridad', 'medio'),
            pertinencia=request.data.get('pertinencia', 'medio'),
            fortalezas=request.data.get('fortalezas', []),
            puntos_mejora=request.data.get('puntos_mejora', []),
            recomendaciones=request.data.get('recomendaciones', []),
            accion_sugerida=request.data.get('accion_sugerida', ''),
            publicada=True
        )
        
        # Calcular nivel de preparación
        recomendacion.nivel_preparacion = recomendacion.calcular_nivel_preparacion()
        recomendacion.save()
        
        return Response({
            'mensaje': 'Recomendaciones generadas',
            'recomendacion': RecomendacionSerializer(recomendacion).data
        }, status=status.HTTP_201_CREATED)


# =====================================================
# PRÁCTICA INDIVIDUAL
# =====================================================

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
    """
    GET /api/practica/tipos-visa/
    Obtiene tipos de visa disponibles para práctica.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        tipos = [
            {'codigo': 'estudiante', 'nombre': 'Visa de Estudiante', 'preguntas': 10},
            {'codigo': 'trabajo', 'nombre': 'Visa de Trabajo', 'preguntas': 10},
            {'codigo': 'turismo', 'nombre': 'Visa de Turismo', 'preguntas': 10},
            {'codigo': 'vivienda', 'nombre': 'Visa de Vivienda', 'preguntas': 10},
        ]
        
        # Marcar como sugerido el tipo de visa del usuario si tiene solicitud
        # Por ahora retornamos sin sugerencia
        return Response(tipos)


class IniciarPracticaView(APIView):
    """
    POST /api/practica/iniciar/
    Inicia un cuestionario de práctica.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        tipo_visa = request.data.get('tipo_visa')
        
        if tipo_visa not in BANCO_PREGUNTAS:
            return Response(
                {'error': 'Tipo de visa no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        practica = Practica.objects.create(
            cliente=request.user,
            tipo_visa=tipo_visa,
            total_preguntas=len(BANCO_PREGUNTAS[tipo_visa])
        )
        
        # Retornar preguntas sin respuestas correctas
        preguntas = [
            {'id': p['id'], 'pregunta': p['pregunta']}
            for p in BANCO_PREGUNTAS[tipo_visa]
        ]
        
        return Response({
            'practica_id': practica.id,
            'tipo_visa': tipo_visa,
            'preguntas': preguntas
        }, status=status.HTTP_201_CREATED)


class FinalizarPracticaView(APIView):
    """
    POST /api/practica/<id>/finalizar/
    Finaliza un cuestionario y calcula resultado.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            practica = Practica.objects.get(
                pk=pk,
                cliente=request.user,
                completado=False
            )
        except Practica.DoesNotExist:
            return Response(
                {'error': 'Práctica no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
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
        
        # Determinar mensaje según calificación
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
    """
    GET /api/practica/historial/
    Historial de prácticas del usuario.
    """
    serializer_class = PracticaListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Practica.objects.filter(
            cliente=self.request.user,
            completado=True
        ).order_by('-fecha_completado')


class EstadisticasPracticaView(APIView):
    """
    GET /api/practica/estadisticas/
    Estadísticas de práctica del usuario.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        practicas = Practica.objects.filter(
            cliente=request.user,
            completado=True
        )
        
        total = practicas.count()
        if total == 0:
            return Response({
                'total_practicas': 0,
                'promedio_porcentaje': 0,
                'mejor_resultado': None,
                'por_tipo_visa': {}
            })
        
        from django.db.models import Avg, Max
        
        stats = practicas.aggregate(
            promedio=Avg('porcentaje'),
            mejor=Max('porcentaje')
        )
        
        por_tipo = practicas.values('tipo_visa').annotate(
            cantidad=Count('id'),
            promedio=Avg('porcentaje')
        )
        
        return Response({
            'total_practicas': total,
            'promedio_porcentaje': round(stats['promedio'] or 0),
            'mejor_resultado': stats['mejor'],
            'por_tipo_visa': {item['tipo_visa']: item for item in por_tipo}
        })
