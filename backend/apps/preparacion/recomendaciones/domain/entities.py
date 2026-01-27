"""
Entidades de Dominio para Recomendaciones.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict

from .value_objects import (
    NivelPreparacion,
    NivelImpacto,
    NivelIndicador,
    CategoriaRecomendacion,
    TipoPregunta,
    EstadoSimulacro,
    FormatoDocumento,
    IndicadorDesempeno,
    PuntoMejora,
    Fortaleza,
    RecomendacionAccionable,
    PreguntaSimulacro,
    MetadatosDocumento,
    AccionSugerida,
    calcular_nivel_preparacion,
    SECCIONES_DOCUMENTO,
)


@dataclass
class TranscripcionSimulacro:
    """
    Entidad que representa la transcripción de un simulacro para análisis.
    """
    simulacro_id: str
    contenido: str = ""
    preguntas: List[PreguntaSimulacro] = field(default_factory=list)
    fecha_simulacro: Optional[datetime] = None
    
    def tiene_contenido(self) -> bool:
        """Verifica si tiene contenido para analizar."""
        return len(self.contenido.strip()) > 0 or len(self.preguntas) > 0
    
    def obtener_preguntas_por_tipo(self, tipo: TipoPregunta) -> List[PreguntaSimulacro]:
        """Obtiene preguntas de un tipo específico."""
        return [p for p in self.preguntas if p.tipo == tipo]


@dataclass
class AnalisisIA:
    """
    Entidad que representa el análisis realizado por IA sobre un simulacro.
    """
    simulacro_id: str
    indicadores: List[IndicadorDesempeno] = field(default_factory=list)
    puntos_mejora: List[PuntoMejora] = field(default_factory=list)
    fortalezas: List[Fortaleza] = field(default_factory=list)
    
    fecha_analisis: datetime = field(default_factory=datetime.now)
    completado: bool = False
    
    def agregar_indicador(self, indicador: IndicadorDesempeno):
        """Agrega un indicador de desempeño."""
        self.indicadores.append(indicador)
    
    def agregar_punto_mejora(self, punto: PuntoMejora):
        """Agrega un punto de mejora."""
        self.puntos_mejora.append(punto)
    
    def agregar_fortaleza(self, fortaleza: Fortaleza):
        """Agrega una fortaleza."""
        self.fortalezas.append(fortaleza)
    
    def obtener_nivel_preparacion(self) -> NivelPreparacion:
        """Calcula el nivel de preparación basado en los indicadores."""
        return calcular_nivel_preparacion(self.indicadores)
    
    def obtener_puntos_mejora_por_categoria(
        self, 
        categoria: CategoriaRecomendacion
    ) -> List[PuntoMejora]:
        """Obtiene puntos de mejora de una categoría específica."""
        return [p for p in self.puntos_mejora if p.categoria == categoria]
    
    def marcar_completado(self):
        """Marca el análisis como completado."""
        self.completado = True


@dataclass
class DocumentoRecomendaciones:
    """
    Entidad raíz que representa el documento de recomendaciones generado.
    """
    id: Optional[str] = None
    simulacro_id: str = ""
    
    # Contenido del documento
    fortalezas: List[Fortaleza] = field(default_factory=list)
    puntos_mejora: List[PuntoMejora] = field(default_factory=list)
    recomendaciones: List[RecomendacionAccionable] = field(default_factory=list)
    
    # Metadatos
    metadatos: Optional[MetadatosDocumento] = None
    nivel_preparacion: NivelPreparacion = NivelPreparacion.MEDIO
    estado: EstadoSimulacro = EstadoSimulacro.PENDIENTE_ANALISIS
    
    # Fechas
    fecha_generacion: Optional[datetime] = None
    fecha_publicacion: Optional[datetime] = None
    
    # Acción sugerida
    accion_sugerida: Optional[AccionSugerida] = None
    
    def generar_desde_analisis(self, analisis: AnalisisIA):
        """
        Genera el documento a partir de un análisis de IA.
        """
        self.fortalezas = list(analisis.fortalezas)
        self.puntos_mejora = list(analisis.puntos_mejora)
        self.nivel_preparacion = analisis.obtener_nivel_preparacion()
        
        # Crear metadatos
        self.metadatos = MetadatosDocumento(
            simulacro_id=self.simulacro_id,
            nivel_preparacion=self.nivel_preparacion,
            estado_simulacro=EstadoSimulacro.FEEDBACK_GENERADO,
        )
        
        self.fecha_generacion = datetime.now()
        self.estado = EstadoSimulacro.FEEDBACK_GENERADO
        
        # Generar acción sugerida
        self.accion_sugerida = AccionSugerida.para_nivel(self.nivel_preparacion)
    
    def agregar_recomendacion(self, recomendacion: RecomendacionAccionable):
        """Agrega una recomendación al documento."""
        self.recomendaciones.append(recomendacion)
    
    def obtener_secciones(self) -> List[str]:
        """Obtiene las secciones del documento."""
        return SECCIONES_DOCUMENTO.copy()
    
    def tiene_seccion(self, nombre_seccion: str) -> bool:
        """Verifica si el documento tiene una sección específica."""
        return nombre_seccion in SECCIONES_DOCUMENTO
    
    def obtener_recomendaciones_por_categoria(
        self,
        categoria: CategoriaRecomendacion
    ) -> List[RecomendacionAccionable]:
        """Obtiene recomendaciones de una categoría específica."""
        return [r for r in self.recomendaciones if r.categoria == categoria]
    
    def obtener_recomendaciones_por_impacto(
        self,
        impacto: NivelImpacto
    ) -> List[RecomendacionAccionable]:
        """Obtiene recomendaciones por nivel de impacto."""
        return [r for r in self.recomendaciones if r.impacto == impacto]
    
    def agrupar_recomendaciones_por_impacto(self) -> Dict[NivelImpacto, List[RecomendacionAccionable]]:
        """Agrupa las recomendaciones por nivel de impacto."""
        resultado = {
            NivelImpacto.ALTO: [],
            NivelImpacto.MEDIO: [],
            NivelImpacto.BAJO: [],
        }
        
        for rec in self.recomendaciones:
            resultado[rec.impacto].append(rec)
        
        return resultado
    
    def agrupar_recomendaciones_por_categoria(self) -> Dict[CategoriaRecomendacion, List[RecomendacionAccionable]]:
        """Agrupa las recomendaciones por categoría."""
        resultado = {}
        
        for rec in self.recomendaciones:
            if rec.categoria not in resultado:
                resultado[rec.categoria] = []
            resultado[rec.categoria].append(rec)
        
        return resultado
    
    def verificar_trazabilidad_completa(self) -> bool:
        """Verifica que todas las recomendaciones estén asociadas a preguntas."""
        return all(r.es_trazable() for r in self.recomendaciones)
    
    def obtener_atributos_trazabilidad(self) -> List[str]:
        """Obtiene los atributos de trazabilidad disponibles."""
        return ["numero_pregunta_origen", "tipo_pregunta_origen"]
    
    def publicar(self):
        """Publica el documento para que sea visible por el migrante."""
        self.estado = EstadoSimulacro.PUBLICADO
        self.fecha_publicacion = datetime.now()
    
    def esta_publicado(self) -> bool:
        """Verifica si el documento está publicado."""
        return self.estado == EstadoSimulacro.PUBLICADO
    
    def puede_descargarse(self) -> bool:
        """Verifica si el documento puede descargarse."""
        return self.estado in [EstadoSimulacro.FEEDBACK_GENERADO, EstadoSimulacro.PUBLICADO]
    
    def exportar_formato(self, formato: FormatoDocumento) -> bytes:
        """
        Exporta el documento en el formato especificado.
        Nota: Implementación real requeriría librerías de generación de PDF/HTML.
        """
        # Placeholder para la implementación real
        return b""


@dataclass
class SimulacroParaRecomendaciones:
    """
    Entidad que representa un simulacro con su transcripción y análisis.
    """
    id: str
    migrante_id: str = ""
    migrante_nombre: str = ""
    
    transcripcion: Optional[TranscripcionSimulacro] = None
    analisis: Optional[AnalisisIA] = None
    documento: Optional[DocumentoRecomendaciones] = None
    
    estado: EstadoSimulacro = EstadoSimulacro.PENDIENTE_ANALISIS
    
    def tiene_transcripcion(self) -> bool:
        """Verifica si tiene transcripción."""
        return self.transcripcion is not None and self.transcripcion.tiene_contenido()
    
    def tiene_analisis(self) -> bool:
        """Verifica si tiene análisis de IA completado."""
        return self.analisis is not None and self.analisis.completado
    
    def tiene_documento(self) -> bool:
        """Verifica si tiene documento de recomendaciones."""
        return self.documento is not None
    
    def puede_generar_documento(self) -> bool:
        """Verifica si puede generar el documento de recomendaciones."""
        return self.tiene_transcripcion() and self.tiene_analisis()
    
    def generar_documento_recomendaciones(self) -> DocumentoRecomendaciones:
        """
        Genera el documento de recomendaciones a partir del análisis.
        """
        if not self.puede_generar_documento():
            raise ValueError("No se puede generar documento sin transcripción y análisis")
        
        self.documento = DocumentoRecomendaciones(
            simulacro_id=self.id,
        )
        self.documento.generar_desde_analisis(self.analisis)
        
        self.estado = EstadoSimulacro.FEEDBACK_GENERADO
        
        return self.documento
