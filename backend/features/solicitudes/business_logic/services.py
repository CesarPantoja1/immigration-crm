# -*- coding: utf-8 -*-
"""
Servicios del dominio para testing BDD de Agendamiento de Entrevistas.

RESPONSABILIDAD:
- Encapsular reglas de negocio y validaciones
- Orquestar operaciones complejas sobre entidades
- Servir como capa de lógica para los steps BDD

LÓGICA EXTRAÍDA DE steps/agendamiento_entrevista.py:
- ReprogramacionService → AgendamientoReprogramacionService
- CancelacionService → AgendamientoCancelacionService
- ConfirmacionService → AgendamientoConfirmacionService
- Excepciones → Excepciones tipadas

IMPORTANTE: Estos servicios NO dependen de Django ni ORM.
"""

from datetime import date, time, datetime, timedelta
from typing import Tuple, Optional, List

from .entities import (
    EntrevistaAgendamientoEntity,
    HorarioEntity,
    OpcionHorarioEntity,
    ReglaEmbajadaEntity,
    ResultadoOperacionEntity,
    crear_resultado,
)
from .constants import MENSAJES


# ============================================================
# EXCEPCIONES DEL DOMINIO
# ============================================================

class AgendamientoException(Exception):
    """Excepción base para errores de agendamiento."""
    pass


class ReprogramacionNoPermitidaException(AgendamientoException):
    """Excepción cuando la reprogramación no está permitida."""
    pass


class CancelacionNoPermitidaException(AgendamientoException):
    """Excepción cuando la cancelación no está permitida."""
    pass


class ModificacionNoPermitidaException(AgendamientoException):
    """Excepción cuando la modificación directa no está permitida."""
    pass


class HorarioNoDisponibleException(AgendamientoException):
    """Excepción cuando el horario no está disponible."""
    pass


# ============================================================
# SERVICIO DE SELECCIÓN DE HORARIO
# ============================================================

class AgendamientoSeleccionService:
    """
    Servicio para gestionar la selección de horarios.
    Encapsula la lógica de selección y validación de disponibilidad.
    """

    @staticmethod
    def seleccionar_horario(entrevista: EntrevistaAgendamientoEntity,
                             opcion_id: str) -> ResultadoOperacionEntity:
        """
        Selecciona un horario para la entrevista.

        Args:
            entrevista: Entrevista a agendar
            opcion_id: ID de la opción a seleccionar

        Returns:
            ResultadoOperacionEntity con el resultado

        Raises:
            HorarioNoDisponibleException: Si el horario no está disponible
        """
        exito = entrevista.seleccionar_opcion(opcion_id)

        if not exito:
            raise HorarioNoDisponibleException(
                f"El horario {opcion_id} no está disponible"
            )

        mensaje = MENSAJES['agendamiento_exitoso'].format(
            fecha_legible=entrevista.horario.obtener_fecha_legible(),
            hora=entrevista.horario.obtener_hora_formateada()
        )

        return crear_resultado(
            exito=True,
            mensaje=mensaje,
            datos={
                'fecha': str(entrevista.horario.fecha),
                'hora': str(entrevista.horario.hora),
                'estado': entrevista.estado
            }
        )

    @staticmethod
    def verificar_disponibilidad(entrevista: EntrevistaAgendamientoEntity,
                                  horario_str: str) -> bool:
        """
        Verifica si un horario específico está disponible.

        Args:
            entrevista: Entrevista con opciones
            horario_str: Horario en formato "HH:MM"

        Returns:
            True si está disponible, False si no
        """
        for opcion in entrevista.opciones_ofrecidas:
            hora_opcion = opcion.horario.hora.strftime('%H:%M')
            if hora_opcion == horario_str and opcion.disponible:
                return True
        return False

    @staticmethod
    def obtener_horarios_disponibles(entrevista: EntrevistaAgendamientoEntity) -> List[str]:
        """
        Obtiene lista de horarios disponibles.

        Returns:
            Lista de horarios en formato "HH:MM"
        """
        disponibles = []
        for opcion in entrevista.opciones_ofrecidas:
            if opcion.disponible:
                disponibles.append(opcion.horario.hora.strftime('%H:%M'))
        return disponibles


# ============================================================
# SERVICIO DE REPROGRAMACIÓN
# ============================================================

