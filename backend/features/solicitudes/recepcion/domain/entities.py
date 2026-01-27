"""
Entidades de Dominio para Recepción de Solicitudes.
Objetos con identidad que encapsulan lógica de negocio.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from .value_objects import (
    TipoVisa, TipoEmbajada, EstadoSolicitud, EstadoDocumento,
    EstadoEnvio, ChecklistDocumentos
)


@dataclass
class Documento:
    """
    Entidad Documento - Representa un documento adjunto a una solicitud.
    """
    nombre: str
    estado: str = "PENDIENTE"
    archivo_path: Optional[str] = None
    version: int = 1
    motivo_rechazo: Optional[str] = None
    fecha_carga: datetime = field(default_factory=datetime.now)
    fecha_revision: Optional[datetime] = None
    revisor_id: Optional[str] = None
    
    def obtener_nombre(self) -> str:
        """Retorna el nombre del documento."""
        return self.nombre
    
    def obtener_estado(self) -> str:
        """Retorna el estado actual del documento."""
        return self.estado
    
    def marcar_en_revision(self) -> None:
        """Marca el documento como en revisión."""
        self.estado = EstadoDocumento.EN_REVISION.value
    
    def aprobar(self, revisor_id: str = None) -> None:
        """Aprueba el documento."""
        self.estado = EstadoDocumento.APROBADO.value
        self.fecha_revision = datetime.now()
        if revisor_id:
            self.revisor_id = revisor_id
    
    def rechazar(self, motivo: str, revisor_id: str = None) -> None:
        """Rechaza el documento con un motivo."""
        if not motivo or len(motivo) < 10:
            raise ValueError("El motivo de rechazo debe tener al menos 10 caracteres")
        self.estado = EstadoDocumento.DESAPROBADO.value
        self.motivo_rechazo = motivo
        self.fecha_revision = datetime.now()
        if revisor_id:
            self.revisor_id = revisor_id
    
    def esta_aprobado(self) -> bool:
        """Verifica si el documento está aprobado."""
        return self.estado == EstadoDocumento.APROBADO.value
    
    def esta_rechazado(self) -> bool:
        """Verifica si el documento está rechazado."""
        return self.estado in [EstadoDocumento.DESAPROBADO.value, 
                               EstadoDocumento.RECHAZADO.value]
    
    def puede_recargar(self) -> bool:
        """Verifica si se puede recargar una nueva versión."""
        return self.esta_rechazado()
    
    def recargar(self, nuevo_archivo_path: str) -> None:
        """Recarga una nueva versión del documento."""
        if not self.puede_recargar():
            raise ValueError("Solo se pueden recargar documentos rechazados")
        self.archivo_path = nuevo_archivo_path
        self.version += 1
        self.estado = EstadoDocumento.EN_REVISION.value
        self.motivo_rechazo = None
        self.fecha_carga = datetime.now()


@dataclass
class SolicitudVisa:
    """
    Entidad SolicitudVisa - Agregado raíz para solicitudes de visa.
    """
    id_migrante: str
    tipo_visa: TipoVisa
    embajada: TipoEmbajada
    id_solicitud: Optional[str] = None
    estado: str = field(default="BORRADOR")
    estado_envio: str = field(default="PENDIENTE")
    documentos: List[Documento] = field(default_factory=list)
    checklist: Optional[ChecklistDocumentos] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)
    notas: str = ""
    
    def obtener_tipo_visa(self) -> str:
        """Retorna el tipo de visa como string."""
        return self.tipo_visa.value if isinstance(self.tipo_visa, TipoVisa) else self.tipo_visa
    
    def obtener_embajada(self) -> str:
        """Retorna la embajada como string."""
        return self.embajada.value if isinstance(self.embajada, TipoEmbajada) else self.embajada
    
    def obtener_estado(self) -> str:
        """Retorna el estado actual de la solicitud."""
        return self.estado
    
    def obtener_estado_envio(self) -> str:
        """Retorna el estado de envío a la embajada."""
        return self.estado_envio
    
    def obtener_documentos(self) -> List[Documento]:
        """Retorna la lista de documentos."""
        return self.documentos
    
    def obtener_total_documentos(self) -> int:
        """Retorna el total de documentos cargados."""
        return len(self.documentos)
    
    def asignar_checklist(self, checklist: ChecklistDocumentos) -> None:
        """Asigna el checklist de documentos obligatorios."""
        self.checklist = checklist
    
    def inicializar_documentos_desde_checklist(self) -> None:
        """Inicializa los documentos desde el checklist asignado."""
        if not self.checklist:
            raise ValueError("No se ha asignado un checklist")
        
        self.documentos = [
            Documento(nombre=nombre, estado="EN_REVISION")
            for nombre in self.checklist.documentos_obligatorios
        ]
        self.estado = EstadoSolicitud.EN_REVISION.value
    
    def cargar_documentos(self, nombres_documentos: List[str], 
                         checklist: ChecklistDocumentos) -> None:
        """
        Carga documentos validando contra el checklist.
        """
        self.checklist = checklist
        
        # Validar que todos los documentos obligatorios estén
        faltantes = checklist.documentos_faltantes(nombres_documentos)
        if faltantes:
            raise ValueError(f"Faltan documentos obligatorios: {faltantes}")
        
        # Crear los documentos con estado EN_REVISION
        self.documentos = [
            Documento(nombre=nombre, estado="EN_REVISION")
            for nombre in nombres_documentos
        ]
        
        # Actualizar estado de la solicitud
        self.estado = EstadoSolicitud.EN_REVISION.value
        self.fecha_actualizacion = datetime.now()
    
    def agregar_documento(self, documento: Documento) -> None:
        """Agrega un documento a la solicitud."""
        self.documentos.append(documento)
        self.fecha_actualizacion = datetime.now()
    
    def obtener_documento_por_nombre(self, nombre: str) -> Optional[Documento]:
        """Busca un documento por su nombre."""
        for doc in self.documentos:
            if doc.nombre == nombre:
                return doc
        return None
    
    def todos_documentos_aprobados(self) -> bool:
        """Verifica si todos los documentos están aprobados."""
        if not self.documentos:
            return False
        return all(doc.esta_aprobado() for doc in self.documentos)
    
    def algun_documento_rechazado(self) -> bool:
        """Verifica si algún documento está rechazado."""
        return any(doc.esta_rechazado() for doc in self.documentos)
    
    def actualizar_estado(self) -> None:
        """Actualiza el estado de la solicitud según los documentos."""
        if self.todos_documentos_aprobados():
            self.estado = EstadoSolicitud.APROBADO.value
        elif self.algun_documento_rechazado():
            self.estado = EstadoSolicitud.DESAPROBADO.value
        else:
            self.estado = EstadoSolicitud.EN_REVISION.value
        self.fecha_actualizacion = datetime.now()
    
    def puede_ser_enviada(self) -> bool:
        """Verifica si la solicitud puede ser enviada a la embajada."""
        return (self.estado == EstadoSolicitud.APROBADO.value and 
                self.estado_envio == EstadoEnvio.PENDIENTE.value)
    
    def marcar_como_enviada(self) -> None:
        """Marca la solicitud como enviada a la embajada."""
        if not self.puede_ser_enviada():
            raise ValueError("La solicitud no puede ser enviada")
        self.estado_envio = EstadoEnvio.ENVIADO.value
        self.estado = EstadoSolicitud.ENVIADO_EMBAJADA.value
        self.fecha_actualizacion = datetime.now()
    
    def calcular_progreso(self) -> int:
        """Calcula el porcentaje de progreso de la solicitud."""
        if not self.documentos:
            return 0
        aprobados = sum(1 for doc in self.documentos if doc.esta_aprobado())
        return int((aprobados / len(self.documentos)) * 100)
    
    def documentos_pendientes(self) -> List[Documento]:
        """Retorna los documentos que no están aprobados."""
        return [doc for doc in self.documentos if not doc.esta_aprobado()]
    
    def __str__(self) -> str:
        return (f"SolicitudVisa(id={self.id_solicitud}, tipo={self.obtener_tipo_visa()}, "
                f"embajada={self.obtener_embajada()}, estado={self.estado})")


@dataclass
class Migrante:
    """
    Entidad Migrante - Representa a un solicitante de visa.
    """
    id: str
    email: str
    nombres: str
    apellidos: str
    telefono: str = ""
    numero_pasaporte: str = ""
    nacionalidad: str = ""
    solicitudes: List[SolicitudVisa] = field(default_factory=list)
    fecha_registro: datetime = field(default_factory=datetime.now)
    
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del migrante."""
        return f"{self.nombres} {self.apellidos}"
    
    def agregar_solicitud(self, solicitud: SolicitudVisa) -> None:
        """Agrega una solicitud al migrante."""
        self.solicitudes.append(solicitud)
    
    def obtener_solicitudes(self) -> List[SolicitudVisa]:
        """Retorna todas las solicitudes del migrante."""
        return self.solicitudes
    
    def total_solicitudes(self) -> int:
        """Retorna el total de solicitudes."""
        return len(self.solicitudes)


