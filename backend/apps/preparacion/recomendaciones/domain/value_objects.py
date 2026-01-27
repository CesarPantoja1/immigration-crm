"""
Value Objects para el dominio de Recomendaciones.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import List, Optional


class NivelIndicador(Enum):
    """Nivel de un indicador de desempeño."""
    ALTA = "Alta"
    ALTO = "Alto"
    MEDIA = "Media"
    MEDIO = "Medio"
    BAJA = "Baja"
    BAJO = "Bajo"


class NivelPreparacion(Enum):
    """Nivel de preparación global del migrante."""
    ALTO = "Alto"
    MEDIO = "Medio"
    BAJO = "Bajo"


class NivelImpacto(Enum):
    """Nivel de impacto de una recomendación."""
    ALTO = "Alto"
    MEDIO = "Medio"
    BAJO = "Bajo"


class CategoriaRecomendacion(Enum):
    """Categorías de recomendaciones."""
    CLARIDAD = "Claridad"
    COHERENCIA = "Coherencia"
    SEGURIDAD = "Seguridad"
    PERTINENCIA = "Pertinencia"


class TipoPregunta(Enum):
    """Tipos de preguntas de entrevista consular."""
    MOTIVO_VIAJE = "Motivo del viaje"
    SITUACION_ECONOMICA = "Situación económica"
    PLANES_PERMANENCIA = "Planes de permanencia"
    LAZOS_FAMILIARES = "Lazos familiares"
    HISTORIAL_VIAJES = "Historial de viajes"


class EstadoSimulacro(Enum):
    """Estados del simulacro para recomendaciones."""
    PENDIENTE_ANALISIS = "Pendiente de análisis"
    EN_ANALISIS = "En análisis"
    FEEDBACK_GENERADO = "Feedback generado"
    PUBLICADO = "Publicado"


class FormatoDocumento(Enum):
    """Formatos de exportación del documento."""
    PDF = "PDF"
    HTML = "HTML"


@dataclass(frozen=True)
class IndicadorDesempeno:
    """Value object que representa un indicador de desempeño evaluado."""
    nombre: str
    valor: NivelIndicador
    descripcion: Optional[str] = None
    
    @classmethod
    def claridad(cls, valor: NivelIndicador, desc: str = None) -> 'IndicadorDesempeno':
        return cls(nombre="Claridad en respuestas", valor=valor, descripcion=desc)
    
    @classmethod
    def coherencia(cls, valor: NivelIndicador, desc: str = None) -> 'IndicadorDesempeno':
        return cls(nombre="Coherencia del discurso", valor=valor, descripcion=desc)
    
    @classmethod
    def seguridad(cls, valor: NivelIndicador, desc: str = None) -> 'IndicadorDesempeno':
        return cls(nombre="Seguridad al responder", valor=valor, descripcion=desc)
    
    @classmethod
    def pertinencia(cls, valor: NivelIndicador, desc: str = None) -> 'IndicadorDesempeno':
        return cls(nombre="Pertinencia de la información", valor=valor, descripcion=desc)


@dataclass(frozen=True)
class PuntoMejora:
    """Value object que representa un punto de mejora identificado."""
    categoria: CategoriaRecomendacion
    descripcion: str
    pregunta_origen: Optional[int] = None  # número de pregunta
    tipo_pregunta_origen: Optional[TipoPregunta] = None


@dataclass(frozen=True)
class Fortaleza:
    """Value object que representa una fortaleza identificada."""
    descripcion: str
    categoria: Optional[CategoriaRecomendacion] = None
    pregunta_origen: Optional[int] = None


@dataclass
class RecomendacionAccionable:
    """Value object que representa una recomendación concreta y medible."""
    id: str = ""
    categoria: CategoriaRecomendacion = CategoriaRecomendacion.CLARIDAD
    descripcion: str = ""
    accion_concreta: str = ""  # Acción específica a tomar
    metrica_exito: str = ""  # Cómo medir el éxito
    impacto: NivelImpacto = NivelImpacto.MEDIO
    
    # Trazabilidad
    numero_pregunta_origen: Optional[int] = None
    tipo_pregunta_origen: Optional[TipoPregunta] = None
    
    def es_trazable(self) -> bool:
        """Verifica si la recomendación está asociada a una pregunta."""
        return self.numero_pregunta_origen is not None


@dataclass(frozen=True)
class PreguntaSimulacro:
    """Value object que representa una pregunta del simulacro."""
    numero: int
    tipo: TipoPregunta
    texto: str = ""
    respuesta_migrante: str = ""


@dataclass
class MetadatosDocumento:
    """Metadatos del documento de recomendaciones."""
    simulacro_id: str
    nivel_preparacion: NivelPreparacion
    estado_simulacro: EstadoSimulacro
    fecha_generacion: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    def a_dict(self) -> dict:
        """Convierte a diccionario para verificación."""
        return {
            "Nivel de preparación": self.nivel_preparacion.value,
            "Estado del simulacro": self.estado_simulacro.value,
        }


@dataclass
class AccionSugerida:
    """Acción sugerida basada en el nivel de preparación."""
    nivel_preparacion: NivelPreparacion
    descripcion: str
    prioridad: int = 1
    
    @classmethod
    def para_nivel(cls, nivel: NivelPreparacion) -> 'AccionSugerida':
        """Factory que crea la acción sugerida según el nivel."""
        acciones = {
            NivelPreparacion.BAJO: cls(
                nivel_preparacion=nivel,
                descripcion="Realizar un nuevo simulacro con asesor",
                prioridad=1
            ),
            NivelPreparacion.MEDIO: cls(
                nivel_preparacion=nivel,
                descripcion="Reforzar los puntos de mejora identificados",
                prioridad=2
            ),
            NivelPreparacion.ALTO: cls(
                nivel_preparacion=nivel,
                descripcion="Mantener el plan actual de preparación",
                prioridad=3
            ),
        }
        return acciones.get(nivel, acciones[NivelPreparacion.MEDIO])


# Mapeo de niveles para cálculos
NIVEL_A_PUNTOS = {
    NivelIndicador.ALTA: 3,
    NivelIndicador.ALTO: 3,
    NivelIndicador.MEDIA: 2,
    NivelIndicador.MEDIO: 2,
    NivelIndicador.BAJA: 1,
    NivelIndicador.BAJO: 1,
}


def calcular_nivel_preparacion(indicadores: List[IndicadorDesempeno]) -> NivelPreparacion:
    """
    Calcula el nivel de preparación global basado en los indicadores.
    
    Reglas:
    - Si todos son Alta/Alto -> Alto
    - Si todos son Baja/Bajo -> Bajo
    - En otro caso -> Medio (promedio)
    """
    if not indicadores:
        return NivelPreparacion.MEDIO
    
    puntos = [NIVEL_A_PUNTOS.get(ind.valor, 2) for ind in indicadores]
    promedio = sum(puntos) / len(puntos)
    
    if promedio >= 2.75:
        return NivelPreparacion.ALTO
    elif promedio <= 1.5:
        return NivelPreparacion.BAJO
    else:
        return NivelPreparacion.MEDIO


# Secciones obligatorias del documento
SECCIONES_DOCUMENTO = [
    "Fortalezas",
    "Puntos de mejora",
    "Recomendaciones",
    "Nivel de preparación",
]
