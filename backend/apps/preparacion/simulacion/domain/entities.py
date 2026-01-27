"""
Entidades de Dominio para Simulación de Entrevistas.
"""
from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import List, Optional

from .value_objects import (
    TipoVisado,
    ModalidadSimulacro,
    EstadoSimulacro,
    NivelDificultad,
    Pregunta,
    RespuestaMigrante,
    HorarioSimulacro,
    ResultadoPractica,
    Transcripcion,
    FeedbackAsesor,
    MAX_SIMULACROS_CON_ASESOR,
    obtener_preguntas_por_visado,
)


@dataclass
class SimulacroConAsesor:
    """
    Entidad que representa un simulacro de entrevista guiado por un asesor.
    Tiene límite de 2 simulacros por migrante.
    """
    id: Optional[str] = None
    migrante_id: str = ""
    migrante_nombre: str = ""
    asesor_id: str = ""
    fecha_cita_real: date = None
    horario: Optional[HorarioSimulacro] = None
    modalidad: ModalidadSimulacro = ModalidadSimulacro.VIRTUAL
    estado: EstadoSimulacro = EstadoSimulacro.AGENDADO
    
    # Transcripción y feedback
    transcripcion: Optional[Transcripcion] = None
    feedback: Optional[FeedbackAsesor] = None
    
    # Control
    numero_intento: int = 1  # 1 o 2
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    def puede_agendarse(self, intentos_previos: int) -> tuple[bool, str]:
        """
        Verifica si se puede agendar un nuevo simulacro.
        
        Args:
            intentos_previos: Número de simulacros ya realizados
            
        Returns:
            Tupla (puede_agendar, mensaje)
        """
        # Verificar límite de simulacros
        if intentos_previos >= MAX_SIMULACROS_CON_ASESOR:
            return False, "Error: Límite de 2 simulacros alcanzado"
        
        # Verificar que sea antes de la cita real
        if self.horario and self.fecha_cita_real:
            if not self.horario.es_antes_de(self.fecha_cita_real):
                return False, "Error: La simulación debe ser antes de la cita real"
        
        # Determinar mensaje según número de intento
        if intentos_previos == 0:
            return True, "Simulacro agendado exitosamente"
        elif intentos_previos == 1:
            return True, "Segundo y último simulacro agendado"
        
        return True, "Simulacro agendado exitosamente"
    
    def agendar(self, fecha: date, hora: time, modalidad: ModalidadSimulacro) -> tuple[bool, str]:
        """
        Agenda el simulacro.
        """
        self.horario = HorarioSimulacro(fecha=fecha, hora=hora)
        self.modalidad = modalidad
        self.estado = EstadoSimulacro.AGENDADO
        
        return True, "Simulacro agendado exitosamente"
    
    def iniciar_sesion(self) -> tuple[bool, str]:
        """
        El asesor inicia la sesión de simulación.
        """
        if self.estado != EstadoSimulacro.AGENDADO:
            return False, "El simulacro no está en estado agendado"
        
        self.estado = EstadoSimulacro.EN_PROGRESO
        return True, "Sesión de simulación iniciada"
    
    def terminar_simulacion(self, contenido_transcripcion: str) -> tuple[bool, str]:
        """
        Termina la simulación y guarda la transcripción.
        """
        if self.estado != EstadoSimulacro.EN_PROGRESO:
            return False, "El simulacro no está en progreso"
        
        # Guardar transcripción
        self.transcripcion = Transcripcion(
            simulacro_id=self.id or "",
            contenido=contenido_transcripcion
        )
        
        # Cambiar estado
        self.estado = EstadoSimulacro.PENDIENTE_FEEDBACK
        
        return True, "Simulación terminada, pendiente de feedback"
    
    def agregar_feedback(self, feedback: FeedbackAsesor) -> tuple[bool, str]:
        """
        El asesor agrega feedback al simulacro.
        """
        if self.estado != EstadoSimulacro.PENDIENTE_FEEDBACK:
            return False, "El simulacro no está pendiente de feedback"
        
        self.feedback = feedback
        self.estado = EstadoSimulacro.COMPLETADO
        
        return True, "Feedback agregado exitosamente"
    
    def tiene_transcripcion(self) -> bool:
        """Verifica si tiene transcripción guardada."""
        return self.transcripcion is not None and self.transcripcion.tiene_contenido()
    
    def esta_completado(self) -> bool:
        """Verifica si el simulacro está completado."""
        return self.estado == EstadoSimulacro.COMPLETADO


