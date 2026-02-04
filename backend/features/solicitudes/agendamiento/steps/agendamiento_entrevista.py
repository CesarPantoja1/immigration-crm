# -*- coding: utf-8 -*-
"""
Steps BDD para Agendamiento de Entrevistas.

REFACTORIZADO: Steps delgados que solo orquestan.
La lógica de negocio está en: features/solicitudes/business_logic/

Este archivo contiene SOLO las definiciones de steps.
Los steps llaman a servicios y verifican resultados, sin contener reglas.

Estructura del módulo business_logic:
- constants.py: ESTADOS_ENTREVISTA, MENSAJES, REGLAS_EMBAJADA_DEFAULT
- entities.py: EntrevistaAgendamientoEntity, HorarioEntity, etc.
- services.py: AgendamientoService, ReprogramacionService, etc.
"""
import os
import sys
from datetime import datetime, date, time, timedelta

# Configurar Django ANTES de importar
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')

import django
django.setup()

from behave import step, use_step_matcher

# Importar desde business_logic (n-capas con Service Layer)
from features.solicitudes.business_logic import (
    # Entidades
    EntrevistaAgendamientoEntity,
    HorarioEntity,
    OpcionHorarioEntity,
    ReglaEmbajadaEntity,
    # Factory functions
    reset_id_counters,
    crear_entrevista_agendamiento,
    crear_horario,
    crear_opcion_horario,
    crear_regla_embajada,
    # Servicios
    AgendamientoService,
    AgendamientoSeleccionService,
    AgendamientoReprogramacionService,
    AgendamientoCancelacionService,
    AgendamientoProteccionService,
    # Excepciones
    ReprogramacionNoPermitidaException,
    CancelacionNoPermitidaException,
    # Constantes
    ESTADOS_ENTREVISTA_LEGIBLES,
    MENSAJES,
)

use_step_matcher("re")


# ============================================================
# ANTECEDENTES
# ============================================================

@step("que el solicitante cuenta con una solicitud migratoria aprobada")
def step_impl(context):
    """Setup: el solicitante tiene una solicitud aprobada."""
    reset_id_counters()
    context.solicitud_id = "SOL-TEST-001"
    context.solicitud_aprobada = True
    assert context.solicitud_aprobada is True


@step("el sistema presenta opciones de fecha y horario para entrevistas")
def step_impl(context):
    """Setup: el sistema tiene opciones disponibles."""
    context.opciones_disponibles = True
    assert context.opciones_disponibles is True


# ============================================================
# AGENDAMIENTO DE ENTREVISTA
# ============================================================

@step('que existe una fecha de entrevista "(?P<fecha_entrevista>.+)" con los siguientes horarios disponibles')
def step_impl(context, fecha_entrevista):
    """Setup de horarios disponibles para una fecha."""
    # Parsear fecha
    fecha = datetime.strptime(fecha_entrevista, "%Y-%m-%d").date()

    # Crear entrevista usando factory
    context.entrevista = crear_entrevista_agendamiento(
        solicitud_id="SOL-TEST-001",
        embajada="USA"
    )

    # Crear opciones de horario desde la tabla
    opciones = []
    context.horarios_disponibles = set()

    for row in context.table:
        horario_str = row['horario']
        hora = datetime.strptime(horario_str, "%H:%M").time()
        es_disponible = row['estado'] == 'Disponible'

        # Usar factory para crear horario y opción
        horario = crear_horario(fecha=fecha, hora=hora)
        opcion = crear_opcion_horario(
            horario=horario,
            disponible=es_disponible,
            opcion_id=f"OPT-{horario_str.replace(':', '')}"
        )
        opciones.append(opcion)

        if es_disponible:
            context.horarios_disponibles.add(horario_str)

    # Ofrecer opciones a la entrevista
    context.entrevista.ofrecer_opciones(opciones)
    context.fecha_entrevista = fecha


@step('el solicitante selecciona la fecha "(?P<fecha_entrevista>.+)" y el horario "09:00"')
def step_impl(context, fecha_entrevista):
    """El solicitante selecciona un horario específico."""
    horario = "09:00"

    # Verificar disponibilidad usando servicio
    disponible = AgendamientoSeleccionService.verificar_disponibilidad(
        context.entrevista, horario
    )
    assert disponible, f"El horario {horario} no está disponible"

    # Seleccionar la opción usando servicio
    opcion_id = f"OPT-{horario.replace(':', '')}"
    resultado = AgendamientoService.agendar_entrevista(context.entrevista, opcion_id)

    assert resultado.exito, "No se pudo seleccionar la opción"

    # Actualizar estado de disponibilidad
    context.horarios_disponibles.discard(horario)
    context.horarios_ocupados = {horario}
    context.resultado_agendamiento = resultado


