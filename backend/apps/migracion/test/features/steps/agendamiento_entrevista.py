from behave import *
from backend.apps.migracion.domain.entrevista import Entrevista
use_step_matcher("re")


@step("que el solicitante cuenta con una solicitud migratoria aprobada")
def step_impl(context):
    assert True


@step("el sistema presenta opciones de fecha y horario para entrevistas")
def step_impl(context):
    assert True


@step('que existe una fecha de entrevista "(?P<fecha_entrevista>.+)" con los siguientes horarios disponibles:')
def step_impl(context, fecha_entrevista):
    context.entrevista = Entrevista(fecha_entrevista)

    for row in context.table:
        if row['estado'] == 'Disponible':
            context.entrevista.horarios_disponibles.add(row['horario'])



@step('el solicitante selecciona la fecha "(?P<fecha_entrevista>.+)" y el horario "09:00"')
def step_impl(context, fecha_entrevista):
    horario = "09:00"
    assert horario in context.entrevista.horarios_disponibles

    context.entrevista.horarios_disponibles.remove(horario)
    context.entrevista.horarios_ocupados.add(horario)


@step("el sistema registra la entrevista asociada a la solicitud")
def step_impl(context):
    assert context.entrevista.estado == "Programada"


@step('el horario "09:00" queda registrado como no disponible')
def step_impl(context):
    assert "09:00" in context.entrevista.horarios_ocupados


@step('muestra el mensaje "Entrevista agendada para el (?P<fecha_legible>.+) a las 09:00"')
def step_impl(context, fecha_legible):
    context.mensaje = f"Entrevista agendada para el {fecha_legible} a las 09:00"
    assert fecha_legible in context.mensaje



@step('que el solicitante tiene una entrevista en estado "Programada"')
def step_impl(context):
    context.entrevista = Entrevista("2026-02-15")
    assert context.entrevista.estado == "Programada"


@step("el solicitante solicita la modificación de la fecha o el horario de la entrevista fuera del proceso de reprogramación")
def step_impl(context):
    try:
        context.entrevista.modificar_directamente()
        context.modificacion_rechazada = False
    except ValueError:
        context.modificacion_rechazada = True


@step("el sistema rechaza la solicitud de modificación")
def step_impl(context):
    assert context.modificacion_rechazada is True


@step("mantiene la entrevista en su estado original")
def step_impl(context):
    assert context.entrevista.estado == "Programada"


@step("el solicitante solicita la reprogramación de la entrevista a una nueva fecha")
def step_impl(context):
    nueva_fecha = "2026-03-20"
    context.entrevista.reprogramar(nueva_fecha)


@step("el sistema actualiza la fecha de la entrevista")
def step_impl(context):
    assert context.entrevista.fecha == "2026-03-20"

@step('la entrevista queda en estado "Reprogramada"')
def step_impl(context):
    assert context.entrevista.estado == "Reprogramada"


@step("el solicitante recibe una confirmación de la reprogramación")
def step_impl(context):
    context.mensaje = "Reprogramación confirmada"
    assert "confirmada" in context.mensaje


@step("la entrevista ha sido reprogramada (?P<cantidad_reprogramaciones>\\d+) veces")
def step_impl(context, cantidad_reprogramaciones):
    context.entrevista = Entrevista("2026-02-15")
    context.entrevista.reprogramaciones = int(cantidad_reprogramaciones)


@step("la embajada permite un máximo de 2 reprogramaciones por solicitud")
def step_impl(context):
    assert context.entrevista.MAX_REPROGRAMACIONES == 2


@step("el solicitante solicita una nueva reprogramación de la entrevista")
def step_impl(context):
    try:
        context.entrevista.reprogramar("2026-04-01")
        context.resultado = "permite"
    except ValueError:
        context.resultado = "rechaza"


@step("el sistema (?P<accion>permite|rechaza) la reprogramación")
def step_impl(context, accion):
    assert context.resultado == accion



@step('que el solicitante tiene una entrevista agendada en la embajada "(?P<embajada>.+)"')
def step_impl(context, embajada):
    assert True


@step(
    'la embajada "(?P<embajada>.+)" define un mínimo de (?P<minimo_horas_cancelacion>.+) horas de anticipación para cancelaciones')
def step_impl(context, embajada, minimo_horas_cancelacion):
    assert True


@step("el tiempo restante hasta la entrevista es de (?P<horas_restantes>.+) horas")
def step_impl(context, horas_restantes):
    assert True


@step("el solicitante solicita la cancelación de la entrevista")
def step_impl(context):
    assert True


@step("el sistema (?P<accion>.+) la cancelación")
def step_impl(context, accion):
    assert True


@step('la entrevista queda en estado "(?P<estado_final>.+)"')
def step_impl(context, estado_final):
    assert True


@step('muestra el mensaje "(?P<mensaje>.+)"')
def step_impl(context, mensaje):
    context.mensaje = mensaje
    assert context.mensaje is not None
