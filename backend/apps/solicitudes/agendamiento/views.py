"""
Views para el módulo de Agendamiento de Entrevistas.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta

from apps.solicitudes.models import Solicitud, Entrevista


class EsAsesorOAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.rol in ['asesor', 'admin']


# Configuración de reglas por embajada
REGLAS_EMBAJADA = {
    'usa': {'min_horas_cancelacion': 24, 'max_reprogramaciones': 2},
    'espana': {'min_horas_cancelacion': 48, 'max_reprogramaciones': 2},
    'canada': {'min_horas_cancelacion': 72, 'max_reprogramaciones': 2},
    'brasil': {'min_horas_cancelacion': 24, 'max_reprogramaciones': 2},
}


class EntrevistasListView(generics.ListAPIView):
    """
    GET /api/entrevistas/
    Lista entrevistas del usuario.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.rol == 'cliente':
            entrevistas = Entrevista.objects.filter(
                solicitud__cliente=user
            ).select_related('solicitud')
        elif user.rol == 'asesor':
            entrevistas = Entrevista.objects.filter(
                solicitud__asesor=user
            ).select_related('solicitud')
        else:
            entrevistas = Entrevista.objects.all().select_related('solicitud')
        
        # Filtros
        estado = request.query_params.get('estado')
        if estado:
            entrevistas = entrevistas.filter(estado=estado)
        
        data = []
        for e in entrevistas.order_by('fecha', 'hora'):
            data.append({
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
            })
        
        return Response(data)


