"""
Casos de Uso para Agendamiento de Entrevistas.
Orquestan la lógica de dominio y servicios de infraestructura.
"""
from dataclasses import dataclass
from datetime import date, time, datetime
from typing import List, Optional, Dict, Any

from ..domain.entities import Entrevista, RespuestaEmbajada, GestorEntrevistas
from ..domain.value_objects import (
    EstadoEntrevista,
    ModoAsignacion,
    MotivoCancelacion,
    HorarioEntrevista,
    OpcionHorario,
    obtener_regla_embajada
)
from ..domain.services import (
    ResultadoOperacion,
    AsignacionEntrevistaService,
    ReprogramacionService,
    CancelacionService,
    ConfirmacionService,
    NotificacionEntrevistaService,
    ValidacionEntrevistaService,
    ProcesamientoRespuestaEmbajadaService
)
from ..domain.repositories import (
    IEntrevistaRepository,
    IRespuestaEmbajadaRepository,
    IGestorEntrevistasRepository
)
from ..domain.exceptions import (
    EntrevistaNoEncontradaException,
    EntrevistaYaAgendadaException,
    SolicitudNoAprobadaException,
    OpcionNoDisponibleException
)


# ============================================================
# DTOs (Data Transfer Objects)
# ============================================================

@dataclass
class AsignarFechaFijaDTO:
    """DTO para asignar fecha fija de entrevista."""
    solicitud_id: str
    embajada: str
    fecha: date
    hora: time
    ubicacion: str = ""


@dataclass
class OfrecerOpcionesDTO:
    """DTO para ofrecer opciones de horario."""
    solicitud_id: str
    embajada: str
    opciones: List[Dict[str, Any]]  # [{fecha, hora, id}]


@dataclass
class SeleccionarOpcionDTO:
    """DTO para seleccionar una opción de horario."""
    entrevista_id: str
    opcion_id: str


@dataclass
class ReprogramarEntrevistaDTO:
    """DTO para reprogramar una entrevista."""
    entrevista_id: str
    nueva_fecha: date
    nueva_hora: time


@dataclass
class CancelarEntrevistaDTO:
    """DTO para cancelar una entrevista."""
    entrevista_id: str
    motivo: str  # Valor de MotivoCancelacion
    detalle: str = ""


@dataclass
class RespuestaEntrevistaDTO:
    """DTO con información de entrevista."""
    id: str
    codigo: str
    solicitud_id: str
    embajada: str
    estado: str
    modo_asignacion: Optional[str]
    fecha: Optional[str]
    hora: Optional[str]
    ubicacion: str
    veces_reprogramada: int
    opciones_horario: List[Dict[str, Any]]
    puede_reprogramar: bool
    puede_cancelar: bool
    mensaje: str = ""


# ============================================================
# Casos de Uso
# ============================================================

