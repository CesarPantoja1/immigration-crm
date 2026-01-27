"""
Value Objects para el dominio de Recepción de Solicitudes.
Objetos inmutables definidos por sus atributos, sin identidad propia.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List


class TipoVisa(Enum):
    """Tipos de visa disponibles en el sistema."""
    VIVIENDA = "VIVIENDA"
    TRABAJO = "TRABAJO"
    ESTUDIO = "ESTUDIO"
    TURISMO = "TURISMO"


class TipoEmbajada(Enum):
    """Embajadas disponibles en el sistema."""
    ESTADOUNIDENSE = "ESTADOUNIDENSE"
    BRASILEÑA = "BRASILEÑA"
    ESPAÑOLA = "ESPAÑOLA"
    CANADIENSE = "CANADIENSE"


class EstadoSolicitud(Enum):
    """Estados posibles de una solicitud de visa."""
    BORRADOR = "BORRADOR"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    DESAPROBADO = "DESAPROBADO"
    REQUIERE_CORRECCIONES = "REQUIERE_CORRECCIONES"
    ENVIADO_EMBAJADA = "ENVIADO_EMBAJADA"
    APROBADO_EMBAJADA = "APROBADO_EMBAJADA"
    RECHAZADO_EMBAJADA = "RECHAZADO_EMBAJADA"


class EstadoDocumento(Enum):
    """Estados posibles de un documento."""
    PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    DESAPROBADO = "DESAPROBADO"
    RECHAZADO = "RECHAZADO"


class EstadoEnvio(Enum):
    """Estados de envío de la solicitud a la embajada."""
    PENDIENTE = "PENDIENTE"
    ENVIADO = "ENVIADO"
    RECIBIDO = "RECIBIDO"
    ERROR = "ERROR"


class TipoNotificacion(Enum):
    """Tipos de notificaciones del sistema."""
    VISA_APROBADA = "VISA_APROBADA"
    VISA_RECHAZADA = "VISA_RECHAZADA"
    DOCUMENTO_RECHAZADO = "DOCUMENTO_RECHAZADO"
    SOLICITUD_ENVIADA = "SOLICITUD_ENVIADA"
    ENTREVISTA_AGENDADA = "ENTREVISTA_AGENDADA"
    RECORDATORIO = "RECORDATORIO"


@dataclass(frozen=True)
class ChecklistDocumentos:
    """
    Value Object que representa el checklist de documentos 
    obligatorios según el tipo de visa.
    """
    tipo_visa: TipoVisa
    documentos_obligatorios: List[str]
    
    def total_documentos(self) -> int:
        """Retorna el total de documentos obligatorios."""
        return len(self.documentos_obligatorios)
    
    def contiene_documento(self, nombre_documento: str) -> bool:
        """Verifica si un documento está en el checklist."""
        return nombre_documento in self.documentos_obligatorios
    
    def documentos_faltantes(self, documentos_cargados: List[str]) -> List[str]:
        """Retorna la lista de documentos faltantes."""
        return [doc for doc in self.documentos_obligatorios 
                if doc not in documentos_cargados]


@dataclass(frozen=True)
class ResultadoRevision:
    """Value Object para el resultado de revisión de un documento."""
    CORRECTO = "Correcto"
    INCORRECTO = "Incorrecto"
    
    valor: str
    motivo: str = ""
    
    def es_aprobado(self) -> bool:
        """Verifica si el resultado es aprobatorio."""
        return self.valor == self.CORRECTO
    
    def es_rechazado(self) -> bool:
        """Verifica si el resultado es de rechazo."""
        return self.valor == self.INCORRECTO


@dataclass(frozen=True)
class DatosPersonales:
    """Value Object para datos personales del migrante."""
    nombres: str
    apellidos: str
    numero_pasaporte: str
    nacionalidad: str
    fecha_nacimiento: str
    email: str
    telefono: str = ""
    
    def nombre_completo(self) -> str:
        """Retorna el nombre completo."""
        return f"{self.nombres} {self.apellidos}"
    
    def __post_init__(self):
        """Validaciones al crear el objeto."""
        if not self.nombres or not self.apellidos:
            raise ValueError("Nombres y apellidos son requeridos")
        if not self.numero_pasaporte:
            raise ValueError("Número de pasaporte es requerido")
        if not self.email:
            raise ValueError("Email es requerido")
