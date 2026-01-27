"""
Casos de Uso para Recepción de Solicitudes.
Orquestan la lógica de dominio y coordinan las operaciones.
"""
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

from ..domain.entities import SolicitudVisa, Documento, Asesor
from ..domain.value_objects import (
    TipoVisa, TipoEmbajada, EstadoSolicitud, 
    EstadoDocumento, ChecklistDocumentos
)
from ..domain.repositories import (
    ISolicitudRepository, IDocumentoRepository, 
    IMigranteRepository, IChecklistRepository
)
from ..domain.services import (
    RevisionSolicitudService, EnvioEmbajadaService,
    NotificacionService, ProgresoSolicitudService
)
from ..domain.exceptions import (
    SolicitudNoEncontradaException, DocumentosFaltantesException,
    EnvioNoPermitidoException, DocumentoNoEncontradoException
)


# =====================================================
# DTOs (Data Transfer Objects)
# =====================================================

@dataclass
class CrearSolicitudDTO:
    """DTO para crear una solicitud."""
    migrante_id: str
    tipo_visa: str
    embajada: str
    datos_personales: Dict = None


@dataclass
class CargarDocumentoDTO:
    """DTO para cargar un documento."""
    solicitud_id: str
    nombre_documento: str
    archivo_path: str = None


@dataclass
class RevisarDocumentoDTO:
    """DTO para revisar un documento."""
    solicitud_id: str
    nombre_documento: str
    resultado: str  # "Correcto" o "Incorrecto"
    motivo: str = ""
    asesor_id: str = None


@dataclass
class SolicitudResponseDTO:
    """DTO de respuesta con información de solicitud."""
    id: str
    codigo: str
    tipo_visa: str
    embajada: str
    estado: str
    estado_envio: str
    progreso: int
    total_documentos: int
    documentos_aprobados: int
    fecha_creacion: datetime
    
    @classmethod
    def from_entity(cls, solicitud: SolicitudVisa) -> 'SolicitudResponseDTO':
        """Crea un DTO desde una entidad."""
        progreso = ProgresoSolicitudService.calcular_progreso(solicitud)
        return cls(
            id=solicitud.id_solicitud or "",
            codigo=solicitud.id_solicitud or "",
            tipo_visa=solicitud.obtener_tipo_visa(),
            embajada=solicitud.obtener_embajada(),
            estado=solicitud.obtener_estado(),
            estado_envio=solicitud.obtener_estado_envio(),
            progreso=progreso['porcentaje'],
            total_documentos=progreso['total'],
            documentos_aprobados=progreso['aprobados'],
            fecha_creacion=solicitud.fecha_creacion
        )


# =====================================================
# CASOS DE USO
# =====================================================

class CrearSolicitudUseCase:
    """
    Caso de Uso: Crear una nueva solicitud de visa.
    
    Actor: Migrante
    Precondición: El migrante está autenticado
    Postcondición: Se crea una solicitud en estado BORRADOR
    """
    
    def __init__(
        self, 
        solicitud_repo: ISolicitudRepository,
        checklist_repo: IChecklistRepository,
        event_bus = None
    ):
        self.solicitud_repo = solicitud_repo
        self.checklist_repo = checklist_repo
        self.event_bus = event_bus
    
    def execute(self, dto: CrearSolicitudDTO) -> SolicitudResponseDTO:
        """
        Ejecuta la creación de una solicitud.
        
        Args:
            dto: Datos para crear la solicitud
            
        Returns:
            SolicitudResponseDTO con los datos de la solicitud creada
        """
        # Validar tipo de visa
        try:
            tipo_visa = TipoVisa(dto.tipo_visa)
        except ValueError:
            raise ValueError(f"Tipo de visa inválido: {dto.tipo_visa}")
        
        # Validar embajada
        try:
            embajada = TipoEmbajada(dto.embajada)
        except ValueError:
            raise ValueError(f"Embajada inválida: {dto.embajada}")
        
        # Crear entidad de dominio
        solicitud = SolicitudVisa(
            id_migrante=dto.migrante_id,
            tipo_visa=tipo_visa,
            embajada=embajada,
            estado="BORRADOR"
        )
        
        # Obtener checklist de documentos obligatorios
        documentos_obligatorios = self.checklist_repo.find_by_tipo_visa(dto.tipo_visa)
        if documentos_obligatorios:
            checklist = ChecklistDocumentos(tipo_visa, documentos_obligatorios)
            solicitud.asignar_checklist(checklist)
        
        # Persistir
        solicitud_guardada = self.solicitud_repo.save(solicitud)
        
        # Publicar evento
        if self.event_bus:
            self.event_bus.publish('SOLICITUD_CREADA', {
                'solicitud_id': solicitud_guardada.id_solicitud,
                'migrante_id': dto.migrante_id,
                'tipo_visa': dto.tipo_visa
            })
        
        return SolicitudResponseDTO.from_entity(solicitud_guardada)


