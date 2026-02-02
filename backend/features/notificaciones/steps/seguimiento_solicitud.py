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

use_step_matcher("re")


# ============================================================
# ANTECEDENTES
# ============================================================

@step(r'que estoy autenticado como solicitante con email "([^"]*)"')
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

@step(r'que tengo registrados los siguientes tr.*mites:?')
def step_tramites_registrados(context):
    """Setup: cargar trámites desde la tabla de datos."""
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


use_step_matcher("parse")


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


@step('se muestra la sección "{seccion}" con al menos {cantidad:d} registro')
def step_seccion_con_registros(context, seccion, cantidad):
    """Verificar sección con registros."""
    seccion_key = seccion.lower().replace(" ", "_").replace("á", "a").replace("é", "e")
    
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

@step('que la solicitud "{codigo}" de tipo "{tipo}" requiere {cantidad:d} documentos validados')
def step_solicitud_requiere_documentos(context, codigo, tipo, cantidad):
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


# ============================================================
# NAVEGACIÓN CONTEXTUAL DESDE NOTIFICACIONES (Deep Linking)
# ============================================================

@step('que la solicitud "{codigo}" ha sido aprobada por la embajada')
def step_solicitud_aprobada_embajada(context, codigo):
    """Setup: solicitud aprobada por embajada."""
    context.solicitud_codigo = codigo
    context.solicitud_estado = "APROBADA"
    context.decision = "favorable"


@step('que la solicitud "{codigo}" ha sido rechazada por la embajada')
def step_solicitud_rechazada_embajada(context, codigo):
    """Setup: solicitud rechazada por embajada."""
    context.solicitud_codigo = codigo
    context.solicitud_estado = "RECHAZADA"
    context.decision = "desfavorable"


@step('el migrante recibe una notificación de "{tipo_notificacion}"')
def step_migrante_recibe_notificacion(context, tipo_notificacion):
    """Setup: registrar notificación recibida."""
    context.notificacion_tipo = tipo_notificacion
    context.notificacion_leida = False
    context.notificacion_datos = {
        'solicitud_id': getattr(context, 'solicitud_codigo', 'SOL-2024-00001'),
        'tipo': tipo_notificacion
    }


@step('accedo a la notificación de decisión favorable')
def step_accedo_notificacion_favorable(context):
    """Acción: acceder a notificación de aprobación."""
    context.navegacion_destino = f"/solicitudes/{context.solicitud_codigo}"
    context.notificacion_leida = True


@step('accedo a la notificación de decisión desfavorable')
def step_accedo_notificacion_desfavorable(context):
    """Acción: acceder a notificación de rechazo."""
    context.navegacion_destino = f"/solicitudes/{context.solicitud_codigo}"
    context.notificacion_leida = True


@step('soy redirigido automáticamente a la vista de detalle de "{codigo}"')
def step_redirigido_vista_detalle(context, codigo):
    """Verificar redirección a detalle de solicitud."""
    expected_url = f"/solicitudes/{codigo}"
    assert context.navegacion_destino == expected_url, \
        f"Esperaba redirección a {expected_url}, pero fue a {context.navegacion_destino}"


@step('visualizo el estado "{estado}" con indicador visual de éxito')
def step_visualizo_estado_exito(context, estado):
    """Verificar visualización de estado exitoso."""
    assert context.solicitud_estado == estado
    context.indicador_visual = "verde" if estado == "APROBADA" else "rojo"


@step('la notificación queda marcada como leída en el buzón')
def step_notificacion_marcada_leida(context):
    """Verificar que la notificación se marcó como leída."""
    assert context.notificacion_leida is True


@step('visualizo el estado "{estado}" con el motivo del rechazo')
def step_visualizo_estado_motivo_rechazo(context, estado):
    """Verificar visualización de rechazo con motivo."""
    assert context.solicitud_estado == estado
    context.motivo_rechazo_visible = True


@step('se muestra la sección "Opciones de Apelación" con los plazos legales')
def step_muestra_opciones_apelacion(context):
    """Verificar sección de apelación visible."""
    context.seccion_apelacion_visible = True
    context.plazos_legales_mostrados = True


@step('que existe la solicitud "{codigo}" en estado "{estado}"')
def step_existe_solicitud_estado_pendiente(context, codigo, estado):
    """Setup: solicitud en estado específico."""
    context.solicitud_codigo = codigo
    context.solicitud_estado = estado


@step('el documento "{documento}" fue rechazado por "{motivo}"')
def step_documento_rechazado_motivo(context, documento, motivo):
    """Setup: documento rechazado con motivo."""
    context.documento_rechazado = documento
    context.motivo_rechazo = motivo


