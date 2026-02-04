"""
Entidades (Dataclasses) para Simulación de Entrevistas.
Representan los modelos de dominio sin dependencias de Django ORM.
Mapean a: apps.preparacion.models.Simulacro, Practica
"""
from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import List, Optional

from .constants import NivelDificultad


@dataclass
class HorarioSimulacro:
    """Horario del simulacro"""
    fecha: date
    hora: time


@dataclass
class Pregunta:
    """Pregunta de práctica"""
    id: str
    texto: str
    respuestas: List[str]
    respuesta_correcta: int
    explicacion: str = ""
    dificultad: NivelDificultad = NivelDificultad.MEDIO


@dataclass
class RespuestaMigrante:
    """Respuesta del migrante a una pregunta"""
    pregunta_id: str
    respuesta_seleccionada: int
    es_correcta: bool
    tiempo_segundos: int = 0


@dataclass
class ResultadoPractica:
    """Resultado de una sesión de práctica"""
    total_preguntas: int
    respuestas_correctas: int
    respuestas_incorrectas: int
    tiempo_total_segundos: int = 0

    def calcular_porcentaje(self) -> int:
        if self.total_preguntas == 0:
            return 0
        return int((self.respuestas_correctas / self.total_preguntas) * 100)

    def obtener_calificacion(self) -> str:
        porcentaje = self.calcular_porcentaje()
        if porcentaje >= 90:
            return "Excelente"
        elif porcentaje >= 70:
            return "Bueno"
        elif porcentaje >= 50:
            return "Regular"
        return "Insuficiente"

    def obtener_mensaje_motivacional(self) -> str:
        calificacion = self.obtener_calificacion()
        mensajes = {
            "Excelente": "Muy bien! Estas muy preparado",
            "Bueno": "Buen trabajo, repasa las preguntas incorrectas",
            "Regular": "Necesitas practicar más antes del simulacro real",
            "Insuficiente": "Te recomendamos practicar más antes de la entrevista"
        }
        return mensajes.get(calificacion, "Sigue practicando")


@dataclass
class Transcripcion:
    """Transcripción de un simulacro"""
    simulacro_id: str
    contenido: str
    fecha: datetime = field(default_factory=datetime.now)


@dataclass
class FeedbackAsesor:
    """Feedback del asesor sobre un simulacro"""
    simulacro_id: str
    asesor_id: str
    comentarios: str
    puntuacion: int
    fortalezas: List[str] = field(default_factory=list)
    areas_mejora: List[str] = field(default_factory=list)
    recomendaciones: str = ""


@dataclass
class PreguntaIncorrecta:
    """Pregunta respondida incorrectamente"""
    pregunta: Pregunta
    indice_respuesta_usuario: int
    explicacion: str
