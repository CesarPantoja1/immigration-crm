from behave import step, use_step_matcher
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional

use_step_matcher("parse")


# ==============================================================================
# DOMINIO DE ALERTAS
# ==============================================================================

@dataclass
class Notificacion:
    tipo: str
    id_solicitud: Optional[str] = None
    id_simulacro: Optional[str] = None
    fecha_hora_entrevista: Optional[str] = None
    fecha_hora_anterior: Optional[str] = None
    nueva_fecha_hora: Optional[str] = None
    detalle: Optional[str] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)


@dataclass
class CentroNotificaciones:
    notificaciones: List[Notificacion] = field(default_factory=list)

    def agregar(self, notificacion: Notificacion):
        self.notificaciones.append(notificacion)

    def total(self) -> int:
        return len(self.notificaciones)

    def ultima(self) -> Optional[Notificacion]:
        return self.notificaciones[-1] if self.notificaciones else None

    def nuevas_desde(self, indice: int) -> List[Notificacion]:
        return self.notificaciones[indice:]

    def buscar_coincidencia(self, criterios: Dict[str, str]) -> Optional[Notificacion]:
        """Busca una notificación que coincida con los criterios."""
        for notif in reversed(self.notificaciones):
            coincide = True
            for key, value in criterios.items():
                attr_value = getattr(notif, key.replace(" ", "_"), None)
                if attr_value != value:
                    coincide = False
                    break
            if coincide:
                return notif
        return None


@dataclass
class Entrevista:
    fecha_hora: str
    estado: str = "Programada"
    fecha_hora_anterior: Optional[str] = None


@dataclass
class Simulacro:
    id: str
    id_solicitud: str
    estado: str = "Pendiente"


@dataclass
class DocumentoRecomendaciones:
    id_simulacro: str
    estado: str = "Borrador"


@dataclass
class Solicitud:
    id: str
    estado: str
    asesor: Optional[str] = None
    entrevista: Optional[Entrevista] = None