class ProcesarAprobacionEmbajadaUseCase:
    """
    Caso de Uso: Procesar la aprobación de una solicitud por la embajada.
    
    La embajada aprueba la solicitud y asigna cita (fecha fija u opciones).
    """
    
    def __init__(
        self,
        entrevista_repo: IEntrevistaRepository,
        respuesta_repo: IRespuestaEmbajadaRepository,
        gestor_repo: IGestorEntrevistasRepository
    ):
        self.entrevista_repo = entrevista_repo
        self.respuesta_repo = respuesta_repo
        self.gestor_repo = gestor_repo
        self.procesamiento_service = ProcesamientoRespuestaEmbajadaService()
    
    def ejecutar_con_fecha_fija(self, dto: AsignarFechaFijaDTO) -> RespuestaEntrevistaDTO:
        """Procesa aprobación con fecha fija asignada."""
        # Verificar que no existe entrevista activa
        entrevista_existente = self.entrevista_repo.obtener_por_solicitud(dto.solicitud_id)
        if entrevista_existente:
            raise EntrevistaYaAgendadaException(dto.solicitud_id)
        
        # Crear respuesta de embajada
        respuesta = RespuestaEmbajada.crear_aprobacion_con_fecha_fija(
            solicitud_id=dto.solicitud_id,
            embajada=dto.embajada,
            fecha=dto.fecha,
            hora=dto.hora,
            ubicacion=dto.ubicacion
        )
        
        # Guardar respuesta
        self.respuesta_repo.guardar(respuesta)
        
        # Guardar entrevista
        entrevista = respuesta.entrevista
        self.entrevista_repo.guardar(entrevista)
        
        return self._crear_respuesta_dto(entrevista, respuesta.mensaje)
    
    def ejecutar_con_opciones(self, dto: OfrecerOpcionesDTO) -> RespuestaEntrevistaDTO:
        """Procesa aprobación con opciones de horario."""
        # Verificar que no existe entrevista activa
        entrevista_existente = self.entrevista_repo.obtener_por_solicitud(dto.solicitud_id)
        if entrevista_existente:
            raise EntrevistaYaAgendadaException(dto.solicitud_id)
        
        # Convertir opciones
        opciones = []
        for i, opt in enumerate(dto.opciones):
            opcion = OpcionHorario(
                id=opt.get('id', f'OPT-{i+1}'),
                horario=HorarioEntrevista(
                    fecha=opt['fecha'],
                    hora=opt['hora']
                ),
                disponible=opt.get('disponible', True)
            )
            opciones.append(opcion)
        
        # Crear respuesta de embajada
        respuesta = RespuestaEmbajada.crear_aprobacion_con_opciones(
            solicitud_id=dto.solicitud_id,
            embajada=dto.embajada,
            opciones=opciones
        )
        
        # Guardar respuesta
        self.respuesta_repo.guardar(respuesta)
        
        # Guardar entrevista
        entrevista = respuesta.entrevista
        self.entrevista_repo.guardar(entrevista)
        
        return self._crear_respuesta_dto(entrevista, respuesta.mensaje)
    
    def _crear_respuesta_dto(self, entrevista: Entrevista, mensaje: str = "") -> RespuestaEntrevistaDTO:
        """Crea DTO de respuesta desde entidad."""
        puede_reprog, _ = entrevista.puede_reprogramar()
        puede_cancel, _ = entrevista.puede_cancelar()
        
        opciones = [
            {
                'id': opt.id,
                'fecha': str(opt.horario.fecha),
                'hora': str(opt.horario.hora),
                'disponible': opt.disponible,
                'horario_legible': opt.horario.formato_legible()
            }
            for opt in entrevista.opciones_horario
        ]
        
        return RespuestaEntrevistaDTO(
            id=entrevista.id_entrevista or "",
            codigo=entrevista.codigo or "",
            solicitud_id=entrevista.solicitud_id,
            embajada=entrevista.embajada,
            estado=entrevista.estado.value,
            modo_asignacion=entrevista.modo_asignacion.value if entrevista.modo_asignacion else None,
            fecha=str(entrevista.horario.fecha) if entrevista.horario else None,
            hora=str(entrevista.horario.hora) if entrevista.horario else None,
            ubicacion=entrevista.ubicacion,
            veces_reprogramada=entrevista.veces_reprogramada,
            opciones_horario=opciones,
            puede_reprogramar=puede_reprog,
            puede_cancelar=puede_cancel,
            mensaje=mensaje
        )


class SeleccionarOpcionHorarioUseCase:
    """
    Caso de Uso: Migrante selecciona una opción de horario.
    """
    
    def __init__(self, entrevista_repo: IEntrevistaRepository):
        self.entrevista_repo = entrevista_repo
        self.asignacion_service = AsignacionEntrevistaService()
    
    def ejecutar(self, dto: SeleccionarOpcionDTO) -> RespuestaEntrevistaDTO:
        """Ejecuta la selección de opción."""
        # Obtener entrevista
        entrevista = self.entrevista_repo.obtener_por_id(dto.entrevista_id)
        if not entrevista:
            raise EntrevistaNoEncontradaException(dto.entrevista_id)
        
        # Seleccionar opción
        resultado = self.asignacion_service.seleccionar_opcion(entrevista, dto.opcion_id)
        
        # Guardar cambios
        self.entrevista_repo.guardar(entrevista)
        
        return self._crear_respuesta_dto(entrevista, resultado.mensaje)
    
    def _crear_respuesta_dto(self, entrevista: Entrevista, mensaje: str = "") -> RespuestaEntrevistaDTO:
        """Crea DTO de respuesta."""
        puede_reprog, _ = entrevista.puede_reprogramar()
        puede_cancel, _ = entrevista.puede_cancelar()
        
        return RespuestaEntrevistaDTO(
            id=entrevista.id_entrevista or "",
            codigo=entrevista.codigo or "",
            solicitud_id=entrevista.solicitud_id,
            embajada=entrevista.embajada,
            estado=entrevista.estado.value,
            modo_asignacion=entrevista.modo_asignacion.value if entrevista.modo_asignacion else None,
            fecha=str(entrevista.horario.fecha) if entrevista.horario else None,
            hora=str(entrevista.horario.hora) if entrevista.horario else None,
            ubicacion=entrevista.ubicacion,
            veces_reprogramada=entrevista.veces_reprogramada,
            opciones_horario=[],
            puede_reprogramar=puede_reprog,
            puede_cancelar=puede_cancel,
            mensaje=mensaje
        )


