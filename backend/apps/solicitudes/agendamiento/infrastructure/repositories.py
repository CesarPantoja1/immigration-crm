"""
Implementación de Repositorios para Agendamiento con Django ORM.
"""
from typing import List, Optional
from datetime import date, timedelta
from django.utils import timezone

from ..domain.entities import Entrevista, RespuestaEmbajada, GestorEntrevistas
from ..domain.repositories import (
    IEntrevistaRepository,
    IRespuestaEmbajadaRepository,
    IGestorEntrevistasRepository
)
from ..domain.value_objects import (
    EstadoEntrevista,
    ModoAsignacion,
    MotivoCancelacion,
    HorarioEntrevista,
    OpcionHorario
)
from .models import (
    EntrevistaModel,
    OpcionHorarioModel,
    HistorialHorarioModel,
    RespuestaEmbajadaModel,
    HorarioDisponibleModel,
    ReglaEmbajadaModel
)


class DjangoEntrevistaRepository(IEntrevistaRepository):
    """Implementación Django del repositorio de Entrevistas."""
    
    def guardar(self, entrevista: Entrevista) -> Entrevista:
        """Guarda o actualiza una entrevista."""
        if entrevista.id_entrevista:
            # Actualizar existente
            try:
                model = EntrevistaModel.objects.get(id=entrevista.id_entrevista)
            except EntrevistaModel.DoesNotExist:
                model = EntrevistaModel()
        else:
            model = EntrevistaModel()
        
        # Mapear entidad a modelo
        model.solicitud_id = entrevista.solicitud_id
        model.embajada = entrevista.embajada
        model.estado = entrevista.estado.value
        model.modo_asignacion = entrevista.modo_asignacion.value if entrevista.modo_asignacion else None
        model.fecha = entrevista.horario.fecha if entrevista.horario else None
        model.hora = entrevista.horario.hora if entrevista.horario else None
        model.ubicacion = entrevista.ubicacion
        model.notas = entrevista.notas
        model.veces_reprogramada = entrevista.veces_reprogramada
        model.cancelada = entrevista.cancelada
        model.motivo_cancelacion = entrevista.motivo_cancelacion.value if entrevista.motivo_cancelacion else None
        model.detalle_cancelacion = entrevista.detalle_cancelacion
        model.fecha_confirmacion = entrevista.fecha_confirmacion
        model.fecha_completada = entrevista.fecha_completada
        
        model.save()
        
        # Guardar opciones de horario
        if entrevista.opciones_horario:
            self._guardar_opciones(model, entrevista.opciones_horario, entrevista.opcion_seleccionada)
        
        # Guardar historial de horarios
        if entrevista.historial_horarios:
            self._guardar_historial(model, entrevista.historial_horarios)
        
        entrevista.id_entrevista = str(model.id)
        entrevista.codigo = model.codigo
        
        return entrevista
    
    def _guardar_opciones(self, model: EntrevistaModel, opciones: List[OpcionHorario], seleccionada_id: Optional[str]):
        """Guarda las opciones de horario."""
        for opcion in opciones:
            OpcionHorarioModel.objects.update_or_create(
                id=opcion.id,
                defaults={
                    'entrevista': model,
                    'fecha': opcion.horario.fecha,
                    'hora': opcion.horario.hora,
                    'disponible': opcion.disponible,
                    'seleccionada': opcion.id == seleccionada_id
                }
            )
    
    def _guardar_historial(self, model: EntrevistaModel, historial: List[HorarioEntrevista]):
        """Guarda el historial de horarios."""
        for horario in historial:
            existe = HistorialHorarioModel.objects.filter(
                entrevista=model,
                fecha=horario.fecha,
                hora=horario.hora
            ).exists()
            
            if not existe:
                HistorialHorarioModel.objects.create(
                    entrevista=model,
                    fecha=horario.fecha,
                    hora=horario.hora
                )
    
    def obtener_por_id(self, entrevista_id: str) -> Optional[Entrevista]:
        """Obtiene una entrevista por su ID."""
        try:
            model = EntrevistaModel.objects.get(id=entrevista_id)
            return self._model_a_entidad(model)
        except EntrevistaModel.DoesNotExist:
            return None
    
    def obtener_por_solicitud(self, solicitud_id: str) -> Optional[Entrevista]:
        """Obtiene la entrevista activa de una solicitud."""
        try:
            model = EntrevistaModel.objects.filter(
                solicitud_id=solicitud_id
            ).exclude(
                estado__in=['CANCELADA', 'COMPLETADA', 'NO_ASISTIO']
            ).first()
            
            if model:
                return self._model_a_entidad(model)
            return None
        except Exception:
            return None
    
    def obtener_por_codigo(self, codigo: str) -> Optional[Entrevista]:
        """Obtiene una entrevista por su código."""
        try:
            model = EntrevistaModel.objects.get(codigo=codigo)
            return self._model_a_entidad(model)
        except EntrevistaModel.DoesNotExist:
            return None
    
    def listar_por_migrante(self, migrante_id: str) -> List[Entrevista]:
        """Lista todas las entrevistas de un migrante."""
        models = EntrevistaModel.objects.filter(
            solicitud__migrante_id=migrante_id
        ).order_by('-fecha_creacion')
        
        return [self._model_a_entidad(m) for m in models]
    
    def listar_por_embajada(self, embajada: str) -> List[Entrevista]:
        """Lista todas las entrevistas de una embajada."""
        models = EntrevistaModel.objects.filter(
            embajada=embajada
        ).order_by('-fecha_creacion')
        
        return [self._model_a_entidad(m) for m in models]
    
    def listar_por_fecha(self, fecha: date) -> List[Entrevista]:
        """Lista todas las entrevistas de una fecha."""
        models = EntrevistaModel.objects.filter(
            fecha=fecha
        ).order_by('hora')
        
        return [self._model_a_entidad(m) for m in models]
    
    def listar_pendientes(self) -> List[Entrevista]:
        """Lista entrevistas pendientes de asignación."""
        models = EntrevistaModel.objects.filter(
            estado='PENDIENTE_ASIGNACION'
        ).order_by('fecha_creacion')
        
        return [self._model_a_entidad(m) for m in models]
    
    def listar_proximas(self, dias: int = 7) -> List[Entrevista]:
        """Lista entrevistas en los próximos X días."""
        hoy = date.today()
        fecha_limite = hoy + timedelta(days=dias)
        
        models = EntrevistaModel.objects.filter(
            fecha__gte=hoy,
            fecha__lte=fecha_limite,
            estado__in=['AGENDADA', 'CONFIRMADA', 'REPROGRAMADA']
        ).order_by('fecha', 'hora')
        
        return [self._model_a_entidad(m) for m in models]
    
    def eliminar(self, entrevista_id: str) -> bool:
        """Elimina una entrevista."""
        try:
            EntrevistaModel.objects.get(id=entrevista_id).delete()
            return True
        except EntrevistaModel.DoesNotExist:
            return False
    
    def _model_a_entidad(self, model: EntrevistaModel) -> Entrevista:
        """Convierte un modelo Django a entidad de dominio."""
        horario = None
        if model.fecha and model.hora:
            horario = HorarioEntrevista(fecha=model.fecha, hora=model.hora)
        
        # Cargar opciones
        opciones = []
        opcion_seleccionada = None
        for opcion_model in model.opciones_horario.all():
            opcion = OpcionHorario(
                id=str(opcion_model.id),
                horario=HorarioEntrevista(fecha=opcion_model.fecha, hora=opcion_model.hora),
                disponible=opcion_model.disponible
            )
            opciones.append(opcion)
            if opcion_model.seleccionada:
                opcion_seleccionada = str(opcion_model.id)
        
        # Cargar historial
        historial = [
            HorarioEntrevista(fecha=h.fecha, hora=h.hora)
            for h in model.historial_horarios.all()
        ]
        
        return Entrevista(
            solicitud_id=str(model.solicitud_id),
            embajada=model.embajada,
            estado=EstadoEntrevista(model.estado),
            modo_asignacion=ModoAsignacion(model.modo_asignacion) if model.modo_asignacion else None,
            horario=horario,
            opciones_horario=opciones,
            opcion_seleccionada=opcion_seleccionada,
            id_entrevista=str(model.id),
            codigo=model.codigo,
            ubicacion=model.ubicacion,
            notas=model.notas,
            veces_reprogramada=model.veces_reprogramada,
            historial_horarios=historial,
            cancelada=model.cancelada,
            motivo_cancelacion=MotivoCancelacion(model.motivo_cancelacion) if model.motivo_cancelacion else None,
            detalle_cancelacion=model.detalle_cancelacion,
            fecha_creacion=model.fecha_creacion,
            fecha_confirmacion=model.fecha_confirmacion,
            fecha_completada=model.fecha_completada
        )


