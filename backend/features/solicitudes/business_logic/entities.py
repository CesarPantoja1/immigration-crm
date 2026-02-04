# -*- coding: utf-8 -*-
"""
Entidades del dominio para testing BDD de Agendamiento de Entrevistas.

RESPONSABILIDAD:
- Representar conceptos del dominio (Entrevista, Horario, etc.)
- Encapsular comportamientos básicos sin lógica de negocio compleja
- Servir como objetos en memoria para testing (sin ORM)

LÓGICA EXTRAÍDA DE steps/agendamiento_entrevista.py:
- HorarioEntrevista → HorarioEntity
- OpcionHorario → OpcionHorarioEntity
- ReglaEmbajada → ReglaEmbajadaEntity
- Entrevista → EntrevistaAgendamientoEntity

IMPORTANTE: Estas entidades NO dependen de Django ni ORM.
"""

from dataclasses import dataclass, field
from datetime import date, time
from typing import List, Optional

from .constants import (
    ESTADOS_ENTREVISTA,
    ESTADOS_ENTREVISTA_LEGIBLES,
    REGLAS_EMBAJADA_DEFAULT,
    REGLA_EMBAJADA_DEFAULT,
)


# ============================================================
# ENTIDADES DE HORARIO
# ============================================================

@dataclass
class HorarioEntity:
    """
    Representa un horario de entrevista.
    Combina fecha y hora en una sola entidad.
    """
    fecha: date
    hora: time

    def obtener_fecha_legible(self) -> str:
        """Retorna la fecha en formato legible."""
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        return f"{self.fecha.day} de {meses[self.fecha.month]} de {self.fecha.year}"

    def obtener_hora_formateada(self) -> str:
        """Retorna la hora formateada."""
        return self.hora.strftime('%H:%M')

    def obtener_legible(self) -> str:
        """Retorna fecha y hora en formato legible."""
        return f"{self.obtener_fecha_legible()} a las {self.obtener_hora_formateada()}"


@dataclass
class OpcionHorarioEntity:
    """
    Representa una opción de horario disponible para seleccionar.
    """
    id: str
    horario: HorarioEntity
    disponible: bool = True

    def marcar_ocupado(self):
        """Marca la opción como ocupada (no disponible)."""
        self.disponible = False

    def esta_disponible(self) -> bool:
        """Verifica si la opción está disponible."""
        return self.disponible


# ============================================================
# ENTIDADES DE REGLAS
# ============================================================

@dataclass
class ReglaEmbajadaEntity:
    """
    Representa las reglas de una embajada para entrevistas.
    Define límites de reprogramación y cancelación.
    """
    embajada: str
    max_reprogramaciones: int = 2
    horas_minimas_cancelacion: int = 48

    @classmethod
    def para_embajada(cls, embajada: str) -> 'ReglaEmbajadaEntity':
        """Factory method para crear regla según embajada."""
        reglas = REGLAS_EMBAJADA_DEFAULT.get(embajada, REGLA_EMBAJADA_DEFAULT)
        return cls(
            embajada=embajada,
            max_reprogramaciones=reglas.get('max_reprogramaciones', 2),
            horas_minimas_cancelacion=reglas.get('horas_minimas_cancelacion', 48)
        )


# ============================================================
# ENTIDAD PRINCIPAL: ENTREVISTA
# ============================================================

