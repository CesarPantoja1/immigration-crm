"""
Servicios (Lógica de Negocio) para Simulación de Entrevistas.
Contiene la lógica de negocio que coordina las entidades.
Mapean a: apps.preparacion.services
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from .constants import (
    TipoVisado,
    ModalidadSimulacro,
    EstadoSimulacro,
    BANCO_PREGUNTAS,
)
from .entities import (
    HorarioSimulacro,
    Pregunta,
    RespuestaMigrante,
    ResultadoPractica,
    Transcripcion,
    FeedbackAsesor,
)


@dataclass
class SesionPracticaIndividual:
    """Sesión de práctica individual con cuestionario"""
    id: str
    migrante_id: str
    tipo_visado: TipoVisado
    preguntas: List[Pregunta] = field(default_factory=list)
    respuestas: List[RespuestaMigrante] = field(default_factory=list)
    completada: bool = False

    def responder_pregunta(self, indice_respuesta: int, tiempo_segundos: int = 0):
        if len(self.respuestas) < len(self.preguntas):
            pregunta_actual = self.preguntas[len(self.respuestas)]
            es_correcta = indice_respuesta == pregunta_actual.respuesta_correcta
            respuesta = RespuestaMigrante(
                pregunta_id=pregunta_actual.id,
                respuesta_seleccionada=indice_respuesta,
                es_correcta=es_correcta,
                tiempo_segundos=tiempo_segundos
            )
            self.respuestas.append(respuesta)

    def finalizar_practica(self) -> ResultadoPractica:
        self.completada = True
        correctas = sum(1 for r in self.respuestas if r.es_correcta)
        return ResultadoPractica(
            total_preguntas=len(self.preguntas),
            respuestas_correctas=correctas,
            respuestas_incorrectas=len(self.preguntas) - correctas,
            tiempo_total_segundos=sum(r.tiempo_segundos for r in self.respuestas)
        )


@dataclass
class SimulacroConAsesor:
    """Simulacro con asesor - mapea a apps.preparacion.models.Simulacro"""
    id: str
    migrante_id: str
    migrante_nombre: str
    asesor_id: str
    fecha_cita_real: date
    modalidad: ModalidadSimulacro = ModalidadSimulacro.VIRTUAL
    estado: EstadoSimulacro = EstadoSimulacro.PROPUESTO
    horario: Optional[HorarioSimulacro] = None
    numero_intento: int = 0
    transcripcion: Optional[Transcripcion] = None
    feedback: Optional[FeedbackAsesor] = None

    def iniciar_sesion(self) -> tuple:
        if self.estado in [EstadoSimulacro.AGENDADO, EstadoSimulacro.EN_PROGRESO]:
            self.estado = EstadoSimulacro.EN_PROGRESO
            return True, "Sesión iniciada"
        return False, "No se puede iniciar la sesión"

    def terminar_simulacion(self, contenido_transcripcion: str) -> tuple:
        if self.estado == EstadoSimulacro.EN_PROGRESO:
            self.transcripcion = Transcripcion(
                simulacro_id=self.id,
                contenido=contenido_transcripcion
            )
            return True, "Simulación terminada"
        return False, "No se puede terminar"

    def agregar_feedback(self, feedback: FeedbackAsesor):
        self.feedback = feedback
        self.estado = EstadoSimulacro.COMPLETADO
    
    def validar_fecha_antes_cita(self, fecha_propuesta: date, fecha_cita_embajada: date) -> tuple:
        """Valida que la fecha propuesta sea anterior a la cita con la embajada."""
        if fecha_propuesta >= fecha_cita_embajada:
            return False, "La fecha del simulacro debe ser anterior a la cita con la embajada"
        return True, None


@dataclass
class GestorSimulacros:
    """Gestor de simulacros para un migrante"""
    migrante_id: str
    migrante_nombre: str
    fecha_cita_real: date
    simulacros_con_asesor: List[SimulacroConAsesor] = field(default_factory=list)
    practicas_individuales: List[SesionPracticaIndividual] = field(default_factory=list)
    max_simulacros: int = 2
    # Diccionario para rastrear simulacros por solicitud
    simulacros_por_solicitud: dict = field(default_factory=dict)

    def contar_simulacros_realizados(self, solicitud_id: str = None) -> int:
        """Cuenta los simulacros COMPLETADOS, opcionalmente por solicitud."""
        if solicitud_id:
            return self.simulacros_por_solicitud.get(solicitud_id, {}).get('completados', 0)
        return len([s for s in self.simulacros_con_asesor if s.estado == EstadoSimulacro.COMPLETADO])

    def contar_simulacros_con_asesor(self, solicitud_id: str = None) -> int:
        """Cuenta los simulacros activos, opcionalmente por solicitud."""
        estados_activos = [EstadoSimulacro.AGENDADO, EstadoSimulacro.EN_PROGRESO, EstadoSimulacro.COMPLETADO]
        if solicitud_id:
            return self.simulacros_por_solicitud.get(solicitud_id, {}).get('activos', 0)
        return len([s for s in self.simulacros_con_asesor if s.estado in estados_activos])

    def puede_agendar_simulacro(self, solicitud_id: str = None) -> tuple:
        """Verifica disponibilidad de simulacros para una solicitud específica."""
        contador = self.contar_simulacros_con_asesor(solicitud_id)
        if contador >= self.max_simulacros:
            return False, "Ha alcanzado el limite de 2 simulacros para esta visa"
        disponibles = self.max_simulacros - contador
        if contador == 0:
            return True, "Puede solicitar hasta 2 simulacros para esta visa"
        return True, f"Tiene {disponibles} simulacro disponible para esta solicitud"

    def registrar_simulacro_solicitud(self, solicitud_id: str, completado: bool = False):
        """Registra un simulacro para una solicitud específica."""
        if solicitud_id not in self.simulacros_por_solicitud:
            self.simulacros_por_solicitud[solicitud_id] = {'activos': 0, 'completados': 0}
        
        self.simulacros_por_solicitud[solicitud_id]['activos'] += 1
        if completado:
            self.simulacros_por_solicitud[solicitud_id]['completados'] += 1
    
    def validar_fecha_simulacro(self, fecha_propuesta: date, fecha_cita_embajada: date = None) -> tuple:
        """Valida que la fecha propuesta sea anterior a la cita con la embajada."""
        fecha_cita = fecha_cita_embajada or self.fecha_cita_real
        if fecha_propuesta >= fecha_cita:
            return False, "La fecha del simulacro debe ser anterior a su cita con la embajada"
        return True, None

    def iniciar_practica_individual(self, tipo_visado: TipoVisado) -> SesionPracticaIndividual:
        preguntas = BANCO_PREGUNTAS.get(tipo_visado, BANCO_PREGUNTAS[TipoVisado.ESTUDIANTE])[:10]
        sesion = SesionPracticaIndividual(
            id=f"PRAC-{len(self.practicas_individuales) + 1}",
            migrante_id=self.migrante_id,
            tipo_visado=tipo_visado,
            preguntas=preguntas
        )
        self.practicas_individuales.append(sesion)
        return sesion
