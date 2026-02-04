# -*- coding: utf-8 -*-
"""Servicios del dominio para testing BDD de Agendamiento de Entrevistas."""

from datetime import date, time, datetime
from typing import Tuple, List

from .entities import (
    EntrevistaAgendamientoEntity,
    ResultadoOperacionEntity,
    crear_resultado,
)
from .constants import MENSAJES


# Excepciones
class AgendamientoException(Exception):
    pass


class ReprogramacionNoPermitidaException(AgendamientoException):
    pass


class CancelacionNoPermitidaException(AgendamientoException):
    pass


class ModificacionNoPermitidaException(AgendamientoException):
    pass


class HorarioNoDisponibleException(AgendamientoException):
    pass


class AgendamientoSeleccionService:
    """Servicio para gestionar la selección de horarios."""

    @staticmethod
    def seleccionar_horario(entrevista: EntrevistaAgendamientoEntity,
                             opcion_id: str) -> ResultadoOperacionEntity:
        exito = entrevista.seleccionar_opcion(opcion_id)
        if not exito:
            raise HorarioNoDisponibleException(f"El horario {opcion_id} no está disponible")

        mensaje = MENSAJES['agendamiento_exitoso'].format(
            fecha_legible=entrevista.horario.obtener_fecha_legible(),
            hora=entrevista.horario.obtener_hora_formateada()
        )
        return crear_resultado(
            exito=True, mensaje=mensaje,
            datos={'fecha': str(entrevista.horario.fecha), 'hora': str(entrevista.horario.hora), 'estado': entrevista.estado}
        )

    @staticmethod
    def verificar_disponibilidad(entrevista: EntrevistaAgendamientoEntity, horario_str: str) -> bool:
        for opcion in entrevista.opciones_ofrecidas:
            if opcion.horario.hora.strftime('%H:%M') == horario_str and opcion.disponible:
                return True
        return False

    @staticmethod
    def obtener_horarios_disponibles(entrevista: EntrevistaAgendamientoEntity) -> List[str]:
        return [op.horario.hora.strftime('%H:%M') for op in entrevista.opciones_ofrecidas if op.disponible]


class AgendamientoReprogramacionService:
    """Servicio para gestionar la reprogramación de entrevistas."""

    @staticmethod
    def puede_reprogramar(entrevista: EntrevistaAgendamientoEntity) -> Tuple[bool, str]:
        if not entrevista.puede_reprogramar():
            return False, MENSAJES['reprogramacion_rechazada']
        return True, ""

    @staticmethod
    def reprogramar(entrevista: EntrevistaAgendamientoEntity,
                    nueva_fecha: date, nueva_hora: time) -> ResultadoOperacionEntity:
        puede, mensaje_error = AgendamientoReprogramacionService.puede_reprogramar(entrevista)
        if not puede:
            raise ReprogramacionNoPermitidaException(mensaje_error)

        entrevista.aplicar_reprogramacion(nueva_fecha, nueva_hora)

        if entrevista.veces_reprogramada >= entrevista.regla.max_reprogramaciones:
            mensaje = MENSAJES['reprogramacion_permitida']
        else:
            mensaje = MENSAJES['reprogramacion_exitosa']

        return crear_resultado(
            exito=True, mensaje=mensaje,
            datos={
                'nueva_fecha': str(nueva_fecha), 'nueva_hora': str(nueva_hora),
                'veces_reprogramada': entrevista.veces_reprogramada,
                'reprogramaciones_restantes': entrevista.regla.max_reprogramaciones - entrevista.veces_reprogramada
            }
        )

    @staticmethod
    def es_ultima_reprogramacion(entrevista: EntrevistaAgendamientoEntity) -> bool:
        return entrevista.veces_reprogramada + 1 >= entrevista.regla.max_reprogramaciones


