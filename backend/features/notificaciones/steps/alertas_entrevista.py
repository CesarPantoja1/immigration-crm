from behave import step, use_step_matcher

from app.models import SistemaMigratorio


use_step_matcher("parse")


@step("que soy un solicitante autenticado en el sistema de gestión migratoria")
def paso_solicitante_autenticado(context):
    context.sistema = SistemaMigratorio()
    context.sistema.autenticar_solicitante()
    assert context.sistema.solicitante_autenticado is True


@step('que gestiono la solicitud "{id_solicitud}" en estado "{estado}"')
def paso_gestiona_solicitud(context, id_solicitud, estado):
    context.sistema.establecer_solicitud(id_solicitud, estado)
    assert context.sistema.solicitudes[id_solicitud].estado == estado


@step('tengo asignado al asesor "{asesor}"')
def paso_asignar_asesor(context, asesor):
    for id_solicitud in context.sistema.solicitudes:
        context.sistema.asignar_asesor_a_solicitud(id_solicitud, asesor)
        assert context.sistema.solicitudes[id_solicitud].asesor == asesor


@step("el catálogo de tipos de notificación incluye:")
def paso_catalogo_notificaciones(context):
    tipos = [row["tipo"] for row in context.table]
    context.sistema.establecer_tipos_notificacion(tipos)
    assert len(context.sistema.tipos_notificacion) == len(tipos)


@step("el sistema tiene configuradas ventanas de recordatorio de entrevista:")
def paso_ventanas_recordatorio(context):
    ventanas = [row["ventana"] for row in context.table]
    context.sistema.establecer_ventanas_recordatorio(ventanas)
    assert len(context.sistema.ventanas_recordatorio) == len(ventanas)


@step("el sistema tiene configurada una ventana de control de preparación:")
def paso_ventanas_preparacion(context):
    ventanas = [row["ventana"] for row in context.table]
    context.sistema.establecer_ventanas_preparacion(ventanas)
    assert len(context.sistema.ventanas_preparacion) == len(ventanas)


@step('que la solicitud "{id_solicitud}" no tiene entrevista registrada')
def paso_solicitud_sin_entrevista(context, id_solicitud):
    context.sistema.limpiar_entrevista(id_solicitud)
    assert context.sistema.solicitudes[id_solicitud].entrevista is None


@step('el asesor "{asesor}" registra una entrevista para "{id_solicitud}" en "{fecha_hora}"')
def paso_registra_entrevista(context, asesor, id_solicitud, fecha_hora):
    context.sistema.registrar_entrevista(id_solicitud, fecha_hora, asesor)
    assert context.sistema.solicitudes[id_solicitud].entrevista is not None


@step("en el centro de notificaciones del migrante aparece una notificación nueva con:")
def paso_notificacion_migrante(context):
    esperado = {heading: context.table[0][heading] for heading in context.table.headings}
    notificacion = context.sistema.notificaciones_migrante.buscar_coincidencia(esperado)
    assert notificacion is not None, f"No se encontró notificación: {esperado}"


@step("en el centro de notificaciones del asesor aparece una notificación nueva con:")
def paso_notificacion_asesor(context):
    esperado = {heading: context.table[0][heading] for heading in context.table.headings}
    notificacion = context.sistema.notificaciones_asesor.buscar_coincidencia(esperado)
    assert notificacion is not None, f"No se encontró notificación: {esperado}"


@step('la notificación queda asociada a la solicitud "{id_solicitud}" al abrir su detalle')
def paso_notificacion_asociada(context, id_solicitud):
    notificacion = context.sistema.notificaciones_migrante.ultima()
    assert notificacion is not None, "No hay notificaciones"
    assert notificacion.id_solicitud == id_solicitud


@step('que la solicitud "{id_solicitud}" tiene una entrevista "{estado}" para "{fecha_hora}"')
def paso_entrevista_programada(context, id_solicitud, estado, fecha_hora):
    context.sistema.establecer_entrevista(id_solicitud, estado, fecha_hora)
    entrevista = context.sistema.solicitudes[id_solicitud].entrevista
    assert entrevista is not None


@step('la fecha y hora actual del sistema es "{fecha_hora}"')
def paso_fecha_actual(context, fecha_hora):
    context.sistema.establecer_fecha_hora_actual(fecha_hora)
    assert context.sistema.fecha_hora_actual is not None


@step('el sistema evalúa recordatorios configurados para la entrevista de "{id_solicitud}"')
def paso_evalua_recordatorios(context, id_solicitud):
    context.indice_notificaciones_migrante = context.sistema.notificaciones_migrante.total()
    context.sistema.evaluar_recordatorios(id_solicitud)


@step('el detalle de la notificación es "{detalle}"')
def paso_detalle_notificacion(context, detalle):
    notificacion = context.sistema.notificaciones_migrante.ultima()
    assert notificacion is not None, "No hay notificaciones"
    assert notificacion.detalle == detalle


@step('el asesor "{asesor}" reprograma la entrevista de "{id_solicitud}" a "{fecha_hora}"')
def paso_reprograma_entrevista(context, asesor, id_solicitud, fecha_hora):
    context.sistema.reprogramar_entrevista(id_solicitud, fecha_hora, asesor)
    entrevista = context.sistema.solicitudes[id_solicitud].entrevista
    assert entrevista is not None
    assert entrevista.estado == "Reprogramada"


