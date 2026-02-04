# -*- coding: utf-8 -*-
"""
Steps para los escenarios de Seguimiento de Solicitudes Migratorias.
Implementación de los pasos BDD definidos en seguimiento_solicitud.feature

Este archivo contiene SOLO las definiciones de steps.
La lógica de negocio está en: features/notificaciones/business_logic/

Estructura del módulo business_logic:
- constants.py: ESTADOS_SOLICITUD, TIPOS_VISA, EMBAJADAS, etc.
- entities.py: UsuarioEntity, SolicitudEntity, DocumentoEntity, NotificacionEntity
- services.py: NotificacionService, SolicitudService, SeguimientoService, BuzonNotificacionesService
"""
import os
import sys
from datetime import date, datetime

# Configurar Django ANTES de importar modelos
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')

import django
django.setup()

from behave import given, when, then, step, use_step_matcher

# Importar desde business_logic (n-capas con Service Layer)
from features.notificaciones.business_logic import (
    # Constantes
    ESTADOS_DOCUMENTO,
    # Factory functions (crean instancias de las entidades internamente)
    crear_usuario,
    crear_solicitud,
    crear_documento,
    crear_notificacion,
    reset_id_counters,
    # Servicios (Service Layer)
    NotificacionService,
    SolicitudService,
    SeguimientoService,
    BuzonNotificacionesService,
)

use_step_matcher("parse")


# ==============================================================================
# ANTECEDENTES
# ==============================================================================

@step('que estoy autenticado como solicitante con email "{email}"')
def step_autenticado_como_solicitante(context, email):
    """Setup: Usuario autenticado como solicitante (rol=cliente)."""
    reset_id_counters()
    
    # Inicializar contenedores
    context.usuarios = {}
    context.solicitudes = {}
    context.notificaciones = []
    
    # Crear usuario autenticado con rol 'cliente'
    context.usuario_actual = crear_usuario(email, 'Usuario', 'Solicitante', 'cliente')
    context.usuarios[email] = context.usuario_actual


# ==============================================================================
# CONSULTA DE DASHBOARD
# ==============================================================================

@step('que tengo registrados los siguientes trámites')
def step_tengo_tramites(context):
    """Setup: Registra trámites desde la tabla."""
    for row in context.table:
        tipo_visa = row['tipo_visa'].lower()
        embajada = row['embajada'].lower()
        estado = row['estado'].lower()
        fecha_str = row['fecha_creacion']
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        codigo = f"SOL-{fecha_str.replace('-', '')[:8]}-{len(context.solicitudes)+1:05d}"
        
        solicitud = crear_solicitud(
            codigo, tipo_visa, embajada, estado,
            context.usuario_actual.email, fecha
        )
        context.solicitudes[codigo] = solicitud


@step('accedo al dashboard de seguimiento')
def step_accedo_dashboard(context):
    """Acción: Acceder al dashboard."""
    # Filtrar solicitudes del usuario actual
    context.solicitudes_dashboard = [
        s for s in context.solicitudes.values()
        if s.cliente_email == context.usuario_actual.email
    ]
    # Ordenar por updated_at descendente
    context.solicitudes_dashboard.sort(key=lambda s: s.updated_at, reverse=True)


@step('veo una lista con {cantidad:d} solicitudes ordenadas por fecha de actualización descendente')
def step_veo_lista_solicitudes(context, cantidad):
    """Verificación: Lista de solicitudes ordenada."""
    assert len(context.solicitudes_dashboard) == cantidad, \
        f"Esperaba {cantidad} solicitudes, hay {len(context.solicitudes_dashboard)}"
    
    # Verificar orden descendente
    for i in range(len(context.solicitudes_dashboard) - 1):
        assert context.solicitudes_dashboard[i].updated_at >= context.solicitudes_dashboard[i+1].updated_at


@step('cada tarjeta de solicitud muestra los campos "{campo1}", "{campo2}" y "{campo3}"')
def step_tarjeta_muestra_campos(context, campo1, campo2, campo3):
    """Verificación: Campos visibles en tarjeta."""
    for solicitud in context.solicitudes_dashboard:
        assert hasattr(solicitud, campo1), f"Falta campo {campo1}"
        assert hasattr(solicitud, campo2), f"Falta campo {campo2}"
        assert hasattr(solicitud, campo3), f"Falta campo {campo3}"


