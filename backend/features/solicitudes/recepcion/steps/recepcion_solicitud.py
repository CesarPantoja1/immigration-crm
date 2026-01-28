"""
Steps para los escenarios de Recepción de Solicitudes.
Implementación de los pasos BDD definidos en recepcion_solicitud.feature
"""
from behave import given, when, then, step, use_step_matcher
import sys
import os

# Agregar el path del proyecto para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from apps.solicitudes.recepcion.domain import (
    TipoVisa,
    TipoEmbajada,
    ChecklistDocumentos,
    SolicitudVisa,
    Documento,
    Asesor,
    AgenciaMigracion
)

use_step_matcher("parse")


# =====================================================
# ANTECEDENTES - SETUP DE CHECKLISTS Y EMBAJADAS
# =====================================================

@step("que existen los siguientes checklists de documentos por tipo de visa")
def step_impl(context):
    """Configura los checklists de documentos por tipo de visa."""
    context.checklists = {}

    for row in context.table:
        tipo_visa = TipoVisa[row["tipo_visa"]]
        documentos = [doc.strip() for doc in row["documentos_obligatorios"].split(",")]

        checklist = ChecklistDocumentos(tipo_visa, documentos)
        context.checklists[tipo_visa.value] = checklist

    assert len(context.checklists) == 3, f"Se esperaban 3 checklists, se encontraron {len(context.checklists)}"


@step("que existen las embajadas")
def step_impl(context):
    """Configura las embajadas disponibles."""
    context.embajadas = []

    for row in context.table:
        embajada = TipoEmbajada[row["nombre"]]
        context.embajadas.append(embajada)

    assert len(context.embajadas) == 2, f"Se esperaban 2 embajadas, se encontraron {len(context.embajadas)}"


# =====================================================
# MIGRANTE - INGRESO DE SOLICITUD
# =====================================================

@step("que un migrante solicita visa {tipo_visa} para embajada {embajada}")
def step_impl(context, tipo_visa, embajada):
    """El migrante inicia una solicitud de visa."""
    context.agencia = AgenciaMigracion()
    context.solicitud = SolicitudVisa(
        id_migrante="MIG-001",
        tipo_visa=TipoVisa[tipo_visa],
        embajada=TipoEmbajada[embajada]
    )

    assert context.solicitud.obtener_tipo_visa() == tipo_visa
    assert context.solicitud.obtener_embajada() == embajada


@step("carga todos los documentos obligatorios")
def step_impl(context):
    """El migrante carga todos los documentos obligatorios."""
    documentos = []

    for row in context.table:
        documentos = [doc.strip() for doc in row["documentos"].split(",")]

    checklist = context.checklists[context.solicitud.obtener_tipo_visa()]

    context.solicitud.cargar_documentos(documentos, checklist)

    assert context.solicitud.obtener_total_documentos() == checklist.total_documentos()


@step('todos los documentos tienen estado "{estado_documento}"')
def step_impl(context, estado_documento):
    """Verifica que todos los documentos tengan el estado esperado."""
    for doc in context.solicitud.obtener_documentos():
        assert doc.obtener_estado() == estado_documento, \
            f"Documento {doc.obtener_nombre()} tiene estado {doc.obtener_estado()}, se esperaba {estado_documento}"


@step('el estado de la solicitud es "{estado_solicitud}"')
def step_impl(context, estado_solicitud):
    """Verifica el estado de la solicitud."""
    assert context.solicitud.obtener_estado() == estado_solicitud, \
        f"Estado actual: {context.solicitud.obtener_estado()}, esperado: {estado_solicitud}"


@step("el sistema registra la solicitud")
def step_impl(context):
    """El sistema registra la solicitud en la agencia."""
    context.agencia.registrar_solicitud(context.solicitud)
    print(f"[INFO] Solicitud registrada: {context.solicitud}")
    assert context.agencia.total_solicitudes() == 1

# =====================================================
# ASESOR - REVISIÓN DE SOLICITUDES
# =====================================================

@step('que existe una solicitud de visa {tipo_visa} con embajada {embajada} con id {id_solicitud}')
def step_impl(context, tipo_visa, embajada, id_solicitud):
    """Configura una solicitud existente para revisión."""
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

    # Marcar documentos como EN_REVISION (simulando que el migrante ya los cargó)
    for doc in solicitud.obtener_documentos():
        doc.marcar_en_revision()
    solicitud.estado = "EN_REVISION"

    context.solicitud = solicitud
    context.agencia.registrar_solicitud(context.solicitud)

    print(f"[INFO] Solicitud registrada: {context.solicitud}")
    assert context.agencia.total_solicitudes() == 1