@dataclass
class SesionPracticaIndividual:
    """
    Entidad que representa una sesión de práctica individual (auto-preparación).
    """
    id: Optional[str] = None
    migrante_id: str = ""
    tipo_visado: TipoVisado = TipoVisado.ESTUDIANTE
    
    # Preguntas y respuestas
    preguntas: List[Pregunta] = field(default_factory=list)
    respuestas: List[RespuestaMigrante] = field(default_factory=list)
    pregunta_actual_indice: int = 0
    
    # Resultado
    resultado: Optional[ResultadoPractica] = None
    
    # Control
    fecha_inicio: datetime = field(default_factory=datetime.now)
    fecha_fin: Optional[datetime] = None
    activa: bool = True
    
    def cargar_cuestionario(self, tipo_visado: TipoVisado) -> bool:
        """
        Carga el cuestionario para el tipo de visado seleccionado.
        """
        self.tipo_visado = tipo_visado
        self.preguntas = obtener_preguntas_por_visado(tipo_visado)
        self.pregunta_actual_indice = 0
        self.respuestas = []
        self.activa = True
        
        return len(self.preguntas) > 0
    
    def obtener_pregunta_actual(self) -> Optional[Pregunta]:
        """Obtiene la pregunta actual."""
        if 0 <= self.pregunta_actual_indice < len(self.preguntas):
            return self.preguntas[self.pregunta_actual_indice]
        return None
    
    def responder_pregunta(self, indice_respuesta: int, tiempo_segundos: int = 0) -> RespuestaMigrante:
        """
        Registra la respuesta a la pregunta actual.
        """
        pregunta = self.obtener_pregunta_actual()
        if not pregunta:
            raise ValueError("No hay pregunta actual")
        
        es_correcta = pregunta.es_correcta(indice_respuesta)
        
        respuesta = RespuestaMigrante(
            pregunta_id=pregunta.id,
            respuesta_seleccionada=indice_respuesta,
            es_correcta=es_correcta,
            tiempo_respuesta_segundos=tiempo_segundos
        )
        
        self.respuestas.append(respuesta)
        self.pregunta_actual_indice += 1
        
        return respuesta
    
    def tiene_mas_preguntas(self) -> bool:
        """Verifica si hay más preguntas."""
        return self.pregunta_actual_indice < len(self.preguntas)
    
    def finalizar_practica(self) -> ResultadoPractica:
        """
        Finaliza la práctica y calcula el resultado.
        """
        self.fecha_fin = datetime.now()
        self.activa = False
        
        correctas = sum(1 for r in self.respuestas if r.es_correcta)
        incorrectas = len(self.respuestas) - correctas
        tiempo_total = sum(r.tiempo_respuesta_segundos for r in self.respuestas)
        
        self.resultado = ResultadoPractica(
            total_preguntas=len(self.preguntas),
            respuestas_correctas=correctas,
            respuestas_incorrectas=incorrectas,
            tiempo_total_segundos=tiempo_total,
            tipo_visado=self.tipo_visado
        )
        
        return self.resultado
    
    def obtener_tema_preguntas(self) -> str:
        """Obtiene el tema de las preguntas del cuestionario."""
        if self.preguntas:
            return self.preguntas[0].tema
        return ""


@dataclass
class GestorSimulacros:
    """
    Agregado raíz para gestionar los simulacros de un migrante.
    """
    migrante_id: str
    migrante_nombre: str
    fecha_cita_real: Optional[date] = None
    
    simulacros_con_asesor: List[SimulacroConAsesor] = field(default_factory=list)
    practicas_individuales: List[SesionPracticaIndividual] = field(default_factory=list)
    
    def contar_simulacros_con_asesor(self) -> int:
        """Cuenta los simulacros realizados con asesor."""
        return len(self.simulacros_con_asesor)
    
    def puede_agendar_simulacro(self) -> tuple[bool, str]:
        """Verifica si puede agendar un nuevo simulacro."""
        intentos = self.contar_simulacros_con_asesor()
        
        if intentos >= MAX_SIMULACROS_CON_ASESOR:
            return False, "Error: Límite de 2 simulacros alcanzado"
        
        return True, "Puede agendar simulacro"
    
    def crear_simulacro_con_asesor(
        self,
        asesor_id: str,
        fecha: date,
        hora: time,
        modalidad: ModalidadSimulacro
    ) -> tuple[SimulacroConAsesor, str]:
        """
        Crea y agenda un nuevo simulacro con asesor.
        """
        intentos_previos = self.contar_simulacros_con_asesor()
        
        simulacro = SimulacroConAsesor(
            migrante_id=self.migrante_id,
            migrante_nombre=self.migrante_nombre,
            asesor_id=asesor_id,
            fecha_cita_real=self.fecha_cita_real,
            numero_intento=intentos_previos + 1
        )
        
        # Verificar si puede agendarse
        puede, mensaje = simulacro.puede_agendarse(intentos_previos)
        if not puede:
            return simulacro, mensaje
        
        # Verificar fecha antes de cita real
        if self.fecha_cita_real and fecha >= self.fecha_cita_real:
            return simulacro, "Error: La simulación debe ser antes de la cita real"
        
        # Agendar
        simulacro.agendar(fecha, hora, modalidad)
        self.simulacros_con_asesor.append(simulacro)
        
        # Mensaje según intento
        if intentos_previos == 0:
            return simulacro, "Simulacro agendado exitosamente"
        else:
            return simulacro, "Segundo y último simulacro agendado"
    
    def iniciar_practica_individual(
        self,
        tipo_visado: TipoVisado
    ) -> SesionPracticaIndividual:
        """
        Inicia una nueva sesión de práctica individual.
        """
        sesion = SesionPracticaIndividual(
            migrante_id=self.migrante_id,
            tipo_visado=tipo_visado
        )
        sesion.cargar_cuestionario(tipo_visado)
        
        self.practicas_individuales.append(sesion)
        
        return sesion
    
    def obtener_simulacro_en_progreso(self) -> Optional[SimulacroConAsesor]:
        """Obtiene el simulacro actualmente en progreso."""
        for sim in self.simulacros_con_asesor:
            if sim.estado in [EstadoSimulacro.AGENDADO, EstadoSimulacro.EN_PROGRESO]:
                return sim
        return None