class AgendamientoReprogramacionService:
    """
    Servicio para gestionar la reprogramación de entrevistas.
    Encapsula las reglas de negocio de reprogramación.
    """

    @staticmethod
    def puede_reprogramar(entrevista: EntrevistaAgendamientoEntity) -> Tuple[bool, str]:
        """
        Verifica si una entrevista puede ser reprogramada.

        Returns:
            Tupla (puede_reprogramar, mensaje)
        """
        if not entrevista.puede_reprogramar():
            return False, MENSAJES['reprogramacion_rechazada']
        return True, ""

    @staticmethod
    def reprogramar(entrevista: EntrevistaAgendamientoEntity,
                    nueva_fecha: date,
                    nueva_hora: time) -> ResultadoOperacionEntity:
        """
        Reprograma una entrevista a una nueva fecha y hora.

        Args:
            entrevista: Entrevista a reprogramar
            nueva_fecha: Nueva fecha
            nueva_hora: Nueva hora

        Returns:
            ResultadoOperacionEntity con el resultado

        Raises:
            ReprogramacionNoPermitidaException: Si no se puede reprogramar
        """
        puede, mensaje_error = AgendamientoReprogramacionService.puede_reprogramar(entrevista)

        if not puede:
            raise ReprogramacionNoPermitidaException(mensaje_error)

        # Aplicar reprogramación
        entrevista.aplicar_reprogramacion(nueva_fecha, nueva_hora)

        # Determinar mensaje según si es la última reprogramación
        if entrevista.veces_reprogramada >= entrevista.regla.max_reprogramaciones:
            mensaje = MENSAJES['reprogramacion_permitida']
        else:
            mensaje = MENSAJES['reprogramacion_exitosa']
            if entrevista.veces_reprogramada == entrevista.regla.max_reprogramaciones:
                mensaje += ". " + MENSAJES['reprogramacion_ultima']

        return crear_resultado(
            exito=True,
            mensaje=mensaje,
            datos={
                'nueva_fecha': str(nueva_fecha),
                'nueva_hora': str(nueva_hora),
                'veces_reprogramada': entrevista.veces_reprogramada,
                'reprogramaciones_restantes': entrevista.regla.max_reprogramaciones - entrevista.veces_reprogramada
            }
        )

    @staticmethod
    def es_ultima_reprogramacion(entrevista: EntrevistaAgendamientoEntity) -> bool:
        """
        Verifica si la próxima reprogramación sería la última permitida.
        """
        return entrevista.veces_reprogramada + 1 >= entrevista.regla.max_reprogramaciones


# ============================================================
# SERVICIO DE CANCELACIÓN
# ============================================================

class AgendamientoCancelacionService:
    """
    Servicio para gestionar la cancelación de entrevistas.
    Encapsula las reglas de negocio de cancelación por embajada.
    """

    @staticmethod
    def calcular_horas_restantes(entrevista: EntrevistaAgendamientoEntity,
                                   fecha_actual: datetime = None) -> int:
        """
        Calcula las horas restantes hasta la entrevista.

        Args:
            entrevista: Entrevista con horario
            fecha_actual: Fecha actual (si None, usa datetime.now())

        Returns:
            Horas restantes como entero
        """
        if not entrevista.horario:
            return 0

        fecha_actual = fecha_actual or datetime.now()
        fecha_entrevista = datetime.combine(
            entrevista.horario.fecha,
            entrevista.horario.hora
        )

        diferencia = fecha_entrevista - fecha_actual
        return int(diferencia.total_seconds() / 3600)

    @staticmethod
    def puede_cancelar(entrevista: EntrevistaAgendamientoEntity,
                        horas_restantes: int = None) -> Tuple[bool, str]:
        """
        Verifica si una entrevista puede ser cancelada.

        Args:
            entrevista: Entrevista a verificar
            horas_restantes: Horas restantes (si None, calcula automáticamente)

        Returns:
            Tupla (puede_cancelar, mensaje)
        """
        if horas_restantes is None:
            horas_restantes = AgendamientoCancelacionService.calcular_horas_restantes(entrevista)

        if not entrevista.puede_cancelar(horas_restantes):
            return False, MENSAJES['cancelacion_rechazada']

        return True, ""

    @staticmethod
    def cancelar(entrevista: EntrevistaAgendamientoEntity,
                 motivo: str,
                 detalle: str = "",
                 horas_restantes: int = None) -> ResultadoOperacionEntity:
        """
        Cancela una entrevista.

        Args:
            entrevista: Entrevista a cancelar
            motivo: Motivo de cancelación
            detalle: Detalle adicional
            horas_restantes: Horas restantes (si None, calcula automáticamente)

        Returns:
            ResultadoOperacionEntity con el resultado

        Raises:
            CancelacionNoPermitidaException: Si no se puede cancelar
        """
        puede, mensaje_error = AgendamientoCancelacionService.puede_cancelar(
            entrevista, horas_restantes
        )

        if not puede:
            raise CancelacionNoPermitidaException(mensaje_error)

        # Aplicar cancelación
        entrevista.aplicar_cancelacion()

        return crear_resultado(
            exito=True,
            mensaje=MENSAJES['cancelacion_exitosa'],
            datos={
                'motivo': motivo,
                'detalle': detalle,
                'estado': entrevista.estado
            }
        )


