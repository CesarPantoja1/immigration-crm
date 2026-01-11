from behave import *
use_step_matcher("re")


@step("que el solicitante cuenta con una solicitud migratoria aprobada")
def step_impl(context):
    assert True


@step("el sistema presenta opciones de fecha y horario para entrevistas")
def step_impl(context):
    assert True


@step('que existe una fecha de entrevista "(?P<fecha_entrevista>.+)" con los siguientes horarios disponibles:')
def step_impl(context, fecha_entrevista):
    # La tabla se accede con context.table
    assert True


@step('el solicitante selecciona la fecha "(?P<fecha_entrevista>.+)" y el horario "09:00"')
def step_impl(context, fecha_entrevista):
    assert True


@step("el sistema registra la entrevista asociada a la solicitud")
def step_impl(context):
    assert True


@step('el horario "09:00" queda registrado como no disponible')
def step_impl(context):
    assert True


@step('muestra el mensaje "Entrevista agendada para el (?P<fecha_legible>.+) a las 09:00"')
def step_impl(context, fecha_legible):
    assert True


@step('que el solicitante tiene una entrevista en estado "Programada"')
def step_impl(context):
    assert True


@step(
    "el solicitante solicita la modificación de la fecha o el horario de la entrevista fuera del proceso de reprogramación")
def step_impl(context):
    assert True


@step("el sistema rechaza la solicitud de modificación")
def step_impl(context):
    assert True


@step("mantiene la entrevista en su estado original")
def step_impl(context):
    assert True


@step("el solicitante solicita la reprogramación de la entrevista a una nueva fecha")
def step_impl(context):
    assert True


@step("el sistema actualiza la fecha de la entrevista")
def step_impl(context):
    assert True


@step('la entrevista queda en estado "Reprogramada"')
def step_impl(context):
    assert True


@step("el solicitante recibe una confirmación de la reprogramación")
def step_impl(context):
    assert True


@step("la entrevista ha sido reprogramada (?P<cantidad_reprogramaciones>.+) veces")
def step_impl(context, cantidad_reprogramaciones):
    assert True


@step("la embajada permite un máximo de 2 reprogramaciones por solicitud")
def step_impl(context):
    assert True


@step("el solicitante solicita una nueva reprogramación de la entrevista")
def step_impl(context):
    assert True


@step("el sistema (?P<accion>.+) la reprogramación")
def step_impl(context, accion):
    assert True


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
    assert True