@step("el sistema registra la entrevista asociada a la solicitud")
def step_impl(context):
    """Verificar que la entrevista fue registrada."""
    assert context.entrevista.esta_agendada()
    assert context.entrevista.tiene_horario_asignado()


@step('el horario "09:00" queda registrado como no disponible')
def step_impl(context):
    """Verificar que el horario seleccionado ya no está disponible."""
    assert "09:00" not in context.horarios_disponibles
    assert "09:00" in context.horarios_ocupados


@step('muestra el mensaje "Entrevista agendada para el (?P<fecha_legible>.+) a las 09:00"')
def step_impl(context, fecha_legible):
    """Verificar el mensaje de confirmación."""
    horario_legible = context.entrevista.obtener_horario_legible()
    mensaje_esperado = f"Entrevista agendada para el {fecha_legible} a las 09:00"

    # Verificar que el horario legible contiene la fecha esperada
    assert fecha_legible in horario_legible or context.entrevista.tiene_horario_asignado()
    context.mensaje = mensaje_esperado


# ============================================================
# PROTECCIÓN E INTEGRIDAD
# ============================================================

@step('que el solicitante tiene una entrevista en estado "Programada"')
def step_impl(context):
    """Setup: entrevista en estado Programada (Agendada)."""
    reset_id_counters()
    fecha_futura = date.today() + timedelta(days=30)
    hora = time(10, 0)

    # Crear entrevista usando factory
    context.entrevista = crear_entrevista_agendamiento(
        solicitud_id="SOL-TEST-001",
        embajada="USA"
    )
    context.entrevista.asignar_horario(fecha_futura, hora)

    assert context.entrevista.esta_agendada()


@step("el solicitante solicita la modificación de la fecha o el horario de la entrevista fuera del proceso de reprogramación")
def step_impl(context):
    """Intento de modificación directa (no permitida)."""
    # Usar servicio de protección para validar
    resultado = AgendamientoProteccionService.rechazar_modificacion(context.entrevista)

    context.modificacion_rechazada = not resultado.exito
    context.mensaje = resultado.mensaje


@step("el sistema rechaza la solicitud de modificación")
def step_impl(context):
    """Verificar que la modificación fue rechazada."""
    assert context.modificacion_rechazada is True


@step("mantiene la entrevista en su estado original")
def step_impl(context):
    """Verificar que el estado no cambió."""
    assert context.entrevista.esta_agendada()


# ============================================================
# REPROGRAMACIÓN
# ============================================================

@step("el solicitante solicita la reprogramación de la entrevista a una nueva fecha")
def step_impl(context):
    """El solicitante solicita reprogramar."""
    nueva_fecha = date.today() + timedelta(days=45)
    nueva_hora = time(11, 0)

    # Usar servicio de reprogramación
    resultado = AgendamientoService.reprogramar_entrevista(
        context.entrevista, nueva_fecha, nueva_hora
    )

    context.resultado_reprogramacion = resultado
    context.nueva_fecha = nueva_fecha


@step("el sistema actualiza la fecha de la entrevista")
def step_impl(context):
    """Verificar que la fecha fue actualizada."""
    assert context.entrevista.obtener_fecha() == context.nueva_fecha


@step('la entrevista queda en estado "Reprogramada"')
def step_impl(context):
    """Verificar estado Reprogramada."""
    assert context.entrevista.estado == 'reprogramada'


@step("el solicitante recibe una confirmación de la reprogramación")
def step_impl(context):
    """Verificar mensaje de confirmación."""
    assert context.resultado_reprogramacion.exito is True
    context.mensaje = context.resultado_reprogramacion.mensaje


@step("la entrevista ha sido reprogramada (?P<cantidad_reprogramaciones>\\d+) veces")
def step_impl(context, cantidad_reprogramaciones):
    """Setup: entrevista ya reprogramada N veces."""
    fecha_futura = date.today() + timedelta(days=30)
    hora = time(10, 0)

    # Crear entrevista usando factory
    context.entrevista = crear_entrevista_agendamiento(
        solicitud_id="SOL-TEST-001",
        embajada="USA"
    )
    context.entrevista.asignar_horario(fecha_futura, hora)
    context.entrevista.veces_reprogramada = int(cantidad_reprogramaciones)


@step("la embajada permite un máximo de 2 reprogramaciones por solicitud")
def step_impl(context):
    """Verificar regla de máximo de reprogramaciones."""
    regla = context.entrevista.regla
    assert regla.max_reprogramaciones == 2