@dataclass
class SistemaMigratorio:
    """Sistema simplificado para testing de alertas."""

    solicitante_autenticado: bool = False
    asesor_autenticado: bool = False
    asesor_actual: Optional[str] = None
    solicitudes: Dict[str, Solicitud] = field(default_factory=dict)
    simulacros: Dict[str, Simulacro] = field(default_factory=dict)
    recomendaciones: Dict[str, DocumentoRecomendaciones] = field(default_factory=dict)
    notificaciones_migrante: CentroNotificaciones = field(default_factory=CentroNotificaciones)
    notificaciones_asesor: CentroNotificaciones = field(default_factory=CentroNotificaciones)
    tipos_notificacion: List[str] = field(default_factory=list)
    ventanas_recordatorio: List[str] = field(default_factory=list)
    ventanas_preparacion: List[str] = field(default_factory=list)
    fecha_hora_actual: Optional[datetime] = None

    def autenticar_solicitante(self):
        self.solicitante_autenticado = True

    def autenticar_asesor(self, asesor: str):
        self.asesor_autenticado = True
        self.asesor_actual = asesor

    def establecer_solicitud(self, id_solicitud: str, estado: str):
        self.solicitudes[id_solicitud] = Solicitud(id=id_solicitud, estado=estado)

    def asignar_asesor_a_solicitud(self, id_solicitud: str, asesor: str):
        if id_solicitud in self.solicitudes:
            self.solicitudes[id_solicitud].asesor = asesor

    def establecer_tipos_notificacion(self, tipos: List[str]):
        self.tipos_notificacion = tipos

    def establecer_ventanas_recordatorio(self, ventanas: List[str]):
        self.ventanas_recordatorio = ventanas

    def establecer_ventanas_preparacion(self, ventanas: List[str]):
        self.ventanas_preparacion = ventanas

    def limpiar_entrevista(self, id_solicitud: str):
        if id_solicitud in self.solicitudes:
            self.solicitudes[id_solicitud].entrevista = None

    def registrar_entrevista(self, id_solicitud: str, fecha_hora: str, asesor: str):
        if id_solicitud in self.solicitudes:
            self.solicitudes[id_solicitud].entrevista = Entrevista(
                fecha_hora=fecha_hora,
                estado="Programada"
            )
            # Emitir notificación
            self.notificaciones_migrante.agregar(Notificacion(
                tipo="Entrevista agendada",
                id_solicitud=id_solicitud,
                fecha_hora_entrevista=fecha_hora
            ))

    def establecer_entrevista(self, id_solicitud: str, estado: str, fecha_hora: str):
        if id_solicitud in self.solicitudes:
            self.solicitudes[id_solicitud].entrevista = Entrevista(
                fecha_hora=fecha_hora,
                estado=estado
            )

    def establecer_fecha_hora_actual(self, fecha_hora: str):
        self.fecha_hora_actual = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")

    def evaluar_recordatorios(self, id_solicitud: str):
        """Evalúa y emite recordatorios según ventanas configuradas."""
        solicitud = self.solicitudes.get(id_solicitud)
        if not solicitud or not solicitud.entrevista:
            return

        entrevista = solicitud.entrevista

        # No emitir recordatorios para entrevistas canceladas
        if entrevista.estado == "Cancelada":
            return

        # No emitir recordatorios basados en fechas anteriores (reprogramadas)
        fecha_entrevista = datetime.strptime(entrevista.fecha_hora, "%Y-%m-%d %H:%M")

        if self.fecha_hora_actual:
            diferencia = fecha_entrevista - self.fecha_hora_actual
            horas_restantes = diferencia.total_seconds() / 3600

            # Verificar ventanas
            if "24h" in self.ventanas_recordatorio and 23 <= horas_restantes <= 25:
                self.notificaciones_migrante.agregar(Notificacion(
                    tipo="Recordatorio entrevista",
                    id_solicitud=id_solicitud,
                    fecha_hora_entrevista=entrevista.fecha_hora,
                    detalle="Faltan 24h"
                ))
            elif "2h" in self.ventanas_recordatorio and 1 <= horas_restantes <= 3:
                self.notificaciones_migrante.agregar(Notificacion(
                    tipo="Recordatorio entrevista",
                    id_solicitud=id_solicitud,
                    fecha_hora_entrevista=entrevista.fecha_hora,
                    detalle="Faltan 2h"
                ))

    def reprogramar_entrevista(self, id_solicitud: str, nueva_fecha: str, asesor: str):
        solicitud = self.solicitudes.get(id_solicitud)
        if solicitud and solicitud.entrevista:
            fecha_anterior = solicitud.entrevista.fecha_hora
            solicitud.entrevista.fecha_hora_anterior = fecha_anterior
            solicitud.entrevista.fecha_hora = nueva_fecha
            solicitud.entrevista.estado = "Reprogramada"

            # Emitir notificación
            self.notificaciones_migrante.agregar(Notificacion(
                tipo="Entrevista reprogramada",
                id_solicitud=id_solicitud,
                fecha_hora_anterior=fecha_anterior,
                nueva_fecha_hora=nueva_fecha
            ))

    def establecer_entrevista_anterior(self, id_solicitud: str, estado: str, fecha_hora: str):
        solicitud = self.solicitudes.get(id_solicitud)
        if solicitud and solicitud.entrevista:
            solicitud.entrevista.fecha_hora_anterior = fecha_hora

    def cancelar_entrevista(self, id_solicitud: str, asesor: str):
        solicitud = self.solicitudes.get(id_solicitud)
        if solicitud and solicitud.entrevista:
            fecha_hora = solicitud.entrevista.fecha_hora
            solicitud.entrevista.estado = "Cancelada"

            # Emitir notificación
            self.notificaciones_migrante.agregar(Notificacion(
                tipo="Entrevista cancelada",
                id_solicitud=id_solicitud,
                fecha_hora_entrevista=fecha_hora
            ))

    def establecer_estado_entrevista(self, id_solicitud: str, estado: str):
        solicitud = self.solicitudes.get(id_solicitud)
        if solicitud:
            if solicitud.entrevista:
                solicitud.entrevista.estado = estado
            else:
                solicitud.entrevista = Entrevista(fecha_hora="", estado=estado)

    def establecer_fecha_entrevista(self, id_solicitud: str, fecha_hora: str):
        solicitud = self.solicitudes.get(id_solicitud)
        if solicitud and solicitud.entrevista:
            solicitud.entrevista.fecha_hora = fecha_hora

    def asegurar_sin_simulacro_en_estado(self, id_solicitud: str, estado: str):
        """Asegura que no hay simulacro en el estado dado."""
        for sim_id in list(self.simulacros.keys()):
            sim = self.simulacros[sim_id]
            if sim.id_solicitud == id_solicitud and sim.estado == estado:
                del self.simulacros[sim_id]

    def evaluar_preparacion(self, id_solicitud: str):
        """Evalúa si se debe alertar sobre preparación."""
        solicitud = self.solicitudes.get(id_solicitud)
        if not solicitud or not solicitud.entrevista:
            return

        # Verificar si hay simulacro confirmado
        tiene_simulacro_confirmado = any(
            sim.id_solicitud == id_solicitud and sim.estado == "Confirmado"
            for sim in self.simulacros.values()
        )

        if not tiene_simulacro_confirmado:
            fecha_entrevista = datetime.strptime(solicitud.entrevista.fecha_hora, "%Y-%m-%d %H:%M")
            if self.fecha_hora_actual:
                diferencia = fecha_entrevista - self.fecha_hora_actual
                dias_restantes = diferencia.days

                # Si falta una semana o menos
                if "7d" in self.ventanas_preparacion and dias_restantes <= 7:
                    self.notificaciones_migrante.agregar(Notificacion(
                        tipo="Preparación recomendada",
                        id_solicitud=id_solicitud,
                        detalle="Realizar simulación de entrevista"
                    ))

    def crear_simulacro(self, id_simulacro: str, id_solicitud: str):
        self.simulacros[id_simulacro] = Simulacro(
            id=id_simulacro,
            id_solicitud=id_solicitud,
            estado="Pendiente"
        )

    def establecer_estado_simulacro(self, id_simulacro: str, estado: str):
        if id_simulacro in self.simulacros:
            self.simulacros[id_simulacro].estado = estado

    def actualizar_estado_simulacro(self, id_simulacro: str, estado: str):
        if id_simulacro in self.simulacros:
            self.simulacros[id_simulacro].estado = estado

            # Notificar al asesor si se completa
            if estado == "Completado":
                self.notificaciones_asesor.agregar(Notificacion(
                    tipo="Simulación completada",
                    id_simulacro=id_simulacro,
                    detalle="Generar recomendaciones"
                ))

    def crear_recomendaciones(self, id_simulacro: str, estado: str):
        self.recomendaciones[id_simulacro] = DocumentoRecomendaciones(
            id_simulacro=id_simulacro,
            estado=estado
        )

    def publicar_recomendaciones(self, id_simulacro: str):
        if id_simulacro in self.recomendaciones:
            self.recomendaciones[id_simulacro].estado = "Publicado"

            # Notificar al migrante
            self.notificaciones_migrante.agregar(Notificacion(
                tipo="Recomendaciones listas",
                id_simulacro=id_simulacro
            ))


