"""
Excepciones de Dominio para Recepción de Solicitudes.
"""


class DomainException(Exception):
    """Excepción base del dominio."""
    pass


# =====================================================
# EXCEPCIONES DE SOLICITUD
# =====================================================

class SolicitudException(DomainException):
    """Excepción base para solicitudes."""
    pass


class SolicitudNoEncontradaException(SolicitudException):
    """La solicitud no existe."""
    def __init__(self, id_solicitud: str):
        super().__init__(f"Solicitud {id_solicitud} no encontrada")
        self.id_solicitud = id_solicitud


class SolicitudYaExisteException(SolicitudException):
    """La solicitud ya existe."""
    def __init__(self, id_solicitud: str):
        super().__init__(f"Solicitud {id_solicitud} ya existe")
        self.id_solicitud = id_solicitud


class SolicitudEstadoInvalidoException(SolicitudException):
    """El estado de la solicitud no permite la operación."""
    def __init__(self, estado_actual: str, operacion: str):
        super().__init__(
            f"No se puede {operacion} una solicitud en estado {estado_actual}"
        )
        self.estado_actual = estado_actual
        self.operacion = operacion


# =====================================================
# EXCEPCIONES DE DOCUMENTO
# =====================================================

class DocumentoException(DomainException):
    """Excepción base para documentos."""
    pass


class DocumentoNoEncontradoException(DocumentoException):
    """El documento no existe."""
    def __init__(self, nombre: str):
        super().__init__(f"Documento '{nombre}' no encontrado")
        self.nombre = nombre


class DocumentoInvalidoException(DocumentoException):
    """El documento no es válido."""
    def __init__(self, nombre: str, motivo: str):
        super().__init__(f"Documento '{nombre}' inválido: {motivo}")
        self.nombre = nombre
        self.motivo = motivo


class DocumentoNoRecargableException(DocumentoException):
    """El documento no puede ser recargado."""
    def __init__(self, nombre: str):
        super().__init__(
            f"El documento '{nombre}' no puede ser recargado en su estado actual"
        )
        self.nombre = nombre


class MotivoRechazoInvalidoException(DocumentoException):
    """El motivo de rechazo no es válido."""
    def __init__(self):
        super().__init__("Debe proporcionar un motivo de rechazo")


# =====================================================
# EXCEPCIONES DE CHECKLIST
# =====================================================

class ChecklistException(DomainException):
    """Excepción base para checklists."""
    pass


class ChecklistNoEncontradoException(ChecklistException):
    """No existe checklist para el tipo de visa."""
    def __init__(self, tipo_visa: str):
        super().__init__(f"No existe checklist para visa tipo {tipo_visa}")
        self.tipo_visa = tipo_visa


class DocumentosFaltantesException(ChecklistException):
    """Faltan documentos requeridos."""
    def __init__(self, documentos_faltantes: list):
        super().__init__(
            f"Faltan documentos requeridos: {', '.join(documentos_faltantes)}"
        )
        self.documentos_faltantes = documentos_faltantes


# =====================================================
# EXCEPCIONES DE ENVÍO
# =====================================================

class EnvioException(DomainException):
    """Excepción base para envíos."""
    pass


class EnvioNoPermitidoException(EnvioException):
    """No se puede enviar la solicitud."""
    def __init__(self, motivo: str):
        super().__init__(f"No se puede enviar la solicitud: {motivo}")
        self.motivo = motivo


class SolicitudYaEnviadaException(EnvioException):
    """La solicitud ya fue enviada."""
    def __init__(self, id_solicitud: str):
        super().__init__(f"La solicitud {id_solicitud} ya fue enviada")
        self.id_solicitud = id_solicitud


# =====================================================
# EXCEPCIONES DE MIGRANTE
# =====================================================

class MigranteException(DomainException):
    """Excepción base para migrantes."""
    pass


class MigranteNoEncontradoException(MigranteException):
    """El migrante no existe."""
    def __init__(self, id_migrante: str):
        super().__init__(f"Migrante {id_migrante} no encontrado")
        self.id_migrante = id_migrante


# =====================================================
# EXCEPCIONES DE ACCESO
# =====================================================

class AccesoDenegadoException(DomainException):
    """No tiene permisos para la operación."""
    def __init__(self, operacion: str):
        super().__init__(f"Acceso denegado para: {operacion}")
        self.operacion = operacion
