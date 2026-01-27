"""
Implementación de Repositorios usando Django ORM.
Adaptadores que implementan los puertos definidos en el dominio.
"""
from typing import List, Optional
from datetime import datetime
from django.db import transaction

from ..domain.entities import SolicitudVisa, Documento, Migrante
from ..domain.value_objects import TipoVisa, TipoEmbajada, ChecklistDocumentos
from ..domain.repositories import (
    ISolicitudRepository, 
    IDocumentoRepository, 
    IMigranteRepository,
    IChecklistRepository
)
from .models import (
    SolicitudModel, 
    DocumentoModel, 
    ChecklistDocumentosModel,
    EventoSolicitudModel
)
from apps.usuarios.infrastructure.models import UsuarioModel


class DjangoSolicitudRepository(ISolicitudRepository):
    """Implementación del repositorio de solicitudes con Django ORM."""
    
    def save(self, solicitud: SolicitudVisa) -> SolicitudVisa:
        """Guarda o actualiza una solicitud."""
        with transaction.atomic():
            # Obtener o crear el migrante
            migrante, _ = UsuarioModel.objects.get_or_create(
                id=1,  # Por defecto
                defaults={
                    'nombre': 'Migrante',
                    'apellido': 'Demo',
                    'rol': 'cliente'
                }
            )
            
            if solicitud.id_solicitud:
                # Actualizar existente
                try:
                    model = SolicitudModel.objects.get(codigo=solicitud.id_solicitud)
                    model.tipo_visa = solicitud.obtener_tipo_visa()
                    model.embajada_nombre = solicitud.obtener_embajada()
                    model.estado = solicitud.estado
                    model.estado_envio = solicitud.estado_envio
                    model.notas = solicitud.notas
                    model.save()
                except SolicitudModel.DoesNotExist:
                    model = self._crear_modelo(solicitud, migrante)
            else:
                model = self._crear_modelo(solicitud, migrante)
            
            # Guardar documentos
            for doc in solicitud.documentos:
                self._guardar_documento(doc, model)
            
            # Actualizar ID de la solicitud
            solicitud.id_solicitud = model.codigo
            
            return solicitud
    
    def _crear_modelo(self, solicitud: SolicitudVisa, migrante) -> SolicitudModel:
        """Crea un nuevo modelo de solicitud."""
        model = SolicitudModel.objects.create(
            migrante=migrante,
            tipo_visa=solicitud.obtener_tipo_visa(),
            embajada_nombre=solicitud.obtener_embajada(),
            estado=solicitud.estado,
            estado_envio=solicitud.estado_envio,
            notas=solicitud.notas
        )
        return model
    
    def _guardar_documento(self, doc: Documento, solicitud_model: SolicitudModel):
        """Guarda un documento asociado a una solicitud."""
        DocumentoModel.objects.update_or_create(
            solicitud=solicitud_model,
            nombre=doc.nombre,
            version=doc.version,
            defaults={
                'estado': doc.estado,
                'motivo_rechazo': doc.motivo_rechazo,
                'fecha_revision': doc.fecha_revision
            }
        )
    
    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudVisa]:
        """Encuentra una solicitud por su ID/código."""
        try:
            model = SolicitudModel.objects.prefetch_related('documentos').get(
                codigo=solicitud_id
            )
            return self._to_entity(model)
        except SolicitudModel.DoesNotExist:
            return None
    
    def find_by_migrante(self, migrante_id: str) -> List[SolicitudVisa]:
        """Encuentra todas las solicitudes de un migrante."""
        models = SolicitudModel.objects.filter(
            migrante__id=migrante_id
        ).prefetch_related('documentos').order_by('-created_at')
        
        return [self._to_entity(m) for m in models]
    
    def find_all(self) -> List[SolicitudVisa]:
        """Retorna todas las solicitudes."""
        models = SolicitudModel.objects.prefetch_related(
            'documentos'
        ).order_by('-created_at')
        
        return [self._to_entity(m) for m in models]
    
    def find_by_estado(self, estado: str) -> List[SolicitudVisa]:
        """Encuentra solicitudes por estado."""
        models = SolicitudModel.objects.filter(
            estado=estado
        ).prefetch_related('documentos').order_by('-created_at')
        
        return [self._to_entity(m) for m in models]
    
    def delete(self, solicitud_id: str) -> bool:
        """Elimina una solicitud (soft delete)."""
        try:
            model = SolicitudModel.objects.get(codigo=solicitud_id)
            model.soft_delete()
            return True
        except SolicitudModel.DoesNotExist:
            return False
    
    def count(self) -> int:
        """Cuenta el total de solicitudes activas."""
        return SolicitudModel.objects.filter(is_deleted=False).count()
    
    def _to_entity(self, model: SolicitudModel) -> SolicitudVisa:
        """Convierte un modelo Django a entidad de dominio."""
        documentos = [
            Documento(
                nombre=doc.nombre,
                estado=doc.estado,
                archivo_path=doc.archivo.path if doc.archivo else None,
                version=doc.version,
                motivo_rechazo=doc.motivo_rechazo,
                fecha_carga=doc.created_at,
                fecha_revision=doc.fecha_revision
            )
            for doc in model.documentos.all()
        ]
        
        return SolicitudVisa(
            id_solicitud=model.codigo,
            id_migrante=str(model.migrante_id),
            tipo_visa=TipoVisa(model.tipo_visa),
            embajada=TipoEmbajada(model.embajada_nombre) if model.embajada_nombre else None,
            estado=model.estado,
            estado_envio=model.estado_envio,
            documentos=documentos,
            fecha_creacion=model.created_at,
            fecha_actualizacion=model.updated_at,
            notas=model.notas
        )


