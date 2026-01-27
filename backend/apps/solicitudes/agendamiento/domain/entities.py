"""
Entidades de Dominio para Agendamiento de Entrevistas.
Considerando que la embajada es quien asigna o da opciones de cita.
"""
from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict
from .value_objects import (
    EstadoEntrevista, ModoAsignacion, MotivoCancelacion,
    HorarioEntrevista, OpcionHorario, ReglaEmbajada,
    NotificacionEmbajada, obtener_regla_embajada
)


@dataclass
class Entrevista:
    """
    Entidad Entrevista - Representa una entrevista asignada por la embajada.
    
    Flujo:
    1. Solicitud aprobada por asesor → se envía a embajada
    2. Embajada responde con:
       a) Fecha fija asignada
       b) Opciones de fechas para elegir
       c) Rechazo de la solicitud
    3. Migrante confirma asistencia (si aplica)
    """
    solicitud_id: str
    embajada: str
    estado: EstadoEntrevista = EstadoEntrevista.PENDIENTE_ASIGNACION
    modo_asignacion: Optional[ModoAsignacion] = None
    
    # Horario asignado (cuando embajada da fecha fija)
    horario: Optional[HorarioEntrevista] = None
    
    # Opciones disponibles (cuando embajada da opciones)
    opciones_horario: List[OpcionHorario] = field(default_factory=list)
    opcion_seleccionada: Optional[str] = None
    
    # Datos de la entrevista
    id_entrevista: Optional[str] = None
    codigo: Optional[str] = None
    ubicacion: str = ""
    notas: str = ""
    
    # Control de reprogramaciones
    veces_reprogramada: int = 0
    historial_horarios: List[HorarioEntrevista] = field(default_factory=list)
    
    # Cancelación
    cancelada: bool = False
    motivo_cancelacion: Optional[MotivoCancelacion] = None
    detalle_cancelacion: str = ""
    
    # Fechas
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_confirmacion: Optional[datetime] = None
    fecha_completada: Optional[datetime] = None
    
    # Reglas de la embajada
    _regla: Optional[ReglaEmbajada] = field(default=None, repr=False)
    
    def __post_init__(self):
        """Inicializa reglas de embajada."""
        if self._regla is None:
            self._regla = obtener_regla_embajada(self.embajada)
    
    @property
    def regla(self) -> ReglaEmbajada:
        """Obtiene las reglas de la embajada."""
        if self._regla is None:
            self._regla = obtener_regla_embajada(self.embajada)
        return self._regla
    
    # =====================================================
    # Métodos para asignación por embajada
    # =====================================================
    
    def asignar_fecha_fija(self, fecha: date, hora: time, ubicacion: str = "") -> None:
        """
        La embajada asigna una fecha fija para la entrevista.
        """
        self.horario = HorarioEntrevista(fecha=fecha, hora=hora)
        self.modo_asignacion = ModoAsignacion.FECHA_FIJA
        self.estado = EstadoEntrevista.AGENDADA
        self.ubicacion = ubicacion
    
    def ofrecer_opciones(self, opciones: List[OpcionHorario]) -> None:
        """
        La embajada ofrece opciones de horarios para que el migrante elija.
        """
        self.opciones_horario = opciones
        self.modo_asignacion = ModoAsignacion.OPCIONES_ELEGIR
        self.estado = EstadoEntrevista.OPCIONES_DISPONIBLES
    
    def seleccionar_opcion(self, opcion_id: str) -> bool:
        """
        El migrante selecciona una de las opciones ofrecidas.
        
        Returns:
            True si la selección fue exitosa
        """
        for opcion in self.opciones_horario:
            if opcion.id == opcion_id and opcion.disponible:
                self.horario = opcion.horario
                self.opcion_seleccionada = opcion_id
                self.estado = EstadoEntrevista.AGENDADA
                return True
        return False
    
    # =====================================================
    # Métodos de estado y validación
    # =====================================================
    
    def obtener_estado(self) -> str:
        """Retorna el estado como string."""
        return self.estado.value
    
    def obtener_fecha(self) -> Optional[date]:
        """Retorna la fecha de la entrevista."""
        return self.horario.fecha if self.horario else None
    
    def obtener_hora(self) -> Optional[time]:
        """Retorna la hora de la entrevista."""
        return self.horario.hora if self.horario else None
    
    def obtener_horario_legible(self) -> str:
        """Retorna el horario en formato legible."""
        if self.horario:
            return f"{self.horario.formato_legible()} a las {self.horario.hora}"
        return "Pendiente de asignación"
    
    def tiene_fecha_asignada(self) -> bool:
        """Verifica si tiene fecha asignada."""
        return self.horario is not None
    
    def esta_confirmada(self) -> bool:
        """Verifica si la entrevista está confirmada."""
        return self.estado == EstadoEntrevista.CONFIRMADA
    
    def esta_pendiente(self) -> bool:
        """Verifica si está pendiente de asignación."""
        return self.estado == EstadoEntrevista.PENDIENTE_ASIGNACION
    
    def tiene_opciones(self) -> bool:
        """Verifica si hay opciones para elegir."""
        return self.estado == EstadoEntrevista.OPCIONES_DISPONIBLES
    
    # =====================================================
    # Métodos de confirmación
    # =====================================================
    
    def confirmar_asistencia(self) -> bool:
        """
        El migrante confirma su asistencia a la entrevista.
        
        Returns:
            True si la confirmación fue exitosa
        """
        if self.estado not in [EstadoEntrevista.AGENDADA, EstadoEntrevista.REPROGRAMADA]:
            return False
        
        if not self.tiene_fecha_asignada():
            return False
        
        self.estado = EstadoEntrevista.CONFIRMADA
        self.fecha_confirmacion = datetime.now()
        return True
    
    # =====================================================
    # Métodos de reprogramación
    # =====================================================
    
    def puede_reprogramar(self) -> tuple[bool, str]:
        """
        Verifica si la entrevista puede ser reprogramada.
        
        Returns:
            Tupla (puede_reprogramar, mensaje)
        """
        if self.veces_reprogramada >= self.regla.max_reprogramaciones:
            return False, f"Error: ha alcanzado el límite máximo de reprogramaciones permitidas"
        
        if self.veces_reprogramada == self.regla.max_reprogramaciones - 1:
            return True, "Esta es su última reprogramación permitida"
        
        return True, "Reprogramación permitida"
    
    def reprogramar(self, nueva_fecha: date, nueva_hora: time) -> tuple[bool, str]:
        """
        Reprograma la entrevista a una nueva fecha.
        
        Returns:
            Tupla (exito, mensaje)
        """
        puede, mensaje = self.puede_reprogramar()
        if not puede:
            return False, mensaje
        
        # Guardar horario anterior en historial
        if self.horario:
            self.historial_horarios.append(self.horario)
        
        # Asignar nuevo horario
        self.horario = HorarioEntrevista(fecha=nueva_fecha, hora=nueva_hora)
        self.veces_reprogramada += 1
        self.estado = EstadoEntrevista.REPROGRAMADA
        
        if self.veces_reprogramada == self.regla.max_reprogramaciones:
            return True, "Esta es su última reprogramación permitida"
        
        return True, "Entrevista reprogramada exitosamente"
    
    # =====================================================
    # Métodos de cancelación
    # =====================================================
    
    def puede_cancelar(self) -> tuple[bool, str]:
        """
        Verifica si la entrevista puede ser cancelada.
        
        Returns:
            Tupla (puede_cancelar, mensaje)
        """
        if not self.horario:
            return True, "No hay fecha asignada, puede cancelarse"
        
        horas_restantes = self.horario.horas_restantes()
        
        if horas_restantes < self.regla.horas_minimas_cancelacion:
            return False, (f"Error: no es posible cancelar la entrevista debido a que "
                          f"no se cumple el tiempo mínimo de anticipación")
        
        return True, "Cancelación permitida"
    
    def cancelar(self, motivo: MotivoCancelacion, detalle: str = "") -> tuple[bool, str]:
        """
        Cancela la entrevista.
        
        Returns:
            Tupla (exito, mensaje)
        """
        puede, mensaje = self.puede_cancelar()
        if not puede:
            return False, mensaje
        
        self.cancelada = True
        self.motivo_cancelacion = motivo
        self.detalle_cancelacion = detalle
        self.estado = EstadoEntrevista.CANCELADA
        
        return True, "Cancelación confirmada exitosamente"
    
    # =====================================================
    # Métodos de finalización
    # =====================================================
    
    def marcar_completada(self) -> None:
        """Marca la entrevista como completada."""
        self.estado = EstadoEntrevista.COMPLETADA
        self.fecha_completada = datetime.now()
    
    def marcar_no_asistio(self) -> None:
        """Marca que el migrante no asistió."""
        self.estado = EstadoEntrevista.NO_ASISTIO
    
    def __str__(self) -> str:
        return (f"Entrevista({self.codigo or self.id_entrevista}, "
                f"embajada={self.embajada}, estado={self.estado.value})")


