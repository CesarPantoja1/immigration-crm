"""
Value Objects para el dominio de Seguimiento de Solicitudes.
"""
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional


class TipoEvento(Enum):
    """Tipos de eventos en el historial de una solicitud."""
    SOLICITUD_CREADA = "SOLICITUD_CREADA"
    SOLICITUD_ENVIADA = "SOLICITUD_ENVIADA"
    SOLICITUD_APROBADA = "SOLICITUD_APROBADA"
    SOLICITUD_RECHAZADA = "SOLICITUD_RECHAZADA"
    DOCUMENTO_CARGADO = "DOCUMENTO_CARGADO"
    DOCUMENTO_APROBADO = "DOCUMENTO_APROBADO"
    DOCUMENTO_RECHAZADO = "DOCUMENTO_RECHAZADO"
    DOCUMENTO_ACTUALIZADO = "DOCUMENTO_ACTUALIZADO"
    ENTREVISTA_AGENDADA = "ENTREVISTA_AGENDADA"
    ENTREVISTA_REPROGRAMADA = "ENTREVISTA_REPROGRAMADA"
    ENTREVISTA_COMPLETADA = "ENTREVISTA_COMPLETADA"
    ENTREVISTA_CANCELADA = "ENTREVISTA_CANCELADA"
    OBSERVACION_AGREGADA = "OBSERVACION_AGREGADA"
    ESTADO_ACTUALIZADO = "ESTADO_ACTUALIZADO"
    ALERTA_VENCIMIENTO = "ALERTA_VENCIMIENTO"


class EstadoSolicitudSeguimiento(Enum):
    """Estados posibles de una solicitud para seguimiento."""
    BORRADOR = "BORRADOR"
    PENDIENTE_REVISION = "PENDIENTE_REVISION"
    EN_REVISION = "EN_REVISION"
    REQUIERE_CORRECCIONES = "REQUIERE_CORRECCIONES"
    APROBADA = "APROBADA"
    ENVIADA_EMBAJADA = "ENVIADA_EMBAJADA"
    RECHAZADA = "RECHAZADA"
    COMPLETADA = "COMPLETADA"


class NivelAlerta(Enum):
    """Niveles de alerta para notificaciones."""
    INFO = "INFO"
    ADVERTENCIA = "ADVERTENCIA"
    URGENTE = "URGENTE"
    CRITICO = "CRITICO"


class TipoAlerta(Enum):
    """Tipos de alerta."""
    VENCIMIENTO_DOCUMENTO = "VENCIMIENTO_DOCUMENTO"
    DOCUMENTO_RECHAZADO = "DOCUMENTO_RECHAZADO"
    ENTREVISTA_PROXIMA = "ENTREVISTA_PROXIMA"
    ACCION_REQUERIDA = "ACCION_REQUERIDA"
    ACTUALIZACION_ESTADO = "ACTUALIZACION_ESTADO"


@dataclass(frozen=True)
class EventoHistorial:
    """Value Object para un evento en el historial."""
    tipo: TipoEvento
    fecha: datetime
    descripcion: str
    datos_adicionales: dict = field(default_factory=dict)
    
    def formato_fecha(self) -> str:
        """Retorna la fecha en formato legible."""
        return self.fecha.strftime("%Y-%m-%d %H:%M:%S")
    
    def es_reciente(self, dias: int = 7) -> bool:
        """Verifica si el evento es reciente."""
        return (datetime.now() - self.fecha).days <= dias


@dataclass(frozen=True)
class ProgresoSolicitud:
    """Value Object para el progreso de una solicitud."""
    total_documentos_requeridos: int
    documentos_aprobados: int
    documentos_pendientes: int
    documentos_rechazados: int
    
    @property
    def porcentaje(self) -> int:
        """Calcula el porcentaje de progreso."""
        if self.total_documentos_requeridos == 0:
            return 0
        return int((self.documentos_aprobados / self.total_documentos_requeridos) * 100)
    
    @property
    def esta_completo(self) -> bool:
        """Verifica si el progreso está completo."""
        return self.documentos_aprobados == self.total_documentos_requeridos
    
    @property
    def tiene_rechazados(self) -> bool:
        """Verifica si hay documentos rechazados."""
        return self.documentos_rechazados > 0
    
    def validaciones_restantes(self) -> int:
        """Retorna la cantidad de validaciones restantes."""
        return self.total_documentos_requeridos - self.documentos_aprobados