@dataclass
class EntrevistaAgendamientoEntity:
    """
    Representa una entrevista en el contexto de agendamiento.

    Estados válidos:
    - pendiente: sin fecha asignada
    - agendada: con fecha asignada (también llamado "Programada")
    - confirmada: confirmada por el solicitante
    - reprogramada: fecha modificada
    - cancelada: cancelada
    - completada: realizada
    """
    solicitud_id: str
    embajada: str
    estado: str = 'pendiente'
    horario: Optional[HorarioEntity] = None
    veces_reprogramada: int = 0
    opciones_ofrecidas: List[OpcionHorarioEntity] = field(default_factory=list)
    regla: Optional[ReglaEmbajadaEntity] = None

    def __post_init__(self):
        """Inicializa la regla de embajada si no se proporcionó."""
        if self.regla is None:
            self.regla = ReglaEmbajadaEntity.para_embajada(self.embajada)
        # Normalizar estado
        if self.estado in ESTADOS_ENTREVISTA_LEGIBLES:
            self.estado = ESTADOS_ENTREVISTA_LEGIBLES[self.estado]

    # --- Gestión de opciones de horario ---

    def ofrecer_opciones(self, opciones: List[OpcionHorarioEntity]):
        """Ofrece opciones de horario al solicitante."""
        self.opciones_ofrecidas = opciones

    def obtener_opciones_disponibles(self) -> List[OpcionHorarioEntity]:
        """Retorna las opciones actualmente disponibles."""
        return [op for op in self.opciones_ofrecidas if op.disponible]

    def seleccionar_opcion(self, opcion_id: str) -> bool:
        """
        Selecciona una opción de horario.
        Retorna True si fue exitoso, False si no está disponible.
        """
        for opcion in self.opciones_ofrecidas:
            if opcion.id == opcion_id and opcion.disponible:
                self.horario = opcion.horario
                self.estado = 'agendada'
                opcion.marcar_ocupado()
                return True
        return False

    # --- Asignación directa de horario ---

    def asignar_horario(self, fecha: date, hora: time):
        """Asigna un horario específico a la entrevista."""
        self.horario = HorarioEntity(fecha=fecha, hora=hora)
        self.estado = 'agendada'

    # --- Consultas de estado ---

    def tiene_horario_asignado(self) -> bool:
        """Verifica si tiene horario asignado."""
        return self.horario is not None

    def obtener_fecha(self) -> Optional[date]:
        """Obtiene la fecha de la entrevista."""
        return self.horario.fecha if self.horario else None

    def obtener_horario_legible(self) -> str:
        """Obtiene el horario en formato legible."""
        if self.horario:
            return self.horario.obtener_legible()
        return ""

    def esta_agendada(self) -> bool:
        """Verifica si la entrevista está agendada."""
        return self.estado == 'agendada'

    def esta_cancelada(self) -> bool:
        """Verifica si la entrevista está cancelada."""
        return self.estado == 'cancelada'

    # --- Operaciones de estado (delegadas a servicios para lógica compleja) ---

    def puede_reprogramar(self) -> bool:
        """Verifica si se puede reprogramar según las reglas."""
        return self.veces_reprogramada < self.regla.max_reprogramaciones

    def puede_cancelar(self, horas_restantes: int) -> bool:
        """Verifica si se puede cancelar según las reglas."""
        return horas_restantes >= self.regla.horas_minimas_cancelacion

    def aplicar_reprogramacion(self, nueva_fecha: date, nueva_hora: time):
        """Aplica una reprogramación (sin validar, eso lo hace el servicio)."""
        self.horario = HorarioEntity(fecha=nueva_fecha, hora=nueva_hora)
        self.veces_reprogramada += 1
        self.estado = 'reprogramada'

    def aplicar_cancelacion(self):
        """Aplica una cancelación (sin validar, eso lo hace el servicio)."""
        self.estado = 'cancelada'

    def aplicar_confirmacion(self):
        """Aplica una confirmación."""
        self.estado = 'confirmada'


# ============================================================
# ENTIDAD DE RESULTADO
# ============================================================

@dataclass
class ResultadoOperacionEntity:
    """
    Representa el resultado de una operación.
    Usado para comunicar éxito/fracaso y mensajes.
    """
    exito: bool
    mensaje: str = ""
    datos: dict = field(default_factory=dict)


# ============================================================
# FACTORY FUNCTIONS
# ============================================================

_id_counter = {'entrevista': 0, 'opcion': 0}


def reset_id_counters():
    """Reinicia los contadores de IDs para cada escenario."""
    global _id_counter
    _id_counter = {'entrevista': 0, 'opcion': 0}


def crear_entrevista_agendamiento(solicitud_id: str, embajada: str,
                                   estado: str = 'pendiente') -> EntrevistaAgendamientoEntity:
    """Factory function para crear una entrevista de agendamiento."""
    return EntrevistaAgendamientoEntity(
        solicitud_id=solicitud_id,
        embajada=embajada,
        estado=estado
    )


def crear_horario(fecha: date, hora: time) -> HorarioEntity:
    """Factory function para crear un horario."""
    return HorarioEntity(fecha=fecha, hora=hora)


def crear_opcion_horario(horario: HorarioEntity, disponible: bool = True,
                          opcion_id: str = None) -> OpcionHorarioEntity:
    """Factory function para crear una opción de horario."""
    _id_counter['opcion'] += 1
    id_generado = opcion_id or f"OPT-{_id_counter['opcion']:03d}"
    return OpcionHorarioEntity(
        id=id_generado,
        horario=horario,
        disponible=disponible
    )


def crear_regla_embajada(embajada: str, max_reprogramaciones: int = None,
                          horas_minimas_cancelacion: int = None) -> ReglaEmbajadaEntity:
    """Factory function para crear una regla de embajada."""
    regla_base = ReglaEmbajadaEntity.para_embajada(embajada)

    if max_reprogramaciones is not None:
        regla_base.max_reprogramaciones = max_reprogramaciones
    if horas_minimas_cancelacion is not None:
        regla_base.horas_minimas_cancelacion = horas_minimas_cancelacion

    return regla_base


def crear_resultado(exito: bool, mensaje: str = "",
                    datos: dict = None) -> ResultadoOperacionEntity:
    """Factory function para crear un resultado de operación."""
    return ResultadoOperacionEntity(
        exito=exito,
        mensaje=mensaje,
        datos=datos or {}
    )