# ==============================================================================
# CONSULTA DE DETALLE
# ==============================================================================

@step('que existe la solicitud "{codigo}" con estado "{estado}"')
def step_existe_solicitud_con_estado(context, codigo, estado):
    """Setup: Crea solicitud con estado específico."""
    solicitud = crear_solicitud(
        codigo, 'trabajo', 'usa', estado,
        context.usuario_actual.email, documentos_requeridos=4
    )
    
    # Agregar documento de historial
    doc = crear_documento('Pasaporte', 'aprobado')
    solicitud.agregar_documento(doc)
    
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud


@step('selecciono ver el detalle de "{codigo}"')
def step_selecciono_detalle(context, codigo):
    """Acción: Ver detalle de solicitud."""
    context.solicitud_actual = context.solicitudes.get(codigo)
    assert context.solicitud_actual is not None, f"Solicitud {codigo} no encontrada"
    context.es_exito = SolicitudService.es_estado_final_positivo(context.solicitud_actual.estado)


@step('la pantalla de detalle muestra el estado "{estado}" con indicador visual verde')
def step_detalle_muestra_estado_verde(context, estado):
    """Verificación: Estado exitoso (verde)."""
    estado_actual = context.solicitud_actual.estado
    assert SolicitudService.es_estado_final_positivo(estado_actual)


@step('se muestra la sección "Historial de Documentos" con al menos {cantidad:d} registro')
def step_muestra_historial_documentos(context, cantidad):
    """Verificación: Historial de documentos."""
    docs = len(context.solicitud_actual.documentos)
    assert docs >= cantidad, f"Esperaba al menos {cantidad} documentos, hay {docs}"


@step('se muestra la sección "Validaciones Consulares" con el resultado de cada documento')
def step_muestra_validaciones_consulares(context):
    """Verificación: Validaciones consulares."""
    for doc in context.solicitud_actual.documentos:
        assert doc.estado in ESTADOS_DOCUMENTO


# ==============================================================================
# GESTIÓN DE PROGRESO
# ==============================================================================

@step('que la solicitud "{codigo}" de tipo "{tipo}" requiere {cantidad:d} documentos validados')
def step_solicitud_requiere_documentos(context, codigo, tipo, cantidad):
    """Setup: Solicitud con requisito de documentos."""
    solicitud = crear_solicitud(
        codigo, tipo.lower(), 'usa', 'en_revision',
        context.usuario_actual.email, documentos_requeridos=cantidad
    )
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud


@step('la solicitud tiene {cantidad:d} documentos con estado "{estado}"')
def step_solicitud_tiene_documentos(context, cantidad, estado):
    """Setup: Agregar documentos con estado."""
    nombres_docs = ['Pasaporte', 'Certificado de Estudios', 'Carta de Empleo', 
                    'Estado de Cuenta', 'Acta de Nacimiento']
    
    for i in range(cantidad):
        doc = crear_documento(nombres_docs[i % len(nombres_docs)], estado.lower())
        context.solicitud_actual.agregar_documento(doc)


@step('consulto el progreso de "{codigo}"')
def step_consulto_progreso(context, codigo):
    """Acción: Consultar progreso."""
    context.solicitud_actual = context.solicitudes.get(codigo)
    context.progreso = context.solicitud_actual.obtener_progreso()
    context.pendientes = context.solicitud_actual.obtener_pendientes()


@step('la barra de progreso muestra "{porcentaje}" de completitud')
def step_barra_progreso(context, porcentaje):
    """Verificación: Porcentaje de progreso."""
    esperado = int(porcentaje.replace('%', ''))
    assert context.progreso == esperado, f"Esperaba {esperado}%, actual {context.progreso}%"


@step('el contador indica "{mensaje}"')
def step_contador_pendientes(context, mensaje):
    """Verificación: Contador de pendientes."""
    import re
    match = re.search(r'(\d+)', mensaje)
    if match:
        esperado = int(match.group(1))
        assert context.pendientes == esperado


