"""
Servicios de la app Solicitudes.
Contiene toda la lógica de negocio relacionada con solicitudes, documentos y entrevistas.
"""
from django.db.models import Q, F, Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from .models import Solicitud, Documento, Entrevista

Usuario = get_user_model()


# Configuración de reglas por embajada
REGLAS_EMBAJADA = {
    'usa': {'min_horas_cancelacion': 24, 'max_reprogramaciones': 2},
    'espana': {'min_horas_cancelacion': 48, 'max_reprogramaciones': 2},
    'canada': {'min_horas_cancelacion': 72, 'max_reprogramaciones': 2},
    'brasil': {'min_horas_cancelacion': 24, 'max_reprogramaciones': 2},
}

# Horarios disponibles para entrevistas
HORARIOS_ENTREVISTA = ['08:00', '09:00', '10:00', '11:00', '14:00', '15:00', '16:00']


class SolicitudService:
    """Servicio para gestión de solicitudes."""
    
    @staticmethod
    def obtener_solicitud(solicitud_id: int, usuario=None) -> Solicitud | None:
        """Obtiene una solicitud por ID, opcionalmente verificando acceso del usuario."""
        try:
            filtros = {'pk': solicitud_id, 'is_deleted': False}
            
            if usuario:
                if usuario.rol == 'cliente':
                    filtros['cliente'] = usuario
                elif usuario.rol == 'asesor':
                    filtros['asesor'] = usuario
            
            return Solicitud.objects.get(**filtros)
        except Solicitud.DoesNotExist:
            return None
    
    @staticmethod
    def listar_solicitudes(usuario, estado: str = None, tipo_visa: str = None):
        """Lista solicitudes según el rol del usuario."""
        if usuario.rol == 'cliente':
            queryset = Solicitud.objects.filter(cliente=usuario, is_deleted=False)
        elif usuario.rol == 'asesor':
            queryset = Solicitud.objects.filter(asesor=usuario, is_deleted=False)
        else:
            queryset = Solicitud.objects.filter(is_deleted=False)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if tipo_visa:
            queryset = queryset.filter(tipo_visa=tipo_visa)
        
        return queryset.prefetch_related('documentos_adjuntos').order_by('-created_at')
    
    @staticmethod
    def crear_solicitud(cliente, tipo_visa: str, embajada: str, 
                        datos_personales: dict = None, observaciones: str = '') -> Solicitud:
        """Crea una nueva solicitud y la asigna automáticamente a un asesor."""
        solicitud = Solicitud.objects.create(
            cliente=cliente,
            tipo_visa=tipo_visa,
            embajada=embajada,
            datos_personales=datos_personales or {},
            observaciones=observaciones,
            estado='pendiente'
        )
        
        # Asignar asesor automáticamente
        SolicitudService._asignar_asesor_automatico(solicitud)
        
        return solicitud
    
    @staticmethod
    def _asignar_asesor_automatico(solicitud: Solicitud):
        """Asigna la solicitud al asesor con menos carga del día."""
        hoy = timezone.now().date()
        
        asesor = Usuario.objects.filter(
            rol='asesor',
            is_active=True
        ).annotate(
            solicitudes_hoy=Count(
                'solicitudes_asignadas',
                filter=Q(solicitudes_asignadas__fecha_asignacion__date=hoy)
            )
        ).filter(
            solicitudes_hoy__lt=F('limite_solicitudes_diarias')
        ).order_by('solicitudes_hoy').first()
        
        if asesor:
            solicitud.asignar_asesor(asesor)
    
    @staticmethod
    def asignar_asesor(solicitud: Solicitud, asesor_id: int) -> tuple[bool, str | None]:
        """Asigna manualmente un asesor a una solicitud."""
        if not solicitud.puede_ser_asignada():
            return False, 'La solicitud ya tiene un asesor asignado'
        
        try:
            asesor = Usuario.objects.get(id=asesor_id, rol='asesor', is_active=True)
            solicitud.asignar_asesor(asesor)
            return True, None
        except Usuario.DoesNotExist:
            return False, 'Asesor no encontrado'
    
    @staticmethod
    def actualizar_estado(solicitud: Solicitud, nuevo_estado: str, notas: str = '', motivo_rechazo: str = '') -> tuple[bool, str | None]:
        """
        Actualiza el estado de una solicitud con validacion de transiciones.

        MAQUINA DE ESTADOS CORREGIDA:
        borrador -> pendiente
        pendiente -> en_revision, rechazada
        en_revision -> aprobada, rechazada
        aprobada -> enviada_embajada, esperando_decision_embajada (atajo directo)
        enviada_embajada -> esperando_decision_embajada
        esperando_decision_embajada -> aprobada_embajada, rechazada_embajada
        aprobada_embajada -> entrevista_agendada (UNICO estado que permite agendar)
        entrevista_agendada -> completada
        """
        transiciones_validas = {
            'borrador': ['pendiente'],
            'pendiente': ['en_revision', 'rechazada'],
            'en_revision': ['aprobada', 'rechazada'],
            'aprobada': ['enviada_embajada', 'esperando_decision_embajada'],
            'enviada_embajada': ['esperando_decision_embajada'],
            'esperando_decision_embajada': ['aprobada_embajada', 'rechazada_embajada'],
            'aprobada_embajada': ['entrevista_agendada'],
            'entrevista_agendada': ['completada'],
        }

        estados_permitidos = transiciones_validas.get(solicitud.estado, [])
        if nuevo_estado not in estados_permitidos:
            return False, f"No se puede cambiar de '{solicitud.estado}' a '{nuevo_estado}'"

        solicitud.estado = nuevo_estado
        if notas:
            solicitud.notas_asesor = notas

        # Registrar fechas importantes segun el estado
        if nuevo_estado in ['aprobada', 'rechazada']:
            solicitud.fecha_revision = timezone.now()
        elif nuevo_estado == 'enviada_embajada':
            solicitud.fecha_envio_embajada = timezone.now()
        elif nuevo_estado in ['aprobada_embajada', 'rechazada_embajada']:
            solicitud.fecha_decision_embajada = timezone.now()
            if nuevo_estado == 'rechazada_embajada' and motivo_rechazo:
                solicitud.motivo_rechazo_embajada = motivo_rechazo

        solicitud.save()
        return True, None

    @staticmethod
    def registrar_decision_embajada(solicitud: Solicitud, decision: str, motivo: str = '') -> tuple[bool, str | None]:
        """
        Registra la decision de la embajada sobre una solicitud.

        Args:
            solicitud: Instancia de Solicitud
            decision: 'aprobada' o 'rechazada'
            motivo: Motivo del rechazo (requerido si decision es rechazada)

        Returns:
            Tuple (exito, mensaje_error)
        """
        if solicitud.estado != 'esperando_decision_embajada':
            return False, 'La solicitud no esta esperando decision de la embajada'

        if decision == 'aprobada':
            return SolicitudService.actualizar_estado(solicitud, 'aprobada_embajada')
        elif decision == 'rechazada':
            if not motivo:
                return False, 'Debe proporcionar un motivo de rechazo'
            return SolicitudService.actualizar_estado(
                solicitud,
                'rechazada_embajada',
                motivo_rechazo=motivo
            )
        else:
            return False, f'Decision invalida: {decision}'
    
    @staticmethod
    def enviar_solicitud(solicitud: Solicitud) -> tuple[bool, str | None]:
        """Cambia una solicitud de borrador a pendiente."""
        if solicitud.estado not in ['borrador', 'pendiente']:
            return False, 'La solicitud ya ha sido enviada'
        
        solicitud.estado = 'pendiente'
        solicitud.save()
        return True, None
    
    @staticmethod
    def obtener_estadisticas_cliente(usuario) -> dict:
        """Obtiene estadísticas para el dashboard del cliente."""
        solicitudes = Solicitud.objects.filter(cliente=usuario, is_deleted=False)
        
        return {
            'total_solicitudes': solicitudes.count(),
            'en_proceso': solicitudes.filter(
                estado__in=['pendiente', 'en_revision', 'aprobada']
            ).count(),
            'aprobadas': solicitudes.filter(estado='aprobada').count(),
            'completadas': solicitudes.filter(estado='completada').count(),
            'rechazadas': solicitudes.filter(estado='rechazada').count(),
            'con_entrevista': solicitudes.filter(estado='entrevista_agendada').count(),
        }
    
    @staticmethod
    def obtener_estadisticas_asesor(usuario) -> dict:
        """Obtiene estadísticas para el dashboard del asesor."""
        hoy = timezone.now().date()
        
        if usuario.rol == 'asesor':
            solicitudes = Solicitud.objects.filter(asesor=usuario, is_deleted=False)
        else:
            solicitudes = Solicitud.objects.filter(is_deleted=False)
        
        return {
            'total_asignadas': solicitudes.count(),
            'asignadas_hoy': solicitudes.filter(fecha_asignacion__date=hoy).count(),
            'pendientes_revision': solicitudes.filter(estado='pendiente').count(),
            'en_revision': solicitudes.filter(estado='en_revision').count(),
            'aprobadas': solicitudes.filter(estado='aprobada').count(),
            'enviadas_embajada': solicitudes.filter(estado='enviada_embajada').count(),
            'limite_diario': usuario.limite_solicitudes_diarias if usuario.rol == 'asesor' else None,
            'disponibilidad': (
                usuario.limite_solicitudes_diarias - 
                solicitudes.filter(fecha_asignacion__date=hoy).count()
            ) if usuario.rol == 'asesor' else None,
        }


