# -*- coding: utf-8 -*-
"""
Steps para los escenarios de Alertas de Entrevistas.
Implementación de los pasos BDD definidos en alertas_entrevista.feature

Este archivo contiene SOLO las definiciones de steps.
La lógica de negocio está en: features/notificaciones/business_logic/

REFACTORIZADO: Steps delgados que solo orquestan, sin reglas de negocio ni ORM.
"""
import os
import sys

# Configurar Django ANTES de importar
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')

import django
django.setup()

from behave import step, use_step_matcher
from dataclasses import dataclass, field
from typing import Dict, Optional, List

# Importar desde business_logic (n-capas con Service Layer)
from features.notificaciones.business_logic import (
    # Entidades
    EntrevistaEntity,
    SimulacroEntity,
    RecomendacionesEntity,
    CentroNotificacionesEntity,
    crear_entrevista,
    crear_simulacro,
    crear_recomendaciones,
    crear_centro_notificaciones,
    reset_id_counters,
    # Servicios
    EntrevistaAlertasService,
    RecordatorioAlertasService,
    PreparacionAlertasService,
    SimulacroAlertasService,
    AlertasEntrevistaService,
    NotificacionService,
    BuzonNotificacionesService,
    # Constantes
    VENTANAS_RECORDATORIO,
    VENTANAS_PREPARACION,
)

use_step_matcher("parse")


# ==============================================================================
# CLASE AUXILIAR: Estado del Sistema para Testing
# ==============================================================================

@dataclass
class NotificacionData:
    """Datos de una notificación en memoria (sin ORM)."""
    tipo: str
    id_solicitud: Optional[str] = None
    id_simulacro: Optional[str] = None
    fecha_hora_entrevista: Optional[str] = None
    fecha_hora_anterior: Optional[str] = None
    nueva_fecha_hora: Optional[str] = None
    detalle: Optional[str] = None
    leida: bool = False


@dataclass
class SolicitudData:
    """Datos de una solicitud en memoria (sin ORM)."""
    id: str
    estado: str
    asesor: Optional[str] = None
    entrevista: Optional[EntrevistaEntity] = None


@dataclass
class SistemaAlertasEntrevista:
    """
    Estado del sistema para testing de alertas.
    Contiene datos en memoria sin dependencia de ORM.
    """
    # Estado de autenticación
    solicitante_autenticado: bool = False
    asesor_autenticado: bool = False
    asesor_actual: Optional[str] = None

    # Datos en memoria
    solicitudes: Dict[str, SolicitudData] = field(default_factory=dict)
    entrevistas: Dict[str, EntrevistaEntity] = field(default_factory=dict)
    simulacros: Dict[str, SimulacroEntity] = field(default_factory=dict)
    recomendaciones: Dict[str, RecomendacionesEntity] = field(default_factory=dict)

    # Centros de notificaciones
    notificaciones_migrante: List[NotificacionData] = field(default_factory=list)
    notificaciones_asesor: List[NotificacionData] = field(default_factory=list)

    # Configuración
    tipos_notificacion: List[str] = field(default_factory=list)
    ventanas_recordatorio: List[str] = field(default_factory=list)
    ventanas_preparacion: List[str] = field(default_factory=list)

    # Estado temporal
    fecha_hora_actual: Optional[str] = None

    def agregar_notificacion_migrante(self, notif: NotificacionData):
        """Agrega notificación al centro del migrante."""
        self.notificaciones_migrante.append(notif)

    def agregar_notificacion_asesor(self, notif: NotificacionData):
        """Agrega notificación al centro del asesor."""
        self.notificaciones_asesor.append(notif)

    def total_notificaciones_migrante(self) -> int:
        return len(self.notificaciones_migrante)

    def total_notificaciones_asesor(self) -> int:
        return len(self.notificaciones_asesor)

    def ultima_notificacion_migrante(self) -> Optional[NotificacionData]:
        return self.notificaciones_migrante[-1] if self.notificaciones_migrante else None

    def ultima_notificacion_asesor(self) -> Optional[NotificacionData]:
        return self.notificaciones_asesor[-1] if self.notificaciones_asesor else None

    def buscar_notificacion(self, lista: List[NotificacionData], criterios: dict) -> Optional[NotificacionData]:
        """Busca una notificación que coincida con los criterios."""
        for notif in reversed(lista):
            coincide = True
            for key, value in criterios.items():
                attr_name = key.replace(' ', '_').replace('-', '_')
                attr_value = getattr(notif, attr_name, None)
                if str(attr_value) != str(value):
                    coincide = False
                    break
            if coincide:
                return notif
        return None