class DjangoRespuestaEmbajadaRepository(IRespuestaEmbajadaRepository):
    """Implementación Django del repositorio de Respuestas de Embajada."""
    
    def guardar(self, respuesta: RespuestaEmbajada) -> RespuestaEmbajada:
        """Guarda una respuesta de embajada."""
        model = RespuestaEmbajadaModel.objects.create(
            solicitud_id=respuesta.solicitud_id,
            tipo_respuesta=respuesta.tipo_respuesta,
            motivo_rechazo=respuesta.motivo_rechazo,
            puede_apelar=respuesta.puede_apelar,
            mensaje=respuesta.mensaje
        )
        
        return respuesta
    
    def obtener_por_solicitud(self, solicitud_id: str) -> List[RespuestaEmbajada]:
        """Obtiene todas las respuestas para una solicitud."""
        models = RespuestaEmbajadaModel.objects.filter(
            solicitud_id=solicitud_id
        ).order_by('-fecha_respuesta')
        
        return [self._model_a_entidad(m) for m in models]
    
    def obtener_ultima_respuesta(self, solicitud_id: str) -> Optional[RespuestaEmbajada]:
        """Obtiene la última respuesta de una solicitud."""
        model = RespuestaEmbajadaModel.objects.filter(
            solicitud_id=solicitud_id
        ).order_by('-fecha_respuesta').first()
        
        if model:
            return self._model_a_entidad(model)
        return None
    
    def _model_a_entidad(self, model: RespuestaEmbajadaModel) -> RespuestaEmbajada:
        """Convierte un modelo a entidad."""
        return RespuestaEmbajada(
            solicitud_id=str(model.solicitud_id),
            tipo_respuesta=model.tipo_respuesta,
            fecha_respuesta=model.fecha_respuesta,
            motivo_rechazo=model.motivo_rechazo,
            puede_apelar=model.puede_apelar,
            mensaje=model.mensaje
        )