class EntrevistaDetailView(APIView):
    """
    GET /api/entrevistas/<id>/
    Detalle de una entrevista.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        user = request.user
        
        try:
            if user.rol == 'cliente':
                entrevista = Entrevista.objects.get(pk=pk, solicitud__cliente=user)
            elif user.rol == 'asesor':
                entrevista = Entrevista.objects.get(pk=pk, solicitud__asesor=user)
            else:
                entrevista = Entrevista.objects.get(pk=pk)
        except Entrevista.DoesNotExist:
            return Response(
                {'error': 'Entrevista no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
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
    """
    GET /api/entrevistas/horarios/?fecha=YYYY-MM-DD&embajada=usa
    Obtiene horarios disponibles para una fecha.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        fecha = request.query_params.get('fecha')
        embajada = request.query_params.get('embajada')
        
        if not fecha:
            return Response(
                {'error': 'Fecha es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Horarios base disponibles
        horarios_base = ['08:00', '09:00', '10:00', '11:00', '14:00', '15:00', '16:00']
        
        # Obtener horarios ya ocupados
        ocupados = Entrevista.objects.filter(
            fecha=fecha,
            estado__in=['agendada', 'confirmada', 'reprogramada']
        ).values_list('hora', flat=True)
        
        ocupados_str = [h.strftime('%H:%M') for h in ocupados]
        
        disponibles = []
        for h in horarios_base:
            disponibles.append({
                'horario': h,
                'estado': 'Ocupado' if h in ocupados_str else 'Disponible'
            })
        
        return Response({
            'fecha': fecha,
            'horarios': disponibles
        })


class AgendarEntrevistaView(APIView):
    """
    POST /api/entrevistas/agendar/
    Agenda una entrevista para una solicitud.
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def post(self, request):
        solicitud_id = request.data.get('solicitud_id')
        fecha = request.data.get('fecha')
        hora = request.data.get('hora')
        ubicacion = request.data.get('ubicacion', '')
        
        if not all([solicitud_id, fecha, hora]):
            return Response(
                {'error': 'solicitud_id, fecha y hora son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            solicitud = Solicitud.objects.get(pk=solicitud_id, is_deleted=False)
        except Solicitud.DoesNotExist:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que la solicitud esté aprobada
        if solicitud.estado not in ['aprobada', 'enviada_embajada']:
            return Response(
                {'error': 'La solicitud debe estar aprobada para agendar entrevista'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya tiene entrevista
        if hasattr(solicitud, 'entrevista'):
            return Response(
                {'error': 'La solicitud ya tiene una entrevista agendada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear entrevista
        entrevista = Entrevista.objects.create(
            solicitud=solicitud,
            fecha=fecha,
            hora=hora,
            ubicacion=ubicacion,
            estado='agendada'
        )
        
        # Actualizar estado de la solicitud
        solicitud.estado = 'entrevista_agendada'
        solicitud.save()
        
        # Crear notificación
        from apps.notificaciones.views import notificar_entrevista_agendada
        notificar_entrevista_agendada(solicitud, fecha, hora)
        
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
    """
    POST /api/entrevistas/<id>/confirmar/
    Confirma una entrevista.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            entrevista = Entrevista.objects.get(
                pk=pk,
                solicitud__cliente=request.user,
                estado='agendada'
            )
        except Entrevista.DoesNotExist:
            return Response(
                {'error': 'Entrevista no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        entrevista.estado = 'confirmada'
        entrevista.save()
        
        return Response({
            'mensaje': 'Entrevista confirmada exitosamente'
        })


class ReprogramarEntrevistaView(APIView):
    """
    POST /api/entrevistas/<id>/reprogramar/
    Reprograma una entrevista.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        user = request.user
        
        try:
            if user.rol == 'cliente':
                entrevista = Entrevista.objects.get(pk=pk, solicitud__cliente=user)
            else:
                entrevista = Entrevista.objects.get(pk=pk)
        except Entrevista.DoesNotExist:
            return Response(
                {'error': 'Entrevista no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar límite de reprogramaciones
        embajada = entrevista.solicitud.embajada
        reglas = REGLAS_EMBAJADA.get(embajada, {'max_reprogramaciones': 2})
        
        if entrevista.veces_reprogramada >= reglas['max_reprogramaciones']:
            return Response({
                'error': 'Error: ha alcanzado el límite máximo de reprogramaciones permitidas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        nueva_fecha = request.data.get('fecha')
        nueva_hora = request.data.get('hora')
        
        if not nueva_fecha or not nueva_hora:
            return Response(
                {'error': 'Nueva fecha y hora son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        entrevista.fecha = nueva_fecha
        entrevista.hora = nueva_hora
        entrevista.estado = 'reprogramada'
        entrevista.veces_reprogramada += 1
        entrevista.save()
        
        mensaje = 'Entrevista reprogramada exitosamente'
        if entrevista.veces_reprogramada == reglas['max_reprogramaciones']:
            mensaje = 'Esta es su última reprogramación permitida'
        
        return Response({'mensaje': mensaje})


class VerificarReprogramacionView(APIView):
    """
    GET /api/entrevistas/<id>/puede-reprogramar/
    Verifica si se puede reprogramar.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            entrevista = Entrevista.objects.get(pk=pk)
        except Entrevista.DoesNotExist:
            return Response(
                {'error': 'Entrevista no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        embajada = entrevista.solicitud.embajada
        reglas = REGLAS_EMBAJADA.get(embajada, {'max_reprogramaciones': 2})
        
        puede = entrevista.veces_reprogramada < reglas['max_reprogramaciones']
        
        return Response({
            'puede_reprogramar': puede,
            'reprogramaciones_usadas': entrevista.veces_reprogramada,
            'max_reprogramaciones': reglas['max_reprogramaciones']
        })


class CancelarEntrevistaView(APIView):
    """
    POST /api/entrevistas/<id>/cancelar/
    Cancela una entrevista.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        user = request.user
        
        try:
            if user.rol == 'cliente':
                entrevista = Entrevista.objects.get(pk=pk, solicitud__cliente=user)
            else:
                entrevista = Entrevista.objects.get(pk=pk)
        except Entrevista.DoesNotExist:
            return Response(
                {'error': 'Entrevista no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar reglas de embajada
        embajada = entrevista.solicitud.embajada
        reglas = REGLAS_EMBAJADA.get(embajada, {'min_horas_cancelacion': 24})
        
        # Calcular horas restantes
        fecha_entrevista = datetime.combine(entrevista.fecha, entrevista.hora)
        fecha_entrevista = timezone.make_aware(fecha_entrevista)
        horas_restantes = (fecha_entrevista - timezone.now()).total_seconds() / 3600
        
        if horas_restantes < reglas['min_horas_cancelacion']:
            return Response({
                'error': 'Error: no es posible cancelar la entrevista debido a que no se cumple el tiempo mínimo de anticipación'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        entrevista.estado = 'cancelada'
        entrevista.motivo_cancelacion = request.data.get('motivo', '')
        entrevista.save()
        
        return Response({
            'mensaje': 'Cancelación confirmada exitosamente'
        })


class VerificarCancelacionView(APIView):
    """
    GET /api/entrevistas/<id>/puede-cancelar/
    Verifica si se puede cancelar.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            entrevista = Entrevista.objects.get(pk=pk)
        except Entrevista.DoesNotExist:
            return Response(
                {'error': 'Entrevista no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        embajada = entrevista.solicitud.embajada
        reglas = REGLAS_EMBAJADA.get(embajada, {'min_horas_cancelacion': 24})
        
        fecha_entrevista = datetime.combine(entrevista.fecha, entrevista.hora)
        fecha_entrevista = timezone.make_aware(fecha_entrevista)
        horas_restantes = (fecha_entrevista - timezone.now()).total_seconds() / 3600
        
        puede = horas_restantes >= reglas['min_horas_cancelacion']
        
        return Response({
            'puede_cancelar': puede,
            'horas_restantes': round(horas_restantes, 1),
            'min_horas_requeridas': reglas['min_horas_cancelacion']
        })


class CalendarioEventosView(APIView):
    """
    GET /api/entrevistas/calendario/?mes=YYYY-MM
    Eventos del calendario.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        mes = request.query_params.get('mes')  # YYYY-MM
        user = request.user
        
        if user.rol == 'cliente':
            entrevistas = Entrevista.objects.filter(
                solicitud__cliente=user
            ).select_related('solicitud', 'solicitud__cliente', 'solicitud__asesor')
        elif user.rol == 'asesor':
            entrevistas = Entrevista.objects.filter(
                solicitud__asesor=user
            ).select_related('solicitud', 'solicitud__cliente', 'solicitud__asesor')
        else:
            entrevistas = Entrevista.objects.all().select_related('solicitud', 'solicitud__cliente', 'solicitud__asesor')
        
        if mes:
            year, month = mes.split('-')
            entrevistas = entrevistas.filter(
                fecha__year=int(year),
                fecha__month=int(month)
            )
        
        eventos = []
        for e in entrevistas.order_by('fecha', 'hora'):
            eventos.append({
                'id': e.id,
                'tipo': 'entrevista',
                'titulo': f'Entrevista - {e.solicitud.get_tipo_visa_display()}',
                'fecha': str(e.fecha),
                'hora': str(e.hora) if e.hora else None,
                'estado': e.estado,
                'ubicacion': e.ubicacion,
                'tipo_visa': e.solicitud.tipo_visa,
                'tipo_visa_display': e.solicitud.get_tipo_visa_display(),
                'solicitud_id': e.solicitud.id,
                'embajada': e.solicitud.get_embajada_display() if e.solicitud.embajada else None,
                'cliente_nombre': e.solicitud.cliente.nombre_completo() if e.solicitud.cliente else None,
                'asesor_nombre': e.solicitud.asesor.nombre_completo() if e.solicitud.asesor else None,
            })
        
        return Response(eventos)


class EntrevistasProximasView(APIView):
    """
    GET /api/entrevistas/proximas/?dias=7
    Entrevistas próximas.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        dias = int(request.query_params.get('dias', 7))
        user = request.user
        
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        
        if user.rol == 'cliente':
            entrevistas = Entrevista.objects.filter(
                solicitud__cliente=user,
                fecha__lte=fecha_limite,
                fecha__gte=timezone.now().date(),
                estado__in=['agendada', 'confirmada', 'reprogramada']
            )
        elif user.rol == 'asesor':
            entrevistas = Entrevista.objects.filter(
                solicitud__asesor=user,
                fecha__lte=fecha_limite,
                fecha__gte=timezone.now().date(),
                estado__in=['agendada', 'confirmada', 'reprogramada']
            )
        else:
            entrevistas = Entrevista.objects.filter(
                fecha__lte=fecha_limite,
                fecha__gte=timezone.now().date(),
                estado__in=['agendada', 'confirmada', 'reprogramada']
            )
        
        data = []
        for e in entrevistas.order_by('fecha', 'hora'):
            data.append({
                'id': e.id,
                'solicitud_id': e.solicitud_id,
                'cliente_nombre': e.solicitud.cliente.nombre_completo(),
                'tipo_visa': e.solicitud.get_tipo_visa_display(),
                'fecha': e.fecha,
                'hora': e.hora,
                'estado': e.estado,
            })
        
        return Response(data)


class DisponibilidadEmbajadaFakerView(APIView):
    """
    GET /api/entrevistas/embajada/disponibilidad/?embajada=usa&mes=2024-02
    Simula la respuesta de disponibilidad de una embajada con datos faker.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        import random
        from datetime import date
        
        embajada = request.query_params.get('embajada', 'usa')
        mes = request.query_params.get('mes')  # formato: YYYY-MM
        
        # Información de embajadas (simulada)
        embajadas_info = {
            'usa': {
                'nombre': 'Embajada de Estados Unidos',
                'direccion': 'Calle 22 Bis #47-51, Bogotá',
                'telefono': '+57 1 275 2000',
                'horario': '8:00 AM - 4:30 PM',
            },
            'espana': {
                'nombre': 'Embajada de España',
                'direccion': 'Calle 94A #11A-70, Bogotá',
                'telefono': '+57 1 622 0090',
                'horario': '9:00 AM - 1:00 PM',
            },
            'canada': {
                'nombre': 'Embajada de Canadá',
                'direccion': 'Carrera 7 #114-33 Piso 14, Bogotá',
                'telefono': '+57 1 657 9800',
                'horario': '8:30 AM - 12:00 PM',
            },
            'brasil': {
                'nombre': 'Embajada de Brasil',
                'direccion': 'Calle 93 #14-20 Piso 8, Bogotá',
                'telefono': '+57 1 218 0800',
                'horario': '9:00 AM - 5:00 PM',
            },
        }
        
        info = embajadas_info.get(embajada, embajadas_info['usa'])
        
        # Generar fechas disponibles para el mes
        if mes:
            try:
                year, month = map(int, mes.split('-'))
            except:
                year = timezone.now().year
                month = timezone.now().month
        else:
            year = timezone.now().year
            month = timezone.now().month
        
        # Generar 15-25 días disponibles en el mes
        dias_en_mes = 28 if month == 2 else (30 if month in [4, 6, 9, 11] else 31)
        num_dias_disponibles = random.randint(15, min(25, dias_en_mes))
        
        dias_disponibles = sorted(random.sample(range(1, dias_en_mes + 1), num_dias_disponibles))
        
        # Horarios estándar
        horarios_base = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', 
                        '11:00', '11:30', '14:00', '14:30', '15:00', '15:30', '16:00']
        
        fechas_disponibilidad = []
        for dia in dias_disponibles:
            try:
                fecha = date(year, month, dia)
                # Excluir fines de semana
                if fecha.weekday() >= 5:
                    continue
                    
                # Generar horarios disponibles aleatorios para ese día
                num_slots = random.randint(3, len(horarios_base))
                slots_dia = random.sample(horarios_base, num_slots)
                
                # Ocupados aleatorios
                slots_disponibles = []
                for h in sorted(slots_dia):
                    ocupado = random.random() < 0.3  # 30% ocupados
                    slots_disponibles.append({
                        'hora': h,
                        'disponible': not ocupado,
                        'capacidad': random.randint(1, 3) if not ocupado else 0
                    })
                
                fechas_disponibilidad.append({
                    'fecha': fecha.isoformat(),
                    'dia_semana': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][fecha.weekday()],
                    'slots': slots_disponibles,
                    'total_disponibles': sum(1 for s in slots_disponibles if s['disponible'])
                })
            except:
                continue
        
        return Response({
            'embajada': embajada,
            'embajada_info': info,
            'mes': f'{year}-{month:02d}',
            'total_fechas_disponibles': len(fechas_disponibilidad),
            'fechas': fechas_disponibilidad,
            'nota': 'Datos simulados para desarrollo. En producción, se conectaría con la API de la embajada.'
        })


class SimularCitaEmbajadaView(APIView):
    """
    POST /api/entrevistas/embajada/simular-cita/
    Simula la confirmación de una cita con la embajada.
    """
    permission_classes = [permissions.IsAuthenticated, EsAsesorOAdmin]
    
    def post(self, request):
        import random
        import string
        
        solicitud_id = request.data.get('solicitud_id')
        fecha = request.data.get('fecha')
        hora = request.data.get('hora')
        embajada = request.data.get('embajada', 'usa')
        
        if not all([solicitud_id, fecha, hora]):
            return Response(
                {'error': 'solicitud_id, fecha y hora son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            solicitud = Solicitud.objects.get(pk=solicitud_id, is_deleted=False)
        except Solicitud.DoesNotExist:
            return Response(
                {'error': 'Solicitud no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generar código de confirmación simulado de la embajada
        codigo_confirmacion = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Ubicaciones por embajada
        ubicaciones = {
            'usa': 'Calle 22 Bis #47-51, Bogotá - Ventanilla 3',
            'espana': 'Calle 94A #11A-70, Bogotá - Sala de Visas',
            'canada': 'Carrera 7 #114-33 Piso 14, Bogotá - Oficina 1402',
            'brasil': 'Calle 93 #14-20 Piso 8, Bogotá - Recepción',
        }
        
        ubicacion = ubicaciones.get(embajada, 'Pendiente de asignar')
        
        # Verificar si ya tiene entrevista
        if hasattr(solicitud, 'entrevista'):
            # Actualizar entrevista existente
            entrevista = solicitud.entrevista
            entrevista.fecha = fecha
            entrevista.hora = hora
            entrevista.ubicacion = ubicacion
            entrevista.notas = f'Código de confirmación embajada: {codigo_confirmacion}'
            entrevista.estado = 'confirmada'
            entrevista.save()
        else:
            # Crear nueva entrevista
            entrevista = Entrevista.objects.create(
                solicitud=solicitud,
                fecha=fecha,
                hora=hora,
                ubicacion=ubicacion,
                estado='confirmada',
                notas=f'Código de confirmación embajada: {codigo_confirmacion}'
            )
        
        # Actualizar estado de la solicitud
        solicitud.estado = 'entrevista_agendada'
        solicitud.save()
        
        return Response({
            'success': True,
            'mensaje': 'Cita confirmada con la embajada (simulación)',
            'entrevista': {
                'id': entrevista.id,
                'fecha': entrevista.fecha,
                'hora': entrevista.hora,
                'ubicacion': entrevista.ubicacion,
                'estado': entrevista.estado,
            },
            'confirmacion_embajada': {
                'codigo': codigo_confirmacion,
                'embajada': embajada,
                'mensaje': f'Su cita ha sido registrada. Código de referencia: {codigo_confirmacion}',
                'instrucciones': [
                    'Llegar 30 minutos antes de la cita',
                    'Traer todos los documentos originales',
                    'No se permiten dispositivos electrónicos',
                    'Presentar identificación con foto',
                ]
            }
        }, status=status.HTTP_201_CREATED)
