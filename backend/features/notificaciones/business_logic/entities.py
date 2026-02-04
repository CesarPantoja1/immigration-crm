# -*- coding: utf-8 -*-

from datetime import date, datetime
from typing import List, Optional

from .constants import ESTADOS_SOLICITUD, TIPOS_VISA, EMBAJADAS, ESTADOS_DOCUMENTO, TIPOS_NOTIFICACION

# ENTIDAD: Usuario

class UsuarioEntity:
    """Representa un usuario en el dominio de testing."""
    
    ROLES = ['cliente', 'asesor', 'admin']
    
    def __init__(self, id: int, email: str, nombre: str, apellido: str, rol: str = 'cliente'):
        self.id = id
        self.email = email
        self.nombre = nombre
        self.apellido = apellido
        self.rol = rol if rol in self.ROLES else 'cliente'
    
    def get_full_name(self) -> str:
        """Retorna nombre completo (método real del modelo)."""
        return f"{self.nombre} {self.apellido}"

# ENTIDAD: Documento

class DocumentoEntity:
    """Representa un documento en el dominio de testing."""
    
    def __init__(self, id: int, nombre: str, estado: str = 'pendiente', 
                 fecha_vencimiento: date = None, observaciones: str = ''):
        self.id = id
        self.nombre = nombre
        self.tipo = nombre  # Alias para compatibilidad
        self.estado = estado if estado in ESTADOS_DOCUMENTO else 'pendiente'
        self.fecha_vencimiento = fecha_vencimiento
        self.observaciones = observaciones
    
    def esta_aprobado(self) -> bool:
        return self.estado == 'aprobado'
    
    def esta_rechazado(self) -> bool:
        return self.estado == 'rechazado'
    
    def esta_pendiente(self) -> bool:
        return self.estado == 'pendiente'

# ENTIDAD: Solicitud

class SolicitudEntity:
    """Representa una solicitud en el dominio de testing."""
    
    def __init__(self, id: int, codigo: str, tipo_visa: str, embajada: str,
                 estado: str, cliente_email: str, fecha_creacion: date = None,
                 documentos_requeridos: int = 0, motivo_rechazo_embajada: str = '',
                 asesor_id: int = None):
        self.id = id
        self.codigo = codigo
        self.tipo_visa = tipo_visa.lower() if tipo_visa.lower() in TIPOS_VISA else 'trabajo'
        self.embajada = embajada.lower() if embajada.lower() in EMBAJADAS else 'usa'
        self.estado = self._normalizar_estado(estado)
        self.cliente_email = cliente_email
        self.asesor_id = asesor_id
        self.fecha_creacion = fecha_creacion or date.today()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.fecha_actualizacion = self.updated_at
        self.documentos_requeridos = documentos_requeridos
        self.documentos: List[DocumentoEntity] = []
        self.motivo_rechazo_embajada = motivo_rechazo_embajada
        self.is_deleted = False  # SoftDeleteModel
    
    def _normalizar_estado(self, estado: str) -> str:
        """Normaliza el estado al formato real."""
        estado_lower = estado.lower()
        mapeo = {
            'en_proceso': 'en_revision',
            'pendiente_correccion': 'en_revision',
            'pendiente_revision': 'pendiente',
            'contrato_pendiente': 'pendiente',
        }
        return mapeo.get(estado_lower, estado_lower)
    
    def agregar_documento(self, documento: DocumentoEntity) -> None:
        self.documentos.append(documento)
    
    def contar_documentos_aprobados(self) -> int:
        return sum(1 for d in self.documentos if d.esta_aprobado())
    
    def contar_documentos_rechazados(self) -> int:
        return sum(1 for d in self.documentos if d.esta_rechazado())
    
    def obtener_documentos_rechazados(self) -> List[DocumentoEntity]:
        return [d for d in self.documentos if d.esta_rechazado()]
    
    def obtener_progreso(self) -> int:
        """Calcula porcentaje de progreso documental."""
        if self.documentos_requeridos == 0:
            return 0
        return int((self.contar_documentos_aprobados() / self.documentos_requeridos) * 100)
    
    def obtener_pendientes(self) -> int:
        """Calcula documentos pendientes."""
        return self.documentos_requeridos - self.contar_documentos_aprobados()
    
    def cambiar_estado(self, nuevo_estado: str) -> None:
        self.estado = self._normalizar_estado(nuevo_estado)
        self.updated_at = datetime.now()
        self.fecha_actualizacion = self.updated_at
    
    # Métodos del modelo real (delegados a SolicitudService)
    def puede_agendar_entrevista(self) -> bool:
        """Fuente: apps/solicitudes/models.py línea 155"""
        return self.estado == 'aprobada_embajada'
    
    def puede_modificar_documentos(self) -> bool:
        """Fuente: apps/solicitudes/models.py líneas 161-171"""
        estados_bloqueados = [
            'enviada_embajada', 'esperando_decision_embajada',
            'aprobada_embajada', 'rechazada_embajada',
            'entrevista_agendada', 'completada'
        ]
        return self.estado not in estados_bloqueados
    
    def puede_ser_asignada(self) -> bool:
        """Fuente: apps/solicitudes/models.py línea 141"""
        return self.estado in ['pendiente', 'borrador'] and self.asesor_id is None