@step('previamente estuvo "{estado}" para "{fecha_hora}"')
def paso_entrevista_anterior(context, estado, fecha_hora):
    for id_solicitud in context.sistema.solicitudes:
        context.sistema.establecer_entrevista_anterior(id_solicitud, estado, fecha_hora)


@step('no aparece ninguna notificación nueva de tipo "{tipo}" asociada a "{fecha_hora}"')
def paso_sin_notificacion_tipo_fecha(context, tipo, fecha_hora):
    nuevas = context.sistema.notificaciones_migrante.nuevas_desde(
        context.indice_notificaciones_migrante
    )
    coincidencias = [
        item
        for item in nuevas
        if item.tipo == tipo and item.fecha_hora_entrevista == fecha_hora
    ]
    assert not coincidencias, f"Se encontraron notificaciones inesperadas: {coincidencias}"


@step('el contador de notificaciones de tipo "{tipo}" para la solicitud "{id_solicitud}" no aumenta')
def paso_contador_tipo_no_aumenta(context, tipo, id_solicitud):
    notificaciones = context.sistema.notificaciones_migrante.notificaciones
    previas = sum(
        1
        for item in notificaciones[: context.indice_notificaciones_migrante]
        if item.tipo == tipo and item.id_solicitud == id_solicitud
    )
    actuales = sum(
        1
        for item in notificaciones
        if item.tipo == tipo and item.id_solicitud == id_solicitud
    )
    assert actuales == previas


@step('el asesor "{asesor}" cancela la entrevista de "{id_solicitud}"')
def paso_cancela_entrevista(context, asesor, id_solicitud):
    context.sistema.cancelar_entrevista(id_solicitud, asesor)
    entrevista = context.sistema.solicitudes[id_solicitud].entrevista
    assert entrevista is not None
    assert entrevista.estado == "Cancelada"


@step('que la solicitud "{id_solicitud}" tiene una entrevista en estado "{estado}"')
def paso_entrevista_estado(context, id_solicitud, estado):
    context.sistema.establecer_estado_entrevista(id_solicitud, estado)
    entrevista = context.sistema.solicitudes[id_solicitud].entrevista
    assert entrevista is not None
    assert entrevista.estado == estado


@step('la entrevista cancelada correspondía a "{fecha_hora}"')
def paso_entrevista_cancelada_fecha(context, fecha_hora):
    for id_solicitud in context.sistema.solicitudes:
        context.sistema.establecer_fecha_entrevista(id_solicitud, fecha_hora)


@step('no aparece ninguna notificación nueva de tipo "{tipo}"')
def paso_sin_notificacion_tipo(context, tipo):
    nuevas = context.sistema.notificaciones_migrante.nuevas_desde(
        context.indice_notificaciones_migrante
    )
    coincidencias = [item for item in nuevas if item.tipo == tipo]
    assert not coincidencias, f"Se encontraron notificaciones inesperadas: {coincidencias}"


@step('el contador de notificaciones no aumenta para la solicitud "{id_solicitud}"')
def paso_contador_no_aumenta(context, id_solicitud):
    notificaciones = context.sistema.notificaciones_migrante.notificaciones
    previas = sum(
        1
        for item in notificaciones[: context.indice_notificaciones_migrante]
        if item.id_solicitud == id_solicitud
    )
    actuales = sum(1 for item in notificaciones if item.id_solicitud == id_solicitud)
    assert actuales == previas


@step('no existe un simulacro en estado "{estado}" asociado a "{id_solicitud}"')
def paso_sin_simulacro_confirmado(context, estado, id_solicitud):
    context.sistema.asegurar_sin_simulacro_en_estado(id_solicitud, estado)


@step('el sistema evalúa el estado de preparación para la entrevista de "{id_solicitud}"')
def paso_evalua_preparacion(context, id_solicitud):
    context.indice_notificaciones_migrante = context.sistema.notificaciones_migrante.total()
    context.sistema.evaluar_preparacion(id_solicitud)


@step('el asesor "{asesor}" está autenticado en el sistema')
def paso_asesor_autenticado(context, asesor):
    context.sistema = SistemaMigratorio()
    context.sistema.autenticar_asesor(asesor)
    assert context.sistema.asesor_autenticado is True


@step('existe un simulacro "{id_simulacro}" asociado a la solicitud "{id_solicitud}"')
def paso_existe_simulacro(context, id_simulacro, id_solicitud):
    context.sistema.crear_simulacro(id_simulacro, id_solicitud)
    assert id_simulacro in context.sistema.simulacros


@step('el simulacro "{id_simulacro}" está en estado "{estado}"')
def paso_simulacro_estado(context, id_simulacro, estado):
    context.sistema.establecer_estado_simulacro(id_simulacro, estado)
    assert context.sistema.simulacros[id_simulacro].estado == estado


@step('el simulacro "{id_simulacro}" cambia a estado "{estado}"')
def paso_simulacro_cambia(context, id_simulacro, estado):
    context.sistema.actualizar_estado_simulacro(id_simulacro, estado)


@step('existe un documento de recomendaciones para el simulacro "{id_simulacro}" en estado "{estado}"')
def paso_documento_recomendaciones(context, id_simulacro, estado):
    context.sistema.crear_recomendaciones(id_simulacro, estado)
    assert id_simulacro in context.sistema.recomendaciones


@step('el documento de recomendaciones del simulacro "{id_simulacro}" se publica en el sistema')
def paso_publica_recomendaciones(context, id_simulacro):
    context.sistema.publicar_recomendaciones(id_simulacro)
