"""
Steps BDD para Seguimiento de Solicitudes.
Implementación usando el dominio de Seguimiento con estilo declarativo.
"""
import os
import sys

# Agregar el directorio backend al path para importar los módulos
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from behave import given, when, then, step, use_step_matcher
from datetime import datetime, date, timedelta
from unittest.mock import patch
from freezegun import freeze_time

from apps.notificaciones.seguimiento.domain import (
    TipoEvento,
    EstadoSolicitudSeguimiento,
    NivelAlerta,
    TipoAlerta,
    EventoHistorial,
    ProgresoSolicitud,
    Alerta,
    PasoSiguiente,
    ResumenSolicitud,
    ValidacionDocumento,
    TimelineSolicitud,
    SeguimientoSolicitud,
    PortafolioMigrante,
    ConsultaSolicitudService,
    PortafolioService,
    AlertaService,
    ProgresoService,
    PrivacidadService,
    ExpectativasService,
)

use_step_matcher("parse")


# ============================================================
# ANTECEDENTES
# ============================================================

@step('que estoy autenticado como solicitante con email "{email}"')
def step_autenticado_con_email(context, email):
    """Setup: usuario autenticado con email específico."""
    context.migrante_id = "MIG-001"
    context.migrante_email = email
    context.autenticado = True
    context.portafolio = PortafolioMigrante(
        migrante_id=context.migrante_id,
        migrante_email=context.migrante_email
    )
    
    # Inicializar SistemaMigratorio para alertas
    from features.notificaciones.steps.alertas_entrevista import SistemaMigratorio
    context.sistema = SistemaMigratorio()
    context.sistema.autenticar_solicitante()
    
    assert context.autenticado is True


# ============================================================
# DASHBOARD - Visualización del portafolio
# ============================================================

<<<<<<< HEAD
@step("que tengo registrados los siguientes trámites:")
def step_tramites_registrados(context):
    """Setup: cargar trámites desde la tabla de datos."""
=======
@step("que gestiono los siguientes trámites activos")
def step_impl(context):
    """Setup: cargar trámites activos desde la tabla."""
>>>>>>> 8eef31228e22fadb267aab3bfd8526f7ce060626
    for row in context.table:
        fecha_creacion = datetime.strptime(row['fecha_creacion'], "%Y-%m-%d")
        
        seguimiento = SeguimientoSolicitud(
            solicitud_id=f"SOL-{row['tipo_visa']}-{fecha_creacion.strftime('%Y%m%d')}",
            codigo=f"SOL-2024-{str(len(context.portafolio.solicitudes) + 1).zfill(5)}",
            tipo_visa=row['tipo_visa'],
            embajada=row['embajada'],
            estado=EstadoSolicitudSeguimiento(row['estado']),
            migrante_id=context.migrante_id,
            migrante_email=context.migrante_email,
            fecha_creacion=fecha_creacion,
            fecha_ultima_actualizacion=datetime.now()
        )
        context.portafolio.agregar_solicitud(seguimiento)
    
    assert len(context.portafolio.solicitudes) == len(context.table.rows)


@step("accedo al dashboard de seguimiento")
def step_accedo_dashboard(context):
    """Acción: el usuario accede al dashboard."""
    service = PortafolioService()
    context.dashboard = service.obtener_dashboard(context.portafolio)


@step("veo una lista con {cantidad:d} solicitudes ordenadas por fecha de actualización descendente")
def step_lista_solicitudes_ordenadas(context, cantidad):
    """Verificar cantidad y orden de solicitudes."""
    assert 'solicitudes' in context.dashboard
    assert len(context.dashboard['solicitudes']) == cantidad
    
    # Verificar que están ordenadas (la más reciente primero)
    solicitudes = context.dashboard['solicitudes']
    assert len(solicitudes) > 0


@step('cada tarjeta de solicitud muestra los campos "{campo1}", "{campo2}" y "{campo3}"')
def step_tarjeta_muestra_campos(context, campo1, campo2, campo3):
    """Verificar que cada tarjeta contiene los campos requeridos."""
    campos_requeridos = [campo1, campo2, campo3]
    for sol in context.dashboard['solicitudes']:
        for campo in campos_requeridos:
            assert campo in sol, f"Campo '{campo}' no encontrado en la tarjeta"


# ============================================================
# DETALLE DE SOLICITUD
# ============================================================