# ==============================================================================
# ANTECEDENTES
# ==============================================================================

@step('que soy un solicitante autenticado en el sistema de gestión migratoria')
def paso_solicitante_autenticado(context):
    """Setup: Usuario autenticado como solicitante."""
    reset_id_counters()
    context.sistema = SistemaAlertasEntrevista()
    context.sistema.solicitante_autenticado = True
    assert context.sistema.solicitante_autenticado is True


@step('gestiono la solicitud "{id_solicitud}" en estado "{estado}"')
def paso_gestiona_solicitud(context, id_solicitud, estado):
    """Setup: Registrar solicitud en el sistema."""
    context.sistema.solicitudes[id_solicitud] = SolicitudData(id=id_solicitud, estado=estado)
    assert context.sistema.solicitudes[id_solicitud].estado == estado


@step('tengo asignado al asesor "{asesor}"')
def paso_asignar_asesor(context, asesor):
    """Setup: Asignar asesor a las solicitudes."""
    for id_solicitud in context.sistema.solicitudes:
        context.sistema.solicitudes[id_solicitud].asesor = asesor
        assert context.sistema.solicitudes[id_solicitud].asesor == asesor


@step("el catálogo de tipos de notificación incluye")
def paso_catalogo_notificaciones(context):
    """Setup: Configurar tipos de notificación."""
    tipos = [row["tipo"] for row in context.table]
    context.sistema.tipos_notificacion = tipos
    assert len(context.sistema.tipos_notificacion) == len(tipos)


@step("el sistema tiene configuradas ventanas de recordatorio de entrevista")
def paso_ventanas_recordatorio(context):
    """Setup: Configurar ventanas de recordatorio."""
    ventanas = [row["ventana"] for row in context.table]
    context.sistema.ventanas_recordatorio = ventanas
    assert len(context.sistema.ventanas_recordatorio) == len(ventanas)


@step("el sistema tiene configurada una ventana de control de preparación")
def paso_ventanas_preparacion(context):
    """Setup: Configurar ventanas de preparación."""
    ventanas = [row["ventana"] for row in context.table]
    context.sistema.ventanas_preparacion = ventanas
    assert len(context.sistema.ventanas_preparacion) == len(ventanas)


# ==============================================================================
# ENTREVISTA AGENDADA
# ==============================================================================

@step('que la solicitud "{id_solicitud}" no tiene entrevista registrada')
def paso_solicitud_sin_entrevista(context, id_solicitud):
    """Setup: Asegurar que no hay entrevista."""
    if id_solicitud in context.sistema.solicitudes:
        context.sistema.solicitudes[id_solicitud].entrevista = None
    if id_solicitud in context.sistema.entrevistas:
        del context.sistema.entrevistas[id_solicitud]
    assert context.sistema.solicitudes[id_solicitud].entrevista is None


@step('el asesor "{asesor}" registra una entrevista para "{id_solicitud}" en "{fecha_hora}"')
def paso_registra_entrevista(context, asesor, id_solicitud, fecha_hora):
    """Acción: Registrar entrevista usando servicio."""
    # Crear entrevista usando servicio
    datos = EntrevistaAlertasService.registrar_entrevista(id_solicitud, fecha_hora)

    # Crear entidad
    entrevista = crear_entrevista(id_solicitud, fecha_hora, datos['estado'])
    context.sistema.entrevistas[id_solicitud] = entrevista
    context.sistema.solicitudes[id_solicitud].entrevista = entrevista

    # Crear notificación usando orquestador
    notif_data = AlertasEntrevistaService.crear_notificacion_entrevista(
        tipo=datos['tipo_notificacion'],
        solicitud_id=id_solicitud,
        fecha_hora=fecha_hora
    )
    context.sistema.agregar_notificacion_migrante(NotificacionData(**notif_data))

    assert context.sistema.solicitudes[id_solicitud].entrevista is not None


use_step_matcher("re")


@step(r"en el centro de notificaciones del migrante aparece una notificaci.n nueva con:?")
def paso_notificacion_migrante(context):
    """Verificación: Notificación en centro del migrante."""
    esperado = {heading: context.table[0][heading] for heading in context.table.headings}
    notificacion = context.sistema.buscar_notificacion(
        context.sistema.notificaciones_migrante, esperado
    )
    assert notificacion is not None, f"No se encontró notificación: {esperado}"


@step(r"en el centro de notificaciones del asesor aparece una notificaci.n nueva con:?")
def paso_notificacion_asesor(context):
    """Verificación: Notificación en centro del asesor."""
    esperado = {heading: context.table[0][heading] for heading in context.table.headings}
    notificacion = context.sistema.buscar_notificacion(
        context.sistema.notificaciones_asesor, esperado
    )
    assert notificacion is not None, f"No se encontró notificación: {esperado}"


