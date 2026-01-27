"""
Entidades de Dominio para Seguimiento de Solicitudes.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from .value_objects import (
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
)


@dataclass
class TimelineSolicitud:
    """
    Entidad que representa el timeline/historial de una solicitud.
    Mantiene el registro cronológico de todos los eventos.
    """
    solicitud_id: str
    eventos: List[EventoHistorial] = field(default_factory=list)
    
    def agregar_evento(
        self,
        tipo: TipoEvento,
        descripcion: str,
        datos: dict = None
    ) -> EventoHistorial:
        """Agrega un nuevo evento al timeline."""
        evento = EventoHistorial(
            tipo=tipo,
            fecha=datetime.now(),
            descripcion=descripcion,
            datos_adicionales=datos or {}
        )
        self.eventos.append(evento)
        return evento
    
    def obtener_cronologia(self, orden_inverso: bool = True) -> List[EventoHistorial]:
        """
        Obtiene los eventos en orden cronológico.
        
        Args:
            orden_inverso: Si True, retorna del más reciente al más antiguo
        """
        return sorted(
            self.eventos,
            key=lambda e: e.fecha,
            reverse=orden_inverso
        )
    
    def obtener_ultimos(self, cantidad: int = 5) -> List[EventoHistorial]:
        """Obtiene los últimos N eventos."""
        return self.obtener_cronologia()[:cantidad]
    
    def filtrar_por_tipo(self, tipo: TipoEvento) -> List[EventoHistorial]:
        """Filtra eventos por tipo."""
        return [e for e in self.eventos if e.tipo == tipo]
    
    def contar_eventos(self) -> int:
        """Retorna el total de eventos."""
        return len(self.eventos)


@dataclass
class SeguimientoSolicitud:
    """
    Entidad principal para el seguimiento de una solicitud.
    Agrupa toda la información necesaria para el seguimiento.
    """
    solicitud_id: str
    codigo: str
    tipo_visa: str
    embajada: str
    estado: EstadoSolicitudSeguimiento
    migrante_id: str
    migrante_email: str
    
    fecha_creacion: datetime
    fecha_ultima_actualizacion: datetime = field(default_factory=datetime.now)
    
    # Documentos y validaciones
    documentos: List[ValidacionDocumento] = field(default_factory=list)
    total_documentos_requeridos: int = 0
    
    # Timeline
    timeline: Optional[TimelineSolicitud] = None
    
    # Alertas activas
    alertas: List[Alerta] = field(default_factory=list)
    
    def __post_init__(self):
        if self.timeline is None:
            self.timeline = TimelineSolicitud(solicitud_id=self.solicitud_id)
    
    # =====================================================
    # Cálculo de progreso
    # =====================================================
    
    def calcular_progreso(self) -> ProgresoSolicitud:
        """Calcula el progreso actual de la solicitud."""
        aprobados = sum(1 for d in self.documentos if d.esta_aprobado())
        rechazados = sum(1 for d in self.documentos if d.esta_rechazado())
        pendientes = self.total_documentos_requeridos - aprobados - rechazados
        
        return ProgresoSolicitud(
            total_documentos_requeridos=self.total_documentos_requeridos,
            documentos_aprobados=aprobados,
            documentos_pendientes=pendientes,
            documentos_rechazados=rechazados
        )
    
    def obtener_porcentaje_progreso(self) -> int:
        """Retorna el porcentaje de progreso."""
        return self.calcular_progreso().porcentaje
    
    def obtener_validaciones_restantes(self) -> int:
        """Retorna la cantidad de validaciones restantes."""
        return self.calcular_progreso().validaciones_restantes()
    
    # =====================================================
    # Gestión de documentos
    # =====================================================
    
    def obtener_documentos_rechazados(self) -> List[ValidacionDocumento]:
        """Obtiene la lista de documentos rechazados."""
        return [d for d in self.documentos if d.esta_rechazado()]
    
    def obtener_documentos_aprobados(self) -> List[ValidacionDocumento]:
        """Obtiene la lista de documentos aprobados."""
        return [d for d in self.documentos if d.esta_aprobado()]
    
    def tiene_documentos_rechazados(self) -> bool:
        """Verifica si hay documentos rechazados."""
        return len(self.obtener_documentos_rechazados()) > 0
    
    def agregar_validacion_documento(
        self,
        nombre: str,
        estado: str,
        motivo_rechazo: str = ""
    ) -> None:
        """Agrega una validación de documento."""
        validacion = ValidacionDocumento(
            nombre=nombre,
            estado=estado,
            motivo_rechazo=motivo_rechazo,
            fecha_validacion=datetime.now()
        )
        # Reemplazar si ya existe
        self.documentos = [d for d in self.documentos if d.nombre != nombre]
        self.documentos.append(validacion)
    
    # =====================================================
    # Gestión de alertas
    # =====================================================
    
    def agregar_alerta(self, alerta: Alerta) -> None:
        """Agrega una alerta."""
        self.alertas.append(alerta)
    
    def obtener_alertas_urgentes(self) -> List[Alerta]:
        """Obtiene las alertas urgentes."""
        return [a for a in self.alertas if a.es_urgente()]
    
    def verificar_vencimientos(self, documentos_con_fecha: List[Dict]) -> List[Alerta]:
        """
        Verifica vencimientos de documentos y genera alertas.
        
        Args:
            documentos_con_fecha: Lista de dicts con 'nombre' y 'fecha_vencimiento'
        """
        alertas_generadas = []
        hoy = date.today()
        
        for doc in documentos_con_fecha:
            fecha_venc = doc.get('fecha_vencimiento')
            if fecha_venc and isinstance(fecha_venc, date):
                dias = (fecha_venc - hoy).days
                
                if dias <= 30:  # Solo alertar si vence en 30 días o menos
                    alerta = Alerta.crear_alerta_vencimiento(
                        documento=doc['nombre'],
                        fecha_vencimiento=fecha_venc,
                        solicitud_id=self.solicitud_id,
                        documento_id=doc.get('id')
                    )
                    alertas_generadas.append(alerta)
                    self.agregar_alerta(alerta)
        
        return alertas_generadas
    
    # =====================================================
    # Siguiente paso
    # =====================================================
    
    def obtener_siguiente_paso(self) -> PasoSiguiente:
        """Determina el siguiente paso según el estado."""
        if self.estado == EstadoSolicitudSeguimiento.REQUIERE_CORRECCIONES:
            return PasoSiguiente.corregir_documentos()
        
        elif self.estado == EstadoSolicitudSeguimiento.APROBADA:
            return PasoSiguiente.esperar_asignacion_entrevista()
        
        elif self.estado == EstadoSolicitudSeguimiento.ENVIADA_EMBAJADA:
            return PasoSiguiente(
                descripcion="Esperar respuesta de la embajada",
                tiempo_estimado="5-15 días hábiles",
                es_accion_usuario=False,
                detalle="Su solicitud está siendo procesada por la embajada"
            )
        
        elif self.estado == EstadoSolicitudSeguimiento.PENDIENTE_REVISION:
            return PasoSiguiente(
                descripcion="Esperar revisión del asesor",
                tiempo_estimado="1-3 días hábiles",
                es_accion_usuario=False,
                detalle="Un asesor revisará sus documentos"
            )
        
        elif self.estado == EstadoSolicitudSeguimiento.BORRADOR:
            return PasoSiguiente(
                descripcion="Completar carga de documentos",
                tiempo_estimado="Inmediato",
                es_accion_usuario=True,
                detalle="Cargue todos los documentos requeridos"
            )
        
        else:
            return PasoSiguiente(
                descripcion="Proceso completado",
                tiempo_estimado="N/A",
                es_accion_usuario=False
            )
    
    # =====================================================
    # Resumen
    # =====================================================
    
    def obtener_resumen(self) -> ResumenSolicitud:
        """Genera un resumen de la solicitud."""
        return ResumenSolicitud(
            codigo=self.codigo,
            tipo_visa=self.tipo_visa,
            embajada=self.embajada,
            estado=self.estado,
            fecha_creacion=self.fecha_creacion.date() if isinstance(self.fecha_creacion, datetime) else self.fecha_creacion,
            fecha_ultima_actualizacion=self.fecha_ultima_actualizacion,
            progreso=self.calcular_progreso()
        )


@dataclass
class PortafolioMigrante:
    """
    Agregado que gestiona todas las solicitudes de un migrante.
    Proporciona una vista consolidada del portafolio.
    """
    migrante_id: str
    migrante_email: str
    solicitudes: List[SeguimientoSolicitud] = field(default_factory=list)
    
    def agregar_solicitud(self, solicitud: SeguimientoSolicitud) -> None:
        """Agrega una solicitud al portafolio."""
        self.solicitudes.append(solicitud)
    
    def obtener_solicitudes_activas(self) -> List[SeguimientoSolicitud]:
        """Obtiene solicitudes activas (no completadas ni rechazadas)."""
        estados_activos = [
            EstadoSolicitudSeguimiento.BORRADOR,
            EstadoSolicitudSeguimiento.PENDIENTE_REVISION,
            EstadoSolicitudSeguimiento.EN_REVISION,
            EstadoSolicitudSeguimiento.REQUIERE_CORRECCIONES,
            EstadoSolicitudSeguimiento.APROBADA,
            EstadoSolicitudSeguimiento.ENVIADA_EMBAJADA,
        ]
        return [s for s in self.solicitudes if s.estado in estados_activos]
    
    def obtener_solicitudes_priorizadas(self) -> List[SeguimientoSolicitud]:
        """
        Obtiene solicitudes ordenadas por prioridad.
        Más recientes y que requieren acción primero.
        """
        return sorted(
            self.solicitudes,
            key=lambda s: s.obtener_resumen().prioridad()
        )
    
    def contar_solicitudes(self) -> int:
        """Retorna el total de solicitudes."""
        return len(self.solicitudes)
    
    def tiene_solicitud(self, solicitud_id: str) -> bool:
        """Verifica si el portafolio contiene una solicitud."""
        return any(s.solicitud_id == solicitud_id for s in self.solicitudes)
    
    def obtener_solicitud(self, solicitud_id: str) -> Optional[SeguimientoSolicitud]:
        """Obtiene una solicitud específica."""
        for s in self.solicitudes:
            if s.solicitud_id == solicitud_id:
                return s
        return None
    
    def obtener_todas_alertas(self) -> List[Alerta]:
        """Obtiene todas las alertas de todas las solicitudes."""
        alertas = []
        for solicitud in self.solicitudes:
            alertas.extend(solicitud.alertas)
        return sorted(alertas, key=lambda a: a.fecha_creacion, reverse=True)
    
    def obtener_alertas_urgentes(self) -> List[Alerta]:
        """Obtiene alertas urgentes de todas las solicitudes."""
        return [a for a in self.obtener_todas_alertas() if a.es_urgente()]