# ENTIDAD: Notificacion

class NotificacionEntity:
    """Representa una notificación en el dominio de testing."""
    
    def __init__(self, id: int, tipo: str, titulo: str, mensaje: str,
                 usuario_id: int, solicitud_id: int = None,
                 leida: bool = False, url_accion: str = '', detalle: str = '',
                 datos: dict = None):
        self.id = id
        self.tipo = tipo if tipo in TIPOS_NOTIFICACION else 'general'
        self.titulo = titulo
        self.mensaje = mensaje
        self.detalle = detalle
        self.usuario_id = usuario_id
        self.solicitud_id = solicitud_id  # FK real
        self.leida = leida
        self.created_at = datetime.now()
        self.fecha_lectura = None
        self.url_accion = url_accion
        self.datos = datos or {}
    
    def marcar_como_leida(self) -> None:
        """Método del modelo real (líneas 117-122)."""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = datetime.now()

# FACTORY FUNCTIONS - Helpers para crear instancias

_id_counter = {'usuario': 0, 'solicitud': 0, 'documento': 0, 'notificacion': 0}


def reset_id_counters():
    """Reinicia los contadores de IDs para cada escenario."""
    global _id_counter
    _id_counter = {'usuario': 0, 'solicitud': 0, 'documento': 0, 'notificacion': 0}


def crear_usuario(email: str, nombre: str = 'Usuario', apellido: str = 'Test', 
                  rol: str = 'cliente') -> UsuarioEntity:
    """Crea una instancia de Usuario."""
    _id_counter['usuario'] += 1
    return UsuarioEntity(_id_counter['usuario'], email, nombre, apellido, rol)


def crear_solicitud(codigo: str, tipo_visa: str, embajada: str, estado: str,
                    cliente_email: str, fecha_creacion: date = None,
                    documentos_requeridos: int = 0) -> SolicitudEntity:
    """Crea una instancia de Solicitud."""
    _id_counter['solicitud'] += 1
    return SolicitudEntity(
        _id_counter['solicitud'], codigo, tipo_visa, embajada, estado,
        cliente_email, fecha_creacion, documentos_requeridos
    )


def crear_documento(nombre: str, estado: str = 'pendiente',
                    fecha_vencimiento: date = None, observaciones: str = '') -> DocumentoEntity:
    """Crea una instancia de Documento."""
    _id_counter['documento'] += 1
    return DocumentoEntity(_id_counter['documento'], nombre, estado, 
                           fecha_vencimiento, observaciones)


def crear_notificacion(tipo: str, titulo: str, mensaje: str, usuario_id: int,
                       solicitud_id: int = None, leida: bool = False,
                       detalle: str = '', datos: dict = None) -> NotificacionEntity:
    """Crea una instancia de Notificación."""
    _id_counter['notificacion'] += 1
    return NotificacionEntity(
        _id_counter['notificacion'], tipo, titulo, mensaje,
        usuario_id, solicitud_id, leida, '', detalle, datos
    )
