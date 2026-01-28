"""
Value Objects para el dominio de Simulación de Entrevistas.
"""
from dataclasses import dataclass, field
from datetime import datetime, date, time
from enum import Enum
from typing import List, Optional


class TipoVisado(Enum):
    """Tipos de visado para simulación."""
    VIVIENDA = "Vivienda"
    ESTUDIANTE = "Estudiante"
    TRABAJO = "Trabajo"
    TURISMO = "Turismo"


class ModalidadSimulacro(Enum):
    """Modalidad del simulacro."""
    VIRTUAL = "Virtual"
    PRESENCIAL = "Presencial"


class EstadoSimulacro(Enum):
    """Estados del simulacro."""
    AGENDADO = "Agendado"
    EN_PROGRESO = "En Progreso"
    PENDIENTE_FEEDBACK = "Pendiente de Feedback"
    COMPLETADO = "Completado"
    CANCELADO = "Cancelado"


class NivelDificultad(Enum):
    """Nivel de dificultad de las preguntas."""
    BASICO = "Básico"
    INTERMEDIO = "Intermedio"
    AVANZADO = "Avanzado"


# Constantes del dominio
MAX_SIMULACROS_CON_ASESOR = 2
TIPOS_VISADO_DISPONIBLES = ["Vivienda", "Estudiante", "Trabajo"]


@dataclass(frozen=True)
class Pregunta:
    """Value Object para una pregunta del cuestionario."""
    id: str
    texto: str
    tipo_visado: TipoVisado
    tema: str
    respuestas: List[str]
    respuesta_correcta: int  # Índice de la respuesta correcta
    explicacion: str = ""
    nivel: NivelDificultad = NivelDificultad.INTERMEDIO
    
    def es_correcta(self, indice_respuesta: int) -> bool:
        """Verifica si la respuesta es correcta."""
        return indice_respuesta == self.respuesta_correcta
    
    def obtener_respuesta_correcta(self) -> str:
        """Obtiene el texto de la respuesta correcta."""
        return self.respuestas[self.respuesta_correcta]


@dataclass(frozen=True)
class RespuestaMigrante:
    """Value Object para una respuesta del migrante."""
    pregunta_id: str
    respuesta_seleccionada: int
    es_correcta: bool
    tiempo_respuesta_segundos: int = 0
    
    def formato_legible(self) -> str:
        """Retorna si la respuesta fue correcta o incorrecta."""
        return "Correcta" if self.es_correcta else "Incorrecta"


@dataclass(frozen=True)
class HorarioSimulacro:
    """Value Object para el horario de un simulacro."""
    fecha: date
    hora: time
    duracion_minutos: int = 60
    
    def datetime_inicio(self) -> datetime:
        """Retorna el datetime de inicio."""
        return datetime.combine(self.fecha, self.hora)
    
    def es_antes_de(self, fecha_limite: date) -> bool:
        """Verifica si el simulacro es antes de una fecha límite."""
        return self.fecha < fecha_limite
    
    def es_futuro(self) -> bool:
        """Verifica si el horario es en el futuro."""
        return self.datetime_inicio() > datetime.now()
    
    def formato_legible(self) -> str:
        """Retorna el horario en formato legible."""
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        return f"{self.fecha.day} de {meses[self.fecha.month]} de {self.fecha.year}"


@dataclass(frozen=True)
class ResultadoPractica:
    """Value Object para el resultado de una práctica individual."""
    total_preguntas: int
    respuestas_correctas: int
    respuestas_incorrectas: int
    tiempo_total_segundos: int
    tipo_visado: TipoVisado
    fecha: datetime = field(default_factory=datetime.now)
    
    @property
    def porcentaje_acierto(self) -> float:
        """Calcula el porcentaje de aciertos."""
        if self.total_preguntas == 0:
            return 0.0
        return (self.respuestas_correctas / self.total_preguntas) * 100
    
    @property
    def aprobado(self) -> bool:
        """Verifica si aprobó (70% o más)."""
        return self.porcentaje_acierto >= 70
    
    def tiempo_promedio_por_pregunta(self) -> float:
        """Calcula el tiempo promedio por pregunta en segundos."""
        if self.total_preguntas == 0:
            return 0.0
        return self.tiempo_total_segundos / self.total_preguntas


@dataclass(frozen=True)
class Transcripcion:
    """Value Object para la transcripción de un simulacro."""
    simulacro_id: str
    contenido: str
    fecha_creacion: datetime = field(default_factory=datetime.now)
    duracion_minutos: int = 0
    
    def tiene_contenido(self) -> bool:
        """Verifica si tiene contenido."""
        return len(self.contenido.strip()) > 0


@dataclass(frozen=True)
class FeedbackAsesor:
    """Value Object para el feedback del asesor."""
    simulacro_id: str
    asesor_id: str
    comentarios: str
    puntuacion: int  # 1-10
    areas_mejora: List[str]
    fortalezas: List[str]
    fecha: datetime = field(default_factory=datetime.now)
    
    def es_aprobatorio(self) -> bool:
        """Verifica si el feedback es aprobatorio (7 o más)."""
        return self.puntuacion >= 7


# Bancos de preguntas por tipo de visado
PREGUNTAS_ESTUDIANTE = [
    Pregunta(
        id="EST-001",
        texto="¿Cómo planea financiar sus estudios en el extranjero?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "Tengo ahorros personales suficientes",
            "Mis padres cubrirán los gastos",
            "Obtuve una beca de la universidad",
            "Todas las anteriores pueden ser válidas"
        ],
        respuesta_correcta=3,
        explicacion="Es importante demostrar solvencia económica de cualquier fuente válida"
    ),
    Pregunta(
        id="EST-002",
        texto="¿Por qué eligió esta universidad específica?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "Es la más barata",
            "Tiene un programa reconocido en mi área de estudio",
            "Está cerca de amigos",
            "Me la recomendó un conocido"
        ],
        respuesta_correcta=1,
        explicacion="Mostrar interés académico genuino es fundamental"
    ),
]

PREGUNTAS_TURISMO = [
    Pregunta(
        id="TUR-001",
        texto="¿Cuál es el propósito principal de su viaje?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "Conocer lugares turísticos",
            "Visitar familiares",
            "Ambos motivos",
            "Buscar trabajo"
        ],
        respuesta_correcta=2,
        explicacion="Es válido combinar turismo con visita familiar"
    ),
    Pregunta(
        id="TUR-002",
        texto="¿Qué lazos tiene en su país de origen que garanticen su retorno?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "Tengo trabajo estable",
            "Mi familia vive aquí",
            "Tengo propiedades",
            "Todas las anteriores"
        ],
        respuesta_correcta=3,
        explicacion="Demostrar arraigo es clave para visas de turismo"
    ),
]

BANCO_PREGUNTAS = {
    TipoVisado.ESTUDIANTE: PREGUNTAS_ESTUDIANTE,
    TipoVisado.TURISMO: PREGUNTAS_TURISMO,
    TipoVisado.TRABAJO: [],  # Por implementar
    TipoVisado.VIVIENDA: [],  # Por implementar
}


def obtener_preguntas_por_visado(tipo: TipoVisado) -> List[Pregunta]:
    """Obtiene las preguntas para un tipo de visado."""
    return BANCO_PREGUNTAS.get(tipo, [])