# ============================================================
# SERVICIO DE CONFIRMACIÓN
# ============================================================

class AgendamientoConfirmacionService:
    """
    Servicio para gestionar la confirmación de entrevistas.
    """

    @staticmethod
    def confirmar(entrevista: EntrevistaAgendamientoEntity) -> ResultadoOperacionEntity:
        """
        Confirma una entrevista agendada.

        Args:
            entrevista: Entrevista a confirmar

        Returns:
            ResultadoOperacionEntity con el resultado
        """
        entrevista.aplicar_confirmacion()

        return crear_resultado(
            exito=True,
            mensaje="Entrevista confirmada exitosamente",
            datos={'estado': entrevista.estado}
        )


# ============================================================
# SERVICIO DE PROTECCIÓN/INTEGRIDAD
# ============================================================

class AgendamientoProteccionService:
    """
    Servicio para proteger la integridad de las entrevistas.
    Previene modificaciones no autorizadas.
    """

    @staticmethod
    def validar_modificacion_directa(entrevista: EntrevistaAgendamientoEntity) -> Tuple[bool, str]:
        """
        Valida si se puede modificar directamente una entrevista.
        La modificación directa NO está permitida; debe usarse reprogramación.

        Returns:
            Tupla (permitido, mensaje) - siempre (False, mensaje_error)
        """
        if entrevista.esta_agendada():
            return False, MENSAJES['modificacion_rechazada']
        return False, MENSAJES['modificacion_rechazada']

    @staticmethod
    def rechazar_modificacion(entrevista: EntrevistaAgendamientoEntity) -> ResultadoOperacionEntity:
        """
        Rechaza un intento de modificación directa.

        Returns:
            ResultadoOperacionEntity indicando rechazo
        """
        return crear_resultado(
            exito=False,
            mensaje=MENSAJES['modificacion_rechazada'],
            datos={'estado_preservado': entrevista.estado}
        )


# ============================================================
# SERVICIO ORQUESTADOR
# ============================================================

class AgendamientoService:
    """
    Servicio orquestador principal para operaciones de agendamiento.
    Combina los servicios específicos para casos de uso completos.
    """

    seleccion = AgendamientoSeleccionService()
    reprogramacion = AgendamientoReprogramacionService()
    cancelacion = AgendamientoCancelacionService()
    confirmacion = AgendamientoConfirmacionService()
    proteccion = AgendamientoProteccionService()

    @classmethod
    def agendar_entrevista(cls, entrevista: EntrevistaAgendamientoEntity,
                           opcion_id: str) -> ResultadoOperacionEntity:
        """Agenda una entrevista seleccionando un horario."""
        return cls.seleccion.seleccionar_horario(entrevista, opcion_id)

    @classmethod
    def reprogramar_entrevista(cls, entrevista: EntrevistaAgendamientoEntity,
                                nueva_fecha: date,
                                nueva_hora: time) -> ResultadoOperacionEntity:
        """Reprograma una entrevista."""
        return cls.reprogramacion.reprogramar(entrevista, nueva_fecha, nueva_hora)

    @classmethod
    def cancelar_entrevista(cls, entrevista: EntrevistaAgendamientoEntity,
                             motivo: str,
                             horas_restantes: int = None) -> ResultadoOperacionEntity:
        """Cancela una entrevista."""
        return cls.cancelacion.cancelar(entrevista, motivo, "", horas_restantes)

    @classmethod
    def confirmar_entrevista(cls, entrevista: EntrevistaAgendamientoEntity) -> ResultadoOperacionEntity:
        """Confirma una entrevista."""
        return cls.confirmacion.confirmar(entrevista)

    @classmethod
    def validar_modificacion(cls, entrevista: EntrevistaAgendamientoEntity) -> ResultadoOperacionEntity:
        """Valida y rechaza modificación directa."""
        return cls.proteccion.rechazar_modificacion(entrevista)