@dataclass(frozen=True)
class Alerta:
    """Value Object para una alerta del sistema."""
    tipo: TipoAlerta
    nivel: NivelAlerta
    titulo: str
    mensaje: str
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_vencimiento: Optional[date] = None
    accion_sugerida: str = ""
    solicitud_id: Optional[str] = None
    documento_id: Optional[str] = None
    
    def es_urgente(self) -> bool:
        """Verifica si la alerta es urgente."""
        return self.nivel in [NivelAlerta.URGENTE, NivelAlerta.CRITICO]
    
    def dias_restantes(self) -> Optional[int]:
        """Calcula días restantes hasta vencimiento."""
        if self.fecha_vencimiento:
            return (self.fecha_vencimiento - date.today()).days
        return None
    
    @classmethod
    def crear_alerta_vencimiento(
        cls,
        documento: str,
        fecha_vencimiento: date,
        solicitud_id: str,
        documento_id: str = None
    ) -> 'Alerta':
        """Factory para crear alerta de vencimiento."""
        dias = (fecha_vencimiento - date.today()).days
        
        if dias <= 7:
            nivel = NivelAlerta.CRITICO
        elif dias <= 15:
            nivel = NivelAlerta.URGENTE
        elif dias <= 30:
            nivel = NivelAlerta.ADVERTENCIA
        else:
            nivel = NivelAlerta.INFO
        
        return cls(
            tipo=TipoAlerta.VENCIMIENTO_DOCUMENTO,
            nivel=nivel,
            titulo=f"Alerta de vencimiento: {documento}",
            mensaje=f"Tu {documento.lower()} vence en {dias} días",
            fecha_vencimiento=fecha_vencimiento,
            accion_sugerida="Renueva el documento para evitar retrasos en el proceso consular",
            solicitud_id=solicitud_id,
            documento_id=documento_id
        )


@dataclass(frozen=True)
class PasoSiguiente:
    """Value Object para describir el siguiente paso del proceso."""
    descripcion: str
    tiempo_estimado: str
    es_accion_usuario: bool = False
    detalle: str = ""
    
    @classmethod
    def esperar_asignacion_entrevista(cls) -> 'PasoSiguiente':
        """Factory para paso de esperar asignación."""
        return cls(
            descripcion="Esperar asignación de fecha de entrevista",
            tiempo_estimado="3-5 días hábiles",
            es_accion_usuario=False,
            detalle="La embajada procesará su solicitud y asignará una fecha"
        )
    
    @classmethod
    def corregir_documentos(cls) -> 'PasoSiguiente':
        """Factory para paso de corrección."""
        return cls(
            descripcion="Corregir documentos observados",
            tiempo_estimado="Inmediato",
            es_accion_usuario=True,
            detalle="Cargue las versiones corregidas de los documentos rechazados"
        )
    
    @classmethod
    def asistir_entrevista(cls, fecha: str) -> 'PasoSiguiente':
        """Factory para paso de asistir a entrevista."""
        return cls(
            descripcion=f"Asistir a entrevista consular el {fecha}",
            tiempo_estimado="Según fecha asignada",
            es_accion_usuario=True,
            detalle="Prepare los documentos originales para la entrevista"
        )


@dataclass(frozen=True)
class ResumenSolicitud:
    """Value Object para el resumen de una solicitud."""
    codigo: str
    tipo_visa: str
    embajada: str
    estado: EstadoSolicitudSeguimiento
    fecha_creacion: date
    fecha_ultima_actualizacion: datetime
    progreso: ProgresoSolicitud
    
    def prioridad(self) -> int:
        """Calcula la prioridad (menor es más prioritario)."""
        # Más reciente = más prioritario
        dias_desde_actualizacion = (datetime.now() - self.fecha_ultima_actualizacion).days
        
        # Estados que requieren acción tienen mayor prioridad
        prioridad_estado = {
            EstadoSolicitudSeguimiento.REQUIERE_CORRECCIONES: 0,
            EstadoSolicitudSeguimiento.EN_REVISION: 1,
            EstadoSolicitudSeguimiento.PENDIENTE_REVISION: 2,
            EstadoSolicitudSeguimiento.APROBADA: 3,
            EstadoSolicitudSeguimiento.ENVIADA_EMBAJADA: 4,
            EstadoSolicitudSeguimiento.BORRADOR: 5,
            EstadoSolicitudSeguimiento.COMPLETADA: 6,
            EstadoSolicitudSeguimiento.RECHAZADA: 7,
        }
        
        return prioridad_estado.get(self.estado, 10) * 100 + dias_desde_actualizacion


@dataclass(frozen=True)
class ValidacionDocumento:
    """Value Object para la validación de un documento."""
    nombre: str
    estado: str  # APROBADO, RECHAZADO, PENDIENTE
    motivo_rechazo: str = ""
    fecha_validacion: Optional[datetime] = None
    
    def esta_rechazado(self) -> bool:
        """Verifica si el documento está rechazado."""
        return self.estado == "RECHAZADO"
    
    def esta_aprobado(self) -> bool:
        """Verifica si el documento está aprobado."""
        return self.estado == "APROBADO"
    
    def permite_nueva_carga(self) -> bool:
        """Verifica si permite cargar nueva versión."""
        return self.estado in ["RECHAZADO", "PENDIENTE"]