class ReprogramarEntrevistaUseCase:
    """
    Caso de Uso: Reprogramar una entrevista.
    
    Valida reglas de la embajada (límite de reprogramaciones).
    """
    
    def __init__(self, entrevista_repo: IEntrevistaRepository):
        self.entrevista_repo = entrevista_repo
        self.reprogramacion_service = ReprogramacionService()
    
    def ejecutar(self, dto: ReprogramarEntrevistaDTO) -> RespuestaEntrevistaDTO:
        """Ejecuta la reprogramación."""
        # Obtener entrevista
        entrevista = self.entrevista_repo.obtener_por_id(dto.entrevista_id)
        if not entrevista:
            raise EntrevistaNoEncontradaException(dto.entrevista_id)
        
        # Reprogramar
        resultado = self.reprogramacion_service.reprogramar(
            entrevista,
            dto.nueva_fecha,
            dto.nueva_hora
        )
        
        # Guardar cambios
        self.entrevista_repo.guardar(entrevista)
        
        return self._crear_respuesta_dto(entrevista, resultado.mensaje)
    
    def _crear_respuesta_dto(self, entrevista: Entrevista, mensaje: str = "") -> RespuestaEntrevistaDTO:
        """Crea DTO de respuesta."""
        puede_reprog, _ = entrevista.puede_reprogramar()
        puede_cancel, _ = entrevista.puede_cancelar()
        
        return RespuestaEntrevistaDTO(
            id=entrevista.id_entrevista or "",
            codigo=entrevista.codigo or "",
            solicitud_id=entrevista.solicitud_id,
            embajada=entrevista.embajada,
            estado=entrevista.estado.value,
            modo_asignacion=entrevista.modo_asignacion.value if entrevista.modo_asignacion else None,
            fecha=str(entrevista.horario.fecha) if entrevista.horario else None,
            hora=str(entrevista.horario.hora) if entrevista.horario else None,
            ubicacion=entrevista.ubicacion,
            veces_reprogramada=entrevista.veces_reprogramada,
            opciones_horario=[],
            puede_reprogramar=puede_reprog,
            puede_cancelar=puede_cancel,
            mensaje=mensaje
        )