class CargarDocumentosUseCase:
    """
    Caso de Uso: Cargar documentos a una solicitud.
    
    Actor: Migrante
    Precondición: La solicitud existe y está en estado que permite carga
    Postcondición: Los documentos quedan en estado EN_REVISION
    """
    
    def __init__(
        self,
        solicitud_repo: ISolicitudRepository,
        checklist_repo: IChecklistRepository,
        event_bus = None
    ):
        self.solicitud_repo = solicitud_repo
        self.checklist_repo = checklist_repo
        self.event_bus = event_bus
    
    def execute(
        self, 
        solicitud_id: str, 
        documentos: List[str]
    ) -> SolicitudResponseDTO:
        """
        Carga documentos a una solicitud.
        
        Args:
            solicitud_id: ID de la solicitud
            documentos: Lista de nombres de documentos a cargar
            
        Returns:
            SolicitudResponseDTO actualizado
        """
        # Obtener solicitud
        solicitud = self.solicitud_repo.find_by_id(solicitud_id)
        if not solicitud:
            raise SolicitudNoEncontradaException(solicitud_id)
        
        # Obtener checklist
        documentos_obligatorios = self.checklist_repo.find_by_tipo_visa(
            solicitud.obtener_tipo_visa()
        )
        
        if documentos_obligatorios:
            checklist = ChecklistDocumentos(
                TipoVisa(solicitud.obtener_tipo_visa()), 
                documentos_obligatorios
            )
            
            # Validar documentos faltantes
            faltantes = checklist.documentos_faltantes(documentos)
            if faltantes:
                raise DocumentosFaltantesException(faltantes)
            
            # Cargar documentos
            solicitud.cargar_documentos(documentos, checklist)
        else:
            # Sin checklist, cargar directamente
            for nombre in documentos:
                doc = Documento(nombre=nombre, estado="EN_REVISION")
                solicitud.agregar_documento(doc)
            solicitud.estado = "EN_REVISION"
        
        # Persistir
        solicitud_guardada = self.solicitud_repo.save(solicitud)
        
        # Publicar eventos
        if self.event_bus:
            for doc in documentos:
                self.event_bus.publish('DOCUMENTO_CARGADO', {
                    'solicitud_id': solicitud_id,
                    'documento': doc
                })
        
        return SolicitudResponseDTO.from_entity(solicitud_guardada)