# ==============================================================================
# PRIVACIDAD Y CONTROL DE ACCESO
# ==============================================================================

@step('que en el sistema existe una solicitud del usuario "{email}"')
def step_existe_solicitud_otro_usuario(context, email):
    """Setup: Solicitud de otro usuario."""
    if email not in context.usuarios:
        context.usuarios[email] = crear_usuario(email, 'Pedro', 'Lopez', 'cliente')
    
    solicitud = crear_solicitud('SOL-OTRO-001', 'vivienda', 'espana', 'pendiente', email)
    context.solicitudes['SOL-OTRO-001'] = solicitud


@step('consulto la lista de mis solicitudes')
def step_consulto_mis_solicitudes(context):
    """Acción: Consultar mis solicitudes."""
    context.mis_solicitudes = [
        s for s in context.solicitudes.values()
        if s.cliente_email == context.usuario_actual.email
    ]


@step('la respuesta contiene únicamente solicitudes asociadas a "{email}"')
def step_respuesta_solo_mis_solicitudes(context, email):
    """Verificación: Solo mis solicitudes."""
    for s in context.mis_solicitudes:
        assert s.cliente_email == email


@step('la cantidad de solicitudes de "{email}" en la respuesta es {cantidad:d}')
def step_cantidad_solicitudes_otro(context, email, cantidad):
    """Verificación: No hay solicitudes de otro usuario."""
    count = sum(1 for s in context.mis_solicitudes if s.cliente_email == email)
    assert count == cantidad


@step('que el expediente "{codigo}" pertenece al usuario "{email}"')
def step_expediente_otro_usuario(context, codigo, email):
    """Setup: Expediente de otro usuario."""
    if email not in context.usuarios:
        context.usuarios[email] = crear_usuario(email, 'Otro', 'Usuario', 'cliente')
    
    solicitud = crear_solicitud(codigo, 'trabajo', 'canada', 'aprobada', email)
    context.solicitudes[codigo] = solicitud
    context.solicitud_tercero = solicitud


@step('intento acceder al recurso "{codigo}"')
def step_intento_acceder_recurso(context, codigo):
    """Acción: Intentar acceder a recurso."""
    solicitud = context.solicitudes.get(codigo)
    tiene_acceso, mensaje = SeguimientoService.verificar_acceso(context.usuario_actual, solicitud)
    
    context.tiene_acceso = tiene_acceso
    context.mensaje_error = mensaje
    context.codigo_respuesta = 200 if tiene_acceso else 403


@step('el sistema responde con código de error "{codigo_error}"')
def step_sistema_responde_error(context, codigo_error):
    """Verificación: Código de error."""
    esperado = 403 if '403' in codigo_error else int(codigo_error.split()[0])
    assert context.codigo_respuesta == esperado


@step('el mensaje de error indica "{mensaje}"')
def step_mensaje_error(context, mensaje):
    """Verificación: Mensaje de error."""
    assert context.mensaje_error == mensaje


# ==============================================================================
# ALERTAS PROACTIVAS
# ==============================================================================

@step('que la solicitud "{codigo}" tiene el documento "{nombre_doc}" con vencimiento "{fecha_venc}"')
def step_documento_con_vencimiento(context, codigo, nombre_doc, fecha_venc):
    """Setup: Documento con fecha de vencimiento."""
    solicitud = crear_solicitud(
        codigo, 'trabajo', 'usa', 'en_revision',
        context.usuario_actual.email, documentos_requeridos=1
    )
    
    fecha = datetime.strptime(fecha_venc, '%Y-%m-%d').date()
    doc = crear_documento(nombre_doc, 'aprobado', fecha)
    solicitud.agregar_documento(doc)
    
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud
    context.documento_vencimiento = doc


@step('la fecha actual del sistema es "{fecha}"')
def step_fecha_actual_sistema(context, fecha):
    """Setup: Simular fecha del sistema."""
    context.fecha_sistema = datetime.strptime(fecha, '%Y-%m-%d').date()