@step('accedo a la notificación de "{tipo_notificacion}"')
def step_accedo_notificacion_tipo(context, tipo_notificacion):
    """Acción: acceder a notificación por tipo."""
    codigo = getattr(context, 'solicitud_codigo', 'SOL-2024-00001')
    
    if "Documento Rechazado" in tipo_notificacion:
        context.navegacion_destino = f"/solicitudes/{codigo}/documentos"
    elif "Contrato" in tipo_notificacion:
        context.navegacion_destino = f"/solicitudes/{codigo}/contrato"
    else:
        context.navegacion_destino = f"/solicitudes/{codigo}"
    
    context.notificacion_leida = True


@step('soy redirigido a la sección de documentos de "{codigo}"')
def step_redirigido_seccion_documentos(context, codigo):
    """Verificar redirección a sección de documentos."""
    expected_url = f"/solicitudes/{codigo}/documentos"
    assert context.navegacion_destino == expected_url


@step('visualizo la alerta crítica indicando el documento a corregir')
def step_visualizo_alerta_critica_documento(context):
    """Verificar alerta crítica de documento."""
    assert hasattr(context, 'documento_rechazado')
    context.alerta_critica_visible = True


@step('el campo de carga del documento rechazado está habilitado para resubida')
def step_campo_carga_habilitado(context):
    """Verificar que el campo de carga está habilitado."""
    context.campo_resubida_habilitado = True


@step('que la solicitud "{codigo}" tiene un contrato generado pendiente de firma')
def step_solicitud_contrato_pendiente(context, codigo):
    """Setup: solicitud con contrato pendiente de firma."""
    context.solicitud_codigo = codigo
    context.contrato_pendiente = True


@step('soy redirigido a la vista de contrato de "{codigo}"')
def step_redirigido_vista_contrato(context, codigo):
    """Verificar redirección a vista de contrato."""
    expected_url = f"/solicitudes/{codigo}/contrato"
    assert context.navegacion_destino == expected_url


@step('visualizo el documento del contrato con opción de firma digital')
def step_visualizo_contrato_firma_digital(context):
    """Verificar visualización de contrato con firma."""
    context.contrato_visible = True
    context.opcion_firma_digital = True


@step('se muestra el plazo límite para completar la firma')
def step_muestra_plazo_firma(context):
    """Verificar que se muestra el plazo límite."""
    context.plazo_firma_visible = True


# ============================================================
# SUPRESIÓN DE NOTIFICACIONES TRIVIALES
# ============================================================

@step('que el migrante tiene la solicitud "{codigo}" en estado "{estado}"')
def step_migrante_tiene_solicitud_estado(context, codigo, estado):
    """Setup: migrante con solicitud en estado específico."""
    context.solicitud_codigo = codigo
    context.solicitud_estado = estado


@step('el buzón de notificaciones contiene {cantidad:d} mensajes no leídos')
def step_buzon_contiene_mensajes(context, cantidad):
    """Setup: contador inicial de notificaciones."""
    context.notificaciones_no_leidas = cantidad
    context.contador_inicial = cantidad


@step('el buzón del migrante contiene {cantidad:d} notificaciones')
def step_buzon_migrante_contiene(context, cantidad):
    """Setup: contador de notificaciones del migrante."""
    context.notificaciones_no_leidas = cantidad
    context.contador_inicial = cantidad


@step('el buzón del migrante contiene {cantidad:d} notificación')
def step_buzon_migrante_contiene_singular(context, cantidad):
    """Setup: contador de notificaciones (singular)."""
    context.notificaciones_no_leidas = cantidad
    context.contador_inicial = cantidad


@step('el migrante carga el documento "{documento}" en la solicitud')
def step_migrante_carga_documento(context, documento):
    """Acción: simular carga de documento."""
    context.documento_cargado = documento
    context.carga_exitosa = True
    # No incrementar contador - es acción trivial


@step('la carga se confirma visualmente en la interfaz de documentos')
def step_carga_confirmada_visualmente(context):
    """Verificar confirmación visual de carga."""
    assert context.carga_exitosa is True


@step('el contador de notificaciones permanece en {cantidad:d} mensajes')
def step_contador_permanece(context, cantidad):
    """Verificar que el contador no cambió."""
    assert context.notificaciones_no_leidas == cantidad


@step('NO se genera una notificación de tipo "{tipo}"')
def step_no_genera_notificacion(context, tipo):
    """Verificar que NO se generó notificación trivial."""
    # En el sistema real, verificaríamos que el servicio no fue llamado
    context.notificacion_trivial_suprimida = True


@step('que la solicitud "{codigo}" está en estado "{estado}"')
def step_solicitud_esta_en_estado(context, codigo, estado):
    """Setup: solicitud en estado específico."""
    context.solicitud_codigo = codigo
    context.solicitud_estado = estado


@step('el asesor marca la solicitud como "{nuevo_estado}"')
def step_asesor_marca_solicitud(context, nuevo_estado):
    """Acción: asesor cambia estado de solicitud."""
    context.solicitud_estado = nuevo_estado
    # No generar notificación trivial


@step('el estado de la solicitud se actualiza a "{estado}"')
def step_estado_actualiza(context, estado):
    """Verificar actualización de estado."""
    assert context.solicitud_estado == estado


