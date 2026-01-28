"""
Servicios de Dominio para Recepción de Solicitudes.
Lógica de negocio que no pertenece a una entidad específica.
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from .entities import SolicitudVisa, Documento
from .value_objects import (
    EstadoDocumento, EstadoSolicitud, TipoNotificacion, ResultadoRevision
)
from .exceptions import (
    DocumentoNoEncontradoException,
    MotivoRechazoInvalidoException,
    EnvioNoPermitidoException,
    SolicitudYaEnviadaException
)


class ValidacionDocumentoService:
    """Servicio para validar documentos."""
    
    EXTENSIONES_PERMITIDAS = ['.pdf', '.jpg', '.jpeg', '.png']
    TAMANO_MAXIMO_MB = 10
    
    def validar_formato(self, archivo_path: str) -> bool:
        """Valida que el formato del archivo sea permitido."""
        extension = archivo_path.lower().split('.')[-1]
        return f'.{extension}' in self.EXTENSIONES_PERMITIDAS
    
    def validar_tamano(self, tamano_bytes: int) -> bool:
        """Valida que el tamaño no exceda el máximo."""
        tamano_mb = tamano_bytes / (1024 * 1024)
        return tamano_mb <= self.TAMANO_MAXIMO_MB


class RevisionSolicitudService:
    """Servicio para revisar solicitudes y documentos."""
    
    def revisar_documento(
        self, 
        solicitud: SolicitudVisa, 
        nombre_documento: str,
        resultado: ResultadoRevision,
        revisor_id: str
    ) -> Documento:
        """Revisa un documento específico de la solicitud."""
        documento = solicitud.obtener_documento_por_nombre(nombre_documento)
        
        if not documento:
            raise DocumentoNoEncontradoException(nombre_documento)
        
        if resultado.es_correcto:
            documento.aprobar(revisor_id)
        else:
            if not resultado.motivo_rechazo:
                raise MotivoRechazoInvalidoException()
            documento.rechazar(resultado.motivo_rechazo, revisor_id)
        
        solicitud.actualizar_estado()
        return documento
    
    def revisar_todos_documentos(
        self,
        solicitud: SolicitudVisa,
        resultados: Dict[str, ResultadoRevision],
        revisor_id: str
    ) -> SolicitudVisa:
        """Revisa todos los documentos de la solicitud."""
        for nombre, resultado in resultados.items():
            self.revisar_documento(solicitud, nombre, resultado, revisor_id)
        
        return solicitud


class EnvioEmbajadaService:
    """Servicio para gestionar envíos a embajada."""
    
    def validar_envio(self, solicitud: SolicitudVisa) -> bool:
        """Valida que la solicitud puede ser enviada."""
        if solicitud.estado_envio == "ENVIADO":
            raise SolicitudYaEnviadaException(solicitud.id_solicitud or "")
        
        if not solicitud.puede_ser_enviada():
            raise EnvioNoPermitidoException(
                "La solicitud debe estar aprobada para ser enviada"
            )
        
        return True
    
    def enviar(self, solicitud: SolicitudVisa) -> SolicitudVisa:
        """Procesa el envío de la solicitud a la embajada."""
        self.validar_envio(solicitud)
        solicitud.marcar_como_enviada()
        return solicitud


class NotificacionService:
    """Servicio para gestionar notificaciones."""
    
    def __init__(self):
        self.notificaciones_enviadas: List[Dict] = []
    
    def notificar_aprobacion(
        self, 
        id_migrante: str, 
        tipo_visa: str
    ) -> Dict:
        """Notifica la aprobación de una visa."""
        notificacion = {
            'tipo': f"VISA_{tipo_visa}_APROBADA",
            'destinatario': id_migrante,
            'mensaje': f"Su solicitud de visa {tipo_visa} ha sido aprobada",
            'fecha': datetime.now()
        }
        self.notificaciones_enviadas.append(notificacion)
        return notificacion
    
    def notificar_rechazo_documento(
        self,
        id_migrante: str,
        nombre_documento: str,
        motivo: str
    ) -> Dict:
        """Notifica el rechazo de un documento."""
        notificacion = {
            'tipo': f"DOCUMENTO_RECHAZADO: {nombre_documento}",
            'destinatario': id_migrante,
            'mensaje': f"El documento {nombre_documento} fue rechazado: {motivo}",
            'fecha': datetime.now()
        }
        self.notificaciones_enviadas.append(notificacion)
        return notificacion
    
    def notificar_envio_embajada(self, id_migrante: str) -> Dict:
        """Notifica que la solicitud fue enviada a la embajada."""
        notificacion = {
            'tipo': "SOLICITUD ENVIADA A EMBAJADA",
            'destinatario': id_migrante,
            'mensaje': "Su solicitud ha sido enviada a la embajada",
            'fecha': datetime.now()
        }
        self.notificaciones_enviadas.append(notificacion)
        return notificacion


class VencimientoDocumentoService:
    """Servicio para verificar vencimiento de documentos."""
    
    DIAS_VALIDEZ_DEFAULT = 180  # 6 meses
    
    def verificar_vencimiento(
        self, 
        fecha_emision: datetime,
        dias_validez: int = None
    ) -> bool:
        """Verifica si un documento está vencido."""
        dias = dias_validez or self.DIAS_VALIDEZ_DEFAULT
        fecha_vencimiento = fecha_emision + timedelta(days=dias)
        return datetime.now() > fecha_vencimiento
    
    def dias_para_vencer(
        self,
        fecha_emision: datetime,
        dias_validez: int = None
    ) -> int:
        """Calcula los días restantes hasta el vencimiento."""
        dias = dias_validez or self.DIAS_VALIDEZ_DEFAULT
        fecha_vencimiento = fecha_emision + timedelta(days=dias)
        diferencia = fecha_vencimiento - datetime.now()
        return max(0, diferencia.days)


class ProgresoSolicitudService:
    """Servicio para calcular el progreso de una solicitud."""
    
    def calcular_progreso(self, solicitud: SolicitudVisa) -> Dict:
        """Calcula el progreso detallado de la solicitud."""
        total = solicitud.obtener_total_documentos()
        if total == 0:
            return {
                'porcentaje': 0,
                'documentos_total': 0,
                'documentos_aprobados': 0,
                'documentos_pendientes': 0,
                'documentos_rechazados': 0
            }
        
        aprobados = sum(1 for d in solicitud.documentos if d.esta_aprobado())
        rechazados = sum(1 for d in solicitud.documentos if d.esta_rechazado())
        pendientes = total - aprobados - rechazados
        
        return {
            'porcentaje': int((aprobados / total) * 100),
            'documentos_total': total,
            'documentos_aprobados': aprobados,
            'documentos_pendientes': pendientes,
            'documentos_rechazados': rechazados
        }