class CancelarEntrevistaUseCase:
    """
    Caso de Uso: Cancelar una entrevista.
    
    Valida tiempo mínimo de anticipación según embajada.
    """
    
    def __init__(self, entrevista_repo: IEntrevistaRepository):
        self.entrevista_repo = entrevista_repo
        self.cancelacion_service = CancelacionService()
    
    def ejecutar(self, dto: CancelarEntrevistaDTO) -> RespuestaEntrevistaDTO:
        """Ejecuta la cancelación."""
        # Obtener entrevista
        entrevista = self.entrevista_repo.obtener_por_id(dto.entrevista_id)
        if not entrevista:
            raise EntrevistaNoEncontradaException(dto.entrevista_id)
        
        # Convertir motivo
        motivo = MotivoCancelacion(dto.motivo)
        
        # Cancelar
        resultado = self.cancelacion_service.cancelar(
            entrevista,
            motivo,
            dto.detalle
        )
        
        # Guardar cambios
        self.entrevista_repo.guardar(entrevista)
        
        return self._crear_respuesta_dto(entrevista, resultado.mensaje)
    
    def _crear_respuesta_dto(self, entrevista: Entrevista, mensaje: str = "") -> RespuestaEntrevistaDTO:
        """Crea DTO de respuesta."""
        return RespuestaEntrevistaDTO(
            id=entrevista.id_entrevista or "",
            codigo=entrevista.codigo or "",
            solicitud_id=entrevista.solicitud_id,
            embajada=entrevista.embajada,
            estado=entrevista.estado.value,
            modo_asignacion=entrevista.modo_asignacion.value if entrevista.modo_asignacion else None,
            fecha=str(entrevista.horario.fecha) if entrevista.horario else None,
            hora=str(entrevista.horario.hora) if entrevista.horario else None,
            ubicacion=entrevista.ubicacion,
            veces_reprogramada=entrevista.veces_reprogramada,
            opciones_horario=[],
            puede_reprogramar=False,
            puede_cancelar=False,
            mensaje=mensaje
        )


class ConfirmarAsistenciaUseCase:
    """
    Caso de Uso: Confirmar asistencia a una entrevista.
    """
    
    def __init__(self, entrevista_repo: IEntrevistaRepository):
        self.entrevista_repo = entrevista_repo
        self.confirmacion_service = ConfirmacionService()
    
    def ejecutar(self, entrevista_id: str) -> RespuestaEntrevistaDTO:
        """Ejecuta la confirmación."""
        # Obtener entrevista
        entrevista = self.entrevista_repo.obtener_por_id(entrevista_id)
        if not entrevista:
            raise EntrevistaNoEncontradaException(entrevista_id)
        
        # Confirmar
        resultado = self.confirmacion_service.confirmar_asistencia(entrevista)
        
        # Guardar cambios
        self.entrevista_repo.guardar(entrevista)
        
        return self._crear_respuesta_dto(entrevista, resultado.mensaje)
    
    def _crear_respuesta_dto(self, entrevista: Entrevista, mensaje: str = "") -> RespuestaEntrevistaDTO:
        """Crea DTO de respuesta."""
        puede_reprog, _ = entrevista.puede_reprogramar()
        puede_cancel, _ = entrevista.puede_cancelar()
        
        return RespuestaEntrevistaDTO(
            id=entrevista.id_entrevista or "",
            codigo=entrevista.codigo or "",
            solicitud_id=entrevista.solicitud_id,
            embajada=entrevista.embajada,
            estado=entrevista.estado.value,
            modo_asignacion=entrevista.modo_asignacion.value if entrevista.modo_asignacion else None,
            fecha=str(entrevista.horario.fecha) if entrevista.horario else None,
            hora=str(entrevista.horario.hora) if entrevista.horario else None,
            ubicacion=entrevista.ubicacion,
            veces_reprogramada=entrevista.veces_reprogramada,
            opciones_horario=[],
            puede_reprogramar=puede_reprog,
            puede_cancelar=puede_cancel,
            mensaje=mensaje
        )