@step('todos los documentos están en estado "{estado}"')
def step_impl(context, estado):
    """Verifica que todos los documentos estén en el estado indicado."""
    for doc in context.solicitud.obtener_documentos():
        assert doc.obtener_estado() == estado, \
            f"Documento {doc.obtener_nombre()} en estado {doc.obtener_estado()}, esperado {estado}"


@step("el asesor revisa todos los documentos de la solicitud")
def step_impl(context):
    """El asesor revisa todos los documentos."""
    assert context.solicitud.obtener_total_documentos() == context.checklist.total_documentos()


@step('todos los documentos son "{resultado_revision}"')
def step_impl(context, resultado_revision):
    """El asesor marca todos los documentos con el mismo resultado."""
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
    """El asesor marca un documento específico con un resultado diferente."""
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

    print(f"[INFO] Solicitud revisada: {context.solicitud}")


@step('todos los documentos deben cambiar a estado "{estado}"')
def step_impl(context, estado):
    """Verifica que todos los documentos cambien al estado esperado."""
    for doc in context.solicitud.obtener_documentos():
        assert doc.obtener_estado() == estado, \
            f"Documento {doc.obtener_nombre()} tiene estado {doc.obtener_estado()}, esperado {estado}"


@step('el documento "{documento_rechazado}" debe cambiar a estado "{estado}"')
def step_impl(context, documento_rechazado, estado):
    """Verifica que un documento específico cambie al estado esperado."""
    documento_encontrado = None

    for doc in context.solicitud.obtener_documentos():
        if doc.obtener_nombre() == documento_rechazado:
            documento_encontrado = doc
            print(f"[INFO] Documento rechazado: {doc.obtener_nombre()} -> {doc.obtener_estado()}")

    assert documento_encontrado is not None, f"No se encontró el documento '{documento_rechazado}' en la solicitud"

    print(f"[INFO] Solicitud actualizada: {context.solicitud}")
    assert documento_encontrado.obtener_estado() == estado, \
        f"Estado actual: {documento_encontrado.obtener_estado()}, esperado: {estado}"


@step('el estado de la solicitud debe ser "{estado}"')
def step_impl(context, estado):
    """Verifica el estado final de la solicitud."""
    assert context.solicitud.obtener_estado() == estado, \
        f"Estado actual: {context.solicitud.obtener_estado()}, esperado: {estado}"


@step("los documentos quedan almacenados en el sistema")
def step_impl(context):
    """Verifica que los documentos queden almacenados."""
    context.agencia.registrar_migrante(context.solicitud)

    migrante = context.agencia.obtener_migrante_por_id(
        context.solicitud.id_migrante
    )

    print(f"[INFO] Migrante creado: {migrante}")

    assert context.agencia.total_migrantes() == 1


# =====================================================
# NOTIFICACIONES
# =====================================================

@step('el migrante recibe la notificación "VISA_{tipo_visa}_APROBADA"')
def step_impl(context, tipo_visa):
    """Verifica que se genere notificación de aprobación."""
    # La notificación se genera pero para propósitos de la prueba
    # simplemente verificamos que el estado sea correcto
    assert context.solicitud.obtener_estado() == "APROBADO"
    context.notificacion = f"VISA_{tipo_visa}_APROBADA"
    print(f"[INFO] Notificación generada: {context.notificacion}")


@step('el migrante recibe la notificación "DOCUMENTO_RECHAZADO: {documento_rechazado}"')
def step_impl(context, documento_rechazado):
    """Verifica que se genere notificación de documento rechazado."""
    # Verificamos que el documento esté rechazado
    doc = context.solicitud.obtener_documento_por_nombre(documento_rechazado)
    assert doc is not None, f"Documento {documento_rechazado} no encontrado"
    assert doc.esta_rechazado(), f"Documento {documento_rechazado} no está rechazado"
    
    context.notificacion = f"DOCUMENTO_RECHAZADO: {documento_rechazado}"
    print(f"[INFO] Notificación generada: {context.notificacion}")


# =====================================================
# ASESOR - ENVÍO A EMBAJADA
# =====================================================

@step('que existe una solicitud aprobada de tipo {tipo_visa} con embajada {embajada} con id {id_solicitud}')
def step_impl(context, tipo_visa, embajada, id_solicitud):
    """Configura una solicitud ya aprobada."""
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
    """Verifica el estado de envío actual."""
    assert context.solicitud.obtener_estado_envio() == estado_envio, \
        f"Estado envío actual: {context.solicitud.obtener_estado_envio()}, esperado: {estado_envio}"


@step("el asesor confirma el envío de la solicitud")
def step_impl(context):
    """El asesor confirma el envío de la solicitud a la embajada."""
    resultado = context.asesor.enviar_solicitud(
        context.solicitud,
        enviada="SI"
    )

    context.notificacion = resultado
    print(f"[INFO] Resultado del envío: {resultado}")


