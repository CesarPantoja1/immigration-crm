"""
Servicio de IA para análisis de transcripciones de simulacros.
Utiliza Google Gemini API para generar recomendaciones personalizadas.
"""
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Configuración por defecto de Gemini API (fallback)
DEFAULT_API_KEY = "AIzaSyC4zzSsFArh2Dbm8fMS0ZuXok1Eizs297o"
DEFAULT_MODEL = "gemini-2.5-flash"
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def get_configuracion_asesor(asesor_id: int = None):
    """
    Obtiene la configuración de IA del asesor.
    Si no tiene configuración, retorna los valores por defecto.
    """
    from .models import ConfiguracionIA
    
    if asesor_id:
        try:
            config = ConfiguracionIA.objects.get(asesor_id=asesor_id, activo=True)
            return {
                'api_key': config.api_key,
                'modelo': config.modelo,
                'config_id': config.id
            }
        except ConfiguracionIA.DoesNotExist:
            pass
    
    # Fallback a configuración por defecto
    return {
        'api_key': DEFAULT_API_KEY,
        'modelo': DEFAULT_MODEL,
        'config_id': None
    }


@dataclass
class AnalisisIA:
    """Resultado del análisis de IA."""
    claridad: str  # bajo, medio, alto
    coherencia: str
    seguridad: str
    pertinencia: str
    nivel_preparacion: str
    fortalezas: List[Dict[str, Any]]
    puntos_mejora: List[Dict[str, Any]]
    recomendaciones: List[Dict[str, Any]]
    accion_sugerida: str
    analisis_completo: bool = True
    error: Optional[str] = None