@dataclass  
class Asesor:
    """
    Entidad Asesor - Representa a un asesor de la agencia.
    """
    id: str = "ASESOR-001"
    nombre: str = "Asesor Genérico"
    email: str = "asesor@agencia.com"
    
    def revisar_solicitud(self, solicitud: SolicitudVisa, 
                         resultados: Dict[str, str]) -> None:
        """
        Revisa todos los documentos de una solicitud.
        
        Args:
            solicitud: La solicitud a revisar
            resultados: Dict con nombre_documento -> "Correcto" o "Incorrecto"
        """
        for doc in solicitud.obtener_documentos():
            resultado = resultados.get(doc.obtener_nombre(), "Correcto")
            if resultado == "Correcto":
                doc.aprobar(revisor_id=self.id)
            else:
                doc.rechazar(
                    motivo=f"Documento {doc.obtener_nombre()} marcado como incorrecto por el asesor",
                    revisor_id=self.id
                )
        
        # Actualizar estado de la solicitud
        solicitud.actualizar_estado()
    
    def enviar_solicitud(self, solicitud: SolicitudVisa, enviada: str = "SI") -> str:
        """
        Envía una solicitud aprobada a la embajada.
        
        Args:
            solicitud: La solicitud a enviar
            enviada: "SI" para confirmar envío
            
        Returns:
            Mensaje de confirmación
        """
        if enviada == "SI" and solicitud.puede_ser_enviada():
            solicitud.marcar_como_enviada()
            return "SOLICITUD ENVIADA A EMBAJADA"
        else:
            raise ValueError("No se puede enviar la solicitud")