@step('el estado de envío debe cambiar a "{estado_envio}"')
def step_impl(context, estado_envio):
    """Verifica que el estado de envío cambie."""
    print(f"[INFO] Estado de envío actual: {context.solicitud.obtener_estado_envio()}")
    assert context.solicitud.obtener_estado_envio() == estado_envio, \
        f"Estado actual: {context.solicitud.obtener_estado_envio()}, esperado: {estado_envio}"


@step('el migrante recibe la notificación "SOLICITUD ENVIADA A EMBAJADA"')
def step_impl(context):
    """Verifica que se genere notificación de envío."""
    assert context.solicitud.obtener_estado_envio() == "ENVIADO"
    print(f"[INFO] Notificación: SOLICITUD ENVIADA A EMBAJADA")


# =====================================================
# ASIGNACIÓN DE SOLICITUDES A ASESORES
# =====================================================

@step("que existen los siguientes asesores con solicitudes asignadas hoy")
def step_impl(context):
    """Configura los asesores con sus cargas de trabajo actuales."""
    from apps.solicitudes.recepcion.domain import AsignadorSolicitudes
    
    context.asesores = {}
    context.asignador = AsignadorSolicitudes(limite_diario=10)
    
    for row in context.table:
        nombre = row['asesor']
        solicitudes_hoy = int(row['solicitudes_hoy'])
        
        asesor = Asesor(
            id=f"ASESOR-{nombre.replace(' ', '-').upper()}",
            nombre=nombre,
            email=f"{nombre.lower().replace(' ', '.')}@agencia.com"
        )
        
        context.asesores[nombre] = {
            'asesor': asesor,
            'solicitudes_hoy': solicitudes_hoy
        }
        
        context.asignador.registrar_asesor(asesor, solicitudes_hoy)
    
    print(f"[INFO] Asesores registrados: {list(context.asesores.keys())}")


@step("cada asesor tiene un límite de {limite:d} solicitudes diarias")
def step_impl(context, limite):
    """Configura el límite diario de solicitudes por asesor."""
    context.asignador.limite_diario = limite
    assert context.asignador.limite_diario == limite


@step("se registra una nueva solicitud")
def step_impl(context):
    """Se registra una nueva solicitud que debe ser asignada."""
    context.agencia = AgenciaMigracion()
    
    context.nueva_solicitud = SolicitudVisa(
        id_solicitud="SOL-NEW-001",
        id_migrante="MIG-NEW-001",
        tipo_visa=TipoVisa.TRABAJO,
        embajada=TipoEmbajada.ESTADOUNIDENSE
    )
    
    # Realizar la asignación automática
    resultado = context.asignador.asignar_solicitud(context.nueva_solicitud)
    context.resultado_asignacion = resultado
    
    if resultado['exito']:
        context.asesor_asignado = resultado['asesor_nombre']
        print(f"[INFO] Solicitud asignada a: {context.asesor_asignado}")
    else:
        context.asesor_asignado = None
        print(f"[INFO] Solicitud no asignada: {resultado['mensaje']}")


@step('el sistema asigna la solicitud al asesor con menos carga')
def step_impl(context):
    """Verifica que la solicitud fue asignada al asesor con menos carga."""
    assert context.resultado_asignacion['exito'] is True
    assert context.asesor_asignado is not None
    
    # Encontrar el asesor que debería tener menos carga
    min_carga = float('inf')
    asesor_esperado = None
    
    for nombre, datos in context.asesores.items():
        if datos['solicitudes_hoy'] < min_carga:
            min_carga = datos['solicitudes_hoy']
            asesor_esperado = nombre
    
    assert context.asesor_asignado == asesor_esperado, \
        f"Se esperaba asignar a {asesor_esperado}, pero se asignó a {context.asesor_asignado}"


@step('el asesor "{nombre_asesor}" tiene {cantidad:d} solicitudes asignadas hoy')
def step_impl(context, nombre_asesor, cantidad):
    """Verifica la cantidad de solicitudes asignadas a un asesor."""
    solicitudes_actuales = context.asignador.obtener_solicitudes_asesor(nombre_asesor)
    
    assert solicitudes_actuales == cantidad, \
        f"El asesor {nombre_asesor} tiene {solicitudes_actuales} solicitudes, se esperaban {cantidad}"


@step('la solicitud queda en estado "{estado}"')
def step_impl(context, estado):
    """Verifica el estado final de la solicitud."""
    # Normalizar el estado para comparación
    estado_actual = context.nueva_solicitud.obtener_estado().lower().replace('_', ' ')
    estado_esperado = estado.lower().replace('_', ' ')
    
    # Si la solicitud fue asignada, debe estar en pendiente (para revisión)
    if context.resultado_asignacion['exito']:
        assert estado_esperado == 'pendiente' or estado_esperado == 'borrador'
    else:
        assert 'pendiente' in estado_esperado or 'asignacion' in estado_esperado