use_step_matcher("parse")


@step('la notificación queda asociada a la solicitud "{id_solicitud}" al abrir su detalle')
def paso_notificacion_asociada(context, id_solicitud):
    """Verificación: Notificación asociada a solicitud."""
    notificacion = context.sistema.ultima_notificacion_migrante()
    assert notificacion is not None, "No hay notificaciones"
    assert notificacion.id_solicitud == id_solicitud


# ==============================================================================
# RECORDATORIOS
# ==============================================================================

@step('que la solicitud "{id_solicitud}" tiene una entrevista "{estado}" para "{fecha_hora}"')
def paso_entrevista_programada(context, id_solicitud, estado, fecha_hora):
    """Setup: Crear entrevista con estado."""
    entrevista = crear_entrevista(id_solicitud, fecha_hora, estado)
    context.sistema.entrevistas[id_solicitud] = entrevista
    if id_solicitud in context.sistema.solicitudes:
        context.sistema.solicitudes[id_solicitud].entrevista = entrevista
    assert entrevista is not None


@step('la fecha y hora actual del sistema es "{fecha_hora}"')
def paso_fecha_actual(context, fecha_hora):
    """Setup: Establecer fecha/hora actual."""
    context.sistema.fecha_hora_actual = fecha_hora
    assert context.sistema.fecha_hora_actual is not None


@step('el sistema evalúa recordatorios configurados para la entrevista de "{id_solicitud}"')
def paso_evalua_recordatorios(context, id_solicitud):
    """Acción: Evaluar recordatorios usando servicio."""
    context.indice_notificaciones_migrante = context.sistema.total_notificaciones_migrante()

    entrevista = context.sistema.entrevistas.get(id_solicitud)
    if not entrevista:
        return

    # Usar servicio para determinar si emitir recordatorio
    debe_emitir, ventana = RecordatorioAlertasService.debe_emitir_recordatorio(
        estado_entrevista=entrevista.estado,
        fecha_hora_entrevista=entrevista.fecha_hora,
        fecha_hora_actual=context.sistema.fecha_hora_actual,
        ventanas_configuradas=context.sistema.ventanas_recordatorio
    )

    if debe_emitir:
        # Generar detalle usando servicio
        detalle = RecordatorioAlertasService.generar_detalle_recordatorio(ventana)

        # Crear notificación
        notif_data = AlertasEntrevistaService.crear_notificacion_entrevista(
            tipo='Recordatorio entrevista',
            solicitud_id=id_solicitud,
            fecha_hora=entrevista.fecha_hora,
            detalle=detalle
        )
        context.sistema.agregar_notificacion_migrante(NotificacionData(**notif_data))


@step('el detalle de la notificación es "{detalle}"')
def paso_detalle_notificacion(context, detalle):
    """Verificación: Detalle de notificación."""
    notificacion = None
    if context.sistema.asesor_autenticado:
        notificacion = context.sistema.ultima_notificacion_asesor()
    if notificacion is None:
        notificacion = context.sistema.ultima_notificacion_migrante()

    assert notificacion is not None, "No hay notificaciones"
    assert notificacion.detalle == detalle, f"Detalle esperado: {detalle}, Obtenido: {notificacion.detalle}"


# ==============================================================================
# REPROGRAMACIÓN
# ==============================================================================

@step('el asesor "{asesor}" reprograma la entrevista de "{id_solicitud}" a "{fecha_hora}"')
def paso_reprograma_entrevista(context, asesor, id_solicitud, fecha_hora):
    """Acción: Reprogramar entrevista usando servicio."""
    entrevista = context.sistema.entrevistas.get(id_solicitud)
    fecha_anterior = entrevista.fecha_hora if entrevista else None

    # Usar servicio
    datos = EntrevistaAlertasService.reprogramar_entrevista(fecha_anterior, fecha_hora)

    # Actualizar entidad
    if entrevista:
        entrevista.reprogramar(fecha_hora)
    else:
        entrevista = crear_entrevista(id_solicitud, fecha_hora, 'Reprogramada')
        entrevista.fecha_hora_anterior = fecha_anterior
        context.sistema.entrevistas[id_solicitud] = entrevista

    if id_solicitud in context.sistema.solicitudes:
        context.sistema.solicitudes[id_solicitud].entrevista = entrevista

    # Crear notificación
    notif_data = AlertasEntrevistaService.crear_notificacion_entrevista(
        tipo=datos['tipo_notificacion'],
        solicitud_id=id_solicitud,
        fecha_hora_anterior=datos['fecha_hora_anterior'],
        nueva_fecha_hora=datos['nueva_fecha_hora']
    )
    context.sistema.agregar_notificacion_migrante(NotificacionData(**notif_data))

    assert entrevista.estado == "Reprogramada"