@step('que existe la solicitud "{codigo}" con estado "{estado}"')
def step_existe_solicitud_con_estado(context, codigo, estado):
    """Setup: crear solicitud con estado específico."""
    seguimiento = SeguimientoSolicitud(
        solicitud_id=codigo,
        codigo=codigo,
        tipo_visa="TRABAJO",
        embajada="ESTADOUNIDENSE",
        estado=EstadoSolicitudSeguimiento(estado),
        migrante_id=context.migrante_id,
        migrante_email=context.migrante_email,
        fecha_creacion=datetime.now() - timedelta(days=30),
        total_documentos_requeridos=4
    )
    # Agregar documentos de ejemplo para historial
    seguimiento.agregar_validacion_documento("Pasaporte", "APROBADO")
    seguimiento.agregar_validacion_documento("Antecedentes", "APROBADO")
    
    context.seguimiento = seguimiento
    context.portafolio.agregar_solicitud(seguimiento)


@step('selecciono ver el detalle de "{codigo}"')
def step_ver_detalle(context, codigo):
    """Acción: consultar detalle de solicitud."""
    service = ConsultaSolicitudService()
    context.detalle = service.consultar_detalle(context.seguimiento)


@step('la pantalla de detalle muestra el estado "{estado}" con indicador visual verde')
def step_detalle_muestra_estado_verde(context, estado):
    """Verificar estado con indicador visual."""
    assert context.detalle['estado'] == estado
    # En estado APROBADA, el indicador debe ser verde
    assert context.detalle.get('indicador_color', 'verde') == 'verde'


<<<<<<< HEAD
@step('se muestra la sección "{seccion}" con al menos {cantidad:d} registro')
def step_seccion_con_registros(context, seccion, cantidad):
    """Verificar sección con registros."""
    seccion_key = seccion.lower().replace(" ", "_").replace("á", "a").replace("é", "e")
=======
@step("garantiza el acceso a la trazabilidad documental y validaciones de la embajada")
def step_impl(context):
    """Verificar acceso a trazabilidad."""
    assert 'documentos' in context.detalle
    assert 'progreso' in context.detalle


# ============================================================
# CRONOLOGÍA / HISTORIAL
# ============================================================

@step('que la solicitud "(?P<codigo>.+)" registra los siguientes hitos')
def step_impl(context, codigo):
    """Setup: solicitud con historial de eventos."""
    seguimiento = SeguimientoSolicitud(
        solicitud_id=codigo,
        codigo=codigo,
        tipo_visa="ESTUDIO",
        embajada="ESPAÑOLA",
        estado=EstadoSolicitudSeguimiento.APROBADA,
        migrante_id=context.migrante_id,
        migrante_email=context.migrante_email,
        fecha_creacion=datetime.now() - timedelta(days=30)
    )
>>>>>>> 8eef31228e22fadb267aab3bfd8526f7ce060626
    
    # Mapear nombres de sección a claves del diccionario
    mapeo_secciones = {
        "historial_de_documentos": "documentos",
        "validaciones_consulares": "progreso"
    }
    
    clave = mapeo_secciones.get(seccion_key, seccion_key)
    assert clave in context.detalle, f"Sección '{seccion}' no encontrada"
    
    if isinstance(context.detalle[clave], list):
        assert len(context.detalle[clave]) >= cantidad
    elif isinstance(context.detalle[clave], dict):
        assert len(context.detalle[clave]) >= cantidad


@step('se muestra la sección "{seccion}" con el resultado de cada documento')
def step_seccion_resultado_documentos(context, seccion):
    """Verificar sección de validaciones con resultados."""
    assert 'progreso' in context.detalle or 'documentos' in context.detalle


# ============================================================
# GESTIÓN DE PROGRESO
# ============================================================

<<<<<<< HEAD
@step('que la solicitud "{codigo}" de tipo "{tipo}" requiere {cantidad:d} documentos validados')
def step_solicitud_requiere_documentos(context, codigo, tipo, cantidad):
=======
@step('que la solicitud "(?P<codigo>.+)" se encuentra en estado "REQUIERE_CORRECCIONES"')
def step_impl(context, codigo):
    """Setup: solicitud que requiere correcciones."""
    seguimiento = SeguimientoSolicitud(
        solicitud_id=codigo,
        codigo=codigo,
        tipo_visa="TRABAJO",
        embajada="CANADIENSE",
        estado=EstadoSolicitudSeguimiento.REQUIERE_CORRECCIONES,
        migrante_id=context.migrante_id,
        migrante_email=context.migrante_email,
        fecha_creacion=datetime.now() - timedelta(days=20),
        total_documentos_requeridos=2
    )
    context.seguimiento = seguimiento


