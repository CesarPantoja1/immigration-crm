"""
Servicios de la app Usuarios.
Contiene toda la lógica de negocio relacionada con usuarios.
"""
from django.contrib.auth import get_user_model, authenticate
from django.db import models
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken

Usuario = get_user_model()


class AuthService:
    """Servicio de autenticación."""
    
    @staticmethod
    def registrar_usuario(email: str, password: str, first_name: str, last_name: str, 
                          telefono: str = '', rol: str = 'cliente') -> tuple[object, dict]:
        """
        Registra un nuevo usuario y genera tokens JWT.
        
        Returns:
            tuple: (usuario, tokens_dict)
        """
        usuario = Usuario.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            telefono=telefono,
            rol=rol
        )
        tokens = AuthService.generar_tokens(usuario)
        return usuario, tokens
    
    @staticmethod
    def login(email: str, password: str, request=None) -> tuple[object | None, dict | None, str | None]:
        """
        Autentica un usuario.
        
        Returns:
            tuple: (usuario, tokens, error_message)
        """
        usuario = authenticate(request=request, email=email, password=password)
        
        if usuario is None:
            return None, None, 'Credenciales inválidas'
        
        if not usuario.is_active:
            return None, None, 'Usuario inactivo'
        
        tokens = AuthService.generar_tokens(usuario)
        return usuario, tokens, None
    
    @staticmethod
    def logout(refresh_token: str) -> bool:
        """Invalida el refresh token."""
        try:
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return True
        except Exception:
            return True  # Consideramos exitoso aunque falle
    
    @staticmethod
    def generar_tokens(usuario) -> dict:
        """Genera tokens JWT para un usuario."""
        refresh = RefreshToken.for_user(usuario)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    
    @staticmethod
    def cambiar_password(usuario, password_actual: str, password_nuevo: str) -> tuple[bool, str | None]:
        """
        Cambia la contraseña de un usuario.
        
        Returns:
            tuple: (success, error_message)
        """
        if not usuario.check_password(password_actual):
            return False, 'Contraseña actual incorrecta'
        
        usuario.set_password(password_nuevo)
        usuario.save()
        return True, None


class UsuarioService:
    """Servicio para gestión de usuarios."""
    
    @staticmethod
    def obtener_usuario(usuario_id: int) -> object | None:
        """Obtiene un usuario por ID."""
        try:
            return Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return None
    
    @staticmethod
    def listar_usuarios(rol: str = None, activo: bool = None) -> models.QuerySet:
        """Lista usuarios con filtros opcionales."""
        queryset = Usuario.objects.all()
        
        if rol:
            queryset = queryset.filter(rol=rol)
        
        if activo is not None:
            queryset = queryset.filter(is_active=activo)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def listar_asesores(activo: bool = True, busqueda: str = None) -> models.QuerySet:
        """Lista asesores con filtros."""
        queryset = Usuario.objects.filter(rol='asesor')
        
        if activo is not None:
            queryset = queryset.filter(is_active=activo)
        
        if busqueda:
            queryset = queryset.filter(
                models.Q(first_name__icontains=busqueda) |
                models.Q(last_name__icontains=busqueda) |
                models.Q(email__icontains=busqueda)
            )
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def actualizar_perfil(usuario, **datos) -> object:
        """Actualiza el perfil de un usuario."""
        campos_permitidos = ['first_name', 'last_name', 'telefono', 'foto_perfil']
        
        for campo, valor in datos.items():
            if campo in campos_permitidos and valor is not None:
                setattr(usuario, campo, valor)
        
        usuario.save()
        return usuario
    
    @staticmethod
    def crear_asesor(email: str, password: str, first_name: str, last_name: str,
                     telefono: str = '', limite_solicitudes: int = 10) -> object:
        """Crea un nuevo asesor."""
        return Usuario.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            telefono=telefono,
            rol='asesor',
            limite_solicitudes_diarias=limite_solicitudes
        )
    
    @staticmethod
    def toggle_estado_usuario(usuario_id: int, rol: str = None) -> tuple[object | None, str | None]:
        """
        Activa/desactiva un usuario.
        
        Returns:
            tuple: (usuario, error_message)
        """
        try:
            filtros = {'pk': usuario_id}
            if rol:
                filtros['rol'] = rol
            
            usuario = Usuario.objects.get(**filtros)
            usuario.is_active = not usuario.is_active
            usuario.save()
            return usuario, None
        except Usuario.DoesNotExist:
            return None, 'Usuario no encontrado'
    
    @staticmethod
    def desactivar_usuario(usuario_id: int, rol: str = None) -> tuple[bool, str | None]:
        """Desactiva un usuario (soft delete)."""
        try:
            filtros = {'pk': usuario_id}
            if rol:
                filtros['rol'] = rol
            
            usuario = Usuario.objects.get(**filtros)
            usuario.is_active = False
            usuario.save()
            return True, None
        except Usuario.DoesNotExist:
            return False, 'Usuario no encontrado'


class AdminService:
    """Servicio para funciones administrativas."""
    
    @staticmethod
    def obtener_estadisticas() -> dict:
        """Obtiene estadísticas del sistema para el dashboard admin."""
        from apps.solicitudes.models import Solicitud
        from apps.preparacion.models import Simulacro
        
        hoy = timezone.now().date()
        
        return {
            'total_usuarios': Usuario.objects.count(),
            'total_asesores': Usuario.objects.filter(rol='asesor').count(),
            'asesores_activos': Usuario.objects.filter(rol='asesor', is_active=True).count(),
            'total_clientes': Usuario.objects.filter(rol='cliente').count(),
            'clientes_activos': Usuario.objects.filter(rol='cliente', is_active=True).count(),
            'solicitudes_totales': Solicitud.objects.count(),
            'solicitudes_pendientes': Solicitud.objects.filter(estado='pendiente').count(),
            'solicitudes_hoy': Solicitud.objects.filter(created_at__date=hoy).count(),
            'simulacros_hoy': Simulacro.objects.filter(fecha=hoy, is_deleted=False).count(),
            'simulacros_semana': Simulacro.objects.filter(
                fecha__gte=hoy - timedelta(days=7),
                is_deleted=False
            ).count(),
        }