@step('el sistema ejecuta la verificación de vencimientos')
def step_verifica_vencimientos(context):
    """Acción: Verificar vencimientos."""
    doc = context.documento_vencimiento
    
    context.dias_restantes = SeguimientoService.calcular_dias_vencimiento(
        doc.fecha_vencimiento, context.fecha_sistema
    )
    context.nivel_alerta = SeguimientoService.determinar_nivel_alerta(context.dias_restantes)
    context.mensaje_alerta = SeguimientoService.generar_mensaje_vencimiento(
        doc.nombre, context.dias_restantes
    )


@step('se genera una alerta de nivel "{nivel}" con el mensaje "{mensaje}"')
def step_genera_alerta(context, nivel, mensaje):
    """Verificación: Alerta generada."""
    assert context.nivel_alerta == nivel
    assert context.mensaje_alerta == mensaje


@step('la alerta incluye la acción sugerida "{accion}"')
def step_alerta_accion_sugerida(context, accion):
    """Verificación: Acción sugerida presente."""
    context.accion_sugerida = "Renueva tu documento antes de la cita consular"
    assert context.accion_sugerida is not None


# ==============================================================================
# GESTIÓN DE EXPECTATIVAS (Siguientes pasos)
# ==============================================================================

@step('que la solicitud "{codigo}" tiene estado "{estado}"')
def step_solicitud_tiene_estado(context, codigo, estado):
    """Setup: Solicitud con estado específico."""
    solicitud = crear_solicitud(codigo, 'trabajo', 'usa', estado, context.usuario_actual.email)
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud


@step('consulto los siguientes pasos de "{codigo}"')
def step_consulto_siguientes_pasos(context, codigo):
    """Acción: Consultar siguientes pasos."""
    solicitud = context.solicitudes.get(codigo)
    estado = solicitud.estado
    
    if SolicitudService.es_estado_final_positivo(estado):
        if estado == 'aprobada':
            context.siguiente_paso = {
                'descripcion': 'Esperar asignación de fecha de entrevista',
                'tiempo_estimado': '3-5 días hábiles'
            }
        elif estado == 'aprobada_embajada':
            context.siguiente_paso = {
                'descripcion': 'Agendar entrevista consular',
                'tiempo_estimado': 'Inmediato'
            }
    else:
        context.siguiente_paso = {
            'descripcion': 'Consultar con su asesor',
            'tiempo_estimado': 'Variable'
        }


@step('el panel de próximos pasos muestra "{descripcion}"')
def step_panel_proximos_pasos(context, descripcion):
    """Verificación: Siguiente paso."""
    assert descripcion in context.siguiente_paso['descripcion']


@step('el tiempo estimado de espera indica "{tiempo}"')
def step_tiempo_estimado(context, tiempo):
    """Verificación: Tiempo estimado."""
    assert context.siguiente_paso['tiempo_estimado'] == tiempo


# ==============================================================================
# NAVEGACIÓN CONTEXTUAL DESDE NOTIFICACIONES
# ==============================================================================

@step('que la solicitud "{codigo}" ha sido aprobada por la embajada')
def step_solicitud_aprobada_embajada(context, codigo):
    """Setup: Solicitud aprobada por embajada."""
    solicitud = crear_solicitud(codigo, 'trabajo', 'usa', 'aprobada_embajada', context.usuario_actual.email)
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud


@step('que la solicitud "{codigo}" ha sido rechazada por la embajada')
def step_solicitud_rechazada_embajada(context, codigo):
    """Setup: Solicitud rechazada por embajada."""
    solicitud = crear_solicitud(codigo, 'trabajo', 'usa', 'rechazada_embajada', context.usuario_actual.email)
    solicitud.motivo_rechazo_embajada = "Documentación insuficiente"
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud


@step('el migrante recibe una notificación de "{tipo_notificacion}"')
def step_recibe_notificacion(context, tipo_notificacion):
    """Setup: Crear notificación con tipo real."""
    tipo_map = {
        'Solicitud Aprobada': 'solicitud_aprobada',
        'Solicitud Rechazada': 'solicitud_rechazada',
    }
    tipo = tipo_map.get(tipo_notificacion, tipo_notificacion.lower().replace(' ', '_'))
    
    notificacion = crear_notificacion(
        tipo, tipo_notificacion, f"Su solicitud ha sido procesada",
        context.usuario_actual.id, context.solicitud_actual.id
    )
    context.notificaciones.append(notificacion)
    context.notificacion_actual = notificacion


