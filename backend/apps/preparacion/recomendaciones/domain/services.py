"""
Servicios de Dominio para Recomendaciones.
"""
from dataclasses import dataclass
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
    AccionSugerida,
    calcular_nivel_preparacion,
    SECCIONES_DOCUMENTO,
)

from .entities import (
    TranscripcionSimulacro,
    AnalisisIA,
    DocumentoRecomendaciones,
    SimulacroParaRecomendaciones,
)

from .repositories import (
    ISimulacroRecomendacionRepository,
    IDocumentoRecomendacionesRepository,
    IAnalisisIARepository,
)


@dataclass
class AnalisisIAService:
    """
    Servicio para realizar análisis de IA sobre transcripciones.
    """
    analisis_repository: IAnalisisIARepository
    
    def analizar_transcripcion(
        self,
        simulacro_id: str,
        transcripcion: TranscripcionSimulacro,
        indicadores: List[dict]
    ) -> AnalisisIA:
        """
        Analiza la transcripción y genera indicadores.
        
        Args:
            simulacro_id: ID del simulacro
            transcripcion: Transcripción a analizar
            indicadores: Lista de indicadores con nombre y valor
            
        Returns:
            Análisis completado
        """
        analisis = AnalisisIA(simulacro_id=simulacro_id)
        
        # Mapear indicadores
        nivel_map = {
            "Alta": NivelIndicador.ALTA,
            "Alto": NivelIndicador.ALTO,
            "Media": NivelIndicador.MEDIA,
            "Medio": NivelIndicador.MEDIO,
            "Baja": NivelIndicador.BAJA,
            "Bajo": NivelIndicador.BAJO,
        }
        
        for ind in indicadores:
            nombre = ind.get("indicador", "")
            valor_str = ind.get("valor", "Media")
            valor = nivel_map.get(valor_str, NivelIndicador.MEDIA)
            
            indicador = IndicadorDesempeno(nombre=nombre, valor=valor)
            analisis.agregar_indicador(indicador)
        
        analisis.marcar_completado()
        
        return self.analisis_repository.guardar(analisis)
    
    def identificar_puntos_mejora(
        self,
        analisis: AnalisisIA,
        puntos: List[dict]
    ) -> AnalisisIA:
        """
        Identifica los puntos de mejora a partir del análisis.
        """
        categoria_map = {
            "Claridad": CategoriaRecomendacion.CLARIDAD,
            "Coherencia": CategoriaRecomendacion.COHERENCIA,
            "Seguridad": CategoriaRecomendacion.SEGURIDAD,
            "Pertinencia": CategoriaRecomendacion.PERTINENCIA,
        }
        
        for punto_dict in puntos:
            categoria_str = punto_dict.get("categoria", "Claridad")
            descripcion = punto_dict.get("descripcion", "")
            
            categoria = categoria_map.get(categoria_str, CategoriaRecomendacion.CLARIDAD)
            
            punto = PuntoMejora(
                categoria=categoria,
                descripcion=descripcion
            )
            analisis.agregar_punto_mejora(punto)
        
        return self.analisis_repository.guardar(analisis)


@dataclass
class GeneracionDocumentoService:
    """
    Servicio para generar documentos de recomendaciones.
    """
    simulacro_repository: ISimulacroRecomendacionRepository
    documento_repository: IDocumentoRecomendacionesRepository
    
    def generar_documento(
        self,
        simulacro_id: str
    ) -> DocumentoRecomendaciones:
        """
        Genera el documento de recomendaciones para un simulacro.
        """
        simulacro = self.simulacro_repository.obtener_por_id(simulacro_id)
        if not simulacro:
            raise ValueError(f"Simulacro {simulacro_id} no encontrado")
        
        if not simulacro.puede_generar_documento():
            raise ValueError("El simulacro no tiene transcripción o análisis")
        
        documento = simulacro.generar_documento_recomendaciones()
        
        # Guardar documento
        documento = self.documento_repository.guardar(documento)
        
        # Actualizar simulacro
        self.simulacro_repository.guardar(simulacro)
        
        return documento
    
    def agregar_recomendaciones_accionables(
        self,
        documento: DocumentoRecomendaciones,
        categorias: List[CategoriaRecomendacion],
        analisis: AnalisisIA
    ) -> DocumentoRecomendaciones:
        """
        Agrega recomendaciones accionables al documento.
        """
        for categoria in categorias:
            puntos = analisis.obtener_puntos_mejora_por_categoria(categoria)
            
            for i, punto in enumerate(puntos):
                recomendacion = RecomendacionAccionable(
                    id=f"REC-{documento.simulacro_id}-{categoria.value}-{i+1}",
                    categoria=categoria,
                    descripcion=f"Mejorar {categoria.value.lower()}",
                    accion_concreta=f"Practicar técnicas de {categoria.value.lower()} en las respuestas",
                    metrica_exito=f"Lograr nivel Alto en {categoria.value} en el próximo simulacro",
                    impacto=NivelImpacto.MEDIO,
                    numero_pregunta_origen=punto.pregunta_origen,
                    tipo_pregunta_origen=punto.tipo_pregunta_origen,
                )
                documento.agregar_recomendacion(recomendacion)
        
        return self.documento_repository.guardar(documento)
    
    def verificar_secciones_completas(
        self,
        documento: DocumentoRecomendaciones
    ) -> tuple[bool, List[str]]:
        """
        Verifica que el documento tenga todas las secciones requeridas.
        """
        secciones_faltantes = []
        
        for seccion in SECCIONES_DOCUMENTO:
            if not documento.tiene_seccion(seccion):
                secciones_faltantes.append(seccion)
        
        return len(secciones_faltantes) == 0, secciones_faltantes


