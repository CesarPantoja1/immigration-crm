"""
Application Services / Use Cases (DDD)
Orquesta las operaciones del dominio
"""
from ..domain.entities import Usuario
from ..domain.repositories import IUsuarioRepository


class CrearUsuarioUseCase:
    """Caso de uso: Crear usuario"""
    
    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository
    
    def execute(self, nombre: str, apellido: str, rol: str) -> Usuario:
        """Ejecuta la creación de un usuario"""
        usuario = Usuario(
            id=None,
            nombre=nombre,
            apellido=apellido,
            rol=rol
        )
        return self.repository.save(usuario)


class ObtenerUsuarioUseCase:
    """Caso de uso: Obtener usuario por ID"""
    
    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository
    
    def execute(self, id: int) -> Usuario:
        """Ejecuta la obtención de un usuario"""
        usuario = self.repository.find_by_id(id)
        if not usuario:
            raise ValueError(f"Usuario con ID {id} no encontrado")
        return usuario


class ListarUsuariosUseCase:
    """Caso de uso: Listar todos los usuarios"""
    
    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository
    
    def execute(self):
        """Ejecuta el listado de usuarios"""
        return self.repository.find_all()