class GeminiAIService:
    """
    Servicio para interactuar con Google Gemini API.
    Analiza transcripciones de simulacros de entrevista consular.
    """
    
    def __init__(self, api_key: str = None, modelo: str = None, asesor_id: int = None):
        """
        Inicializa el servicio con configuración personalizada o del asesor.
        
        Args:
            api_key: API key de Gemini (opcional)
            modelo: Modelo de Gemini a usar (opcional)
            asesor_id: ID del asesor para cargar su configuración (opcional)
        """
        if api_key and modelo:
            # Usar configuración proporcionada
            self.api_key = api_key
            self.modelo = modelo
            self.config_id = None
        else:
            # Cargar configuración del asesor o usar defaults
            config = get_configuracion_asesor(asesor_id)
            self.api_key = api_key or config['api_key']
            self.modelo = modelo or config['modelo']
            self.config_id = config['config_id']
        
        self.api_url = f"{GEMINI_API_BASE_URL}/{self.modelo}:generateContent"
    
    def _incrementar_uso(self):
        """Incrementa el contador de uso si hay configuración asociada."""
        if self.config_id:
            try:
                from .models import ConfiguracionIA
                config = ConfiguracionIA.objects.get(id=self.config_id)
                config.incrementar_uso()
            except Exception as e:
                logger.warning(f"No se pudo incrementar uso: {e}")
    
    def _build_prompt(self, transcripcion: str, tipo_visa: str = "general") -> str:
        """Construye el prompt para el análisis de la transcripción."""
        
        prompt = f"""Eres un experto asesor en entrevistas consulares para visas. Analiza la siguiente transcripción de un simulacro de entrevista consular y proporciona un análisis detallado.

TRANSCRIPCIÓN DEL SIMULACRO:
---
{transcripcion}
---

TIPO DE VISA: {tipo_visa}

Por favor, analiza la transcripción y proporciona tu evaluación en el siguiente formato JSON exacto (sin markdown, solo el JSON puro):

{{
    "indicadores": {{
        "claridad": "alto|medio|bajo",
        "coherencia": "alto|medio|bajo", 
        "seguridad": "alto|medio|bajo",
        "pertinencia": "alto|medio|bajo"
    }},
    "fortalezas": [
        {{
            "categoria": "string (ej: Claridad, Documentación, Actitud)",
            "descripcion": "string descriptivo de la fortaleza",
            "pregunta_relacionada": "string (número o tipo de pregunta si aplica)",
            "impacto": "alto|medio|bajo"
        }}
    ],
    "puntos_mejora": [
        {{
            "categoria": "string (ej: Claridad, Seguridad, Pertinencia, Coherencia)",
            "descripcion": "string descriptivo del punto a mejorar",
            "pregunta_relacionada": "string (número o tipo de pregunta si aplica)",
            "impacto": "alto|medio|bajo"
        }}
    ],
    "recomendaciones": [
        {{
            "categoria": "string",
            "titulo": "string corto",
            "descripcion": "string con la recomendación específica y accionable",
            "pregunta_relacionada": "string (número o tipo de pregunta si aplica)",
            "impacto": "alto|medio|bajo",
            "accion_concreta": "string con paso específico a seguir"
        }}
    ],
    "nivel_preparacion": "alto|medio|bajo",
    "accion_sugerida": "string con el siguiente paso recomendado según el nivel (bajo: Realizar nuevo simulacro con asesor, medio: Reforzar puntos de mejora identificados, alto: Mantener plan actual de preparación)",
    "resumen_ejecutivo": "string con un párrafo resumiendo el desempeño general"
}}

CRITERIOS DE EVALUACIÓN:
- CLARIDAD: ¿Las respuestas son claras, directas y fáciles de entender?
- COHERENCIA: ¿El discurso es lógico y las ideas están bien conectadas?
- SEGURIDAD: ¿El candidato muestra confianza al responder? ¿Hay titubeos o inseguridades?
- PERTINENCIA: ¿Las respuestas abordan directamente lo que se pregunta?

NIVELES:
- ALTO: Desempeño excelente, muy preparado para la entrevista real
- MEDIO: Desempeño aceptable pero con áreas de mejora
- BAJO: Requiere más preparación antes de la entrevista real

Proporciona al menos 3 fortalezas, 3 puntos de mejora y 5 recomendaciones accionables.
Cada recomendación debe ser específica, medible y vinculada a una pregunta o momento del simulacro cuando sea posible.

Responde ÚNICAMENTE con el JSON, sin explicaciones adicionales ni markdown."""

        return prompt
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Realiza la llamada a la API de Gemini."""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 4096,
                }
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"Error en Gemini API: {response.status_code} - {response.text}")
                return None
            
            # Incrementar contador de uso si hay configuración
            self._incrementar_uso()
            
            result = response.json()
            
            # Extraer el texto de la respuesta
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0].get("text", "")
            
            logger.error(f"Respuesta inesperada de Gemini: {result}")
            return None
            
        except requests.exceptions.Timeout:
            logger.error("Timeout al llamar a Gemini API")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con Gemini API: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al llamar a Gemini API: {e}")
            return None
    
    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """Parsea la respuesta JSON de Gemini."""
        try:
            # Limpiar la respuesta (a veces viene con markdown)
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de Gemini: {e}")
            logger.error(f"Respuesta recibida: {response_text[:500]}...")
            return None
    
    def analizar_transcripcion(self, transcripcion: str, tipo_visa: str = "general") -> AnalisisIA:
        """
        Analiza una transcripción de simulacro y genera recomendaciones.
        
        Args:
            transcripcion: Texto de la transcripción del simulacro
            tipo_visa: Tipo de visa (estudiante, trabajo, turismo, etc.)
        
        Returns:
            AnalisisIA con los resultados del análisis
        """
        if not transcripcion or len(transcripcion.strip()) < 50:
            return AnalisisIA(
                claridad="medio",
                coherencia="medio",
                seguridad="medio",
                pertinencia="medio",
                nivel_preparacion="medio",
                fortalezas=[],
                puntos_mejora=[],
                recomendaciones=[],
                accion_sugerida="La transcripción es muy corta para un análisis completo.",
                analisis_completo=False,
                error="Transcripción insuficiente para análisis"
            )
        
        # Construir y enviar prompt
        prompt = self._build_prompt(transcripcion, tipo_visa)
        response_text = self._call_gemini_api(prompt)
        
        if not response_text:
            return AnalisisIA(
                claridad="medio",
                coherencia="medio",
                seguridad="medio",
                pertinencia="medio",
                nivel_preparacion="medio",
                fortalezas=[],
                puntos_mejora=[],
                recomendaciones=[],
                accion_sugerida="No se pudo completar el análisis.",
                analisis_completo=False,
                error="Error de comunicación con el servicio de IA"
            )
        
        # Parsear respuesta
        parsed = self._parse_response(response_text)
        
        if not parsed:
            return AnalisisIA(
                claridad="medio",
                coherencia="medio",
                seguridad="medio",
                pertinencia="medio",
                nivel_preparacion="medio",
                fortalezas=[],
                puntos_mejora=[],
                recomendaciones=[],
                accion_sugerida="No se pudo procesar la respuesta del análisis.",
                analisis_completo=False,
                error="Error al procesar respuesta de IA"
            )
        
        # Extraer indicadores
        indicadores = parsed.get("indicadores", {})
        
        return AnalisisIA(
            claridad=indicadores.get("claridad", "medio"),
            coherencia=indicadores.get("coherencia", "medio"),
            seguridad=indicadores.get("seguridad", "medio"),
            pertinencia=indicadores.get("pertinencia", "medio"),
            nivel_preparacion=parsed.get("nivel_preparacion", "medio"),
            fortalezas=parsed.get("fortalezas", []),
            puntos_mejora=parsed.get("puntos_mejora", []),
            recomendaciones=parsed.get("recomendaciones", []),
            accion_sugerida=parsed.get("accion_sugerida", ""),
            analisis_completo=True,
            error=None
        )


def analizar_simulacro(
    transcripcion: str, 
    tipo_visa: str = "general",
    asesor_id: int = None,
    api_key: str = None,
    modelo: str = None
) -> AnalisisIA:
    """
    Función de conveniencia para analizar un simulacro.
    
    Args:
        transcripcion: Texto de la transcripción
        tipo_visa: Tipo de visa del proceso
        asesor_id: ID del asesor para usar su configuración de IA
        api_key: API key de Gemini (opcional, usa la del asesor si no se especifica)
        modelo: Modelo de Gemini (opcional, usa el del asesor si no se especifica)
    
    Returns:
        AnalisisIA con los resultados
    """
    service = GeminiAIService(
        api_key=api_key,
        modelo=modelo,
        asesor_id=asesor_id
    )
    return service.analizar_transcripcion(transcripcion, tipo_visa)
