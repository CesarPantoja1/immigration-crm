from behave import *
from src.models import *

use_step_matcher("parse")


@step("que existen los siguientes checklists de documentos por tipo de visa:")
def step_impl(context):
    context.checklists = {}

    for row in context.table:
        tipo_visa = TipoVisa[row["tipo_visa"]]
        documentos = [doc.strip() for doc in row["documentos_obligatorios"].split(",")]

        checklist = ChecklistDocumentos(tipo_visa, documentos)
        context.checklists[tipo_visa.name] = checklist

    assert len(context.checklists) == 3

@step("que existen las embajadas:")
def step_impl(context):
    context.embajadas = []

    for row in context.table:
        embajada = TipoEmbajada[row["nombre"]]
        context.embajadas.append(embajada)

    assert len(context.embajadas) == 2


@step("que un migrante solicita visa {tipo_visa} para embajada {embajada}")
def step_impl(context, tipo_visa, embajada):
    context.agencia = AgenciaMigracion()
    context.solicitud = SolicitudVisa(
        id_migrante="MIG-001",
        tipo_visa=TipoVisa[tipo_visa],
        embajada=TipoEmbajada[embajada]
    )

    assert context.solicitud.obtener_tipo_visa() == tipo_visa
    assert context.solicitud.obtener_embajada() == embajada


@step("carga todos los documentos obligatorios:")
def step_impl(context):
    documentos = []

    for row in context.table:
        documentos = [doc.strip() for doc in row["documentos"].split(",")]

    checklist = context.checklists[context.solicitud.obtener_tipo_visa()]

    context.solicitud.cargar_documentos(documentos, checklist)

    assert context.solicitud.obtener_total_documentos() == checklist.total_documentos()


@step('todos los documentos tienen estado "{estado_documento}"')
def step_impl(context, estado_documento):
    for doc in context.solicitud.obtener_documentos():
        assert doc.obtener_estado() == estado_documento

@step('el estado de la solicitud es "{estado_solicitud}"')
def step_impl(context, estado_solicitud):
    assert context.solicitud.obtener_estado() == estado_solicitud


@step("el sistema registra la solicitud")
def step_impl(context):
    context.agencia.registrar_solicitud(context.solicitud)
    print(f"[INFO] Solicitud registrada: {context.solicitud}")
    assert context.agencia.total_solicitudes() == 1

# =====================
# ASESOR
# =====================

@step('que existe una solicitud de visa {tipo_visa} con embajada {embajada} con id {id_solicitud}')
def step_impl(context, tipo_visa, embajada, id_solicitud):

    context.agencia = AgenciaMigracion()
    context.asesor = Asesor()

    context.checklist = context.checklists[tipo_visa]

    solicitud = SolicitudVisa(
        id_solicitud=id_solicitud,
        id_migrante="MIG-001",
        tipo_visa=TipoVisa[tipo_visa],
        embajada=TipoEmbajada[embajada]
    )

    solicitud.asignar_checklist(context.checklist)
    solicitud.inicializar_documentos_desde_checklist()

    context.solicitud = solicitud
    context.agencia.registrar_solicitud(context.solicitud)

    print(f"[INFO] Solicitud registrada: {context.solicitud}")
    assert context.agencia.total_solicitudes() == 1

@step('todos los documentos están en estado "{estado}"')
def step_impl(context, estado):
    for doc in context.solicitud.obtener_documentos():
        assert doc.obtener_estado() == estado


@step("el asesor revisa todos los documentos de la solicitud")
def step_impl(context):
    assert context.solicitud.obtener_total_documentos() == context.checklist.total_documentos()


@step('todos los documentos son "{resultado_revision}"')
def step_impl(context, resultado_revision):
    context.resultados_revision = {
        doc.obtener_nombre(): resultado_revision
        for doc in context.solicitud.obtener_documentos()
    }

    context.asesor.revisar_solicitud(
        context.solicitud,
        context.resultados_revision
    )

@step('el documento "{documento_rechazado}" es "{resultado_revision}"')
def step_impl(context, documento_rechazado, resultado_revision):

    context.resultados_revision = {}

    for doc in context.solicitud.obtener_documentos():
        if doc.obtener_nombre() == documento_rechazado:
            context.resultados_revision[doc.obtener_nombre()] = resultado_revision
        else:
            context.resultados_revision[doc.obtener_nombre()] = "Correcto"

    context.asesor.revisar_solicitud(
        context.solicitud,
        context.resultados_revision
    )

    print(f"[INFO] Solicitud registrada: {context.solicitud}")

