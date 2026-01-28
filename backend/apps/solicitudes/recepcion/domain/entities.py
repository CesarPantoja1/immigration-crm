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
        return self.nombre
    
    def obtener_estado(self) -> str:
        return self.estado
    
    def marcar_en_revision(self) -> None:
        self.estado = "EN_REVISION"
    
    def aprobar(self, revisor_id: str = None) -> None:
        self.estado = "APROBADO"
        self.fecha_revision = datetime.now()
        self.revisor_id = revisor_id
    
    def rechazar(self, motivo: str, revisor_id: str = None) -> None:
        self.estado = "DESAPROBADO"
        self.motivo_rechazo = motivo
        self.fecha_revision = datetime.now()
        self.revisor_id = revisor_id
    
    def esta_aprobado(self) -> bool:
        return self.estado == "APROBADO"
    
    def esta_rechazado(self) -> bool:
        return self.estado == "DESAPROBADO"
    
    def puede_recargar(self) -> bool:
        return self.estado == "DESAPROBADO"
    
    def recargar(self, nuevo_archivo_path: str) -> None:
        if self.puede_recargar():
            self.archivo_path = nuevo_archivo_path
            self.estado = "EN_REVISION"
            self.version += 1
            self.motivo_rechazo = None


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
        return self.tipo_visa.value if isinstance(self.tipo_visa, TipoVisa) else self.tipo_visa
    
    def obtener_embajada(self) -> str:
        return self.embajada.value if isinstance(self.embajada, TipoEmbajada) else self.embajada
    
    def obtener_estado(self) -> str:
        return self.estado
    
    def obtener_estado_envio(self) -> str:
        return self.estado_envio
    
    def obtener_documentos(self) -> List[Documento]:
        return self.documentos
    
    def obtener_total_documentos(self) -> int:
        return len(self.documentos)
    
    def asignar_checklist(self, checklist: ChecklistDocumentos) -> None:
        self.checklist = checklist
    
    def inicializar_documentos_desde_checklist(self) -> None:
        if self.checklist:
            for nombre_doc in self.checklist.obtener_documentos():
                self.documentos.append(Documento(nombre=nombre_doc))
    
    def cargar_documentos(self, nombres_documentos: List[str], 
                         checklist: ChecklistDocumentos) -> None:
        self.asignar_checklist(checklist)
        for nombre in nombres_documentos:
            doc = Documento(nombre=nombre, estado="EN_REVISION")
            self.documentos.append(doc)
        self.estado = "EN_REVISION"
    
    def agregar_documento(self, documento: Documento) -> None:
        self.documentos.append(documento)
        self.fecha_actualizacion = datetime.now()
    
    def obtener_documento_por_nombre(self, nombre: str) -> Optional[Documento]:
        for doc in self.documentos:
            if doc.nombre == nombre:
                return doc
        return None
    
    def todos_documentos_aprobados(self) -> bool:
        if not self.documentos:
            return False
        return all(doc.esta_aprobado() for doc in self.documentos)
    
    def algun_documento_rechazado(self) -> bool:
        return any(doc.esta_rechazado() for doc in self.documentos)
    
    def actualizar_estado(self) -> None:
        if self.todos_documentos_aprobados():
            self.estado = "APROBADO"
        elif self.algun_documento_rechazado():
            self.estado = "DESAPROBADO"
        self.fecha_actualizacion = datetime.now()
    
    def puede_ser_enviada(self) -> bool:
        return self.estado == "APROBADO" and self.estado_envio == "PENDIENTE"
    
    def marcar_como_enviada(self) -> None:
        if self.puede_ser_enviada():
            self.estado_envio = "ENVIADO"
            self.fecha_actualizacion = datetime.now()
    
    def calcular_progreso(self) -> int:
        if not self.documentos:
            return 0
        aprobados = sum(1 for doc in self.documentos if doc.esta_aprobado())
        return int((aprobados / len(self.documentos)) * 100)
    
    def documentos_pendientes(self) -> List[Documento]:
        return [doc for doc in self.documentos if doc.estado == "PENDIENTE"]


@dataclass
class Migrante:
    """Entidad Migrante - Persona que solicita la visa."""
    id: str
    nombre: str
    apellido: str
    email: str
    pasaporte: Optional[str] = None
    nacionalidad: Optional[str] = None
    telefono: Optional[str] = None
    
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