class RevisarDocumentoUseCase:
    """
    Caso de Uso: Revisar un documento de una solicitud.
    
    Actor: Asesor
    Precondición: El documento está en estado EN_REVISION
    Postcondición: El documento cambia a APROBADO o DESAPROBADO
    """
    
    def __init__(
        self,
        solicitud_repo: ISolicitudRepository,
        event_bus = None
    ):
        self.solicitud_repo = solicitud_repo
        self.event_bus = event_bus
    
    def execute(self, dto: RevisarDocumentoDTO) -> Dict:
        """
        Revisa un documento.
        
        Args:
            dto: Datos de la revisión
            
        Returns:
            Dict con el resultado de la revisión
        """
        # Obtener solicitud
        solicitud = self.solicitud_repo.find_by_id(dto.solicitud_id)
        if not solicitud:
            raise SolicitudNoEncontradaException(dto.solicitud_id)
        
        # Obtener documento
        documento = solicitud.obtener_documento_por_nombre(dto.nombre_documento)
        if not documento:
            raise DocumentoNoEncontradoException(dto.nombre_documento)
        
        # Aplicar revisión
        if dto.resultado == "Correcto":
            documento.aprobar(revisor_id=dto.asesor_id)
            evento = 'DOCUMENTO_APROBADO'
        else:
            motivo = dto.motivo or f"Documento {dto.nombre_documento} marcado como incorrecto"
            if len(motivo) < 10:
                motivo = motivo + " - Por favor revise el documento"
            documento.rechazar(motivo=motivo, revisor_id=dto.asesor_id)
            evento = 'DOCUMENTO_RECHAZADO'
        
        # Actualizar estado de la solicitud
        solicitud.actualizar_estado()
        
        # Persistir
        self.solicitud_repo.save(solicitud)
        
        # Publicar evento
        if self.event_bus:
            self.event_bus.publish(evento, {
                'solicitud_id': dto.solicitud_id,
                'documento': dto.nombre_documento,
                'resultado': dto.resultado,
                'asesor_id': dto.asesor_id
            })
        
        return {
            'documento': dto.nombre_documento,
            'estado': documento.obtener_estado(),
            'solicitud_estado': solicitud.obtener_estado()
        }


class RevisarSolicitudCompletaUseCase:
    """
    Caso de Uso: Revisar todos los documentos de una solicitud.
    
    Actor: Asesor
    Precondición: La solicitud tiene documentos en revisión
    Postcondición: Todos los documentos quedan revisados y la solicitud actualizada
    """
    
    def __init__(
        self,
        solicitud_repo: ISolicitudRepository,
        event_bus = None
    ):
        self.solicitud_repo = solicitud_repo
        self.event_bus = event_bus
    
    def execute(
        self, 
        solicitud_id: str, 
        resultados: Dict[str, str],
        asesor_id: str = None
    ) -> SolicitudResponseDTO:
        """
        Revisa todos los documentos de una solicitud.
        
        Args:
            solicitud_id: ID de la solicitud
            resultados: Dict con nombre_documento -> "Correcto" o "Incorrecto"
            asesor_id: ID del asesor que revisa
            
        Returns:
            SolicitudResponseDTO actualizado
        """
        # Obtener solicitud
        solicitud = self.solicitud_repo.find_by_id(solicitud_id)
        if not solicitud:
            raise SolicitudNoEncontradaException(solicitud_id)
        
        # Usar servicio de dominio para revisar
        resumen = RevisionSolicitudService.revisar_documentos(
            solicitud, resultados, asesor_id or "ASESOR-001"
        )
        
        # Persistir
        solicitud_guardada = self.solicitud_repo.save(solicitud)
        
        # Publicar eventos
        if self.event_bus:
            if resumen['rechazados'] > 0:
                self.event_bus.publish('SOLICITUD_REQUIERE_CORRECCIONES', {
                    'solicitud_id': solicitud_id,
                    'documentos_rechazados': resumen['rechazados']
                })
            elif resumen['aprobados'] == resumen['total_documentos']:
                self.event_bus.publish('SOLICITUD_APROBADA', {
                    'solicitud_id': solicitud_id,
                    'asesor_id': asesor_id
                })
        
        return SolicitudResponseDTO.from_entity(solicitud_guardada)