@dataclass
class RespuestaEmbajada:
    """
    Entidad que representa la respuesta de la embajada a una solicitud.
    """
    solicitud_id: str
    tipo_respuesta: str  # 'APROBADA', 'RECHAZADA'
    fecha_respuesta: datetime = field(default_factory=datetime.now)
    
    # Para aprobación
    entrevista: Optional[Entrevista] = None
    
    # Para rechazo
    motivo_rechazo: str = ""
    puede_apelar: bool = False
    
    # Notificaciones
    mensaje: str = ""
    
    def es_aprobacion(self) -> bool:
        return self.tipo_respuesta == 'APROBADA'
    
    def es_rechazo(self) -> bool:
        return self.tipo_respuesta == 'RECHAZADA'
    
    @classmethod
    def crear_aprobacion_con_fecha_fija(
        cls,
        solicitud_id: str,
        embajada: str,
        fecha: date,
        hora: time,
        ubicacion: str = ""
    ) -> 'RespuestaEmbajada':
        """Crea una respuesta de aprobación con fecha fija."""
        entrevista = Entrevista(
            solicitud_id=solicitud_id,
            embajada=embajada
        )
        entrevista.asignar_fecha_fija(fecha, hora, ubicacion)
        
        return cls(
            solicitud_id=solicitud_id,
            tipo_respuesta='APROBADA',
            entrevista=entrevista,
            mensaje=f"Su solicitud ha sido aprobada. Entrevista agendada para el {entrevista.obtener_horario_legible()}"
        )
    
    @classmethod
    def crear_aprobacion_con_opciones(
        cls,
        solicitud_id: str,
        embajada: str,
        opciones: List[OpcionHorario]
    ) -> 'RespuestaEmbajada':
        """Crea una respuesta de aprobación con opciones de horario."""
        entrevista = Entrevista(
            solicitud_id=solicitud_id,
            embajada=embajada
        )
        entrevista.ofrecer_opciones(opciones)
        
        return cls(
            solicitud_id=solicitud_id,
            tipo_respuesta='APROBADA',
            entrevista=entrevista,
            mensaje="Su solicitud ha sido aprobada. Por favor seleccione un horario disponible."
        )
    
    @classmethod
    def crear_rechazo(
        cls,
        solicitud_id: str,
        motivo: str,
        puede_apelar: bool = False
    ) -> 'RespuestaEmbajada':
        """Crea una respuesta de rechazo."""
        return cls(
            solicitud_id=solicitud_id,
            tipo_respuesta='RECHAZADA',
            motivo_rechazo=motivo,
            puede_apelar=puede_apelar,
            mensaje=f"Su solicitud ha sido rechazada. Motivo: {motivo}"
        )