class DjangoDocumentoRepository(IDocumentoRepository):
    """Implementación del repositorio de documentos con Django ORM."""
    
    def save(self, documento: Documento, solicitud_id: str) -> Documento:
        """Guarda o actualiza un documento."""
        solicitud = SolicitudModel.objects.get(codigo=solicitud_id)
        
        model, created = DocumentoModel.objects.update_or_create(
            solicitud=solicitud,
            nombre=documento.nombre,
            version=documento.version,
            defaults={
                'estado': documento.estado,
                'motivo_rechazo': documento.motivo_rechazo,
                'fecha_revision': documento.fecha_revision
            }
        )
        
        return documento
    
    def find_by_id(self, documento_id: str) -> Optional[Documento]:
        """Encuentra un documento por su ID."""
        try:
            model = DocumentoModel.objects.get(id=documento_id)
            return self._to_entity(model)
        except DocumentoModel.DoesNotExist:
            return None
    
    def find_by_solicitud(self, solicitud_id: str) -> List[Documento]:
        """Encuentra todos los documentos de una solicitud."""
        models = DocumentoModel.objects.filter(
            solicitud__codigo=solicitud_id
        ).order_by('nombre', '-version')
        
        return [self._to_entity(m) for m in models]
    
    def find_by_estado(self, estado: str) -> List[Documento]:
        """Encuentra documentos por estado."""
        models = DocumentoModel.objects.filter(estado=estado)
        return [self._to_entity(m) for m in models]
    
    def delete(self, documento_id: str) -> bool:
        """Elimina un documento."""
        try:
            DocumentoModel.objects.filter(id=documento_id).delete()
            return True
        except:
            return False
    
    def _to_entity(self, model: DocumentoModel) -> Documento:
        """Convierte un modelo Django a entidad de dominio."""
        return Documento(
            nombre=model.nombre,
            estado=model.estado,
            archivo_path=model.archivo.path if model.archivo else None,
            version=model.version,
            motivo_rechazo=model.motivo_rechazo,
            fecha_carga=model.created_at,
            fecha_revision=model.fecha_revision
        )