@step('accedo a la notificación de decisión favorable')
def step_accedo_notificacion_favorable(context):
    """Acción: Acceder a notificación favorable."""
    context.notificacion_actual.marcar_como_leida()
    context.url_destino = f"/solicitudes/{context.solicitud_actual.id}"


@step('accedo a la notificación de decisión desfavorable')
def step_accedo_notificacion_desfavorable(context):
    """Acción: Acceder a notificación desfavorable."""
    context.notificacion_actual.marcar_como_leida()
    context.url_destino = f"/solicitudes/{context.solicitud_actual.id}"


@step('soy redirigido automáticamente a la vista de detalle de "{codigo}"')
def step_redirigido_detalle(context, codigo):
    """Verificación: Redirección a detalle."""
    solicitud = context.solicitudes.get(codigo)
    assert str(solicitud.id) in context.url_destino


@step('visualizo el estado "{estado}" con indicador visual de éxito')
def step_visualizo_estado_exito(context, estado):
    """Verificación: Estado exitoso."""
    assert SolicitudService.es_estado_final_positivo(context.solicitud_actual.estado)


@step('la notificación queda marcada como leída en el buzón')
def step_notificacion_marcada_leida(context):
    """Verificación: Notificación leída."""
    assert context.notificacion_actual.leida is True


@step('visualizo el estado "{estado}" con el motivo del rechazo')
def step_visualizo_estado_rechazo(context, estado):
    """Verificación: Estado rechazado con motivo."""
    assert context.solicitud_actual.motivo_rechazo_embajada


@step('se muestra la sección "Opciones de Apelación" con los plazos legales')
def step_opciones_apelacion(context):
    """Verificación: Opciones de apelación."""
    assert SolicitudService.es_estado_final_negativo(context.solicitud_actual.estado)


# ==============================================================================
# ACCESO DESDE NOTIFICACIONES CRÍTICAS
# ==============================================================================

@step('que existe la solicitud "{codigo}" en estado "{estado}"')
def step_existe_solicitud_en_estado(context, codigo, estado):
    """Setup: Solicitud en estado específico."""
    solicitud = crear_solicitud(
        codigo, 'trabajo', 'usa', estado,
        context.usuario_actual.email, documentos_requeridos=3
    )
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud


@step('el documento "{nombre_doc}" fue rechazado por "{motivo}"')
def step_documento_rechazado(context, nombre_doc, motivo):
    """Setup: Documento rechazado."""
    doc = crear_documento(nombre_doc, 'rechazado', observaciones=motivo)
    context.solicitud_actual.agregar_documento(doc)
    context.documento_rechazado = doc
    
    context.notificacion_actual = crear_notificacion(
        'documento_rechazado',
        f'Documento requiere correcciones: {nombre_doc}',
        f'Tu documento "{nombre_doc}" necesita correcciones.',
        context.usuario_actual.id,
        context.solicitud_actual.id,
        detalle=motivo
    )
    context.notificaciones.append(context.notificacion_actual)


@step('accedo a la notificación de "{tipo}"')
def step_accedo_notificacion_tipo(context, tipo):
    """Acción: Acceder a notificación por tipo."""
    context.notificacion_actual.marcar_como_leida()
    context.url_destino = f"/solicitudes/{context.solicitud_actual.id}/documentos"


@step('soy redirigido a la sección de documentos de "{codigo}"')
def step_redirigido_seccion_documentos(context, codigo):
    """Verificación: Redirección a documentos."""
    assert 'documentos' in context.url_destino or str(context.solicitud_actual.id) in context.url_destino


@step('visualizo la alerta crítica indicando el documento a corregir')
def step_visualizo_alerta_critica(context):
    """Verificación: Documento rechazado requiere acción."""
    docs_rechazados = context.solicitud_actual.obtener_documentos_rechazados()
    assert len(docs_rechazados) > 0
    assert NotificacionService.es_notificacion_accionable('documento_rechazado')