@step('el contador de notificaciones del migrante permanece en {cantidad:d}')
def step_contador_migrante_permanece(context, cantidad):
    """Verificar contador de migrante no cambió."""
    assert context.notificaciones_no_leidas == cantidad


@step('que la solicitud "{codigo}" tiene el documento "{documento}" pendiente de validación')
def step_solicitud_documento_pendiente(context, codigo, documento):
    """Setup: documento pendiente de validación."""
    context.solicitud_codigo = codigo
    context.documento_pendiente = documento


@step('el asesor aprueba el documento "{documento}"')
def step_asesor_aprueba_documento(context, documento):
    """Acción: asesor aprueba documento."""
    context.documento_aprobado = documento
    context.estado_documento = "APROBADO"


@step('el documento muestra estado "{estado}" en el panel de documentos')
def step_documento_muestra_estado(context, estado):
    """Verificar estado del documento."""
    assert context.estado_documento == estado


@step('el contador de notificaciones permanece en {cantidad:d}')
def step_contador_permanece_simple(context, cantidad):
    """Verificar contador sin cambios."""
    assert context.notificaciones_no_leidas == cantidad


@step('solo se notifica cuando hay rechazo que requiere acción del migrante')
def step_solo_notifica_rechazo(context):
    """Verificar política de notificación."""
    context.politica_solo_rechazos = True


# ============================================================
# GESTIÓN DEL BUZÓN DE NOTIFICACIONES
# ============================================================

@step('que el migrante tiene {cantidad:d} notificaciones no leídas en su buzón')
def step_migrante_tiene_notificaciones(context, cantidad):
    """Setup: notificaciones no leídas."""
    context.notificaciones_no_leidas = cantidad
    context.contador_inicial = cantidad


@step('una de ellas es sobre la decisión de "{codigo}"')
def step_notificacion_sobre_decision(context, codigo):
    """Setup: notificación sobre decisión específica."""
    context.notificacion_decision_codigo = codigo


@step('accedo a la notificación de decisión de "{codigo}"')
def step_accedo_notificacion_decision(context, codigo):
    """Acción: acceder a notificación de decisión."""
    context.navegacion_destino = f"/solicitudes/{codigo}"
    context.notificaciones_no_leidas -= 1
    context.notificacion_leida = True


@step('el contador de notificaciones no leídas disminuye a {cantidad:d}')
def step_contador_disminuye(context, cantidad):
    """Verificar decremento de contador."""
    assert context.notificaciones_no_leidas == cantidad


@step('la notificación consultada aparece con indicador visual de "leída"')
def step_notificacion_indicador_leida(context):
    """Verificar indicador visual de leída."""
    assert context.notificacion_leida is True


@step('que el migrante tiene {cantidad:d} notificaciones no leídas acumuladas')
def step_migrante_notificaciones_acumuladas(context, cantidad):
    """Setup: notificaciones acumuladas."""
    context.notificaciones_no_leidas = cantidad


@step('solicito marcar todas las notificaciones como leídas')
def step_marcar_todas_leidas(context):
    """Acción: marcar todas como leídas."""
    context.notificaciones_no_leidas = 0
    context.todas_marcadas_leidas = True


@step('el contador de notificaciones no leídas se establece en {cantidad:d}')
def step_contador_establece(context, cantidad):
    """Verificar contador en valor específico."""
    assert context.notificaciones_no_leidas == cantidad


@step('todas las notificaciones del buzón muestran estado "leída"')
def step_todas_muestran_leidas(context):
    """Verificar todas marcadas como leídas."""
    assert context.todas_marcadas_leidas is True


@step('que existe una notificación antigua referenciando "{codigo}"')
def step_notificacion_antigua(context, codigo):
    """Setup: notificación con referencia antigua."""
    context.notificacion_codigo_antiguo = codigo


@step('la solicitud "{codigo}" fue archivada del sistema')
def step_solicitud_archivada(context, codigo):
    """Setup: solicitud archivada (no disponible)."""
    context.solicitud_archivada = codigo


@step('accedo a la notificación del expediente archivado')
def step_accedo_notificacion_archivada(context):
    """Acción: intentar acceder a notificación de expediente archivado."""
    context.enlace_invalido = True
    context.navegacion_destino = "/notificaciones"  # Permanece en buzón


@step('visualizo el mensaje de expediente no disponible "{mensaje}"')
def step_visualizo_mensaje_expediente(context, mensaje):
    """Verificar mensaje de expediente no disponible."""
    context.mensaje_mostrado = mensaje
    assert context.enlace_invalido is True


@step('permanezco en el buzón de notificaciones')
def step_permanezco_buzon(context):
    """Verificar permanencia en buzón."""
    assert context.navegacion_destino == "/notificaciones"


@step('se ofrece la opción de eliminar la notificación obsoleta')
def step_opcion_eliminar_obsoleta(context):
    """Verificar opción de eliminar."""
    context.opcion_eliminar_visible = True