@step('previamente estuvo "{estado}" para "{fecha_hora}"')
def paso_entrevista_anterior(context, estado, fecha_hora):
    """Setup: Establecer fecha anterior de entrevista."""
    for id_solicitud, entrevista in context.sistema.entrevistas.items():
        entrevista.fecha_hora_anterior = fecha_hora


@step('no aparece ninguna notificación nueva de tipo "{tipo}" asociada a "{fecha_hora}"')
def paso_sin_notificacion_tipo_fecha(context, tipo, fecha_hora):
    """Verificación: No hay notificación con tipo y fecha específicos."""
    nuevas = context.sistema.notificaciones_migrante[context.indice_notificaciones_migrante:]
    coincidencias = [
        item for item in nuevas
        if item.tipo == tipo and item.fecha_hora_entrevista == fecha_hora
    ]
    assert not coincidencias, f"Se encontraron notificaciones inesperadas: {coincidencias}"


@step('el contador de notificaciones de tipo "{tipo}" para la solicitud "{id_solicitud}" no aumenta')
def paso_contador_tipo_no_aumenta(context, tipo, id_solicitud):
    """Verificación: Contador de tipo no aumentó."""
    notificaciones = context.sistema.notificaciones_migrante
    previas = sum(
        1 for item in notificaciones[:context.indice_notificaciones_migrante]
        if item.tipo == tipo and item.id_solicitud == id_solicitud
    )
    actuales = sum(
        1 for item in notificaciones
        if item.tipo == tipo and item.id_solicitud == id_solicitud
    )
    assert actuales == previas


# ==============================================================================
# CANCELACIÓN
# ==============================================================================

@step('el asesor "{asesor}" cancela la entrevista de "{id_solicitud}"')
def paso_cancela_entrevista(context, asesor, id_solicitud):
    """Acción: Cancelar entrevista usando servicio."""
    entrevista = context.sistema.entrevistas.get(id_solicitud)
    fecha_hora = entrevista.fecha_hora if entrevista else None

    # Usar servicio
    datos = EntrevistaAlertasService.cancelar_entrevista(fecha_hora)

    # Actualizar entidad
    if entrevista:
        entrevista.cancelar()

    # Crear notificación
    notif_data = AlertasEntrevistaService.crear_notificacion_entrevista(
        tipo=datos['tipo_notificacion'],
        solicitud_id=id_solicitud,
        fecha_hora=datos['fecha_hora']
    )
    context.sistema.agregar_notificacion_migrante(NotificacionData(**notif_data))

    assert entrevista.estado == "Cancelada"


@step('que la solicitud "{id_solicitud}" tiene una entrevista en estado "{estado}"')
def paso_entrevista_estado(context, id_solicitud, estado):
    """Setup: Crear entrevista con estado específico."""
    entrevista = context.sistema.entrevistas.get(id_solicitud)
    if entrevista:
        entrevista.estado = estado
    else:
        entrevista = crear_entrevista(id_solicitud, "", estado)
        context.sistema.entrevistas[id_solicitud] = entrevista

    if id_solicitud in context.sistema.solicitudes:
        context.sistema.solicitudes[id_solicitud].entrevista = entrevista

    assert entrevista.estado == estado


@step('la entrevista cancelada correspondía a "{fecha_hora}"')
def paso_entrevista_cancelada_fecha(context, fecha_hora):
    """Setup: Establecer fecha de entrevista cancelada."""
    for id_solicitud, entrevista in context.sistema.entrevistas.items():
        entrevista.fecha_hora = fecha_hora


@step('no aparece ninguna notificación nueva de tipo "{tipo}"')
def paso_sin_notificacion_tipo(context, tipo):
    """Verificación: No hay notificación de tipo específico."""
    nuevas = context.sistema.notificaciones_migrante[context.indice_notificaciones_migrante:]
    coincidencias = [item for item in nuevas if item.tipo == tipo]
    assert not coincidencias, f"Se encontraron notificaciones inesperadas: {coincidencias}"


@step('el contador de notificaciones no aumenta para la solicitud "{id_solicitud}"')
def paso_contador_no_aumenta(context, id_solicitud):
    """Verificación: Contador no aumentó."""
    notificaciones = context.sistema.notificaciones_migrante
    previas = sum(
        1 for item in notificaciones[:context.indice_notificaciones_migrante]
        if item.id_solicitud == id_solicitud
    )
    actuales = sum(1 for item in notificaciones if item.id_solicitud == id_solicitud)
    assert actuales == previas


