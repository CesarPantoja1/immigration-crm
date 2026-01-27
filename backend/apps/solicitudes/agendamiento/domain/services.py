"""
Servicios de Dominio para Agendamiento de Entrevistas.
Contienen lógica de negocio que no pertenece a una entidad específica.
"""
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Tuple
from .entities import Entrevista, RespuestaEmbajada, GestorEntrevistas
from .value_objects import (
    EstadoEntrevista, ModoAsignacion, MotivoCancelacion,
    HorarioEntrevista, OpcionHorario, ReglaEmbajada,
    obtener_regla_embajada
)
from .exceptions import (
    ReprogramacionNoPermitidaException,
    CancelacionNoPermitidaException,
    OpcionNoDisponibleException,
    EntrevistaNoConfirmableException,
    FechaInvalidaException
)


@dataclass
class ResultadoOperacion:
    """Resultado de una operación del servicio."""
    exito: bool
    mensaje: str
    datos: dict = None


class AsignacionEntrevistaService:
    """
    Servicio para gestionar la asignación de entrevistas por la embajada.
    
    Maneja los dos modos de asignación:
    1. FECHA_FIJA: Embajada asigna directamente
    2. OPCIONES_ELEGIR: Embajada ofrece opciones y migrante elige
    """
    
    def procesar_asignacion_directa(
        self,
        entrevista: Entrevista,
        fecha: date,
        hora: time,
        ubicacion: str = ""
    ) -> ResultadoOperacion:
        """
        Procesa una asignación directa de fecha por la embajada.
        """
        entrevista.asignar_fecha_fija(fecha, hora, ubicacion)
        
        return ResultadoOperacion(
            exito=True,
            mensaje=f"Entrevista asignada para el {entrevista.obtener_horario_legible()}",
            datos={'entrevista': entrevista}
        )
    
    def procesar_opciones(
        self,
        entrevista: Entrevista,
        opciones: List[OpcionHorario]
    ) -> ResultadoOperacion:
        """
        Procesa opciones de horario ofrecidas por la embajada.
        """
        entrevista.ofrecer_opciones(opciones)
        
        return ResultadoOperacion(
            exito=True,
            mensaje="Opciones de horario disponibles para selección",
            datos={'entrevista': entrevista, 'opciones': opciones}
        )
    
    def seleccionar_opcion(
        self,
        entrevista: Entrevista,
        opcion_id: str
    ) -> ResultadoOperacion:
        """
        Procesa la selección de una opción por el migrante.
        """
        if not entrevista.tiene_opciones():
            return ResultadoOperacion(
                exito=False,
                mensaje="No hay opciones disponibles para seleccionar"
            )
        
        if entrevista.seleccionar_opcion(opcion_id):
            return ResultadoOperacion(
                exito=True,
                mensaje=f"Horario seleccionado: {entrevista.obtener_horario_legible()}",
                datos={'entrevista': entrevista}
            )
        
        raise OpcionNoDisponibleException(opcion_id)


class ReprogramacionService:
    """
    Servicio para gestionar reprogramaciones de entrevistas.
    
    Aplica las reglas específicas de cada embajada.
    """
    
    def validar_reprogramacion(
        self,
        entrevista: Entrevista
    ) -> Tuple[bool, str]:
        """
        Valida si una entrevista puede ser reprogramada.
        """
        return entrevista.puede_reprogramar()
    
    def reprogramar(
        self,
        entrevista: Entrevista,
        nueva_fecha: date,
        nueva_hora: time
    ) -> ResultadoOperacion:
        """
        Reprograma una entrevista a una nueva fecha.
        """
        # Validar fecha futura
        horario_propuesto = HorarioEntrevista(fecha=nueva_fecha, hora=nueva_hora)
        if not horario_propuesto.es_futuro():
            raise FechaInvalidaException("La nueva fecha debe ser en el futuro")
        
        # Validar anticipación mínima
        regla = entrevista.regla
        if not regla.es_fecha_valida(nueva_fecha):
            raise FechaInvalidaException(
                f"Se requieren al menos {regla.dias_minimos_anticipacion} días de anticipación"
            )
        
        exito, mensaje = entrevista.reprogramar(nueva_fecha, nueva_hora)
        
        if not exito:
            raise ReprogramacionNoPermitidaException(mensaje)
        
        return ResultadoOperacion(
            exito=True,
            mensaje=mensaje,
            datos={
                'entrevista': entrevista,
                'nueva_fecha': entrevista.obtener_horario_legible(),
                'veces_reprogramada': entrevista.veces_reprogramada
            }
        )


class CancelacionService:
    """
    Servicio para gestionar cancelaciones de entrevistas.
    """
    
    def validar_cancelacion(
        self,
        entrevista: Entrevista
    ) -> Tuple[bool, str]:
        """
        Valida si una entrevista puede ser cancelada.
        """
        return entrevista.puede_cancelar()
    
    def cancelar(
        self,
        entrevista: Entrevista,
        motivo: MotivoCancelacion,
        detalle: str = ""
    ) -> ResultadoOperacion:
        """
        Cancela una entrevista.
        """
        puede, mensaje = self.validar_cancelacion(entrevista)
        
        if not puede:
            raise CancelacionNoPermitidaException(entrevista.regla.horas_minimas_cancelacion)
        
        exito, mensaje_resultado = entrevista.cancelar(motivo, detalle)
        
        return ResultadoOperacion(
            exito=True,
            mensaje=mensaje_resultado,
            datos={'entrevista': entrevista}
        )