class DocumentoService:
    """Servicio para gestion de documentos."""

    @staticmethod
    def obtener_documento(documento_id: int, usuario=None) -> Documento | None:
        """Obtiene un documento por ID."""
        try:
            filtros = {'pk': documento_id}

            if usuario:
                if usuario.rol == 'cliente':
                    filtros['solicitud__cliente'] = usuario
                elif usuario.rol == 'asesor':
                    filtros['solicitud__asesor'] = usuario

            return Documento.objects.get(**filtros)
        except Documento.DoesNotExist:
            return None

    @staticmethod
    def subir_documento(solicitud: Solicitud, archivo, nombre: str) -> Documento:
        """Sube un nuevo documento a una solicitud."""
        return Documento.objects.create(
            solicitud=solicitud,
            nombre=nombre,
            archivo=archivo,
            estado='pendiente'
        )

    @staticmethod
    def resubir_documento(documento: Documento, nuevo_archivo) -> tuple[bool, str | None]:
        """
        Permite al cliente resubir un documento que fue rechazado.
        El documento vuelve a estado 'pendiente' para nueva revisión.
        
        Args:
            documento: Instancia de Documento rechazado
            nuevo_archivo: Nuevo archivo subido
            
        Returns:
            Tuple (exito, mensaje_error)
        """
        # Solo documentos rechazados pueden ser resubidos
        if documento.estado != 'rechazado':
            return False, 'Solo se pueden resubir documentos rechazados'
        
        # Verificar que la solicitud permita modificaciones
        if not documento.solicitud.puede_modificar_documentos():
            return False, 'La solicitud ya fue enviada a la embajada, no se pueden modificar documentos'
        
        # Guardar el archivo anterior para referencia (opcional)
        archivo_anterior = documento.archivo.name if documento.archivo else None
        
        # Actualizar el documento
        documento.archivo = nuevo_archivo
        documento.estado = 'pendiente'
        documento.motivo_rechazo = ''  # Limpiar motivo anterior
        documento.revisado_por = None
        documento.fecha_revision = None
        documento.save()
        
        return True, None

    @staticmethod
    def puede_modificar_documento(documento: Documento) -> tuple[bool, str | None]:
        """
        Verifica si un documento puede ser modificado (aprobado/rechazado).
        IDEMPOTENTE: permite re-evaluacion mientras la solicitud este en revision.
        """
        solicitud = documento.solicitud
        if not solicitud.puede_modificar_documentos():
            return False, 'No se pueden modificar documentos de una solicitud enviada a la embajada'
        return True, None

    @staticmethod
    def aprobar_documento(documento: Documento, revisor) -> tuple[bool, str | None]:
        """
        Aprueba un documento.
        IDEMPOTENTE: permite re-aprobar mientras la solicitud este en revision.
        """
        puede, error = DocumentoService.puede_modificar_documento(documento)
        if not puede:
            return False, error

        documento.estado = 'aprobado'
        documento.revisado_por = revisor
        documento.fecha_revision = timezone.now()
        documento.motivo_rechazo = ''
        documento.save()
        return True, None

    @staticmethod
    def rechazar_documento(documento: Documento, revisor, motivo: str) -> tuple[bool, str | None]:
        """
        Rechaza un documento con motivo.
        IDEMPOTENTE: permite re-evaluar mientras la solicitud este en revision.
        """
        puede, error = DocumentoService.puede_modificar_documento(documento)
        if not puede:
            return False, error

        documento.estado = 'rechazado'
        documento.revisado_por = revisor
        documento.fecha_revision = timezone.now()
        documento.motivo_rechazo = motivo
        documento.save()
        return True, None

    @staticmethod
    def listar_documentos(solicitud_id: int, usuario=None):
        """Lista documentos de una solicitud."""
        queryset = Documento.objects.filter(solicitud_id=solicitud_id)

        if usuario:
            if usuario.rol == 'cliente':
                queryset = queryset.filter(solicitud__cliente=usuario)
            elif usuario.rol == 'asesor':
                queryset = queryset.filter(solicitud__asesor=usuario)

        return queryset