# ==============================================================================
# PREPARACIÓN
# ==============================================================================

@step('no existe un simulacro en estado "{estado}" asociado a "{id_solicitud}"')
def paso_sin_simulacro_confirmado(context, estado, id_solicitud):
    """Setup: Asegurar que no hay simulacro en estado dado."""
    to_delete = [
        sim_id for sim_id, sim in context.sistema.simulacros.items()
        if sim.solicitud_id == id_solicitud and sim.estado == estado
    ]
    for sim_id in to_delete:
        del context.sistema.simulacros[sim_id]


@step('el sistema evalúa el estado de preparación para la entrevista de "{id_solicitud}"')
def paso_evalua_preparacion(context, id_solicitud):
    """Acción: Evaluar preparación usando servicio."""
    context.indice_notificaciones_migrante = context.sistema.total_notificaciones_migrante()

    entrevista = context.sistema.entrevistas.get(id_solicitud)
    if not entrevista or not entrevista.fecha_hora:
        return

    # Usar servicio
    debe_alertar = PreparacionAlertasService.debe_alertar_preparacion(
        fecha_hora_entrevista=entrevista.fecha_hora,
        fecha_hora_actual=context.sistema.fecha_hora_actual,
        solicitud_id=id_solicitud,
        simulacros=context.sistema.simulacros,
        ventana_dias=7
    )

    if debe_alertar:
        notif_data = AlertasEntrevistaService.crear_notificacion_entrevista(
            tipo='Preparación recomendada',
            solicitud_id=id_solicitud,
            detalle='Realizar simulación de entrevista'
        )
        context.sistema.agregar_notificacion_migrante(NotificacionData(**notif_data))


# ==============================================================================
# SIMULACIÓN / RECOMENDACIONES
# ==============================================================================

@step('que el asesor "{asesor}" está autenticado en el sistema')
def paso_asesor_autenticado(context, asesor):
    """Setup: Autenticar asesor."""
    if not hasattr(context, 'sistema') or context.sistema is None:
        reset_id_counters()
        context.sistema = SistemaAlertasEntrevista()
    context.sistema.asesor_autenticado = True
    context.sistema.asesor_actual = asesor
    assert context.sistema.asesor_autenticado is True


@step('existe un simulacro "{id_simulacro}" asociado a la solicitud "{id_solicitud}"')
def paso_existe_simulacro(context, id_simulacro, id_solicitud):
    """Setup: Crear simulacro."""
    simulacro = crear_simulacro(id_simulacro, id_solicitud)
    context.sistema.simulacros[id_simulacro] = simulacro
    assert id_simulacro in context.sistema.simulacros


@step('el simulacro "{id_simulacro}" está en estado "{estado}"')
def paso_simulacro_estado(context, id_simulacro, estado):
    """Setup: Establecer estado de simulacro."""
    if id_simulacro in context.sistema.simulacros:
        context.sistema.simulacros[id_simulacro].estado = estado
    assert context.sistema.simulacros[id_simulacro].estado == estado


@step('el simulacro "{id_simulacro}" cambia a estado "{estado}"')
def paso_simulacro_cambia(context, id_simulacro, estado):
    """Acción: Cambiar estado de simulacro."""
    simulacro = context.sistema.simulacros.get(id_simulacro)
    estado_anterior = simulacro.estado if simulacro else None

    if simulacro:
        simulacro.estado = estado

    # Verificar si debe notificar usando servicio
    if SimulacroAlertasService.puede_notificar_completado(estado_anterior, estado):
        notif_data = AlertasEntrevistaService.crear_notificacion_simulacro(
            tipo='Simulación completada',
            simulacro_id=id_simulacro,
            detalle='Generar recomendaciones'
        )
        context.sistema.agregar_notificacion_asesor(NotificacionData(**notif_data))


@step('que existe un documento de recomendaciones para el simulacro "{id_simulacro}" en estado "{estado}"')
def paso_documento_recomendaciones(context, id_simulacro, estado):
    """Setup: Crear documento de recomendaciones."""
    if not hasattr(context, 'sistema') or context.sistema is None:
        reset_id_counters()
        context.sistema = SistemaAlertasEntrevista()
        context.sistema.solicitante_autenticado = True

    recomendaciones = crear_recomendaciones(id_simulacro, estado)
    context.sistema.recomendaciones[id_simulacro] = recomendaciones
    assert id_simulacro in context.sistema.recomendaciones