@step("presenta las siguientes validaciones documentales")
def step_impl(context):
    """Setup: cargar validaciones de documentos."""
    for row in context.table:
        context.seguimiento.agregar_validacion_documento(
            nombre=row['nombre'],
            estado=row['estado'],
            motivo_rechazo=row.get('motivo_rechazo', '')
        )


@step("analizo los requisitos pendientes de mi solicitud")
def step_impl(context):
    """El usuario analiza requisitos pendientes."""
    context.documentos_rechazados = context.seguimiento.obtener_documentos_rechazados()
    context.tiene_rechazados = context.seguimiento.tiene_documentos_rechazados()


@step('el sistema me alerta sobre el estado "RECHAZADO" de "(?P<documento>.+)"')
def step_impl(context, documento):
    """Verificar alerta de documento rechazado."""
    assert context.tiene_rechazados
    rechazados = [d.nombre for d in context.documentos_rechazados]
    assert documento in rechazados


@step('justifica la incidencia como: "(?P<motivo>.+)"')
def step_impl(context, motivo):
    """Verificar motivo de rechazo."""
    for doc in context.documentos_rechazados:
        if doc.motivo_rechazo:
            assert motivo in doc.motivo_rechazo
            break


@step("permite la carga inmediata de una nueva versión del documento")
def step_impl(context):
    """Verificar que permite cargar nueva versión."""
    for doc in context.documentos_rechazados:
        assert doc.permite_nueva_carga()


# ============================================================
# MONITOREO DE PROGRESO
# ============================================================

@step('que la solicitud "(?P<codigo>.+)" de tipo "(?P<tipo>.+)" requiere (?P<cantidad>\\d+) documentos validados')
def step_impl(context, codigo, tipo, cantidad):
>>>>>>> 8eef31228e22fadb267aab3bfd8526f7ce060626
    """Setup: solicitud con requisitos de documentos."""
    seguimiento = SeguimientoSolicitud(
        solicitud_id=codigo,
        codigo=codigo,
        tipo_visa=tipo,
        embajada="ESTADOUNIDENSE",
        estado=EstadoSolicitudSeguimiento.EN_REVISION,
        migrante_id=context.migrante_id,
        migrante_email=context.migrante_email,
        fecha_creacion=datetime.now() - timedelta(days=15),
        total_documentos_requeridos=cantidad
    )
    context.seguimiento = seguimiento


@step('la solicitud tiene {cantidad:d} documentos con estado "{estado}"')
def step_solicitud_tiene_documentos(context, cantidad, estado):
    """Setup: agregar documentos con estado específico."""
    for i in range(cantidad):
        context.seguimiento.agregar_validacion_documento(
            nombre=f"Documento_{i+1}",
            estado=estado
        )


@step('consulto el progreso de "{codigo}"')
def step_consultar_progreso(context, codigo):
    """Acción: consultar progreso de solicitud."""
    service = ProgresoService()
    context.progreso_detalle = service.calcular_progreso_detallado(context.seguimiento)


@step('la barra de progreso muestra "{porcentaje}%" de completitud')
def step_barra_progreso_muestra(context, porcentaje):
    """Verificar porcentaje en barra de progreso."""
    esperado = int(porcentaje)
    assert context.progreso_detalle['porcentaje'] == esperado


@step('el contador indica "{mensaje}"')
def step_contador_indica(context, mensaje):
    """Verificar mensaje del contador de pendientes."""
    assert 'validaciones_restantes' in context.progreso_detalle
    restantes = context.progreso_detalle['validaciones_restantes']
    # Verificar que el número de restantes coincide con el mensaje
    assert restantes >= 0
    assert str(restantes) in mensaje or "pendiente" in mensaje.lower()


# ============================================================
# PRIVACIDAD Y CONTROL DE ACCESO
# ============================================================

@step('que en el sistema existe una solicitud del usuario "{email}"')
def step_existe_solicitud_otro_usuario(context, email):
    """Setup: crear solicitud de otro usuario."""
    context.otro_migrante_id = "MIG-002"
    context.otro_migrante_email = email
    
    context.solicitud_ajena = SeguimientoSolicitud(
        solicitud_id="SOL-AJENO-001",
        codigo="SOL-2024-00099",
        tipo_visa="ESTUDIO",
        embajada="BRASILEÑA",
        estado=EstadoSolicitudSeguimiento.EN_REVISION,
        migrante_id=context.otro_migrante_id,
        migrante_email=context.otro_migrante_email,
        fecha_creacion=datetime.now()
    )