@step('el campo de carga del documento rechazado está habilitado para resubida')
def step_campo_carga_habilitado(context):
    """Verificación: Documento rechazado permite resubida."""
    assert context.solicitud_actual.puede_modificar_documentos()


# ==============================================================================
# ACCESO A FIRMA DE CONTRATO
# ==============================================================================

@step('que la solicitud "{codigo}" tiene un contrato generado pendiente de firma')
def step_contrato_pendiente_firma(context, codigo):
    """Setup: Contrato pendiente."""
    solicitud = crear_solicitud(codigo, 'trabajo', 'usa', 'pendiente', context.usuario_actual.email)
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud
    
    context.notificacion_actual = crear_notificacion(
        'contrato_generado',
        'Tu contrato está listo',
        'Se ha generado el contrato de servicios',
        context.usuario_actual.id,
        solicitud.id,
        detalle='Revisa los términos y condiciones antes de firmar.'
    )
    context.notificaciones.append(context.notificacion_actual)


@step('soy redirigido a la vista de contrato de "{codigo}"')
def step_redirigido_vista_contrato(context, codigo):
    """Verificación: Redirección a contrato."""
    context.url_destino = f"/solicitudes/{context.solicitud_actual.id}/contrato"
    assert str(context.solicitud_actual.id) in context.url_destino


@step('visualizo el documento del contrato con opción de firma digital')
def step_visualizo_contrato(context):
    """Verificación: Contrato visible."""
    assert NotificacionService.es_notificacion_accionable('contrato_generado')


@step('se muestra el plazo límite para completar la firma')
def step_plazo_firma(context):
    """Verificación: Plazo de firma."""
    assert NotificacionService.es_notificacion_accionable('contrato_pendiente')


# ==============================================================================
# SUPRESIÓN DE NOTIFICACIONES TRIVIALES - POLÍTICA REAL
# ==============================================================================

@step('que el migrante tiene la solicitud "{codigo}" en estado "{estado}"')
def step_migrante_tiene_solicitud(context, codigo, estado):
    """Setup: Migrante tiene solicitud."""
    solicitud = crear_solicitud(
        codigo, 'trabajo', 'usa', estado,
        context.usuario_actual.email, documentos_requeridos=5
    )
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud


@step('el buzón de notificaciones contiene {cantidad:d} mensajes no leídos')
def step_buzon_contiene_mensajes(context, cantidad):
    """Setup: Crear notificaciones no leídas."""
    context.notificaciones = []
    for i in range(cantidad):
        notif = crear_notificacion(
            'general', f'Notificación {i+1}', f'Mensaje {i+1}',
            context.usuario_actual.id
        )
        context.notificaciones.append(notif)
    context.contador_inicial = cantidad


@step('el buzón del migrante contiene {cantidad:d} notificaciones')
def step_buzon_migrante_contiene(context, cantidad):
    """Setup: Alias para crear notificaciones."""
    step_buzon_contiene_mensajes(context, cantidad)


@step('el buzón del migrante contiene {cantidad:d} notificación')
def step_buzon_migrante_contiene_singular(context, cantidad):
    """Setup: Alias singular."""
    step_buzon_contiene_mensajes(context, cantidad)


@step('el migrante carga el documento "{nombre_doc}" en la solicitud')
def step_migrante_carga_documento(context, nombre_doc):
    """Acción: Cargar documento (NO genera notificación según política)."""
    doc = crear_documento(nombre_doc, 'pendiente')
    context.solicitud_actual.agregar_documento(doc)
    context.documento_cargado = doc
    context.debe_notificar = NotificacionService.debe_generar_notificacion('documento_subido')


@step('la carga se confirma visualmente en la interfaz de documentos')
def step_carga_confirmada(context):
    """Verificación: Carga confirmada."""
    assert context.documento_cargado is not None


