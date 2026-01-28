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

    # Alias para compatibilidad con los tests
    @property
    def indice_correcta(self) -> int:
        """Alias de respuesta_correcta para compatibilidad."""
        return self.respuesta_correcta

    @property
    def opciones(self) -> List[str]:
        """Alias de respuestas para compatibilidad."""
        return self.respuestas

    def es_correcta(self, indice_respuesta: int) -> bool:
        """Verifica si la respuesta es correcta."""
        return indice_respuesta == self.respuesta_correcta

    def obtener_respuesta_correcta(self) -> str:
        """Obtiene el texto de la respuesta correcta."""
        if 0 <= self.respuesta_correcta < len(self.respuestas):
            return self.respuestas[self.respuesta_correcta]
        return ""


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


@dataclass
class PreguntaIncorrecta:
    """
    Representa una pregunta respondida incorrectamente para mostrar al usuario.
    Esta clase NO es frozen porque se usa para construir vistas/reportes.
    """
    pregunta: Pregunta
    indice_respuesta_usuario: int
    explicacion: str

    @property
    def respuesta_usuario(self) -> str:
        """Obtiene el texto de la respuesta del usuario."""
        if 0 <= self.indice_respuesta_usuario < len(self.pregunta.respuestas):
            return self.pregunta.respuestas[self.indice_respuesta_usuario]
        return ""

    @property
    def respuesta_correcta(self) -> str:
        """Obtiene el texto de la respuesta correcta."""
        return self.pregunta.obtener_respuesta_correcta()

    @property
    def texto(self) -> str:
        """Obtiene el texto de la pregunta."""
        return self.pregunta.texto


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

    def calcular_porcentaje(self) -> int:
        """Calcula el porcentaje de aciertos (retorna entero)."""
        if self.total_preguntas == 0:
            return 0
        return int((self.respuestas_correctas / self.total_preguntas) * 100)

    @property
    def porcentaje_acierto(self) -> float:
        """Calcula el porcentaje de aciertos (retorna float)."""
        if self.total_preguntas == 0:
            return 0.0
        return (self.respuestas_correctas / self.total_preguntas) * 100

    @property
    def aprobado(self) -> bool:
        """Verifica si aprobó (70% o más)."""
        return self.porcentaje_acierto >= 70

    def obtener_calificacion(self) -> str:
        """Obtiene la calificación textual según el porcentaje."""
        porcentaje = self.calcular_porcentaje()
        if porcentaje >= 80:
            return "Excelente"
        elif porcentaje >= 60:
            return "Bueno"
        elif porcentaje >= 40:
            return "Regular"
        else:
            return "Insuficiente"

    def obtener_mensaje_motivacional(self) -> str:
        """Obtiene un mensaje motivacional según el resultado."""
        porcentaje = self.calcular_porcentaje()
        if porcentaje >= 80:
            return "¡Muy bien! Estás muy preparado"
        elif porcentaje >= 60:
            return "Buen trabajo, repasa las preguntas incorrectas"
        elif porcentaje >= 40:
            return "Necesitas practicar más antes del simulacro real"
        else:
            return "Te recomendamos estudiar más este tema"

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
    areas_mejora: List[str] = field(default_factory=list)
    fortalezas: List[str] = field(default_factory=list)
    recomendaciones: str = ""
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
    Pregunta(
        id="EST-003",
        texto="¿Cuáles son sus planes después de completar sus estudios?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "Quedarme a trabajar en el país de estudios",
            "Regresar a mi país de origen",
            "Aplicar a otra universidad",
            "Aún no lo he decidido"
        ],
        respuesta_correcta=1,
        explicacion="Es importante demostrar intención de retorno"
    ),
    Pregunta(
        id="EST-004",
        texto="¿Tiene experiencia previa en el área que va a estudiar?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "No, es completamente nuevo para mí",
            "Sí, trabajé en el área",
            "Hice cursos relacionados",
            "Tengo conocimientos básicos"
        ],
        respuesta_correcta=2,
        explicacion="La experiencia previa fortalece tu caso"
    ),
    Pregunta(
        id="EST-005",
        texto="¿Cómo se enteró de esta universidad?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "Por internet",
            "A través de un agente educativo",
            "Por recomendación de un profesor",
            "Investigué rankings universitarios"
        ],
        respuesta_correcta=3,
        explicacion="Investigación seria demuestra compromiso"
    ),
    Pregunta(
        id="EST-006",
        texto="¿Tiene familia o amigos en el país de destino?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "Sí, muchos",
            "Algunos conocidos",
            "No, nadie",
            "Solo contactos de la universidad"
        ],
        respuesta_correcta=3,
        explicacion="No tener lazos puede ser positivo para visa de estudiante"
    ),
    Pregunta(
        id="EST-007",
        texto="¿Qué idioma utilizará para sus estudios?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "Español",
            "Inglés",
            "El idioma local",
            "Varios idiomas"
        ],
        respuesta_correcta=1,
        explicacion="Depende del país, pero el inglés es común"
    ),
    Pregunta(
        id="EST-008",
        texto="¿Ha sido aceptado en la universidad?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "Sí, tengo carta de aceptación",
            "Estoy en proceso",
            "Aún no he aplicado",
            "Solo tengo aceptación condicional"
        ],
        respuesta_correcta=0,
        explicacion="La carta de aceptación es crucial"
    ),
    Pregunta(
        id="EST-009",
        texto="¿Cuánto tiempo durará su programa de estudios?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "6 meses",
            "1 año",
            "2-4 años",
            "Más de 5 años"
        ],
        respuesta_correcta=2,
        explicacion="Programas de grado suelen ser 2-4 años"
    ),
    Pregunta(
        id="EST-010",
        texto="¿Dónde planea alojarse durante sus estudios?",
        tipo_visado=TipoVisado.ESTUDIANTE,
        tema="Financiación y Universidad",
        respuestas=[
            "Residencia universitaria",
            "Con familiares",
            "Apartamento propio",
            "Aún no lo he decidido"
        ],
        respuesta_correcta=0,
        explicacion="Tener plan de alojamiento es importante"
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
    Pregunta(
        id="TUR-003",
        texto="¿Cuánto tiempo planea quedarse?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "1 semana",
            "2-3 semanas",
            "1 mes",
            "Varios meses"
        ],
        respuesta_correcta=1,
        explicacion="Estancias cortas son más creíbles para turismo"
    ),
    Pregunta(
        id="TUR-004",
        texto="¿Cómo financiará su viaje?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "Ahorros propios",
            "Préstamo bancario",
            "Familiares pagarán",
            "Aún no lo sé"
        ],
        respuesta_correcta=0,
        explicacion="Ahorros propios demuestran solvencia"
    ),
    Pregunta(
        id="TUR-005",
        texto="¿Ha viajado al extranjero antes?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "Sí, varias veces",
            "Sí, una vez",
            "No, es mi primer viaje",
            "Solo a países vecinos"
        ],
        respuesta_correcta=0,
        explicacion="Historial de viajes ayuda a tu credibilidad"
    ),
    Pregunta(
        id="TUR-006",
        texto="¿Qué lugares específicos visitará?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "Aún no lo he planificado",
            "Los lugares turísticos principales",
            "Tengo itinerario detallado",
            "Lo que recomienden"
        ],
        respuesta_correcta=2,
        explicacion="Un itinerario muestra preparación"
    ),
    Pregunta(
        id="TUR-007",
        texto="¿Viaja solo o acompañado?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "Solo",
            "Con mi familia",
            "Con amigos",
            "En tour organizado"
        ],
        respuesta_correcta=1,
        explicacion="Viajar en familia reduce riesgo de no retorno"
    ),
    Pregunta(
        id="TUR-008",
        texto="¿Dónde se alojará durante su estadía?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "Hotel",
            "Casa de familiares",
            "Airbnb",
            "No lo he decidido"
        ],
        respuesta_correcta=0,
        explicacion="Reservas de hotel son evidencia concreta"
    ),
    Pregunta(
        id="TUR-009",
        texto="¿Cuál es su ocupación actual?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "Empleado",
            "Empresario",
            "Estudiante",
            "Desempleado"
        ],
        respuesta_correcta=0,
        explicacion="Empleo estable muestra razón para retornar"
    ),
    Pregunta(
        id="TUR-010",
        texto="¿Ha solicitado visa para este país antes?",
        tipo_visado=TipoVisado.TURISMO,
        tema="Lazos familiares y motivo viaje",
        respuestas=[
            "Sí, y fue aprobada",
            "Sí, pero fue negada",
            "No, es mi primera vez",
            "Sí, pero la cancelé"
        ],
        respuesta_correcta=2,
        explicacion="Primera solicitud o aprobaciones previas son positivas"
    ),
]

BANCO_PREGUNTAS = {
    TipoVisado.ESTUDIANTE: PREGUNTAS_ESTUDIANTE,
    TipoVisado.TURISMO: PREGUNTAS_TURISMO,
    TipoVisado.TRABAJO: [],  # Por implementar
    TipoVisado.VIVIENDA: [],  # Por implementar
}


def obtener_preguntas_por_visado(tipo: TipoVisado) -> List[Pregunta]:
    """Obtiene las preguntas para un tipo de visado (máximo 10)."""
    preguntas = BANCO_PREGUNTAS.get(tipo, [])
    # Retornar solo las primeras 10 preguntas
    return preguntas[:10]