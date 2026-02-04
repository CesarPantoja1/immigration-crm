# -*- coding: utf-8 -*-
"""Entidades del dominio para testing BDD de Agendamiento de Entrevistas."""

from dataclasses import dataclass, field
from datetime import date, time
from typing import List, Optional

from .constants import (
    ESTADOS_ENTREVISTA_LEGIBLES,
    REGLAS_EMBAJADA_DEFAULT,
    REGLA_EMBAJADA_DEFAULT,
)


@dataclass
class HorarioEntity:
    """Representa un horario de entrevista (fecha + hora)."""
    fecha: date
    hora: time

    def obtener_fecha_legible(self) -> str:
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        return f"{self.fecha.day} de {meses[self.fecha.month]} de {self.fecha.year}"

    def obtener_hora_formateada(self) -> str:
        return self.hora.strftime('%H:%M')

    def obtener_legible(self) -> str:
        return f"{self.obtener_fecha_legible()} a las {self.obtener_hora_formateada()}"


@dataclass
class OpcionHorarioEntity:
    """Opción de horario disponible para seleccionar."""
    id: str
    horario: HorarioEntity
    disponible: bool = True

    def marcar_ocupado(self):
        self.disponible = False

    def esta_disponible(self) -> bool:
        return self.disponible


@dataclass
class ReglaEmbajadaEntity:
    """Reglas de una embajada para entrevistas."""
    embajada: str
    max_reprogramaciones: int = 2
    horas_minimas_cancelacion: int = 48

    @classmethod
    def para_embajada(cls, embajada: str) -> 'ReglaEmbajadaEntity':
        reglas = REGLAS_EMBAJADA_DEFAULT.get(embajada, REGLA_EMBAJADA_DEFAULT)
        return cls(
            embajada=embajada,
            max_reprogramaciones=reglas.get('max_reprogramaciones', 2),
            horas_minimas_cancelacion=reglas.get('horas_minimas_cancelacion', 48)
        )


@dataclass
class EntrevistaAgendamientoEntity:
    """Representa una entrevista en el contexto de agendamiento."""
    solicitud_id: str
    embajada: str
    estado: str = 'pendiente'
    horario: Optional[HorarioEntity] = None
    veces_reprogramada: int = 0
    opciones_ofrecidas: List[OpcionHorarioEntity] = field(default_factory=list)
    regla: Optional[ReglaEmbajadaEntity] = None

    def __post_init__(self):
        if self.regla is None:
            self.regla = ReglaEmbajadaEntity.para_embajada(self.embajada)
        if self.estado in ESTADOS_ENTREVISTA_LEGIBLES:
            self.estado = ESTADOS_ENTREVISTA_LEGIBLES[self.estado]

    def ofrecer_opciones(self, opciones: List[OpcionHorarioEntity]):
        self.opciones_ofrecidas = opciones

    def obtener_opciones_disponibles(self) -> List[OpcionHorarioEntity]:
        return [op for op in self.opciones_ofrecidas if op.disponible]

    def seleccionar_opcion(self, opcion_id: str) -> bool:
        for opcion in self.opciones_ofrecidas:
            if opcion.id == opcion_id and opcion.disponible:
                self.horario = opcion.horario
                self.estado = 'agendada'
                opcion.marcar_ocupado()
                return True
        return False

    def asignar_horario(self, fecha: date, hora: time):
        self.horario = HorarioEntity(fecha=fecha, hora=hora)
        self.estado = 'agendada'

    def tiene_horario_asignado(self) -> bool:
        return self.horario is not None

    def obtener_fecha(self) -> Optional[date]:
        return self.horario.fecha if self.horario else None

    def obtener_horario_legible(self) -> str:
        return self.horario.obtener_legible() if self.horario else ""

    def esta_agendada(self) -> bool:
        return self.estado == 'agendada'

    def esta_cancelada(self) -> bool:
        return self.estado == 'cancelada'

    def puede_reprogramar(self) -> bool:
        return self.veces_reprogramada < self.regla.max_reprogramaciones

    def puede_cancelar(self, horas_restantes: int) -> bool:
        return horas_restantes >= self.regla.horas_minimas_cancelacion

    def aplicar_reprogramacion(self, nueva_fecha: date, nueva_hora: time):
        self.horario = HorarioEntity(fecha=nueva_fecha, hora=nueva_hora)
        self.veces_reprogramada += 1
        self.estado = 'reprogramada'

    def aplicar_cancelacion(self):
        self.estado = 'cancelada'

    def aplicar_confirmacion(self):
        self.estado = 'confirmada'


@dataclass
class ResultadoOperacionEntity:
    """Resultado de una operación."""
    exito: bool
    mensaje: str = ""
    datos: dict = field(default_factory=dict)


# Factory functions
_id_counter = {'entrevista': 0, 'opcion': 0}


def reset_id_counters():
    global _id_counter
    _id_counter = {'entrevista': 0, 'opcion': 0}


def crear_entrevista_agendamiento(solicitud_id: str, embajada: str,
                                   estado: str = 'pendiente') -> EntrevistaAgendamientoEntity:
    return EntrevistaAgendamientoEntity(solicitud_id=solicitud_id, embajada=embajada, estado=estado)


def crear_horario(fecha: date, hora: time) -> HorarioEntity:
    return HorarioEntity(fecha=fecha, hora=hora)


def crear_opcion_horario(horario: HorarioEntity, disponible: bool = True,
                          opcion_id: str = None) -> OpcionHorarioEntity:
    _id_counter['opcion'] += 1
    id_generado = opcion_id or f"OPT-{_id_counter['opcion']:03d}"
    return OpcionHorarioEntity(id=id_generado, horario=horario, disponible=disponible)


def crear_regla_embajada(embajada: str, max_reprogramaciones: int = None,
                          horas_minimas_cancelacion: int = None) -> ReglaEmbajadaEntity:
    regla_base = ReglaEmbajadaEntity.para_embajada(embajada)
    if max_reprogramaciones is not None:
        regla_base.max_reprogramaciones = max_reprogramaciones
    if horas_minimas_cancelacion is not None:
        regla_base.horas_minimas_cancelacion = horas_minimas_cancelacion
    return regla_base


def crear_resultado(exito: bool, mensaje: str = "", datos: dict = None) -> ResultadoOperacionEntity:
    return ResultadoOperacionEntity(exito=exito, mensaje=mensaje, datos=datos or {})