class ConsultarEntrevistaUseCase:
    """
    Caso de Uso: Consultar información de una entrevista.
    """
    
    def __init__(self, entrevista_repo: IEntrevistaRepository):
        self.entrevista_repo = entrevista_repo
    
    def ejecutar_por_id(self, entrevista_id: str) -> Optional[RespuestaEntrevistaDTO]:
        """Consulta por ID de entrevista."""
        entrevista = self.entrevista_repo.obtener_por_id(entrevista_id)
        if not entrevista:
            return None
        return self._crear_respuesta_dto(entrevista)
    
    def ejecutar_por_solicitud(self, solicitud_id: str) -> Optional[RespuestaEntrevistaDTO]:
        """Consulta por ID de solicitud."""
        entrevista = self.entrevista_repo.obtener_por_solicitud(solicitud_id)
        if not entrevista:
            return None
        return self._crear_respuesta_dto(entrevista)
    
    def ejecutar_por_codigo(self, codigo: str) -> Optional[RespuestaEntrevistaDTO]:
        """Consulta por código de entrevista."""
        entrevista = self.entrevista_repo.obtener_por_codigo(codigo)
        if not entrevista:
            return None
        return self._crear_respuesta_dto(entrevista)
    
    def _crear_respuesta_dto(self, entrevista: Entrevista) -> RespuestaEntrevistaDTO:
        """Crea DTO de respuesta."""
        puede_reprog, _ = entrevista.puede_reprogramar()
        puede_cancel, _ = entrevista.puede_cancelar()
        
        opciones = [
            {
                'id': opt.id,
                'fecha': str(opt.horario.fecha),
                'hora': str(opt.horario.hora),
                'disponible': opt.disponible,
                'horario_legible': opt.horario.formato_legible()
            }
            for opt in entrevista.opciones_horario
        ]
        
        return RespuestaEntrevistaDTO(
            id=entrevista.id_entrevista or "",
            codigo=entrevista.codigo or "",
            solicitud_id=entrevista.solicitud_id,
            embajada=entrevista.embajada,
            estado=entrevista.estado.value,
            modo_asignacion=entrevista.modo_asignacion.value if entrevista.modo_asignacion else None,
            fecha=str(entrevista.horario.fecha) if entrevista.horario else None,
            hora=str(entrevista.horario.hora) if entrevista.horario else None,
            ubicacion=entrevista.ubicacion,
            veces_reprogramada=entrevista.veces_reprogramada,
            opciones_horario=opciones,
            puede_reprogramar=puede_reprog,
            puede_cancelar=puede_cancel
        )


class ListarEntrevistasUseCase:
    """
    Caso de Uso: Listar entrevistas con diferentes filtros.
    """
    
    def __init__(self, entrevista_repo: IEntrevistaRepository):
        self.entrevista_repo = entrevista_repo
    
    def listar_por_migrante(self, migrante_id: str) -> List[RespuestaEntrevistaDTO]:
        """Lista entrevistas de un migrante."""
        entrevistas = self.entrevista_repo.listar_por_migrante(migrante_id)
        return [self._crear_respuesta_dto(e) for e in entrevistas]
    
    def listar_proximas(self, dias: int = 7) -> List[RespuestaEntrevistaDTO]:
        """Lista entrevistas próximas."""
        entrevistas = self.entrevista_repo.listar_proximas(dias)
        return [self._crear_respuesta_dto(e) for e in entrevistas]
    
    def listar_pendientes(self) -> List[RespuestaEntrevistaDTO]:
        """Lista entrevistas pendientes de asignación."""
        entrevistas = self.entrevista_repo.listar_pendientes()
        return [self._crear_respuesta_dto(e) for e in entrevistas]
    
    def _crear_respuesta_dto(self, entrevista: Entrevista) -> RespuestaEntrevistaDTO:
        """Crea DTO de respuesta."""
        puede_reprog, _ = entrevista.puede_reprogramar()
        puede_cancel, _ = entrevista.puede_cancelar()
        
        return RespuestaEntrevistaDTO(
            id=entrevista.id_entrevista or "",
            codigo=entrevista.codigo or "",
            solicitud_id=entrevista.solicitud_id,
            embajada=entrevista.embajada,
            estado=entrevista.estado.value,
            modo_asignacion=entrevista.modo_asignacion.value if entrevista.modo_asignacion else None,
            fecha=str(entrevista.horario.fecha) if entrevista.horario else None,
            hora=str(entrevista.horario.hora) if entrevista.horario else None,
            ubicacion=entrevista.ubicacion,
            veces_reprogramada=entrevista.veces_reprogramada,
            opciones_horario=[],
            puede_reprogramar=puede_reprog,
            puede_cancelar=puede_cancel
        )


class ObtenerReglasEmbajadaUseCase:
    """
    Caso de Uso: Obtener las reglas de una embajada.
    """
    
    def ejecutar(self, embajada: str) -> Dict[str, Any]:
        """Obtiene las reglas de la embajada."""
        regla = obtener_regla_embajada(embajada)
        
        return {
            'embajada': regla.embajada,
            'max_reprogramaciones': regla.max_reprogramaciones,
            'horas_minimas_cancelacion': regla.horas_minimas_cancelacion,
            'dias_minimos_anticipacion': regla.dias_minimos_anticipacion
        }