# ==============================================================================
# STEPS
# ==============================================================================

@step('gestiono la solicitud "{id_solicitud}" en estado "{estado}"')
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
    # Buscar en el centro de notificaciones del asesor si está autenticado, sino del migrante
    notificacion = None
    if context.sistema.asesor_autenticado:
        notificacion = context.sistema.notificaciones_asesor.ultima()
    if notificacion is None:
        notificacion = context.sistema.notificaciones_migrante.ultima()
    assert notificacion is not None, "No hay notificaciones"
    assert notificacion.detalle == detalle, f"Detalle esperado: {detalle}, Obtenido: {notificacion.detalle}"


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


@step('que el asesor "{asesor}" está autenticado en el sistema')
def paso_asesor_autenticado(context, asesor):
    if not hasattr(context, 'sistema') or context.sistema is None:
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


@step('que existe un documento de recomendaciones para el simulacro "{id_simulacro}" en estado "{estado}"')
def paso_documento_recomendaciones(context, id_simulacro, estado):
    if not hasattr(context, 'sistema') or context.sistema is None:
        context.sistema = SistemaMigratorio()
        context.sistema.autenticar_solicitante()
    context.sistema.crear_recomendaciones(id_simulacro, estado)
    assert id_simulacro in context.sistema.recomendaciones


@step('el documento de recomendaciones del simulacro "{id_simulacro}" se publica en el sistema')
def paso_publica_recomendaciones(context, id_simulacro):
    context.sistema.publicar_recomendaciones(id_simulacro)