class EntrevistaService:
    """Servicio para gestión de entrevistas."""
    
    @staticmethod
    def obtener_entrevista(entrevista_id: int, usuario=None) -> Entrevista | None:
        """Obtiene una entrevista por ID."""
        try:
            filtros = {'pk': entrevista_id}
            
            if usuario:
                if usuario.rol == 'cliente':
                    filtros['solicitud__cliente'] = usuario
                elif usuario.rol == 'asesor':
                    filtros['solicitud__asesor'] = usuario
            
            return Entrevista.objects.select_related('solicitud', 'solicitud__cliente').get(**filtros)
        except Entrevista.DoesNotExist:
            return None
    
    @staticmethod
    def listar_entrevistas(usuario, estado: str = None):
        """Lista entrevistas según el rol del usuario."""
        if usuario.rol == 'cliente':
            queryset = Entrevista.objects.filter(solicitud__cliente=usuario)
        elif usuario.rol == 'asesor':
            queryset = Entrevista.objects.filter(solicitud__asesor=usuario)
        else:
            queryset = Entrevista.objects.all()
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.select_related('solicitud', 'solicitud__cliente').order_by('fecha', 'hora')
    
    @staticmethod
    def obtener_horarios_disponibles(fecha: str) -> list:
        """Obtiene horarios disponibles para una fecha."""
        ocupados = Entrevista.objects.filter(
            fecha=fecha,
            estado__in=['agendada', 'confirmada', 'reprogramada']
        ).values_list('hora', flat=True)
        
        ocupados_str = [h.strftime('%H:%M') for h in ocupados]
        
        return [
            {'horario': h, 'estado': 'Ocupado' if h in ocupados_str else 'Disponible'}
            for h in HORARIOS_ENTREVISTA
        ]
    
    @staticmethod
    def agendar(solicitud: Solicitud, fecha: str, hora: str,
                ubicacion: str = '') -> tuple[Entrevista | None, str | None]:
        """
        Agenda una entrevista para una solicitud.

        CRITICO: Solo se puede agendar si la solicitud fue APROBADA POR LA EMBAJADA.
        
        FLUJO CORRECTO:
        1. Asesor aprueba solicitud (estado: aprobada)
        2. Asesor envía a embajada (estado: enviada_embajada o esperando_decision_embajada)
        3. Asesor registra decisión de embajada
        4. Si embajada aprueba -> estado: aprobada_embajada
        5. SOLO ENTONCES se puede agendar entrevista -> estado: entrevista_agendada
        
        Esto corrige el flujo anterior donde se saltaba la decision de la embajada.
        
        Args:
            solicitud: Instancia de Solicitud (debe estar en estado 'aprobada_embajada')
            fecha: Fecha de la entrevista (YYYY-MM-DD)
            hora: Hora de la entrevista (HH:MM)
            ubicacion: Ubicación de la entrevista
            
        Returns:
            Tuple (Entrevista | None, error_mensaje | None)
        """
        # Validacion CRITICA: solo permitir si la embajada aprobo
        if not solicitud.puede_agendar_entrevista():
            if solicitud.estado == 'enviada_embajada':
                return None, 'La embajada aun no ha aprobado la solicitud'
            elif solicitud.estado == 'esperando_decision_embajada':
                return None, 'La solicitud esta pendiente de decision de la embajada'
            elif solicitud.estado == 'rechazada_embajada':
                return None, 'La solicitud fue rechazada por la embajada, no se puede agendar entrevista'
            elif solicitud.estado == 'aprobada':
                return None, 'La solicitud aun no ha sido enviada a la embajada. Primero debe enviarla y esperar la aprobacion de la embajada.'
            else:
                return None, f'La solicitud debe estar aprobada por la embajada para agendar entrevista (estado actual: {solicitud.estado})'

        if hasattr(solicitud, 'entrevista'):
            return None, 'La solicitud ya tiene una entrevista agendada'

        entrevista = Entrevista.objects.create(
            solicitud=solicitud,
            fecha=fecha,
            hora=hora,
            ubicacion=ubicacion,
            estado='agendada'
        )

        solicitud.estado = 'entrevista_agendada'
        solicitud.save()

        return entrevista, None
    
    @staticmethod
    def confirmar(entrevista: Entrevista) -> tuple[bool, str | None]:
        """Confirma una entrevista."""
        if entrevista.estado != 'agendada':
            return False, 'La entrevista no está en estado agendada'
        
        entrevista.estado = 'confirmada'
        entrevista.save()
        return True, None
    
    @staticmethod
    def puede_reprogramar(entrevista: Entrevista) -> tuple[bool, dict]:
        """Verifica si una entrevista puede ser reprogramada."""
        reglas = REGLAS_EMBAJADA.get(entrevista.solicitud.embajada, {'max_reprogramaciones': 2})
        puede = entrevista.veces_reprogramada < reglas['max_reprogramaciones']
        
        return puede, {
            'puede_reprogramar': puede,
            'reprogramaciones_usadas': entrevista.veces_reprogramada,
            'max_reprogramaciones': reglas['max_reprogramaciones']
        }
    
    @staticmethod
    def reprogramar(entrevista: Entrevista, nueva_fecha: str, 
                    nueva_hora: str) -> tuple[bool, str | None]:
        """Reprograma una entrevista."""
        puede, info = EntrevistaService.puede_reprogramar(entrevista)
        
        if not puede:
            return False, 'Ha alcanzado el límite máximo de reprogramaciones permitidas'
        
        entrevista.fecha = nueva_fecha
        entrevista.hora = nueva_hora
        entrevista.estado = 'reprogramada'
        entrevista.veces_reprogramada += 1
        entrevista.save()
        
        return True, None
    
    @staticmethod
    def puede_cancelar(entrevista: Entrevista) -> tuple[bool, dict]:
        """Verifica si una entrevista puede ser cancelada."""
        reglas = REGLAS_EMBAJADA.get(
            entrevista.solicitud.embajada, 
            {'min_horas_cancelacion': 24}
        )
        
        fecha_entrevista = datetime.combine(entrevista.fecha, entrevista.hora)
        fecha_entrevista = timezone.make_aware(fecha_entrevista)
        horas_restantes = (fecha_entrevista - timezone.now()).total_seconds() / 3600
        
        puede = horas_restantes >= reglas['min_horas_cancelacion']
        
        return puede, {
            'puede_cancelar': puede,
            'horas_restantes': round(horas_restantes, 1),
            'min_horas_requeridas': reglas['min_horas_cancelacion']
        }
    
    @staticmethod
    def cancelar(entrevista: Entrevista, motivo: str = '') -> tuple[bool, str | None]:
        """Cancela una entrevista."""
        puede, info = EntrevistaService.puede_cancelar(entrevista)
        
        if not puede:
            return False, 'No es posible cancelar: no cumple tiempo mínimo de anticipación'
        
        entrevista.estado = 'cancelada'
        entrevista.motivo_cancelacion = motivo
        entrevista.save()
        
        return True, None
    
    @staticmethod
    def obtener_proximas(usuario, dias: int = 7):
        """Obtiene entrevistas próximas del usuario."""
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=dias)
        
        queryset = EntrevistaService.listar_entrevistas(usuario)
        return queryset.filter(
            fecha__gte=hoy,
            fecha__lte=limite,
            estado__in=['agendada', 'confirmada', 'reprogramada']
        )
    
    @staticmethod
    def obtener_eventos_calendario(usuario, fecha_inicio: str = None, fecha_fin: str = None):
        """Obtiene eventos para el calendario."""
        queryset = EntrevistaService.listar_entrevistas(usuario)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        return queryset.exclude(estado='cancelada')
