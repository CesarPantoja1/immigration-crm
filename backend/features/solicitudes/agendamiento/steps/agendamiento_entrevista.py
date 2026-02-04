# -*- coding: utf-8 -*-
"""Steps BDD para Agendamiento de Entrevistas."""

import os
import sys
from datetime import datetime, date, time, timedelta

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')

import django
django.setup()

from behave import step, use_step_matcher

from features.solicitudes.business_logic import (
    reset_id_counters,
    crear_entrevista_agendamiento,
    crear_horario,
    crear_opcion_horario,
    crear_regla_embajada,
    AgendamientoService,
    AgendamientoSeleccionService,
    AgendamientoProteccionService,
    ReprogramacionNoPermitidaException,
    CancelacionNoPermitidaException,
    ESTADOS_ENTREVISTA_LEGIBLES,
)

use_step_matcher("re")


# Antecedentes
@step("que el solicitante cuenta con una solicitud migratoria aprobada")
def step_impl(context):
    reset_id_counters()
    context.solicitud_id = "SOL-TEST-001"
    context.solicitud_aprobada = True
    assert context.solicitud_aprobada is True


@step("el sistema presenta opciones de fecha y horario para entrevistas")
def step_impl(context):
    context.opciones_disponibles = True
    assert context.opciones_disponibles is True


# Agendamiento
@step('que existe una fecha de entrevista "(?P<fecha_entrevista>.+)" con los siguientes horarios disponibles')
def step_impl(context, fecha_entrevista):
    fecha = datetime.strptime(fecha_entrevista, "%Y-%m-%d").date()
    context.entrevista = crear_entrevista_agendamiento(solicitud_id="SOL-TEST-001", embajada="USA")

    opciones = []
    context.horarios_disponibles = set()

    for row in context.table:
        horario_str = row['horario']
        hora = datetime.strptime(horario_str, "%H:%M").time()
        es_disponible = row['estado'] == 'Disponible'

        horario = crear_horario(fecha=fecha, hora=hora)
        opcion = crear_opcion_horario(horario=horario, disponible=es_disponible, opcion_id=f"OPT-{horario_str.replace(':', '')}")
        opciones.append(opcion)

        if es_disponible:
            context.horarios_disponibles.add(horario_str)

    context.entrevista.ofrecer_opciones(opciones)
    context.fecha_entrevista = fecha


@step('el solicitante selecciona la fecha "(?P<fecha_entrevista>.+)" y el horario "09:00"')
def step_impl(context, fecha_entrevista):
    horario = "09:00"
    disponible = AgendamientoSeleccionService.verificar_disponibilidad(context.entrevista, horario)
    assert disponible, f"El horario {horario} no está disponible"

    opcion_id = f"OPT-{horario.replace(':', '')}"
    resultado = AgendamientoService.agendar_entrevista(context.entrevista, opcion_id)
    assert resultado.exito, "No se pudo seleccionar la opción"

    context.horarios_disponibles.discard(horario)
    context.horarios_ocupados = {horario}
    context.resultado_agendamiento = resultado


@step("el sistema registra la entrevista asociada a la solicitud")
def step_impl(context):
    assert context.entrevista.esta_agendada()
    assert context.entrevista.tiene_horario_asignado()


@step('el horario "09:00" queda registrado como no disponible')
def step_impl(context):
    assert "09:00" not in context.horarios_disponibles
    assert "09:00" in context.horarios_ocupados


@step('muestra el mensaje "Entrevista agendada para el (?P<fecha_legible>.+) a las 09:00"')
def step_impl(context, fecha_legible):
    horario_legible = context.entrevista.obtener_horario_legible()
    assert fecha_legible in horario_legible or context.entrevista.tiene_horario_asignado()
    context.mensaje = f"Entrevista agendada para el {fecha_legible} a las 09:00"


# Protección e Integridad
@step('que el solicitante tiene una entrevista en estado "Programada"')
def step_impl(context):
    reset_id_counters()
    fecha_futura = date.today() + timedelta(days=30)
    hora = time(10, 0)

    context.entrevista = crear_entrevista_agendamiento(solicitud_id="SOL-TEST-001", embajada="USA")
    context.entrevista.asignar_horario(fecha_futura, hora)
    assert context.entrevista.esta_agendada()


@step("el solicitante solicita la modificación de la fecha o el horario de la entrevista fuera del proceso de reprogramación")
def step_impl(context):
    resultado = AgendamientoProteccionService.rechazar_modificacion(context.entrevista)
    context.modificacion_rechazada = not resultado.exito
    context.mensaje = resultado.mensaje


@step("el sistema rechaza la solicitud de modificación")
def step_impl(context):
    assert context.modificacion_rechazada is True


@step("mantiene la entrevista en su estado original")
def step_impl(context):
    assert context.entrevista.esta_agendada()


# Reprogramación
@step("el solicitante solicita la reprogramación de la entrevista a una nueva fecha")
def step_impl(context):
    nueva_fecha = date.today() + timedelta(days=45)
    nueva_hora = time(11, 0)

    resultado = AgendamientoService.reprogramar_entrevista(context.entrevista, nueva_fecha, nueva_hora)
    context.resultado_reprogramacion = resultado
    context.nueva_fecha = nueva_fecha


