"""
Excepciones personalizadas para el dominio de Recepción de Solicitudes.
"""


class DomainException(Exception):
    """Excepción base para errores de dominio."""
    pass


class SolicitudException(DomainException):
    """Excepciones relacionadas con solicitudes."""
    pass


class SolicitudNoEncontradaException(SolicitudException):
    """La solicitud no fue encontrada."""
    
    def __init__(self, solicitud_id: str):
        self.solicitud_id = solicitud_id
        super().__init__(f"Solicitud con ID {solicitud_id} no encontrada")


class SolicitudYaExisteException(SolicitudException):
    """La solicitud ya existe."""
    
    def __init__(self, solicitud_id: str):
        self.solicitud_id = solicitud_id
        super().__init__(f"Ya existe una solicitud con ID {solicitud_id}")


class SolicitudEstadoInvalidoException(SolicitudException):
    """El estado de la solicitud no permite la operación."""
    
    def __init__(self, estado_actual: str, operacion: str):
        self.estado_actual = estado_actual
        self.operacion = operacion
        super().__init__(
            f"No se puede realizar '{operacion}' cuando la solicitud está en estado '{estado_actual}'"
        )


class DocumentoException(DomainException):
    """Excepciones relacionadas con documentos."""
    pass


class DocumentoNoEncontradoException(DocumentoException):
    """El documento no fue encontrado."""
    
    def __init__(self, documento_nombre: str):
        self.documento_nombre = documento_nombre
        super().__init__(f"Documento '{documento_nombre}' no encontrado")


class DocumentoInvalidoException(DocumentoException):
    """El documento no es válido."""
    
    def __init__(self, mensaje: str):
        super().__init__(mensaje)


class DocumentoNoRecargableException(DocumentoException):
    """El documento no puede ser recargado."""
    
    def __init__(self, documento_nombre: str, estado: str):
        self.documento_nombre = documento_nombre
        self.estado = estado
        super().__init__(
            f"El documento '{documento_nombre}' en estado '{estado}' no puede ser recargado. "
            "Solo se pueden recargar documentos rechazados."
        )


class MotivoRechazoInvalidoException(DocumentoException):
    """El motivo de rechazo no es válido."""
    
    def __init__(self):
        super().__init__("El motivo de rechazo debe tener al menos 10 caracteres")


class ChecklistException(DomainException):
    """Excepciones relacionadas con checklists."""
    pass


class ChecklistNoEncontradoException(ChecklistException):
    """El checklist no fue encontrado."""
    
    def __init__(self, tipo_visa: str):
        self.tipo_visa = tipo_visa
        super().__init__(f"No existe checklist para el tipo de visa '{tipo_visa}'")


class DocumentosFaltantesException(ChecklistException):
    """Faltan documentos obligatorios."""
    
    def __init__(self, documentos_faltantes: list):
        self.documentos_faltantes = documentos_faltantes
        super().__init__(
            f"Faltan los siguientes documentos obligatorios: {', '.join(documentos_faltantes)}"
        )


class EnvioException(DomainException):
    """Excepciones relacionadas con el envío a embajada."""
    pass


class EnvioNoPermitidoException(EnvioException):
    """El envío a embajada no está permitido."""
    
    def __init__(self, motivo: str):
        self.motivo = motivo
        super().__init__(f"No se puede enviar a embajada: {motivo}")


class SolicitudYaEnviadaException(EnvioException):
    """La solicitud ya fue enviada a la embajada."""
    
    def __init__(self, solicitud_id: str):
        self.solicitud_id = solicitud_id
        super().__init__(f"La solicitud {solicitud_id} ya fue enviada a la embajada")


class MigranteException(DomainException):
    """Excepciones relacionadas con migrantes."""
    pass


class MigranteNoEncontradoException(MigranteException):
    """El migrante no fue encontrado."""
    
    def __init__(self, migrante_id: str):
        self.migrante_id = migrante_id
        super().__init__(f"Migrante con ID {migrante_id} no encontrado")


class AccesoDenegadoException(DomainException):
    """Acceso denegado a un recurso."""
    
    def __init__(self, recurso: str, usuario: str):
        self.recurso = recurso
        self.usuario = usuario
        super().__init__(
            f"El usuario '{usuario}' no tiene permisos para acceder a '{recurso}'"
        )