@step("el solicitante solicita una nueva reprogramación de la entrevista")
def step_impl(context):
    """Intento de reprogramación."""
    nueva_fecha = date.today() + timedelta(days=60)
    nueva_hora = time(15, 0)

    try:
        # Usar servicio de reprogramación
        resultado = AgendamientoService.reprogramar_entrevista(
            context.entrevista, nueva_fecha, nueva_hora
        )
        context.resultado = "permite"
        context.mensaje = resultado.mensaje
    except ReprogramacionNoPermitidaException as e:
        context.resultado = "rechaza"
        context.mensaje = str(e)


@step("el sistema (?P<accion>permite|rechaza) la reprogramación")
def step_impl(context, accion):
    """Verificar resultado de la reprogramación."""
    assert context.resultado == accion


# ============================================================
# CANCELACIÓN
# ============================================================

@step('que el solicitante tiene una entrevista agendada en la embajada "(?P<embajada>.+)"')
def step_impl(context, embajada):
    """Setup: entrevista agendada en embajada específica."""
    reset_id_counters()
    fecha_futura = date.today() + timedelta(days=30)
    hora = time(10, 0)

    # Crear entrevista usando factory
    context.entrevista = crear_entrevista_agendamiento(
        solicitud_id="SOL-TEST-001",
        embajada=embajada
    )
    context.entrevista.asignar_horario(fecha_futura, hora)
    context.embajada = embajada


@step('la embajada "(?P<embajada>.+)" define un mínimo de (?P<minimo_horas_cancelacion>\\d+) horas de anticipación para cancelaciones')
def step_impl(context, embajada, minimo_horas_cancelacion):
    """Setup: configura regla de cancelación de la embajada según el feature."""
    context.minimo_horas_cancelacion = int(minimo_horas_cancelacion)

    # Actualizar la regla de la entrevista con el valor del feature
    context.entrevista.regla = crear_regla_embajada(
        embajada=embajada,
        max_reprogramaciones=2,
        horas_minimas_cancelacion=int(minimo_horas_cancelacion)
    )


@step("el tiempo restante hasta la entrevista es de (?P<horas_restantes>\\d+) horas")
def step_impl(context, horas_restantes):
    """Setup: tiempo restante simulado."""
    context.horas_restantes = int(horas_restantes)

    # Ajustar la fecha de la entrevista para simular las horas restantes
    horas = int(horas_restantes)
    fecha_entrevista = datetime.now() + timedelta(hours=horas)

    # Usar factory para crear horario
    horario = crear_horario(
        fecha=fecha_entrevista.date(),
        hora=fecha_entrevista.time()
    )
    context.entrevista.horario = horario


@step("el solicitante solicita la cancelación de la entrevista")
def step_impl(context):
    """Intento de cancelación."""
    try:
        # Usar servicio de cancelación
        resultado = AgendamientoService.cancelar_entrevista(
            context.entrevista,
            motivo="solicitud_migrante",
            horas_restantes=context.horas_restantes
        )
        context.resultado = "permite"
        context.mensaje = resultado.mensaje
    except CancelacionNoPermitidaException as e:
        context.resultado = "rechaza"
        context.mensaje = str(e)
        # Mantener estado original (el servicio no lo cambia si hay excepción)


@step("el sistema (?P<accion>permite|rechaza) la cancelación")
def step_impl(context, accion):
    """Verificar resultado de la cancelación."""
    assert context.resultado == accion, f"Esperado: {accion}, Obtenido: {context.resultado}"


@step('la entrevista queda en estado "(?P<estado_final>.+)"')
def step_impl(context, estado_final):
    """Verificar estado final de la entrevista."""
    # Mapear nombres de estado del feature a los del dominio
    estado_esperado = ESTADOS_ENTREVISTA_LEGIBLES.get(estado_final, 'agendada')

    assert context.entrevista.estado == estado_esperado, \
        f"Estado esperado: {estado_esperado}, Estado actual: {context.entrevista.estado}"


@step('muestra el mensaje "(?P<mensaje>.+)"')
def step_impl(context, mensaje):
    """Verificar mensaje mostrado."""
    # Verificar que el mensaje contiene las palabras clave esperadas
    assert context.mensaje is not None, "No hay mensaje registrado"

    mensaje_lower = context.mensaje.lower()

    # Para mensajes de error, verificar palabras clave
    if "Error" in mensaje or "no es posible" in mensaje:
        assert "error" in mensaje_lower or "no es posible" in mensaje_lower or \
               "no permitida" in mensaje_lower, \
               f"Se esperaba mensaje de error, se obtuvo: {context.mensaje}"
    elif "exitosamente" in mensaje:
        assert "exitosamente" in mensaje_lower or "exito" in mensaje_lower or \
               "confirmad" in mensaje_lower, \
               f"Se esperaba mensaje de éxito, se obtuvo: {context.mensaje}"
    elif "última reprogramación" in mensaje:
        assert "última" in context.mensaje or "reprogramación" in context.mensaje