class ConfirmacionService:
    """
    Servicio para gestionar confirmaciones de asistencia.
    """
    
    def confirmar_asistencia(
        self,
        entrevista: Entrevista
    ) -> ResultadoOperacion:
        """
        Confirma la asistencia a una entrevista.
        """
        if not entrevista.tiene_fecha_asignada():
            return ResultadoOperacion(
                exito=False,
                mensaje="No hay fecha asignada para confirmar"
            )
        
        if entrevista.confirmar_asistencia():
            return ResultadoOperacion(
                exito=True,
                mensaje="Asistencia confirmada exitosamente",
                datos={'entrevista': entrevista}
            )
        
        raise EntrevistaNoConfirmableException(entrevista.estado.value)


class NotificacionEntrevistaService:
    """
    Servicio para gestionar notificaciones relacionadas con entrevistas.
    """
    
    def generar_recordatorio(
        self,
        entrevista: Entrevista,
        dias_anticipacion: int = 1
    ) -> Optional[dict]:
        """
        Genera un recordatorio para una entrevista próxima.
        """
        if not entrevista.tiene_fecha_asignada():
            return None
        
        dias_restantes = entrevista.horario.dias_restantes()
        
        if dias_restantes <= dias_anticipacion:
            return {
                'tipo': 'RECORDATORIO_ENTREVISTA',
                'solicitud_id': entrevista.solicitud_id,
                'mensaje': f"Recordatorio: Su entrevista es el {entrevista.obtener_horario_legible()}",
                'dias_restantes': dias_restantes,
                'horario': entrevista.obtener_horario_legible(),
                'ubicacion': entrevista.ubicacion
            }
        
        return None
    
    def notificar_cambio_estado(
        self,
        entrevista: Entrevista,
        estado_anterior: EstadoEntrevista
    ) -> dict:
        """
        Genera notificación de cambio de estado.
        """
        mensajes = {
            EstadoEntrevista.AGENDADA: "Su entrevista ha sido agendada",
            EstadoEntrevista.OPCIONES_DISPONIBLES: "Tiene opciones de horario disponibles para su entrevista",
            EstadoEntrevista.CONFIRMADA: "Ha confirmado su asistencia a la entrevista",
            EstadoEntrevista.REPROGRAMADA: "Su entrevista ha sido reprogramada",
            EstadoEntrevista.CANCELADA: "Su entrevista ha sido cancelada",
            EstadoEntrevista.COMPLETADA: "Su entrevista ha sido completada",
        }
        
        return {
            'tipo': 'CAMBIO_ESTADO_ENTREVISTA',
            'solicitud_id': entrevista.solicitud_id,
            'estado_anterior': estado_anterior.value,
            'estado_nuevo': entrevista.estado.value,
            'mensaje': mensajes.get(entrevista.estado, "Estado de entrevista actualizado"),
            'horario': entrevista.obtener_horario_legible() if entrevista.tiene_fecha_asignada() else None
        }


class ValidacionEntrevistaService:
    """
    Servicio para validaciones de entrevistas.
    """
    
    def validar_fecha_disponible(
        self,
        embajada: str,
        fecha: date,
        hora: time
    ) -> Tuple[bool, str]:
        """
        Valida si una fecha/hora está disponible para agendar.
        """
        horario = HorarioEntrevista(fecha=fecha, hora=hora)
        
        if not horario.es_futuro():
            return False, "La fecha debe ser en el futuro"
        
        regla = obtener_regla_embajada(embajada)
        if not regla.es_fecha_valida(fecha):
            return False, f"Se requieren al menos {regla.dias_minimos_anticipacion} días de anticipación"
        
        return True, "Fecha disponible"
    
    def validar_entrevista_activa(
        self,
        entrevista: Entrevista
    ) -> Tuple[bool, str]:
        """
        Valida si la entrevista está en un estado activo.
        """
        estados_activos = [
            EstadoEntrevista.AGENDADA,
            EstadoEntrevista.CONFIRMADA,
            EstadoEntrevista.OPCIONES_DISPONIBLES,
            EstadoEntrevista.REPROGRAMADA
        ]
        
        if entrevista.estado in estados_activos:
            return True, "Entrevista activa"
        
        return False, f"Entrevista en estado {entrevista.estado.value}"


class ProcesamientoRespuestaEmbajadaService:
    """
    Servicio para procesar respuestas de la embajada.
    """
    
    def __init__(self):
        self.asignacion_service = AsignacionEntrevistaService()
    
    def procesar_respuesta(
        self,
        gestor: GestorEntrevistas,
        respuesta: RespuestaEmbajada
    ) -> ResultadoOperacion:
        """
        Procesa una respuesta de la embajada.
        """
        if respuesta.es_rechazo():
            return ResultadoOperacion(
                exito=True,
                mensaje=f"Solicitud rechazada: {respuesta.motivo_rechazo}",
                datos={
                    'tipo': 'RECHAZO',
                    'puede_apelar': respuesta.puede_apelar
                }
            )
        
        # Procesar aprobación
        gestor.procesar_respuesta_embajada(respuesta)
        
        if respuesta.entrevista.modo_asignacion == ModoAsignacion.FECHA_FIJA:
            return ResultadoOperacion(
                exito=True,
                mensaje=respuesta.mensaje,
                datos={
                    'tipo': 'APROBACION',
                    'modo': 'FECHA_FIJA',
                    'entrevista': respuesta.entrevista
                }
            )
        else:
            return ResultadoOperacion(
                exito=True,
                mensaje=respuesta.mensaje,
                datos={
                    'tipo': 'APROBACION',
                    'modo': 'OPCIONES',
                    'opciones': respuesta.entrevista.opciones_horario
                }
            )
