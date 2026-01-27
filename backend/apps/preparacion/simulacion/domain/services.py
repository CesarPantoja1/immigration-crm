"""
Servicios de Dominio para Simulación.
"""
from dataclasses import dataclass
from datetime import date, time
from typing import Optional, List

from .entities import SimulacroConAsesor, SesionPracticaIndividual, GestorSimulacros
from .value_objects import (
    TipoVisado,
    ModalidadSimulacro,
    EstadoSimulacro,
    ResultadoPractica,
    Transcripcion,
    FeedbackAsesor,
    MAX_SIMULACROS_CON_ASESOR,
)
from .exceptions import (
    LimiteSimulacrosAlcanzadoError,
    SimulacroFueraDeFechaError,
    SimulacroNoEncontradoError,
    CuestionarioNoDisponibleError,
)
from .repositories import ISimulacroRepository, ISesionPracticaRepository


@dataclass
class AgendamientoSimulacroService:
    """
    Servicio para agendar simulacros con asesor.
    """
    simulacro_repository: ISimulacroRepository
    
    def agendar_simulacro(
        self,
        migrante_id: str,
        migrante_nombre: str,
        asesor_id: str,
        fecha_simulacro: date,
        hora_simulacro: time,
        modalidad: ModalidadSimulacro,
        fecha_cita_real: date
    ) -> tuple[SimulacroConAsesor, str]:
        """
        Agenda un simulacro con asesor.
        
        Returns:
            Tupla (simulacro, mensaje)
        """
        # Contar simulacros previos
        intentos_previos = self.simulacro_repository.contar_por_migrante(migrante_id)
        
        # Verificar límite
        if intentos_previos >= MAX_SIMULACROS_CON_ASESOR:
            raise LimiteSimulacrosAlcanzadoError()
        
        # Verificar que sea antes de la cita real
        if fecha_simulacro >= fecha_cita_real:
            raise SimulacroFueraDeFechaError()
        
        # Crear gestor para el migrante
        gestor = GestorSimulacros(
            migrante_id=migrante_id,
            migrante_nombre=migrante_nombre,
            fecha_cita_real=fecha_cita_real
        )
        
        # Simular simulacros previos
        gestor.simulacros_con_asesor = list(
            self.simulacro_repository.obtener_por_migrante(migrante_id)
        )
        
        # Crear simulacro
        simulacro, mensaje = gestor.crear_simulacro_con_asesor(
            asesor_id=asesor_id,
            fecha=fecha_simulacro,
            hora=hora_simulacro,
            modalidad=modalidad
        )
        
        # Guardar
        simulacro_guardado = self.simulacro_repository.guardar(simulacro)
        
        return simulacro_guardado, mensaje
    
    def verificar_disponibilidad(
        self,
        migrante_id: str,
        fecha_simulacro: date,
        fecha_cita_real: date
    ) -> tuple[bool, str]:
        """
        Verifica si un migrante puede agendar un simulacro.
        """
        # Contar simulacros previos
        intentos_previos = self.simulacro_repository.contar_por_migrante(migrante_id)
        
        if intentos_previos >= MAX_SIMULACROS_CON_ASESOR:
            return False, "Error: Límite de 2 simulacros alcanzado"
        
        if fecha_simulacro >= fecha_cita_real:
            return False, "Error: La simulación debe ser antes de la cita real"
        
        return True, "Disponible para agendar"


@dataclass
class EjecucionSimulacroService:
    """
    Servicio para ejecutar simulacros guiados.
    """
    simulacro_repository: ISimulacroRepository
    
    def iniciar_sesion(self, simulacro_id: str, asesor_id: str) -> tuple[bool, str]:
        """
        El asesor inicia una sesión de simulación.
        """
        simulacro = self.simulacro_repository.obtener_por_id(simulacro_id)
        if not simulacro:
            raise SimulacroNoEncontradoError(simulacro_id)
        
        if simulacro.asesor_id != asesor_id:
            return False, "El asesor no está asignado a este simulacro"
        
        exito, mensaje = simulacro.iniciar_sesion()
        if exito:
            self.simulacro_repository.guardar(simulacro)
        
        return exito, mensaje
    
    def terminar_simulacion(
        self,
        simulacro_id: str,
        contenido_transcripcion: str
    ) -> tuple[bool, str]:
        """
        Termina la simulación y guarda la transcripción.
        """
        simulacro = self.simulacro_repository.obtener_por_id(simulacro_id)
        if not simulacro:
            raise SimulacroNoEncontradoError(simulacro_id)
        
        exito, mensaje = simulacro.terminar_simulacion(contenido_transcripcion)
        if exito:
            self.simulacro_repository.guardar(simulacro)
        
        return exito, mensaje
    
    def agregar_feedback(
        self,
        simulacro_id: str,
        asesor_id: str,
        puntuacion: int,
        fortalezas: List[str],
        areas_mejora: List[str],
        recomendaciones: str
    ) -> tuple[bool, str]:
        """
        El asesor agrega feedback al simulacro.
        """
        simulacro = self.simulacro_repository.obtener_por_id(simulacro_id)
        if not simulacro:
            raise SimulacroNoEncontradoError(simulacro_id)
        
        feedback = FeedbackAsesor(
            simulacro_id=simulacro_id,
            asesor_id=asesor_id,
            puntuacion=puntuacion,
            fortalezas=fortalezas,
            areas_mejora=areas_mejora,
            recomendaciones=recomendaciones
        )
        
        exito, mensaje = simulacro.agregar_feedback(feedback)
        if exito:
            self.simulacro_repository.guardar(simulacro)
        
        return exito, mensaje