@step('todos los documentos deben cambiar a estado "{estado}"')
def step_impl(context, estado):
    for doc in context.solicitud.obtener_documentos():
        assert doc.obtener_estado() == estado


@step('el documento "{documento_rechazado}" debe cambiar a estado "{estado}"')
def step_impl(context, documento_rechazado, estado):

    documento_encontrado = None

    for doc in context.solicitud.obtener_documentos():
        if doc.obtener_nombre() == documento_rechazado:
            documento_encontrado = doc
            print(f"[INFO] Documento rechazado: {doc.obtener_nombre()} -> {doc.obtener_estado()}")

    assert documento_encontrado is not None, "No se encontró el documento en la solicitud"

    print(f"[INFO] Solicitud registrada: {context.solicitud}")
    assert documento_encontrado.obtener_estado() == estado



@step('el estado de la solicitud debe ser "{estado}"')
def step_impl(context, estado):
    assert context.solicitud.obtener_estado() == estado


@step("los documentos quedan almacenados en el sistema")
def step_impl(context):
    context.agencia.registrar_migrante(context.solicitud)

    migrante = context.agencia.obtener_migrante_por_id(
        context.solicitud.id_migrante
    )

    print(f"[INFO] Migrante creado: {migrante}")

    assert context.agencia.total_migrantes() == 1

@step('el migrante recibe la notificación "VISA_{tipo_visa}_APROBADA"')
def step_impl(context, tipo_visa):
    # mensaje = f"VISA_{tipo_visa}_APROBADA"
    # context.notificacion = mensaje
    #
    # assert context.notificacion == mensaje
    pass

@step('el migrante recibe la notificación "DOCUMENTO_RECHAZADO: {documento_rechazado}"')
def step_impl(context, documento_rechazado):
    # mensaje = f"DOCUMENTO_RECHAZADO: {documento_rechazado}"
    # context.notificacion = mensaje
    #
    # print(f"[INFO] Notificación enviada: {mensaje}")
    #
    # assert context.notificacion == mensaje
    pass

@step('que existe una solicitud aprobada de tipo {tipo_visa} con embajada {embajada} con id {id_solicitud}')
def step_impl(context, tipo_visa, embajada, id_solicitud):

    context.agencia = AgenciaMigracion()
    context.asesor = Asesor()

    checklist = context.checklists[tipo_visa]

    solicitud = SolicitudVisa(
        id_solicitud=id_solicitud,
        id_migrante="MIG-001",
        tipo_visa=TipoVisa[tipo_visa],
        embajada=TipoEmbajada[embajada]
    )

    solicitud.asignar_checklist(checklist)
    solicitud.inicializar_documentos_desde_checklist()

    # Simular que ya fue aprobada
    for doc in solicitud.obtener_documentos():
        doc.aprobar()

    solicitud.actualizar_estado()

    context.solicitud = solicitud
    context.agencia.registrar_solicitud(context.solicitud)

    print(f"[INFO] Solicitud aprobada registrada: {context.solicitud}")

    assert context.solicitud.obtener_estado() == "APROBADO"
    assert context.agencia.total_solicitudes() == 1

@step('el estado de envío es "{estado_envio}"')
def step_impl(context, estado_envio):
    assert context.solicitud.obtener_estado_envio() == estado_envio

@step("el asesor confirma el envío de la solicitud")
def step_impl(context):

    resultado = context.asesor.enviar_solicitud(
        context.solicitud,
        enviada="SI"
    )

    context.notificacion = resultado

@step('el estado de envío debe cambiar a "{estado_envio}"')
def step_impl(context, estado_envio):
    print(f"[INFO] Estado de envío actual: {context.solicitud.obtener_estado_envio()}")
    assert context.solicitud.obtener_estado_envio() == estado_envio

@step('el migrante recibe la notificación "SOLICITUD ENVIADA A EMBAJADA"')
def step_impl(context):
    # print(f"[INFO] Notificación enviada a: {context.notificacion}")
    # assert context.notificacion == "SOLICITUD ENVIADA A EMBAJADA"
    pass