@dataclass  
class Asesor:
    """Entidad Asesor - Persona que revisa solicitudes."""
    id: str
    nombre: str
    email: str
    solicitudes_asignadas: List[str] = field(default_factory=list)
    limite_diario: int = 10
    
    def puede_recibir_solicitud(self, solicitudes_hoy: int) -> bool:
        return solicitudes_hoy < self.limite_diario


@dataclass
class AgenciaMigracion:
    """Agregado para gestionar la agencia."""
    nombre: str = "MigraFácil"
    solicitudes: List[SolicitudVisa] = field(default_factory=list)
    
    def agregar_solicitud(self, solicitud: SolicitudVisa) -> None:
        self.solicitudes.append(solicitud)
    
    def obtener_solicitud(self, id_solicitud: str) -> Optional[SolicitudVisa]:
        for s in self.solicitudes:
            if s.id_solicitud == id_solicitud:
                return s
        return None
    
    def solicitudes_por_estado(self, estado: str) -> List[SolicitudVisa]:
        return [s for s in self.solicitudes if s.obtener_estado() == estado]


@dataclass
class AsignadorSolicitudes:
    """
    Servicio de Dominio para asignar solicitudes a asesores.
    Implementa la regla de negocio de límite diario por asesor.
    """
    limite_diario: int = 10
    asesores: Dict[str, Dict] = field(default_factory=dict)
    
    def registrar_asesor(self, asesor: Asesor, solicitudes_hoy: int = 0) -> None:
        """Registra un asesor con su carga actual de trabajo."""
        self.asesores[asesor.nombre] = {
            'asesor': asesor,
            'solicitudes_hoy': solicitudes_hoy
        }
    
    def obtener_solicitudes_asesor(self, nombre: str) -> int:
        """Obtiene el número de solicitudes asignadas hoy a un asesor."""
        if nombre in self.asesores:
            return self.asesores[nombre]['solicitudes_hoy']
        return 0
    
    def asesor_disponible(self, nombre: str) -> bool:
        """Verifica si un asesor tiene disponibilidad."""
        return self.obtener_solicitudes_asesor(nombre) < self.limite_diario
    
    def obtener_asesor_con_menos_carga(self) -> Optional[str]:
        """Encuentra el asesor con menos solicitudes asignadas hoy."""
        asesor_elegido = None
        min_carga = float('inf')
        
        for nombre, datos in self.asesores.items():
            solicitudes = datos['solicitudes_hoy']
            if solicitudes < self.limite_diario and solicitudes < min_carga:
                min_carga = solicitudes
                asesor_elegido = nombre
        
        return asesor_elegido
    
    def asignar_solicitud(self, solicitud: SolicitudVisa) -> Dict:
        """Asigna una solicitud al asesor con menos carga."""
        asesor_nombre = self.obtener_asesor_con_menos_carga()
        
        if asesor_nombre is None:
            return {
                'exito': False,
                'asesor_nombre': None,
                'mensaje': 'No hay asesores disponibles. Todos han alcanzado el límite diario.'
            }
        
        self.asesores[asesor_nombre]['solicitudes_hoy'] += 1
        
        return {
            'exito': True,
            'asesor_nombre': asesor_nombre,
            'mensaje': f'Solicitud asignada exitosamente a {asesor_nombre}'
        }
    
    def asignar_a_asesor_especifico(self, solicitud: SolicitudVisa, 
                                     nombre_asesor: str) -> Dict:
        """Intenta asignar una solicitud a un asesor específico."""
        if nombre_asesor not in self.asesores:
            return {
                'exito': False,
                'mensaje': f'Asesor {nombre_asesor} no encontrado'
            }
        
        if not self.asesor_disponible(nombre_asesor):
            return {
                'exito': False,
                'mensaje': 'El asesor ha alcanzado el límite diario de solicitudes'
            }
        
        self.asesores[nombre_asesor]['solicitudes_hoy'] += 1
        
        return {
            'exito': True,
            'asesor_nombre': nombre_asesor,
            'mensaje': f'Solicitud asignada a {nombre_asesor}'
        }