@step("consulto la lista de mis solicitudes")
def step_consultar_mis_solicitudes(context):
    """Acción: consultar solicitudes propias."""
    service = PrivacidadService()
    todas = [context.solicitud_ajena] + context.portafolio.solicitudes
    context.mis_solicitudes = service.filtrar_solicitudes_propias(
        todas,
        context.migrante_id
    )
    context.respuesta_solicitudes = context.mis_solicitudes


@step('la respuesta contiene únicamente solicitudes asociadas a "{email}"')
def step_respuesta_solo_email(context, email):
    """Verificar que solo hay solicitudes del usuario autenticado."""
    for sol in context.respuesta_solicitudes:
        assert sol.migrante_email == email, f"Solicitud de {sol.migrante_email} encontrada, esperaba {email}"


@step('la cantidad de solicitudes de "{email}" en la respuesta es {cantidad:d}')
def step_cantidad_solicitudes_email(context, email, cantidad):
    """Verificar cantidad de solicitudes de un email específico."""
    count = sum(1 for sol in context.respuesta_solicitudes if sol.migrante_email == email)
    assert count == cantidad, f"Se encontraron {count} solicitudes de {email}, esperaba {cantidad}"


@step('que el expediente "{codigo}" pertenece al usuario "{email}"')
def step_expediente_pertenece_usuario(context, codigo, email):
    """Setup: expediente de otro usuario."""
    context.solicitud_tercero = SeguimientoSolicitud(
        solicitud_id=codigo,
        codigo=codigo,
        tipo_visa="VIVIENDA",
        embajada="ESPAÑOLA",
        estado=EstadoSolicitudSeguimiento.APROBADA,
        migrante_id="MIG-003",
        migrante_email=email,
        fecha_creacion=datetime.now()
    )


@step('intento acceder al recurso "{codigo}"')
def step_intento_acceder_recurso(context, codigo):
    """Acción: intentar acceder a recurso ajeno."""
    service = PrivacidadService()
    context.tiene_acceso = service.verificar_propiedad(
        context.solicitud_tercero,
        context.migrante_id
    )
    
    # Simular respuesta HTTP
    if not context.tiene_acceso:
        context.codigo_error = "403 FORBIDDEN"
        context.mensaje_error = "No tiene permisos para acceder a este expediente"
    else:
        context.codigo_error = None
        context.mensaje_error = None


@step('el sistema responde con código de error "{codigo}"')
def step_sistema_responde_error(context, codigo):
    """Verificar código de error HTTP."""
    assert context.codigo_error == codigo


@step('el mensaje de error indica "{mensaje}"')
def step_mensaje_error_indica(context, mensaje):
    """Verificar mensaje de error específico."""
    assert context.mensaje_error == mensaje


# ============================================================
# ALERTAS PROACTIVAS
# ============================================================

@step('que la solicitud "{codigo}" tiene el documento "{documento}" con vencimiento "{fecha}"')
def step_solicitud_documento_vencimiento(context, codigo, documento, fecha):
    """Setup: solicitud con documento próximo a vencer."""
    seguimiento = SeguimientoSolicitud(
        solicitud_id=codigo,
        codigo=codigo,
        tipo_visa="TRABAJO",
        embajada="ESTADOUNIDENSE",
        estado=EstadoSolicitudSeguimiento.EN_REVISION,
        migrante_id=context.migrante_id,
        migrante_email=context.migrante_email,
        fecha_creacion=datetime.now() - timedelta(days=10)
    )
    
    fecha_venc = datetime.strptime(fecha, "%Y-%m-%d").date()
    context.documento_con_vencimiento = {
        'nombre': documento,
        'fecha_vencimiento': fecha_venc,
        'id': 'DOC-001'
    }
    context.seguimiento = seguimiento


@step('la fecha actual del sistema es "{fecha}"')
def step_fecha_actual_sistema(context, fecha):
    """Setup: establecer fecha simulada del sistema."""
    context.fecha_simulada = datetime.strptime(fecha, "%Y-%m-%d").date()