class AgendamientoCancelacionService:
    """Servicio para gestionar la cancelación de entrevistas."""

    @staticmethod
    def calcular_horas_restantes(entrevista: EntrevistaAgendamientoEntity,
                                   fecha_actual: datetime = None) -> int:
        if not entrevista.horario:
            return 0
        fecha_actual = fecha_actual or datetime.now()
        fecha_entrevista = datetime.combine(entrevista.horario.fecha, entrevista.horario.hora)
        diferencia = fecha_entrevista - fecha_actual
        return int(diferencia.total_seconds() / 3600)

    @staticmethod
    def puede_cancelar(entrevista: EntrevistaAgendamientoEntity,
                        horas_restantes: int = None) -> Tuple[bool, str]:
        if horas_restantes is None:
            horas_restantes = AgendamientoCancelacionService.calcular_horas_restantes(entrevista)
        if not entrevista.puede_cancelar(horas_restantes):
            return False, MENSAJES['cancelacion_rechazada']
        return True, ""

    @staticmethod
    def cancelar(entrevista: EntrevistaAgendamientoEntity, motivo: str,
                 detalle: str = "", horas_restantes: int = None) -> ResultadoOperacionEntity:
        puede, mensaje_error = AgendamientoCancelacionService.puede_cancelar(entrevista, horas_restantes)
        if not puede:
            raise CancelacionNoPermitidaException(mensaje_error)

        entrevista.aplicar_cancelacion()
        return crear_resultado(
            exito=True, mensaje=MENSAJES['cancelacion_exitosa'],
            datos={'motivo': motivo, 'detalle': detalle, 'estado': entrevista.estado}
        )


class AgendamientoConfirmacionService:
    """Servicio para gestionar la confirmación de entrevistas."""

    @staticmethod
    def confirmar(entrevista: EntrevistaAgendamientoEntity) -> ResultadoOperacionEntity:
        entrevista.aplicar_confirmacion()
        return crear_resultado(exito=True, mensaje="Entrevista confirmada exitosamente", datos={'estado': entrevista.estado})


class AgendamientoProteccionService:
    """Servicio para proteger la integridad de las entrevistas."""

    @staticmethod
    def validar_modificacion_directa(entrevista: EntrevistaAgendamientoEntity) -> Tuple[bool, str]:
        return False, MENSAJES['modificacion_rechazada']

    @staticmethod
    def rechazar_modificacion(entrevista: EntrevistaAgendamientoEntity) -> ResultadoOperacionEntity:
        return crear_resultado(exito=False, mensaje=MENSAJES['modificacion_rechazada'], datos={'estado_preservado': entrevista.estado})


class AgendamientoService:
    """Servicio orquestador principal para operaciones de agendamiento."""

    seleccion = AgendamientoSeleccionService()
    reprogramacion = AgendamientoReprogramacionService()
    cancelacion = AgendamientoCancelacionService()
    confirmacion = AgendamientoConfirmacionService()
    proteccion = AgendamientoProteccionService()

    @classmethod
    def agendar_entrevista(cls, entrevista: EntrevistaAgendamientoEntity,
                           opcion_id: str) -> ResultadoOperacionEntity:
        return cls.seleccion.seleccionar_horario(entrevista, opcion_id)

    @classmethod
    def reprogramar_entrevista(cls, entrevista: EntrevistaAgendamientoEntity,
                                nueva_fecha: date, nueva_hora: time) -> ResultadoOperacionEntity:
        return cls.reprogramacion.reprogramar(entrevista, nueva_fecha, nueva_hora)

    @classmethod
    def cancelar_entrevista(cls, entrevista: EntrevistaAgendamientoEntity,
                             motivo: str, horas_restantes: int = None) -> ResultadoOperacionEntity:
        return cls.cancelacion.cancelar(entrevista, motivo, "", horas_restantes)

    @classmethod
    def confirmar_entrevista(cls, entrevista: EntrevistaAgendamientoEntity) -> ResultadoOperacionEntity:
        return cls.confirmacion.confirmar(entrevista)

    @classmethod
    def validar_modificacion(cls, entrevista: EntrevistaAgendamientoEntity) -> ResultadoOperacionEntity:
        return cls.proteccion.rechazar_modificacion(entrevista)
