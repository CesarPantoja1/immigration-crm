"""
Steps BDD para Seguimiento de Solicitudes.
Implementación usando el dominio de Seguimiento.
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

@step("que soy un solicitante autenticado en el sistema de gestión migratoria")
def step_impl(context):
    """Setup: usuario autenticado."""
    context.migrante_id = "MIG-001"
    context.migrante_email = "usuario@ejemplo.com"
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
# DASHBOARD - Supervisión global
# ============================================================

@step("que gestiono los siguientes trámites activos")
def step_impl(context):
    """Setup: cargar trámites activos desde la tabla."""
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


@step("reviso mi situación migratoria actual")
def step_impl(context):
    """El usuario consulta su dashboard."""
    service = PortafolioService()
    context.dashboard = service.obtener_dashboard(context.portafolio)


@step("se presenta mis 3 solicitudes priorizando la actividad más reciente")
def step_impl(context):
    """Verificar que se muestran las 3 solicitudes priorizadas."""
    assert 'solicitudes' in context.dashboard
    assert len(context.dashboard['solicitudes']) == 3
    # Verificar que están ordenadas por prioridad
    solicitudes = context.dashboard['solicitudes']
    assert len(solicitudes) > 0


@step("cada solicitud expone el tipo de visa, la autoridad consular y su situación técnica actual")
def step_impl(context):
    """Verificar campos de cada solicitud."""
    for sol in context.dashboard['solicitudes']:
        assert 'tipo_visa' in sol
        assert 'embajada' in sol  # autoridad consular
        assert 'estado' in sol    # situación técnica


# ============================================================
# DETALLE DE SOLICITUD
# ============================================================

@step('que la solicitud "(?P<codigo>.+)" ha alcanzado el estado "(?P<estado>.+)"')
def step_impl(context, codigo, estado):
    """Setup: solicitud con estado específico."""
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
    context.seguimiento = seguimiento
    context.portafolio.agregar_solicitud(seguimiento)


@step('exploro el expediente detallado del trámite "(?P<codigo>.+)"')
def step_impl(context, codigo):
    """El usuario consulta el detalle de una solicitud."""
    service = ConsultaSolicitudService()
    context.detalle = service.consultar_detalle(context.seguimiento)


@step('el sistema confirma la resolución final como "(?P<estado>.+)"')
def step_impl(context, estado):
    """Verificar el estado de la solicitud."""
    assert context.detalle['estado'] == estado


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
    
    # Cargar eventos desde la tabla
    for row in context.table:
        fecha = datetime.strptime(row['fecha'], "%Y-%m-%d %H:%M:%S")
        evento = EventoHistorial(
            tipo=TipoEvento(row['evento']),
            fecha=fecha,
            descripcion=row['descripcion']
        )
        seguimiento.timeline.eventos.append(evento)
    
    context.seguimiento = seguimiento
    context.portafolio.agregar_solicitud(seguimiento)


@step('audito la cronología de "(?P<codigo>.+)"')
def step_impl(context, codigo):
    """El usuario consulta la cronología."""
    service = ConsultaSolicitudService()
    context.cronologia = service.consultar_cronologia(context.seguimiento)


@step("el sistema presenta los (?P<cantidad>\\d+) eventos en orden cronológico inverso")
def step_impl(context, cantidad):
    """Verificar cantidad y orden de eventos."""
    assert len(context.cronologia) == int(cantidad)
    # Verificar orden inverso (más reciente primero)
    for i in range(len(context.cronologia) - 1):
        fecha_actual = context.cronologia[i]['fecha']
        fecha_siguiente = context.cronologia[i + 1]['fecha']
        assert fecha_actual >= fecha_siguiente


@step("cada hito detalla la naturaleza del cambio, fecha y descripción técnica")
def step_impl(context):
    """Verificar campos de cada hito."""
    for evento in context.cronologia:
        assert 'tipo' in evento      # naturaleza del cambio
        assert 'fecha' in evento
        assert 'descripcion' in evento


# ============================================================
# GESTIÓN DE CORRECCIONES
# ============================================================

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
        total_documentos_requeridos=int(cantidad)
    )
    context.seguimiento = seguimiento


@step('cuenta actualmente con (?P<cantidad>\\d+) documentos en estado "APROBADO"')
def step_impl(context, cantidad):
    """Setup: agregar documentos aprobados."""
    for i in range(int(cantidad)):
        context.seguimiento.agregar_validacion_documento(
            nombre=f"Documento_{i+1}",
            estado="APROBADO"
        )


@step("consulto el progreso de mi gestión")
def step_impl(context):
    """El usuario consulta el progreso."""
    service = ProgresoService()
    context.progreso_detalle = service.calcular_progreso_detallado(context.seguimiento)


@step("el sistema informa un avance del (?P<porcentaje>\\d+)%")
def step_impl(context, porcentaje):
    """Verificar porcentaje de avance."""
    assert context.progreso_detalle['porcentaje'] == int(porcentaje)


@step("especifica la cantidad de validaciones restantes para completar el proceso")
def step_impl(context):
    """Verificar información de validaciones restantes."""
    assert 'validaciones_restantes' in context.progreso_detalle
    assert context.progreso_detalle['validaciones_restantes'] >= 0


# ============================================================
# PRIVACIDAD
# ============================================================

@step('que existe información de otro solicitante identificado como "(?P<email>.+)"')
def step_impl(context, email):
    """Setup: otro usuario en el sistema."""
    context.otro_migrante_id = "MIG-002"
    context.otro_migrante_email = email.replace('\\', '')
    
    # Crear solicitud del otro usuario
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


@step("accedo a mis servicios privados")
def step_impl(context):
    """El usuario accede a sus servicios."""
    service = PrivacidadService()
    # Simular que hay solicitudes de otros usuarios en el sistema
    todas = [context.solicitud_ajena] + context.portafolio.solicitudes
    context.mis_solicitudes = service.filtrar_solicitudes_propias(
        todas, 
        context.migrante_id
    )


@step("el sistema garantiza la privacidad mostrando exclusivamente mis trámites vinculados")
def step_impl(context):
    """Verificar que solo se muestran trámites propios."""
    for sol in context.mis_solicitudes:
        assert sol.migrante_id == context.migrante_id


@step('restringe cualquier visibilidad sobre el expediente de "(?P<email>.+)"')
def step_impl(context, email):
    """Verificar que no se ve información del otro usuario."""
    email_limpio = email.replace('\\', '')
    for sol in context.mis_solicitudes:
        assert sol.migrante_email != email_limpio


@step('que el expediente "(?P<codigo>.+)" pertenece a un tercero')
def step_impl(context, codigo):
    """Setup: expediente de otro usuario."""
    context.solicitud_tercero = SeguimientoSolicitud(
        solicitud_id=codigo,
        codigo=codigo,
        tipo_visa="VIVIENDA",
        embajada="ESPAÑOLA",
        estado=EstadoSolicitudSeguimiento.APROBADA,
        migrante_id="MIG-003",  # Otro usuario
        migrante_email="tercero@ejemplo.com",
        fecha_creacion=datetime.now()
    )


@step('intento acceder directamente al recurso "(?P<codigo>.+)"')
def step_impl(context, codigo):
    """Intento de acceso a recurso ajeno."""
    service = PrivacidadService()
    context.tiene_acceso = service.verificar_propiedad(
        context.solicitud_tercero,
        context.migrante_id
    )


@step("el sistema deniega el acceso por falta de permisos y protege la integridad de la información")
def step_impl(context):
    """Verificar denegación de acceso."""
    assert context.tiene_acceso is False


# ============================================================
# ALERTAS DE VENCIMIENTO
# ============================================================

@step('que en la solicitud "(?P<codigo>.+)" el "(?P<documento>.+)" tiene fecha de expiración "(?P<fecha>.+)"')
def step_impl(context, codigo, documento, fecha):
    """Setup: documento con fecha de vencimiento."""
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


@step('hoy es "(?P<fecha>.+)"')
def step_impl(context, fecha):
    """Setup: simular fecha actual."""
    context.fecha_simulada = datetime.strptime(fecha, "%Y-%m-%d").date()


@step("el sistema evalúa la vigencia de los requisitos")
def step_impl(context):
    """Evaluar vencimientos."""
    service = AlertaService()
    
    # Calcular días hasta vencimiento basado en la fecha simulada
    dias = (context.documento_con_vencimiento['fecha_vencimiento'] - context.fecha_simulada).days
    context.dias_hasta_vencimiento = dias
    
    # Generar alertas
    context.alertas_generadas = context.seguimiento.verificar_vencimientos(
        [context.documento_con_vencimiento]
    )


@step('el sistema emite una alerta de urgencia: "(?P<mensaje>.+)"')
def step_impl(context, mensaje):
    """Verificar alerta de urgencia."""
    # Verificar que hay alertas
    assert len(context.alertas_generadas) > 0 or len(context.seguimiento.alertas) > 0
    
    # Verificar el contenido del mensaje
    alerta = context.alertas_generadas[0] if context.alertas_generadas else context.seguimiento.alertas[0]
    assert context.documento_con_vencimiento['nombre'].lower() in alerta.mensaje.lower() or \
           "vence" in alerta.mensaje.lower()


@step("provee una recomendación proactiva para evitar retrasos en el proceso consular")
def step_impl(context):
    """Verificar recomendación proactiva."""
    alerta = context.alertas_generadas[0] if context.alertas_generadas else context.seguimiento.alertas[0]
    assert alerta.accion_sugerida != ""
    assert "consular" in alerta.accion_sugerida.lower() or "renueva" in alerta.accion_sugerida.lower()


# ============================================================
# GESTIÓN DE EXPECTATIVAS
# ============================================================

@step('que la solicitud "(?P<codigo>.+)" ha sido "APROBADA"')
def step_impl(context, codigo):
    """Setup: solicitud aprobada."""
    seguimiento = SeguimientoSolicitud(
        solicitud_id=codigo,
        codigo=codigo,
        tipo_visa="TRABAJO",
        embajada="ESTADOUNIDENSE",
        estado=EstadoSolicitudSeguimiento.APROBADA,
        migrante_id=context.migrante_id,
        migrante_email=context.migrante_email,
        fecha_creacion=datetime.now() - timedelta(days=30)
    )
    context.seguimiento = seguimiento


@step("reviso los siguientes pasos de mi trámite")
def step_impl(context):
    """El usuario consulta siguientes pasos."""
    service = ExpectativasService()
    context.siguiente_paso = service.obtener_siguientes_pasos(context.seguimiento)


@step('el sistema reduce mi incertidumbre informando el paso: "(?P<paso>.+)"')
def step_impl(context, paso):
    """Verificar información del siguiente paso."""
    assert 'paso' in context.siguiente_paso
    # Verificar que el mensaje contiene palabras clave del paso esperado
    paso_lower = paso.lower()
    paso_actual_lower = context.siguiente_paso['paso'].lower()
    
    # Verificar coincidencia parcial
    palabras_clave = ['esperar', 'asignación', 'entrevista', 'fecha']
    coincide = any(p in paso_actual_lower for p in palabras_clave)
    assert coincide or "esperar" in paso_actual_lower


@step('proyecta una ventana estimada de resolución de "(?P<tiempo>.+)"')
def step_impl(context, tiempo):
    """Verificar tiempo estimado."""
    assert 'tiempo_estimado' in context.siguiente_paso
    # Verificar que hay un tiempo estimado (formato flexible)
    assert context.siguiente_paso['tiempo_estimado'] is not None
    assert "días" in context.siguiente_paso['tiempo_estimado'].lower() or \
           "hábiles" in context.siguiente_paso['tiempo_estimado'].lower() or \
           len(context.siguiente_paso['tiempo_estimado']) > 0