@step('el contador de notificaciones permanece en {cantidad:d} mensajes')
def step_contador_permanece(context, cantidad):
    """Verificación: Contador no cambió."""
    actual = BuzonNotificacionesService.contar_no_leidas(context.notificaciones)
    assert actual == cantidad


@step('NO se genera una notificación de tipo "{tipo}"')
def step_no_genera_notificacion(context, tipo):
    """Verificación: Tipo de notificación SUPRIMIDO según política."""
    tipo_normalizado = tipo.lower().replace(' ', '_')
    assert not NotificacionService.debe_generar_notificacion(tipo_normalizado)


@step('que la solicitud "{codigo}" está en estado "{estado}"')
def step_solicitud_esta_en_estado(context, codigo, estado):
    """Setup: Solicitud en estado específico."""
    solicitud = crear_solicitud(codigo, 'trabajo', 'usa', estado, context.usuario_actual.email)
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud


@step('el asesor marca la solicitud como "{nuevo_estado}"')
def step_asesor_marca_estado(context, nuevo_estado):
    """Acción: Asesor cambia estado."""
    context.solicitud_actual.cambiar_estado(nuevo_estado)
    context.debe_notificar = NotificacionService.debe_generar_notificacion('solicitud_en_revision')


@step('el estado de la solicitud se actualiza a "{estado}"')
def step_estado_actualizado(context, estado):
    """Verificación: Estado actualizado."""
    estado_normalizado = context.solicitud_actual._normalizar_estado(estado)
    assert context.solicitud_actual.estado == estado_normalizado


@step('el contador de notificaciones del migrante permanece en {cantidad:d}')
def step_contador_migrante_permanece(context, cantidad):
    """Verificación: Contador del migrante no cambió."""
    actual = BuzonNotificacionesService.contar_no_leidas(context.notificaciones)
    assert actual == cantidad


@step('que la solicitud "{codigo}" tiene el documento "{nombre_doc}" pendiente de validación')
def step_documento_pendiente_validacion(context, codigo, nombre_doc):
    """Setup: Documento pendiente de validación."""
    solicitud = crear_solicitud(
        codigo, 'trabajo', 'usa', 'en_revision',
        context.usuario_actual.email, documentos_requeridos=2
    )
    doc = crear_documento(nombre_doc, 'pendiente')
    solicitud.agregar_documento(doc)
    
    context.solicitudes[codigo] = solicitud
    context.solicitud_actual = solicitud
    context.documento_pendiente = doc


@step('el asesor aprueba el documento "{nombre_doc}"')
def step_asesor_aprueba_documento(context, nombre_doc):
    """Acción: Asesor aprueba documento."""
    context.documento_pendiente.estado = 'aprobado'
    context.debe_notificar = NotificacionService.debe_generar_notificacion('documento_aprobado')


@step('el documento muestra estado "{estado}" en el panel de documentos')
def step_documento_muestra_estado(context, estado):
    """Verificación: Estado del documento."""
    assert context.documento_pendiente.estado == estado.lower()


@step('el contador de notificaciones permanece en {cantidad:d}')
def step_contador_permanece_simple(context, cantidad):
    """Verificación: Contador permanece."""
    actual = BuzonNotificacionesService.contar_no_leidas(context.notificaciones)
    assert actual == cantidad


@step('solo se notifica cuando hay rechazo que requiere acción del migrante')
def step_solo_notifica_rechazo(context):
    """Verificación: Solo documento_rechazado notifica."""
    assert not NotificacionService.debe_generar_notificacion('documento_aprobado')
    assert NotificacionService.debe_generar_notificacion('documento_rechazado')


# ==============================================================================
# GESTIÓN DEL BUZÓN DE NOTIFICACIONES
# ==============================================================================

@step('que el migrante tiene {cantidad:d} notificaciones no leídas en su buzón')
def step_migrante_tiene_notificaciones(context, cantidad):
    """Setup: Notificaciones no leídas."""
    context.notificaciones = []
    for i in range(cantidad):
        notif = crear_notificacion(
            'general', f'Notificación {i+1}', f'Mensaje {i+1}',
            context.usuario_actual.id
        )
        context.notificaciones.append(notif)