class EnviarSolicitudEmbajadaUseCase:
    """
    Caso de Uso: Enviar solicitud aprobada a la embajada.
    
    Actor: Asesor
    Precondición: La solicitud está APROBADA con todos los documentos aprobados
    Postcondición: La solicitud queda en estado ENVIADO_EMBAJADA
    """
    
    def __init__(
        self,
        solicitud_repo: ISolicitudRepository,
        event_bus = None
    ):
        self.solicitud_repo = solicitud_repo
        self.event_bus = event_bus
    
    def execute(self, solicitud_id: str, asesor_id: str = None) -> Dict:
        """
        Envía la solicitud a la embajada.
        
        Args:
            solicitud_id: ID de la solicitud
            asesor_id: ID del asesor que envía
            
        Returns:
            Dict con el resultado del envío
        """
        # Obtener solicitud
        solicitud = self.solicitud_repo.find_by_id(solicitud_id)
        if not solicitud:
            raise SolicitudNoEncontradaException(solicitud_id)
        
        # Usar servicio de dominio para enviar
        resultado = EnvioEmbajadaService.enviar(solicitud)
        
        # Persistir
        self.solicitud_repo.save(solicitud)
        
        # Publicar evento
        if self.event_bus:
            self.event_bus.publish('SOLICITUD_ENVIADA', {
                'solicitud_id': solicitud_id,
                'embajada': solicitud.obtener_embajada(),
                'asesor_id': asesor_id
            })
        
        return resultado


class ConsultarSolicitudUseCase:
    """
    Caso de Uso: Consultar detalles de una solicitud.
    
    Actor: Migrante o Asesor
    """
    
    def __init__(self, solicitud_repo: ISolicitudRepository):
        self.solicitud_repo = solicitud_repo
    
    def execute(self, solicitud_id: str) -> SolicitudResponseDTO:
        """
        Consulta los detalles de una solicitud.
        
        Args:
            solicitud_id: ID de la solicitud
            
        Returns:
            SolicitudResponseDTO con los detalles
        """
        solicitud = self.solicitud_repo.find_by_id(solicitud_id)
        if not solicitud:
            raise SolicitudNoEncontradaException(solicitud_id)
        
        return SolicitudResponseDTO.from_entity(solicitud)


class ListarSolicitudesMigranteUseCase:
    """
    Caso de Uso: Listar todas las solicitudes de un migrante.
    
    Actor: Migrante
    """
    
    def __init__(self, solicitud_repo: ISolicitudRepository):
        self.solicitud_repo = solicitud_repo
    
    def execute(self, migrante_id: str) -> List[SolicitudResponseDTO]:
        """
        Lista las solicitudes de un migrante.
        
        Args:
            migrante_id: ID del migrante
            
        Returns:
            Lista de SolicitudResponseDTO
        """
        solicitudes = self.solicitud_repo.find_by_migrante(migrante_id)
        return [SolicitudResponseDTO.from_entity(s) for s in solicitudes]


class ObtenerProgresoUseCase:
    """
    Caso de Uso: Obtener el progreso de una solicitud.
    
    Actor: Migrante
    """
    
    def __init__(self, solicitud_repo: ISolicitudRepository):
        self.solicitud_repo = solicitud_repo
    
    def execute(self, solicitud_id: str) -> Dict:
        """
        Obtiene el progreso de una solicitud.
        
        Args:
            solicitud_id: ID de la solicitud
            
        Returns:
            Dict con información del progreso
        """
        solicitud = self.solicitud_repo.find_by_id(solicitud_id)
        if not solicitud:
            raise SolicitudNoEncontradaException(solicitud_id)
        
        progreso = ProgresoSolicitudService.calcular_progreso(solicitud)
        siguiente_paso = ProgresoSolicitudService.obtener_siguiente_paso(solicitud)
        
        return {
            **progreso,
            **siguiente_paso,
            'estado': solicitud.obtener_estado(),
            'estado_envio': solicitud.obtener_estado_envio()
        }
