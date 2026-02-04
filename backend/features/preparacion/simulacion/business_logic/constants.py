"""
Constantes para Simulación de Entrevistas.
Contiene enums y constantes que mapean a apps.preparacion.models
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List


class TipoVisado(Enum):
    """Tipos de visa - mapea a Simulacro/Solicitud tipos"""
    ESTUDIANTE = "Estudiante"
    TRABAJO = "Trabajo"
    TURISMO = "Turismo"
    VIVIENDA = "Vivienda"


class ModalidadSimulacro(Enum):
    """Mapea a Simulacro.MODALIDADES"""
    VIRTUAL = "Virtual"
    PRESENCIAL = "Presencial"


class EstadoSimulacro(Enum):
    """Mapea a Simulacro.ESTADOS"""
    SOLICITADO = "solicitado"
    PROPUESTO = "propuesto"
    PENDIENTE = "pendiente_respuesta"
    CONTRAPROPUESTA = "contrapropuesta"
    CONTRAPROPUESTA_FINAL = "contrapropuesta_final"
    AGENDADO = "confirmado"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


class NivelDificultad(Enum):
    """Nivel de dificultad para preguntas de práctica"""
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


# Importación diferida para evitar dependencia circular
def _get_pregunta_class():
    from .entities import Pregunta
    return Pregunta


def _crear_banco_preguntas():
    """Crea el banco de preguntas después de que las clases estén definidas."""
    Pregunta = _get_pregunta_class()
    return {
        TipoVisado.ESTUDIANTE: [
            Pregunta(id="E1", texto="¿Cuál es el propósito de su viaje?",
                     respuestas=["Estudiar", "Trabajar", "Turismo", "Residir"],
                     respuesta_correcta=0, explicacion="El propósito de visa de estudiante es estudiar"),
            Pregunta(id="E2", texto="¿Cómo financiará sus estudios?",
                     respuestas=["Beca", "Familia", "Ahorros", "Préstamo"],
                     respuesta_correcta=0, explicacion="Debe demostrar solvencia económica"),
            Pregunta(id="E3", texto="¿A qué universidad asistirá?",
                     respuestas=["Universidad acreditada", "Instituto", "Colegio", "Academia"],
                     respuesta_correcta=0, explicacion="Debe ser institución acreditada"),
            Pregunta(id="E4", texto="¿Cuánto tiempo durará su programa?",
                     respuestas=["2 años", "6 meses", "1 mes", "5 años"],
                     respuesta_correcta=0, explicacion="Especificar duración exacta"),
            Pregunta(id="E5", texto="¿Dónde vivirá durante sus estudios?",
                     respuestas=["Campus", "Apartamento", "Hotel", "No sé"],
                     respuesta_correcta=0, explicacion="Tener alojamiento definido"),
            Pregunta(id="E6", texto="¿Tiene familia en el país destino?",
                     respuestas=["No", "Sí", "Tal vez", "No recuerdo"],
                     respuesta_correcta=0, explicacion="Ser honesto sobre vínculos"),
            Pregunta(id="E7", texto="¿Qué hará al terminar sus estudios?",
                     respuestas=["Regresar", "Trabajar", "Quedarse", "Viajar"],
                     respuesta_correcta=0, explicacion="Mostrar intención de retorno"),
            Pregunta(id="E8", texto="¿Por qué eligió este país?",
                     respuestas=["Calidad educativa", "Familia", "Trabajo", "Clima"],
                     respuesta_correcta=0, explicacion="Razones académicas son preferibles"),
            Pregunta(id="E9", texto="¿Tiene historial de viajes?",
                     respuestas=["Sí, varios", "No", "Uno", "No recuerdo"],
                     respuesta_correcta=0, explicacion="Historial de viajes es positivo"),
            Pregunta(id="E10", texto="¿Habla el idioma del país?",
                     respuestas=["Sí, fluido", "Básico", "No", "Un poco"],
                     respuesta_correcta=0, explicacion="Dominio del idioma es importante"),
        ]
    }


# Banco de preguntas - se inicializa de forma lazy
class _BancoPreguntas:
    """Clase para cargar el banco de preguntas de forma lazy."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._banco = None
        return cls._instance
    
    def get(self, key, default=None):
        if self._banco is None:
            self._banco = _crear_banco_preguntas()
        return self._banco.get(key, default)
    
    def __getitem__(self, key):
        if self._banco is None:
            self._banco = _crear_banco_preguntas()
        return self._banco[key]


BANCO_PREGUNTAS = _BancoPreguntas()