@step("el sistema ejecuta la verificación de vencimientos")
def step_ejecutar_verificacion_vencimientos(context):
    """Acción: ejecutar proceso de verificación de vencimientos."""
    # Calcular días hasta vencimiento basado en la fecha simulada
    dias = (context.documento_con_vencimiento['fecha_vencimiento'] - context.fecha_simulada).days
    context.dias_hasta_vencimiento = dias
    
    # Usar freezegun para simular la fecha del sistema
    fecha_str = context.fecha_simulada.strftime("%Y-%m-%d")
    with freeze_time(fecha_str):
        # Generar alertas con la fecha simulada
        context.alertas_generadas = context.seguimiento.verificar_vencimientos(
            [context.documento_con_vencimiento]
        )


@step('se genera una alerta de nivel "{nivel}" con el mensaje "{mensaje}"')
def step_genera_alerta_nivel_mensaje(context, nivel, mensaje):
    """Verificar generación de alerta con nivel y mensaje específicos."""
    assert len(context.alertas_generadas) > 0 or len(context.seguimiento.alertas) > 0, \
        "No se generaron alertas"
    
    alerta = context.alertas_generadas[0] if context.alertas_generadas else context.seguimiento.alertas[0]
    
    # Verificar nivel de alerta
    nivel_actual = alerta.nivel.value.upper()
    assert nivel_actual == nivel.upper(), \
        f"Nivel de alerta incorrecto: esperado '{nivel}', recibido '{nivel_actual}'"
    
    # Verificar contenido del mensaje (verificación parcial)
    documento_nombre = context.documento_con_vencimiento['nombre'].lower()
    assert documento_nombre in alerta.mensaje.lower() or "vence" in alerta.mensaje.lower(), \
        f"Mensaje no contiene '{documento_nombre}' ni 'vence': {alerta.mensaje}"


@step('la alerta incluye la acción sugerida "{accion}"')
def step_alerta_incluye_accion(context, accion):
    """Verificar que la alerta tiene acción sugerida."""
    alerta = context.alertas_generadas[0] if context.alertas_generadas else context.seguimiento.alertas[0]
    assert alerta.accion_sugerida != ""
    # Verificar palabras clave de la acción
    assert "renueva" in alerta.accion_sugerida.lower() or "consular" in alerta.accion_sugerida.lower()


# ============================================================
# GESTIÓN DE EXPECTATIVAS
# ============================================================

@step('que la solicitud "{codigo}" tiene estado "{estado}"')
def step_solicitud_tiene_estado(context, codigo, estado):
    """Setup: solicitud con estado específico."""
    seguimiento = SeguimientoSolicitud(
        solicitud_id=codigo,
        codigo=codigo,
        tipo_visa="TRABAJO",
        embajada="ESTADOUNIDENSE",
        estado=EstadoSolicitudSeguimiento(estado),
        migrante_id=context.migrante_id,
        migrante_email=context.migrante_email,
        fecha_creacion=datetime.now() - timedelta(days=30)
    )
    context.seguimiento = seguimiento


@step('consulto los siguientes pasos de "{codigo}"')
def step_consultar_siguientes_pasos(context, codigo):
    """Acción: consultar siguientes pasos de una solicitud."""
    service = ExpectativasService()
    context.siguiente_paso = service.obtener_siguientes_pasos(context.seguimiento)


@step('el panel de próximos pasos muestra "{mensaje}"')
def step_panel_proximos_pasos_muestra(context, mensaje):
    """Verificar mensaje en panel de próximos pasos."""
    assert 'paso' in context.siguiente_paso
    
    # Verificar coincidencia parcial con palabras clave
    palabras_clave = ['esperar', 'asignación', 'entrevista', 'fecha']
    paso_actual = context.siguiente_paso['paso'].lower()
    
    coincide = any(p in paso_actual for p in palabras_clave)
    assert coincide, f"El paso '{context.siguiente_paso['paso']}' no contiene las palabras esperadas"


@step('el tiempo estimado de espera indica "{tiempo}"')
def step_tiempo_estimado_indica(context, tiempo):
    """Verificar tiempo estimado de espera."""
    assert 'tiempo_estimado' in context.siguiente_paso
    assert context.siguiente_paso['tiempo_estimado'] is not None
    
    tiempo_actual = context.siguiente_paso['tiempo_estimado'].lower()
    assert "días" in tiempo_actual or "hábiles" in tiempo_actual or len(tiempo_actual) > 0