@step('el documento de recomendaciones del simulacro "{id_simulacro}" se publica en el sistema')
def paso_publica_recomendaciones(context, id_simulacro):
    """Acción: Publicar recomendaciones."""
    recomendaciones = context.sistema.recomendaciones.get(id_simulacro)
    if recomendaciones:
        recomendaciones.publicar()

    # Verificar si debe notificar
    if SimulacroAlertasService.puede_notificar_recomendaciones(recomendaciones.estado):
        notif_data = AlertasEntrevistaService.crear_notificacion_simulacro(
            tipo='Recomendaciones listas',
            simulacro_id=id_simulacro
        )
        context.sistema.agregar_notificacion_migrante(NotificacionData(**notif_data))


# ==============================================================================
# NAVEGACIÓN CONTEXTUAL (Deep Linking)
# ==============================================================================

@step('que la solicitud "{codigo}" tiene una entrevista programada para "{fecha_hora}"')
def step_solicitud_entrevista_programada(context, codigo, fecha_hora):
    """Setup: Solicitud con entrevista programada."""
    context.solicitud_codigo = codigo
    context.entrevista_fecha_hora = fecha_hora

    # Crear entrevista
    entrevista = crear_entrevista(codigo, fecha_hora, 'Programada')
    context.sistema.entrevistas[codigo] = entrevista
    context.sistema.solicitudes[codigo] = SolicitudData(
        id=codigo, estado='APROBADA', entrevista=entrevista
    )


@step('el migrante recibe la notificación de "{tipo_notificacion}"')
def step_migrante_recibe_notificacion_entrevista(context, tipo_notificacion):
    """Setup: Notificación recibida."""
    context.notificacion_tipo = tipo_notificacion
    context.notificacion_leida = False


@step('accedo a la notificación de cita consular asignada')
def step_accedo_notificacion_cita(context):
    """Acción: Acceder a notificación."""
    context.navegacion_destino = f"/solicitudes/{context.solicitud_codigo}/entrevista"
    context.notificacion_leida = True


@step('soy redirigido a la vista de entrevista de "{codigo}"')
def step_redirigido_vista_entrevista(context, codigo):
    """Verificación: Redirección correcta."""
    expected_url = f"/solicitudes/{codigo}/entrevista"
    assert context.navegacion_destino == expected_url, \
        f"Esperaba {expected_url}, pero fue {context.navegacion_destino}"


@step('visualizo la fecha "{fecha}" y hora "{hora}" de la cita')
def step_visualizo_fecha_hora_cita(context, fecha, hora):
    """Verificación: Visualización de fecha y hora."""
    context.fecha_cita_visible = fecha
    context.hora_cita_visible = hora


@step('se muestra la dirección del consulado y documentos requeridos para el día')
def step_muestra_direccion_consulado(context):
    """Verificación: Información del consulado."""
    context.direccion_consulado_visible = True
    context.documentos_requeridos_visible = True


@step('la notificación queda marcada como leída')
def step_notificacion_queda_leida(context):
    """Verificación: Notificación marcada como leída."""
    assert context.notificacion_leida is True


@step('que la entrevista de "{codigo}" fue reprogramada de "{fecha_anterior}" a "{nueva_fecha}"')
def step_entrevista_reprogramada(context, codigo, fecha_anterior, nueva_fecha):
    """Setup: Entrevista reprogramada."""
    context.solicitud_codigo = codigo
    context.fecha_anterior = fecha_anterior
    context.nueva_fecha = nueva_fecha


@step('accedo a la notificación de cambio de fecha')
def step_accedo_notificacion_cambio_fecha(context):
    """Acción: Acceder a notificación de reprogramación."""
    context.navegacion_destino = f"/solicitudes/{context.solicitud_codigo}/entrevista"
    context.notificacion_leida = True


@step('visualizo la nueva fecha "{fecha}" claramente destacada')
def step_visualizo_nueva_fecha(context, fecha):
    """Verificación: Nueva fecha destacada."""
    context.nueva_fecha_destacada = fecha


@step('se muestra un comparativo con la fecha anterior tachada')
def step_muestra_comparativo_fechas(context):
    """Verificación: Comparativo de fechas."""
    context.comparativo_visible = True
    context.fecha_anterior_tachada = True


@step('que faltan {horas:d} horas para la entrevista de "{codigo}"')
def step_faltan_horas_entrevista(context, horas, codigo):
    """Setup: Tiempo restante."""
    context.solicitud_codigo = codigo
    context.horas_restantes = horas