@dataclass
class AgenciaMigracion:
    """
    Entidad AgenciaMigracion - Gestiona solicitudes y migrantes.
    """
    nombre: str = "MigraFácil"
    solicitudes: List[SolicitudVisa] = field(default_factory=list)
    migrantes: Dict[str, Migrante] = field(default_factory=dict)
    
    def registrar_solicitud(self, solicitud: SolicitudVisa) -> None:
        """Registra una nueva solicitud en la agencia."""
        self.solicitudes.append(solicitud)
    
    def total_solicitudes(self) -> int:
        """Retorna el total de solicitudes registradas."""
        return len(self.solicitudes)
    
    def obtener_solicitud_por_id(self, id_solicitud: str) -> Optional[SolicitudVisa]:
        """Busca una solicitud por su ID."""
        for solicitud in self.solicitudes:
            if solicitud.id_solicitud == id_solicitud:
                return solicitud
        return None
    
    def registrar_migrante(self, solicitud: SolicitudVisa) -> Migrante:
        """Registra un migrante a partir de una solicitud."""
        if solicitud.id_migrante not in self.migrantes:
            migrante = Migrante(
                id=solicitud.id_migrante,
                email=f"{solicitud.id_migrante}@ejemplo.com",
                nombres="Migrante",
                apellidos="Demo"
            )
            self.migrantes[solicitud.id_migrante] = migrante
        
        migrante = self.migrantes[solicitud.id_migrante]
        migrante.agregar_solicitud(solicitud)
        return migrante
    
    def obtener_migrante_por_id(self, id_migrante: str) -> Optional[Migrante]:
        """Busca un migrante por su ID."""
        return self.migrantes.get(id_migrante)
    
    def total_migrantes(self) -> int:
        """Retorna el total de migrantes registrados."""
        return len(self.migrantes)
    
    def solicitudes_por_estado(self, estado: str) -> List[SolicitudVisa]:
        """Filtra solicitudes por estado."""
        return [s for s in self.solicitudes if s.obtener_estado() == estado]
