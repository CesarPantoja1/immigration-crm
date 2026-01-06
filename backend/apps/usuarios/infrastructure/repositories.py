"""
Repository Implementation (Infrastructure)
Implementación concreta del repositorio usando Django ORM
"""
from typing import List, Optional
from ..domain.entities import Usuario
from ..domain.repositories import IUsuarioRepository
from .models import UsuarioModel


class DjangoUsuarioRepository(IUsuarioRepository):
    """Implementación del repositorio de usuarios con Django ORM"""
    
    def save(self, usuario: Usuario) -> Usuario:
        """Guarda o actualiza un usuario"""
        if usuario.id:
            # Actualizar
            usuario_model = UsuarioModel.objects.get(id=usuario.id)
            usuario_model.nombre = usuario.nombre
            usuario_model.apellido = usuario.apellido
            usuario_model.rol = usuario.rol
            usuario_model.save()
        else:
            # Crear
            usuario_model = UsuarioModel.objects.create(
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                rol=usuario.rol
            )
        
        return self._to_entity(usuario_model)
    
    def find_by_id(self, id: int) -> Optional[Usuario]:
        """Encuentra un usuario por ID"""
        try:
            usuario_model = UsuarioModel.objects.get(id=id)
            return self._to_entity(usuario_model)
        except UsuarioModel.DoesNotExist:
            return None
    
    def find_all(self) -> List[Usuario]:
        """Retorna todos los usuarios"""
        usuarios_model = UsuarioModel.objects.all()
        return [self._to_entity(u) for u in usuarios_model]
    
    def delete(self, id: int) -> None:
        """Elimina un usuario"""
        UsuarioModel.objects.filter(id=id).delete()
    
    @staticmethod
    def _to_entity(model: UsuarioModel) -> Usuario:
        """Convierte un modelo ORM a entidad de dominio"""
        return Usuario(
            id=model.id,
            nombre=model.nombre,
            apellido=model.apellido,
            rol=model.rol
        )