@step('el migrante recibe el recordatorio de proximidad de cita')
def step_recibe_recordatorio_proximidad(context):
    """Setup: Recordatorio recibido."""
    context.recordatorio_recibido = True


@step('accedo al recordatorio de entrevista próxima')
def step_accedo_recordatorio(context):
    """Acción: Acceder al recordatorio."""
    context.navegacion_destino = f"/solicitudes/{context.solicitud_codigo}/entrevista"
    context.notificacion_leida = True


@step('visualizo el checklist de preparación con los elementos pendientes')
def step_visualizo_checklist(context):
    """Verificación: Checklist visible."""
    context.checklist_visible = True


@step('se destaca la cuenta regresiva "{mensaje}"')
def step_cuenta_regresiva(context, mensaje):
    """Verificación: Cuenta regresiva."""
    context.cuenta_regresiva_mensaje = mensaje


@step('que existe un simulacro "{id_simulacro}" confirmado para "{codigo}"')
def step_simulacro_confirmado(context, id_simulacro, codigo):
    """Setup: Simulacro confirmado."""
    context.simulacro_id = id_simulacro
    context.solicitud_codigo = codigo
    simulacro = crear_simulacro(id_simulacro, codigo, 'Confirmado')
    context.sistema.simulacros[id_simulacro] = simulacro


@step('accedo a la notificación de práctica programada')
def step_accedo_notificacion_simulacro(context):
    """Acción: Acceder a notificación de simulacro."""
    context.navegacion_destino = f"/simulacros/{context.simulacro_id}"
    context.notificacion_leida = True


@step('soy redirigido a la vista de detalle del simulacro "{id_simulacro}"')
def step_redirigido_vista_simulacro(context, id_simulacro):
    """Verificación: Redirección a simulacro."""
    expected_url = f"/simulacros/{id_simulacro}"
    assert context.navegacion_destino == expected_url


@step('visualizo la fecha, hora y enlace de videoconferencia del simulacro')
def step_visualizo_detalle_simulacro(context):
    """Verificación: Detalles del simulacro."""
    context.detalle_simulacro_visible = True


@step('se muestra el botón para unirse a la sesión cuando esté activa')
def step_boton_unirse_sesion(context):
    """Verificación: Botón de unirse."""
    context.boton_unirse_visible = True


@step('que el asesor propuso el simulacro "{id_simulacro}" para "{codigo}"')
def step_asesor_propuso_simulacro(context, id_simulacro, codigo):
    """Setup: Simulacro propuesto."""
    context.simulacro_id = id_simulacro
    context.solicitud_codigo = codigo
    simulacro = crear_simulacro(id_simulacro, codigo, 'Propuesto')
    context.sistema.simulacros[id_simulacro] = simulacro


@step('el simulacro está en estado "Propuesto" pendiente de aceptación')
def step_simulacro_pendiente_aceptacion(context):
    """Verificación: Estado propuesto."""
    simulacro = context.sistema.simulacros.get(context.simulacro_id)
    assert simulacro.estado == "Propuesto"


@step('accedo a la notificación de "Nueva Propuesta de Simulacro"')
def step_accedo_propuesta_simulacro(context):
    """Acción: Acceder a propuesta de simulacro."""
    context.navegacion_destino = f"/simulacros/{context.simulacro_id}"
    context.notificacion_leida = True


@step('soy redirigido a la vista del simulacro "{id_simulacro}"')
def step_redirigido_simulacro(context, id_simulacro):
    """Verificación: Redirección."""
    expected_url = f"/simulacros/{id_simulacro}"
    assert context.navegacion_destino == expected_url


@step('visualizo las opciones para "Confirmar" o "Solicitar otro horario"')
def step_opciones_confirmar_rechazar(context):
    """Verificación: Opciones de respuesta."""
    context.opciones_respuesta_visible = True


@step('se muestran los horarios alternativos disponibles')
def step_horarios_alternativos(context):
    """Verificación: Horarios alternativos."""
    context.horarios_alternativos_visible = True


@step('que el simulacro "{id_simulacro}" fue completado y evaluado')
def step_simulacro_completado(context, id_simulacro):
    """Setup: Simulacro completado."""
    context.simulacro_id = id_simulacro
    if id_simulacro in context.sistema.simulacros:
        context.sistema.simulacros[id_simulacro].estado = 'Completado'


@step('las recomendaciones están publicadas para el migrante')
def step_recomendaciones_publicadas(context):
    """Setup: Recomendaciones publicadas."""
    context.recomendaciones_publicadas = True


