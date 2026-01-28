"""
Value Objects para el dominio de Agendamiento de Entrevistas.
"""
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, date, time, timedelta
from typing import List, Optional


class EstadoEntrevista(Enum):
    """Estados posibles de una entrevista."""
    PENDIENTE_ASIGNACION = "PENDIENTE_ASIGNACION"  # Esperando que embajada asigne
    AGENDADA = "AGENDADA"  # Fecha asignada por embajada
    OPCIONES_DISPONIBLES = "OPCIONES_DISPONIBLES"  # Embajada ofrece opciones
    CONFIRMADA = "CONFIRMADA"  # Migrante confirmó asistencia
    REPROGRAMADA = "REPROGRAMADA"
    CANCELADA = "CANCELADA"
    COMPLETADA = "COMPLETADA"
    NO_ASISTIO = "NO_ASISTIO"


class ModoAsignacion(Enum):
    """Modo en que la embajada asigna la cita."""
    FECHA_FIJA = "FECHA_FIJA"  # Embajada asigna fecha directamente
    OPCIONES_ELEGIR = "OPCIONES_ELEGIR"  # Embajada ofrece opciones para elegir


class MotivoCancelacion(Enum):
    """Motivos de cancelación de entrevista."""
    SOLICITUD_MIGRANTE = "SOLICITUD_MIGRANTE"
    REPROGRAMACION_EMBAJADA = "REPROGRAMACION_EMBAJADA"
    DOCUMENTOS_INCOMPLETOS = "DOCUMENTOS_INCOMPLETOS"
    EMERGENCIA = "EMERGENCIA"
    OTRO = "OTRO"


@dataclass(frozen=True)
class HorarioEntrevista:
    """Value Object para un horario de entrevista."""
    fecha: date
    hora: time
    duracion_minutos: int = 30
    
    def datetime_inicio(self) -> datetime:
        """Retorna el datetime de inicio."""
        return datetime.combine(self.fecha, self.hora)
    
    def a_datetime(self) -> datetime:
        """Alias de datetime_inicio() para compatibilidad."""
        return self.datetime_inicio()

    def datetime_fin(self) -> datetime:
        """Retorna el datetime de fin."""
        return self.datetime_inicio() + timedelta(minutes=self.duracion_minutos)
    
    def es_futuro(self) -> bool:
        """Verifica si el horario es en el futuro."""
        return self.datetime_inicio() > datetime.now()
    
    def dias_restantes(self) -> int:
        """Calcula los días restantes hasta la entrevista."""
        delta = self.fecha - date.today()
        return delta.days
    
    def horas_restantes(self) -> float:
        """Calcula las horas restantes hasta la entrevista."""
        delta = self.datetime_inicio() - datetime.now()
        return delta.total_seconds() / 3600
    
    def formato_legible(self) -> str:
        """Retorna el horario en formato legible."""
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        return f"{self.fecha.day} de {meses[self.fecha.month]} de {self.fecha.year}"


@dataclass
class OpcionHorario:
    """Value Object para una opción de horario ofrecida por la embajada."""
    id: str
    horario: HorarioEntrevista
    disponible: bool = True
    capacidad_maxima: int = 1
    entrevistas_asignadas: int = 0

    def esta_disponible(self) -> bool:
        """Verifica si la opción está disponible."""
        return self.disponible and self.entrevistas_asignadas < self.capacidad_maxima

    def ocupar(self) -> bool:
        """Marca la opción como ocupada."""
        if self.esta_disponible():
            self.entrevistas_asignadas += 1
            if self.entrevistas_asignadas >= self.capacidad_maxima:
                self.disponible = False
            return True
        return False

    def liberar(self) -> None:
        """Libera un espacio en la opción."""
        if self.entrevistas_asignadas > 0:
            self.entrevistas_asignadas -= 1
            if self.entrevistas_asignadas < self.capacidad_maxima:
                self.disponible = True

    def __str__(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.horario.formato_legible()} a las {self.horario.hora} - {estado}"


@dataclass(frozen=True)
class ReglaEmbajada:
    """Value Object para reglas específicas de una embajada."""
    embajada: str
    max_reprogramaciones: int = 2
    horas_minimas_cancelacion: int = 24
    dias_minimos_anticipacion: int = 7
    
    def puede_reprogramar(self, veces_reprogramada: int) -> bool:
        """Verifica si se puede reprogramar."""
        return veces_reprogramada < self.max_reprogramaciones
    
    def puede_cancelar(self, horas_restantes: float) -> bool:
        """Verifica si se puede cancelar según tiempo restante."""
        return horas_restantes >= self.horas_minimas_cancelacion
    
    def es_fecha_valida(self, fecha: date) -> bool:
        """Verifica si la fecha cumple con la anticipación mínima."""
        dias = (fecha - date.today()).days
        return dias >= self.dias_minimos_anticipacion


@dataclass(frozen=True)
class NotificacionEmbajada:
    """Value Object para notificación recibida de la embajada."""
    tipo: str  # 'APROBACION', 'RECHAZO', 'CITA_ASIGNADA', 'OPCIONES_CITA'
    mensaje: str
    fecha_recepcion: datetime
    datos: dict = None
    
    def es_aprobacion(self) -> bool:
        return self.tipo == 'APROBACION'
    
    def es_rechazo(self) -> bool:
        return self.tipo == 'RECHAZO'
    
    def tiene_cita(self) -> bool:
        return self.tipo in ['CITA_ASIGNADA', 'OPCIONES_CITA']


# Reglas predefinidas por embajada
REGLAS_EMBAJADAS = {
    'USA': ReglaEmbajada(
        embajada='USA',
        max_reprogramaciones=2,
        horas_minimas_cancelacion=24,
        dias_minimos_anticipacion=7
    ),
    'ESTADOUNIDENSE': ReglaEmbajada(
        embajada='ESTADOUNIDENSE',
        max_reprogramaciones=2,
        horas_minimas_cancelacion=24,
        dias_minimos_anticipacion=7
    ),
    'España': ReglaEmbajada(
        embajada='España',
        max_reprogramaciones=2,
        horas_minimas_cancelacion=48,
        dias_minimos_anticipacion=10
    ),
    'ESPAÑOLA': ReglaEmbajada(
        embajada='ESPAÑOLA',
        max_reprogramaciones=2,
        horas_minimas_cancelacion=48,
        dias_minimos_anticipacion=10
    ),
    'Canadá': ReglaEmbajada(
        embajada='Canadá',
        max_reprogramaciones=1,
        horas_minimas_cancelacion=72,
        dias_minimos_anticipacion=14
    ),
    'CANADIENSE': ReglaEmbajada(
        embajada='CANADIENSE',
        max_reprogramaciones=1,
        horas_minimas_cancelacion=72,
        dias_minimos_anticipacion=14
    ),
    'BRASILEÑA': ReglaEmbajada(
        embajada='BRASILEÑA',
        max_reprogramaciones=2,
        horas_minimas_cancelacion=24,
        dias_minimos_anticipacion=7
    ),
}


def obtener_regla_embajada(embajada: str) -> ReglaEmbajada:
    """Obtiene la regla para una embajada específica."""
    return REGLAS_EMBAJADAS.get(
        embajada,
        ReglaEmbajada(embajada=embajada)  # Regla por defecto
    )
