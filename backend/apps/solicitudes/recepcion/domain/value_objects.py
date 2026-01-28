"""
Value Objects para Recepción de Solicitudes.
Objetos inmutables que representan conceptos del dominio.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TipoVisa(Enum):
    """Tipos de visa disponibles."""
    TRABAJO = "TRABAJO"
    ESTUDIO = "ESTUDIO"
    TURISMO = "TURISMO"
    VIVIENDA = "VIVIENDA"


class TipoEmbajada(Enum):
    """Embajadas disponibles."""
    ESTADOUNIDENSE = "ESTADOUNIDENSE"
    BRASILEÑA = "BRASILEÑA"
    CANADIENSE = "CANADIENSE"
    ESPAÑOLA = "ESPAÑOLA"


class EstadoSolicitud(Enum):
    """Estados posibles de una solicitud."""
    BORRADOR = "BORRADOR"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    DESAPROBADO = "DESAPROBADO"
    ENVIADO = "ENVIADO"


class EstadoDocumento(Enum):
    """Estados posibles de un documento."""
    PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    DESAPROBADO = "DESAPROBADO"


class EstadoEnvio(Enum):
    """Estados de envío a embajada."""
    PENDIENTE = "PENDIENTE"
    ENVIADO = "ENVIADO"
    RECIBIDO = "RECIBIDO"


class TipoNotificacion(Enum):
    """Tipos de notificación."""
    VISA_APROBADA = "VISA_APROBADA"
    DOCUMENTO_RECHAZADO = "DOCUMENTO_RECHAZADO"
    SOLICITUD_ENVIADA = "SOLICITUD_ENVIADA"


@dataclass(frozen=True)
class ChecklistDocumentos:
    """Lista de documentos requeridos por tipo de visa."""
    tipo_visa: TipoVisa
    documentos_requeridos: tuple
    
    def obtener_documentos(self) -> List[str]:
        """Retorna la lista de documentos requeridos."""
        return list(self.documentos_requeridos)
    
    def documento_es_requerido(self, nombre: str) -> bool:
        """Verifica si un documento es requerido."""
        return nombre in self.documentos_requeridos


@dataclass(frozen=True)
class ResultadoRevision:
    """Resultado de la revisión de un documento."""
    es_correcto: bool
    motivo_rechazo: Optional[str] = None


@dataclass(frozen=True)
class DatosPersonales:
    """Datos personales del migrante."""
    nombre: str
    apellido: str
    pasaporte: str
    nacionalidad: str
    email: Optional[str] = None
    telefono: Optional[str] = None