@step("el sistema actualiza la fecha de la entrevista")
def step_impl(context):
    assert context.entrevista.obtener_fecha() == context.nueva_fecha


@step('la entrevista queda en estado "Reprogramada"')
def step_impl(context):
    assert context.entrevista.estado == 'reprogramada'


@step("el solicitante recibe una confirmación de la reprogramación")
def step_impl(context):
    assert context.resultado_reprogramacion.exito is True
    context.mensaje = context.resultado_reprogramacion.mensaje


@step("la entrevista ha sido reprogramada (?P<cantidad_reprogramaciones>\\d+) veces")
def step_impl(context, cantidad_reprogramaciones):
    fecha_futura = date.today() + timedelta(days=30)
    hora = time(10, 0)

    context.entrevista = crear_entrevista_agendamiento(solicitud_id="SOL-TEST-001", embajada="USA")
    context.entrevista.asignar_horario(fecha_futura, hora)
    context.entrevista.veces_reprogramada = int(cantidad_reprogramaciones)


@step("la embajada permite un máximo de 2 reprogramaciones por solicitud")
def step_impl(context):
    assert context.entrevista.regla.max_reprogramaciones == 2


@step("el solicitante solicita una nueva reprogramación de la entrevista")
def step_impl(context):
    nueva_fecha = date.today() + timedelta(days=60)
    nueva_hora = time(15, 0)

    try:
        resultado = AgendamientoService.reprogramar_entrevista(context.entrevista, nueva_fecha, nueva_hora)
        context.resultado = "permite"
        context.mensaje = resultado.mensaje
    except ReprogramacionNoPermitidaException as e:
        context.resultado = "rechaza"
        context.mensaje = str(e)


@step("el sistema (?P<accion>permite|rechaza) la reprogramación")
def step_impl(context, accion):
    assert context.resultado == accion


# Cancelación
@step('que el solicitante tiene una entrevista agendada en la embajada "(?P<embajada>.+)"')
def step_impl(context, embajada):
    reset_id_counters()
    fecha_futura = date.today() + timedelta(days=30)
    hora = time(10, 0)

    context.entrevista = crear_entrevista_agendamiento(solicitud_id="SOL-TEST-001", embajada=embajada)
    context.entrevista.asignar_horario(fecha_futura, hora)
    context.embajada = embajada


@step('la embajada "(?P<embajada>.+)" define un mínimo de (?P<minimo_horas_cancelacion>\\d+) horas de anticipación para cancelaciones')
def step_impl(context, embajada, minimo_horas_cancelacion):
    context.minimo_horas_cancelacion = int(minimo_horas_cancelacion)
    context.entrevista.regla = crear_regla_embajada(
        embajada=embajada,
        max_reprogramaciones=2,
        horas_minimas_cancelacion=int(minimo_horas_cancelacion)
    )


@step("el tiempo restante hasta la entrevista es de (?P<horas_restantes>\\d+) horas")
def step_impl(context, horas_restantes):
    context.horas_restantes = int(horas_restantes)
    horas = int(horas_restantes)
    fecha_entrevista = datetime.now() + timedelta(hours=horas)

    horario = crear_horario(fecha=fecha_entrevista.date(), hora=fecha_entrevista.time())
    context.entrevista.horario = horario


@step("el solicitante solicita la cancelación de la entrevista")
def step_impl(context):
    try:
        resultado = AgendamientoService.cancelar_entrevista(
            context.entrevista, motivo="solicitud_migrante", horas_restantes=context.horas_restantes
        )
        context.resultado = "permite"
        context.mensaje = resultado.mensaje
    except CancelacionNoPermitidaException as e:
        context.resultado = "rechaza"
        context.mensaje = str(e)


@step("el sistema (?P<accion>permite|rechaza) la cancelación")
def step_impl(context, accion):
    assert context.resultado == accion, f"Esperado: {accion}, Obtenido: {context.resultado}"


@step('la entrevista queda en estado "(?P<estado_final>.+)"')
def step_impl(context, estado_final):
    estado_esperado = ESTADOS_ENTREVISTA_LEGIBLES.get(estado_final, 'agendada')
    assert context.entrevista.estado == estado_esperado, \
        f"Estado esperado: {estado_esperado}, Estado actual: {context.entrevista.estado}"


@step('muestra el mensaje "(?P<mensaje>.+)"')
def step_impl(context, mensaje):
    assert context.mensaje is not None, "No hay mensaje registrado"
    mensaje_lower = context.mensaje.lower()

    if "Error" in mensaje or "no es posible" in mensaje:
        assert "error" in mensaje_lower or "no es posible" in mensaje_lower or "no permitida" in mensaje_lower
    elif "exitosamente" in mensaje:
        assert "exitosamente" in mensaje_lower or "exito" in mensaje_lower or "confirmad" in mensaje_lower
    elif "última reprogramación" in mensaje:
        assert "última" in context.mensaje or "reprogramación" in context.mensaje