@dataclass 
class NivelPreparacionService:
    """
    Servicio para calcular y asignar niveles de preparación.
    """
    
    def calcular_nivel(self, indicadores: List[IndicadorDesempeno]) -> NivelPreparacion:
        """
        Calcula el nivel de preparación global.
        """
        return calcular_nivel_preparacion(indicadores)
    
    def obtener_accion_sugerida(self, nivel: NivelPreparacion) -> AccionSugerida:
        """
        Obtiene la acción sugerida según el nivel.
        """
        return AccionSugerida.para_nivel(nivel)


@dataclass
class TrazabilidadService:
    """
    Servicio para gestionar la trazabilidad de recomendaciones.
    """
    documento_repository: IDocumentoRecomendacionesRepository
    
    def asociar_recomendaciones_a_preguntas(
        self,
        documento: DocumentoRecomendaciones,
        preguntas: List[PreguntaSimulacro]
    ) -> DocumentoRecomendaciones:
        """
        Asocia las recomendaciones a las preguntas del simulacro.
        """
        tipo_map = {
            "Motivo del viaje": TipoPregunta.MOTIVO_VIAJE,
            "Situación económica": TipoPregunta.SITUACION_ECONOMICA,
            "Planes de permanencia": TipoPregunta.PLANES_PERMANENCIA,
        }
        
        for i, rec in enumerate(documento.recomendaciones):
            if i < len(preguntas):
                pregunta = preguntas[i]
                rec.numero_pregunta_origen = pregunta.numero
                rec.tipo_pregunta_origen = pregunta.tipo
        
        return self.documento_repository.guardar(documento)
    
    def verificar_trazabilidad(
        self,
        documento: DocumentoRecomendaciones
    ) -> tuple[bool, List[str]]:
        """
        Verifica que todas las recomendaciones tengan trazabilidad.
        """
        sin_trazabilidad = []
        
        for rec in documento.recomendaciones:
            if not rec.es_trazable():
                sin_trazabilidad.append(rec.id)
        
        return len(sin_trazabilidad) == 0, sin_trazabilidad


@dataclass
class ClasificacionImpactoService:
    """
    Servicio para clasificar recomendaciones por impacto.
    """
    documento_repository: IDocumentoRecomendacionesRepository
    
    def clasificar_por_impacto(
        self,
        documento: DocumentoRecomendaciones
    ) -> Dict[NivelImpacto, List[RecomendacionAccionable]]:
        """
        Clasifica las recomendaciones por nivel de impacto.
        """
        return documento.agrupar_recomendaciones_por_impacto()
    
    def asignar_impacto_a_recomendacion(
        self,
        recomendacion: RecomendacionAccionable,
        impacto: NivelImpacto
    ) -> RecomendacionAccionable:
        """
        Asigna nivel de impacto a una recomendación.
        """
        recomendacion.impacto = impacto
        return recomendacion


@dataclass
class ConsultaDocumentoService:
    """
    Servicio para consultar documentos de recomendaciones.
    """
    documento_repository: IDocumentoRecomendacionesRepository
    
    def consultar_documento(
        self,
        simulacro_id: str
    ) -> Optional[DocumentoRecomendaciones]:
        """
        Consulta el documento de recomendaciones de un simulacro.
        """
        return self.documento_repository.obtener_por_simulacro(simulacro_id)
    
    def obtener_documento_publicado(
        self,
        simulacro_id: str
    ) -> Optional[DocumentoRecomendaciones]:
        """
        Obtiene el documento si está publicado.
        """
        documento = self.documento_repository.obtener_por_simulacro(simulacro_id)
        
        if documento and documento.esta_publicado():
            return documento
        
        return None
    
    def descargar_documento(
        self,
        simulacro_id: str,
        formato: FormatoDocumento = FormatoDocumento.PDF
    ) -> bytes:
        """
        Descarga el documento en el formato especificado.
        """
        documento = self.documento_repository.obtener_por_simulacro(simulacro_id)
        
        if not documento or not documento.puede_descargarse():
            raise ValueError("Documento no disponible para descarga")
        
        return documento.exportar_formato(formato)