@dataclass
class PracticaIndividualService:
    """
    Servicio para gestionar práctica individual por tipo de visado.
    """
    sesion_repository: ISesionPracticaRepository
    
    def iniciar_practica(
        self,
        migrante_id: str,
        tipo_visado: TipoVisado
    ) -> SesionPracticaIndividual:
        """
        Inicia una nueva sesión de práctica individual.
        """
        sesion = SesionPracticaIndividual(
            migrante_id=migrante_id,
            tipo_visado=tipo_visado
        )
        
        cargado = sesion.cargar_cuestionario(tipo_visado)
        if not cargado:
            raise CuestionarioNoDisponibleError(tipo_visado.value)
        
        return self.sesion_repository.guardar(sesion)
    
    def obtener_pregunta_actual(self, sesion_id: str) -> Optional[dict]:
        """
        Obtiene la pregunta actual de una sesión.
        """
        sesion = self.sesion_repository.obtener_por_id(sesion_id)
        if not sesion or not sesion.activa:
            return None
        
        pregunta = sesion.obtener_pregunta_actual()
        if pregunta:
            return {
                'id': pregunta.id,
                'texto': pregunta.texto,
                'respuestas': pregunta.respuestas,
                'tema': pregunta.tema,
                'numero': sesion.pregunta_actual_indice + 1,
                'total': len(sesion.preguntas)
            }
        return None
    
    def responder_pregunta(
        self,
        sesion_id: str,
        indice_respuesta: int,
        tiempo_segundos: int = 0
    ) -> dict:
        """
        Responde la pregunta actual.
        """
        sesion = self.sesion_repository.obtener_por_id(sesion_id)
        if not sesion:
            return {'error': 'Sesión no encontrada'}
        
        respuesta = sesion.responder_pregunta(indice_respuesta, tiempo_segundos)
        self.sesion_repository.guardar(sesion)
        
        return {
            'es_correcta': respuesta.es_correcta,
            'hay_mas_preguntas': sesion.tiene_mas_preguntas()
        }
    
    def finalizar_practica(self, sesion_id: str) -> ResultadoPractica:
        """
        Finaliza la práctica y devuelve el resultado.
        """
        sesion = self.sesion_repository.obtener_por_id(sesion_id)
        if not sesion:
            raise ValueError("Sesión no encontrada")
        
        resultado = sesion.finalizar_practica()
        self.sesion_repository.guardar(sesion)
        
        return resultado


@dataclass
class ConsultaSimulacroService:
    """
    Servicio para consultar información de simulacros.
    """
    simulacro_repository: ISimulacroRepository
    sesion_repository: ISesionPracticaRepository
    
    def obtener_historial_migrante(self, migrante_id: str) -> dict:
        """
        Obtiene el historial de simulacros y prácticas de un migrante.
        """
        simulacros = self.simulacro_repository.obtener_por_migrante(migrante_id)
        practicas = self.sesion_repository.obtener_por_migrante(migrante_id)
        
        return {
            'simulacros_con_asesor': [
                {
                    'id': s.id,
                    'fecha': s.horario.fecha if s.horario else None,
                    'estado': s.estado.value,
                    'tiene_transcripcion': s.tiene_transcripcion(),
                    'tiene_feedback': s.feedback is not None
                }
                for s in simulacros
            ],
            'simulacros_disponibles': MAX_SIMULACROS_CON_ASESOR - len(simulacros),
            'practicas_individuales': [
                {
                    'id': p.id,
                    'tipo_visado': p.tipo_visado.value,
                    'resultado': p.resultado.porcentaje_acierto if p.resultado else None,
                    'aprobado': p.resultado.aprobado if p.resultado else None
                }
                for p in practicas if p.resultado
            ]
        }
    
    def obtener_simulacros_asesor(self, asesor_id: str) -> List[dict]:
        """
        Obtiene los simulacros pendientes de un asesor.
        """
        simulacros = self.simulacro_repository.obtener_por_asesor(asesor_id)
        
        return [
            {
                'id': s.id,
                'migrante_nombre': s.migrante_nombre,
                'fecha': s.horario.fecha if s.horario else None,
                'hora': s.horario.hora if s.horario else None,
                'modalidad': s.modalidad.value,
                'estado': s.estado.value
            }
            for s in simulacros
            if s.estado in [EstadoSimulacro.AGENDADO, EstadoSimulacro.EN_PROGRESO]
        ]