@step('accedo a la notificación de "Recomendaciones Disponibles"')
def step_accedo_recomendaciones(context):
    """Acción: Acceder a recomendaciones."""
    context.navegacion_destino = f"/simulacros/{context.simulacro_id}/recomendaciones"
    context.notificacion_leida = True


@step('soy redirigido a la vista de recomendaciones del simulacro "{id_simulacro}"')
def step_redirigido_recomendaciones(context, id_simulacro):
    """Verificación: Redirección a recomendaciones."""
    expected_base = f"/simulacros/{id_simulacro}"
    assert expected_base in context.navegacion_destino


@step('visualizo el análisis de fortalezas y áreas de mejora')
def step_visualizo_analisis(context):
    """Verificación: Análisis visible."""
    context.analisis_visible = True


@step('se muestran las preguntas frecuentes sugeridas para practicar')
def step_preguntas_frecuentes(context):
    """Verificación: Preguntas frecuentes."""
    context.preguntas_frecuentes_visible = True


# ==============================================================================
# SUPRESIÓN DE NOTIFICACIONES
# ==============================================================================

@step('que la solicitud "{codigo}" está sin asesor asignado')
def step_solicitud_sin_asesor(context, codigo):
    """Setup: Solicitud sin asesor."""
    context.solicitud_codigo = codigo
    context.sistema.solicitudes[codigo] = SolicitudData(id=codigo, estado='PENDIENTE', asesor=None)


@step('el buzón del sistema contiene {cantidad:d} notificaciones totales')
def step_buzon_sistema_contiene(context, cantidad):
    """Setup: Contador de notificaciones."""
    context.notificaciones_totales = cantidad


@step('el coordinador asigna "{codigo}" al asesor "{asesor}"')
def step_coordinador_asigna(context, codigo, asesor):
    """Acción: Coordinador asigna solicitud."""
    context.sistema.solicitudes[codigo].asesor = asesor
    # NO se genera notificación (política de supresión)


@step('la asignación se registra en el expediente')
def step_asignacion_registrada(context):
    """Verificación: Asignación registrada."""
    solicitud = context.sistema.solicitudes.get(context.solicitud_codigo)
    assert solicitud.asesor is not None


@step('NO se genera notificación al migrante por esta acción administrativa')
def step_no_genera_notificacion_administrativa(context):
    """Verificación: No hay notificación."""
    # Usar servicio para verificar política
    debe_generar = NotificacionService.debe_generar_notificacion('solicitud_asignada')
    assert not debe_generar, "No debería generarse notificación para asignación"


@step('el asesor visualiza la solicitud en su bandeja de trabajo')
def step_asesor_visualiza_bandeja(context):
    """Verificación: Asesor ve solicitud."""
    context.asesor_tiene_solicitud = True


# ==============================================================================
# MANEJO DE ENLACES INVÁLIDOS
# ==============================================================================

@step('que la entrevista de "{codigo}" fue cancelada definitivamente')
def step_entrevista_cancelada_definitiva(context, codigo):
    """Setup: Entrevista cancelada."""
    context.solicitud_codigo = codigo
    context.entrevista_cancelada = True
    # Marcar como que la entrevista ya no existe
    context.entrevista_existe = False


@step('existe una notificación antigua de recordatorio para esa entrevista')
def step_notificacion_antigua_recordatorio(context):
    """Setup: Notificación antigua."""
    context.notificacion_obsoleta = True


@step('accedo a la notificación del recordatorio obsoleto')
def step_accedo_recordatorio_obsoleto(context):
    """Acción: Intentar acceder a recordatorio obsoleto."""
    # Usar servicio para verificar enlace
    enlace_valido, mensaje = BuzonNotificacionesService.verificar_enlace_valido(
        notificacion=None,
        solicitud_existe=context.entrevista_existe if hasattr(context, 'entrevista_existe') else False
    )

    context.enlace_invalido = not enlace_valido
    context.mensaje_error_enlace = mensaje
    context.navegacion_destino = "/notificaciones"


@step('visualizo el mensaje de entrevista cancelada "{mensaje}"')
def step_visualizo_mensaje_entrevista_cancelada(context, mensaje):
    """Verificación: Mensaje de entrevista cancelada."""
    context.mensaje_mostrado = mensaje


@step('se muestra la opción de contactar al asesor para reagendar')
def step_opcion_contactar_asesor(context):
    """Verificación: Opción de contacto."""
    context.opcion_contactar_asesor = True


@step('permanezco en el buzón con la notificación marcada como leída')
def step_permanezco_buzon_leida(context):
    """Verificación: Permanencia en buzón."""
    assert context.navegacion_destino == "/notificaciones"
    context.notificacion_leida = True