class DjangoGestorEntrevistasRepository(IGestorEntrevistasRepository):
    """Implementación Django del repositorio de Gestores de Entrevistas."""
    
    def __init__(self):
        self.entrevista_repo = DjangoEntrevistaRepository()
    
    def guardar(self, gestor: GestorEntrevistas) -> GestorEntrevistas:
        """Guarda el gestor de entrevistas."""
        if gestor.entrevista_actual:
            self.entrevista_repo.guardar(gestor.entrevista_actual)
        
        for entrevista in gestor.historial_entrevistas:
            self.entrevista_repo.guardar(entrevista)
        
        return gestor
    
    def obtener_por_solicitud(self, solicitud_id: str) -> Optional[GestorEntrevistas]:
        """Obtiene el gestor de entrevistas de una solicitud."""
        entrevista_actual = self.entrevista_repo.obtener_por_solicitud(solicitud_id)
        
        if not entrevista_actual:
            return None
        
        # Obtener historial
        all_entrevistas = EntrevistaModel.objects.filter(
            solicitud_id=solicitud_id
        ).order_by('-fecha_creacion')
        
        historial = []
        for model in all_entrevistas:
            if str(model.id) != entrevista_actual.id_entrevista:
                historial.append(self.entrevista_repo._model_a_entidad(model))
        
        return GestorEntrevistas(
            solicitud_id=solicitud_id,
            embajada=entrevista_actual.embajada,
            entrevista_actual=entrevista_actual,
            historial_entrevistas=historial
        )
    
    def crear(self, solicitud_id: str, embajada: str) -> GestorEntrevistas:
        """Crea un nuevo gestor de entrevistas."""
        return GestorEntrevistas(
            solicitud_id=solicitud_id,
            embajada=embajada
        )