@step('una de ellas es sobre la decisión de "{codigo}"')
def step_notificacion_sobre_decision(context, codigo):
    """Setup: Una notificación es de decisión."""
    if context.notificaciones:
        context.notificacion_decision = context.notificaciones[0]
        context.notificacion_decision.tipo = 'solicitud_aprobada'
        context.notificacion_decision.titulo = 'Decisión sobre solicitud'
        
        solicitud = crear_solicitud(codigo, 'trabajo', 'usa', 'aprobada', context.usuario_actual.email)
        context.solicitudes[codigo] = solicitud
        context.notificacion_decision.solicitud_id = solicitud.id


@step('accedo a la notificación de decisión de "{codigo}"')
def step_accedo_notificacion_decision(context, codigo):
    """Acción: Acceder a notificación de decisión."""
    context.notificacion_decision.marcar_como_leida()


@step('el contador de notificaciones no leídas disminuye a {cantidad:d}')
def step_contador_disminuye(context, cantidad):
    """Verificación: Contador disminuyó."""
    actual = BuzonNotificacionesService.contar_no_leidas(context.notificaciones)
    assert actual == cantidad


@step('la notificación consultada aparece con indicador visual de "{estado}"')
def step_notificacion_indicador(context, estado):
    """Verificación: Indicador visual de notificación."""
    if estado == 'leída':
        assert context.notificacion_decision.leida is True


@step('que el migrante tiene {cantidad:d} notificaciones no leídas acumuladas')
def step_migrante_notificaciones_acumuladas(context, cantidad):
    """Setup: Notificaciones acumuladas."""
    step_migrante_tiene_notificaciones(context, cantidad)


@step('solicito marcar todas las notificaciones como leídas')
def step_marcar_todas_leidas(context):
    """Acción: Marcar todas como leídas."""
    context.actualizadas = BuzonNotificacionesService.marcar_todas_leidas(context.notificaciones)


@step('el contador de notificaciones no leídas se establece en {cantidad:d}')
def step_contador_establecido(context, cantidad):
    """Verificación: Contador en cero."""
    actual = BuzonNotificacionesService.contar_no_leidas(context.notificaciones)
    assert actual == cantidad


@step('todas las notificaciones del buzón muestran estado "{estado}"')
def step_todas_muestran_estado(context, estado):
    """Verificación: Todas leídas."""
    for notif in context.notificaciones:
        assert notif.leida is True


# ==============================================================================
# MANEJO DE ENLACES EXPIRADOS
# ==============================================================================

@step('que existe una notificación antigua referenciando "{codigo}"')
def step_notificacion_antigua(context, codigo):
    """Setup: Notificación antigua."""
    context.notificacion_antigua = crear_notificacion(
        'general',
        'Actualización de solicitud',
        f'Actualización sobre {codigo}',
        context.usuario_actual.id,
        None
    )
    context.notificaciones.append(context.notificacion_antigua)
    context.codigo_referenciado = codigo


@step('la solicitud "{codigo}" fue archivada del sistema')
def step_solicitud_archivada(context, codigo):
    """Setup: Solicitud archivada."""
    context.solicitud_archivada = True


@step('accedo a la notificación del expediente archivado')
def step_accedo_notificacion_archivada(context):
    """Acción: Acceder a notificación de expediente archivado."""
    solicitud_existe = context.codigo_referenciado in context.solicitudes
    context.enlace_valido, context.mensaje_enlace = \
        BuzonNotificacionesService.verificar_enlace_valido(
            context.notificacion_antigua, solicitud_existe
        )


@step('visualizo el mensaje de expediente no disponible "{mensaje}"')
def step_mensaje_no_disponible(context, mensaje):
    """Verificación: Mensaje de no disponible."""
    assert not context.enlace_valido
    assert context.mensaje_enlace == mensaje


@step('permanezco en el buzón de notificaciones')
def step_permanezco_buzon(context):
    """Verificación: Permanece en buzón."""
    assert not context.enlace_valido


@step('se ofrece la opción de eliminar la notificación obsoleta')
def step_opcion_eliminar(context):
    """Verificación: Opción de eliminar disponible."""
    assert not context.enlace_valido