class DjangoMigranteRepository(IMigranteRepository):
    """Implementación del repositorio de migrantes con Django ORM."""
    
    def save(self, migrante: Migrante) -> Migrante:
        """Guarda o actualiza un migrante."""
        model, created = UsuarioModel.objects.update_or_create(
            id=int(migrante.id) if migrante.id.isdigit() else None,
            defaults={
                'nombre': migrante.nombres,
                'apellido': migrante.apellidos,
                'rol': 'cliente'
            }
        )
        
        migrante.id = str(model.id)
        return migrante
    
    def find_by_id(self, migrante_id: str) -> Optional[Migrante]:
        """Encuentra un migrante por su ID."""
        try:
            model = UsuarioModel.objects.get(id=migrante_id)
            return self._to_entity(model)
        except UsuarioModel.DoesNotExist:
            return None
    
    def find_by_email(self, email: str) -> Optional[Migrante]:
        """Encuentra un migrante por su email."""
        # El modelo actual no tiene email, retornamos None
        return None
    
    def find_all(self) -> List[Migrante]:
        """Retorna todos los migrantes."""
        models = UsuarioModel.objects.filter(rol='cliente')
        return [self._to_entity(m) for m in models]
    
    def delete(self, migrante_id: str) -> bool:
        """Elimina un migrante."""
        try:
            UsuarioModel.objects.filter(id=migrante_id).delete()
            return True
        except:
            return False
    
    def count(self) -> int:
        """Cuenta el total de migrantes."""
        return UsuarioModel.objects.filter(rol='cliente').count()
    
    def _to_entity(self, model: UsuarioModel) -> Migrante:
        """Convierte un modelo Django a entidad de dominio."""
        return Migrante(
            id=str(model.id),
            email=f"{model.nombre}.{model.apellido}@ejemplo.com",
            nombres=model.nombre,
            apellidos=model.apellido,
            fecha_registro=model.created_at
        )


class DjangoChecklistRepository(IChecklistRepository):
    """Implementación del repositorio de checklists con Django ORM."""
    
    def find_by_tipo_visa(self, tipo_visa: str) -> Optional[List[str]]:
        """Encuentra el checklist de documentos por tipo de visa."""
        try:
            model = ChecklistDocumentosModel.objects.get(
                tipo_visa=tipo_visa,
                activo=True
            )
            return model.documentos_obligatorios
        except ChecklistDocumentosModel.DoesNotExist:
            return None
    
    def save(self, tipo_visa: str, documentos: List[str]) -> None:
        """Guarda un checklist de documentos."""
        ChecklistDocumentosModel.objects.update_or_create(
            tipo_visa=tipo_visa,
            defaults={
                'documentos_obligatorios': documentos,
                'activo': True
            }
        )


class DjangoEventoRepository:
    """Repositorio para eventos de solicitud."""
    
    @staticmethod
    def registrar_evento(
        solicitud_id: str,
        tipo: str,
        descripcion: str,
        usuario_id: str = None,
        datos_adicionales: dict = None
    ):
        """Registra un evento en el timeline de la solicitud."""
        solicitud = SolicitudModel.objects.get(codigo=solicitud_id)
        
        usuario = None
        if usuario_id:
            try:
                usuario = UsuarioModel.objects.get(id=usuario_id)
            except UsuarioModel.DoesNotExist:
                pass
        
        EventoSolicitudModel.objects.create(
            solicitud=solicitud,
            tipo=tipo,
            descripcion=descripcion,
            usuario_responsable=usuario,
            datos_adicionales=datos_adicionales or {}
        )
    
    @staticmethod
    def obtener_timeline(solicitud_id: str) -> List[dict]:
        """Obtiene el timeline de eventos de una solicitud."""
        eventos = EventoSolicitudModel.objects.filter(
            solicitud__codigo=solicitud_id
        ).order_by('-created_at')
        
        return [
            {
                'tipo': e.tipo,
                'descripcion': e.descripcion,
                'fecha': e.created_at,
                'usuario': e.usuario_responsable.nombre if e.usuario_responsable else None,
                'datos': e.datos_adicionales
            }
            for e in eventos
        ]