@dataclass
class GestorEntrevistas:
    """
    Agregado raíz para gestionar entrevistas de una solicitud.
    """
    solicitud_id: str
    embajada: str
    entrevista_actual: Optional[Entrevista] = None
    historial_entrevistas: List[Entrevista] = field(default_factory=list)
    
    def tiene_entrevista_activa(self) -> bool:
        """Verifica si hay una entrevista activa."""
        if not self.entrevista_actual:
            return False
        return self.entrevista_actual.estado not in [
            EstadoEntrevista.CANCELADA,
            EstadoEntrevista.COMPLETADA,
            EstadoEntrevista.NO_ASISTIO
        ]
    
    def procesar_respuesta_embajada(self, respuesta: RespuestaEmbajada) -> None:
        """Procesa la respuesta de la embajada."""
        if respuesta.es_aprobacion() and respuesta.entrevista:
            # Mover entrevista actual al historial si existe
            if self.entrevista_actual:
                self.historial_entrevistas.append(self.entrevista_actual)
            
            self.entrevista_actual = respuesta.entrevista
    
    def obtener_estado(self) -> str:
        """Obtiene el estado actual de la gestión de entrevistas."""
        if not self.entrevista_actual:
            return "SIN_ENTREVISTA"
        return self.entrevista_actual.obtener_estado()
