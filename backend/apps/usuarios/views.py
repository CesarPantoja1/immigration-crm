"""
Views para la API de Usuarios y Autenticación.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import (
    UsuarioSerializer,
    RegistroSerializer,
    LoginSerializer,
    CambiarPasswordSerializer,
    PerfilSerializer,
    CrearAsesorSerializer,
)
from .services import AuthService, UsuarioService, AdminService

Usuario = get_user_model()


# =====================================================
# PERMISOS PERSONALIZADOS
# =====================================================

class EsAdmin(permissions.BasePermission):
    """Permiso que verifica si el usuario es administrador."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'


class EsAsesorOAdmin(permissions.BasePermission):
    """Permiso que verifica si es asesor o admin."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['asesor', 'admin']


# =====================================================
# AUTENTICACIÓN
# =====================================================

class RegistroView(generics.CreateAPIView):
    """
    POST /api/auth/registro/
    Registra un nuevo usuario (cliente por defecto).
    """
    queryset = Usuario.objects.all()
    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        tokens = AuthService.generar_tokens(user)

        return Response({
            'mensaje': 'Usuario registrado exitosamente',
            'usuario': UsuarioSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Inicia sesión y retorna tokens JWT.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario, tokens, error = AuthService.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            request=request
        )

        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'mensaje': 'Login exitoso',
            'usuario': UsuarioSerializer(usuario).data,
            'tokens': tokens
        })


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Invalida el refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        AuthService.logout(refresh_token)
        return Response({'mensaje': 'Logout exitoso'})


# =====================================================
# PERFIL DE USUARIO
# =====================================================

class PerfilView(APIView):
    """
    GET /api/auth/perfil/ - Obtener perfil del usuario actual
    PATCH /api/auth/perfil/ - Actualizar perfil
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = PerfilSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'mensaje': 'Perfil actualizado',
            'usuario': UsuarioSerializer(request.user).data
        })


class CambiarPasswordView(APIView):
    """
    POST /api/auth/cambiar-password/
    Cambia la contraseña del usuario actual.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CambiarPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success, error = AuthService.cambiar_password(
            usuario=request.user,
            password_actual=serializer.validated_data['password_actual'],
            password_nuevo=serializer.validated_data['password_nuevo']
        )

        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'mensaje': 'Contraseña actualizada exitosamente'})


# =====================================================
# GESTIÓN DE USUARIOS
# =====================================================

class UsuarioListView(generics.ListAPIView):
    """
    GET /api/usuarios/
    Lista todos los usuarios.
    """
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        rol = self.request.query_params.get('rol')
        activo_param = self.request.query_params.get('activo')
        activo = activo_param.lower() == 'true' if activo_param else None
        
        return UsuarioService.listar_usuarios(rol=rol, activo=activo)


class AsesoresListView(generics.ListAPIView):
    """
    GET /api/usuarios/asesores/
    Lista todos los asesores activos.
    """
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UsuarioService.listar_asesores(activo=True)


class UsuarioDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/usuarios/<id>/
    PATCH /api/usuarios/<id>/
    Detalle y actualización de usuario.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]


# =====================================================
# ADMINISTRACIÓN
# =====================================================

class CrearAsesorView(generics.CreateAPIView):
    """
    POST /api/admin/asesores/crear/
    Crea un nuevo asesor (solo admin).
    """
    serializer_class = CrearAsesorSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Asesor creado exitosamente',
            'asesor': UsuarioSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class AdminAsesoresListView(generics.ListAPIView):
    """
    GET /api/admin/asesores/
    Lista todos los asesores - solo admin.
    """
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    
    def get_queryset(self):
        activo_param = self.request.query_params.get('activo')
        activo = activo_param.lower() == 'true' if activo_param else None
        busqueda = self.request.query_params.get('busqueda')
        
        return UsuarioService.listar_asesores(activo=activo, busqueda=busqueda)


class AdminAsesorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/admin/asesores/<id>/
    Detalle, actualización y eliminación de asesor - solo admin.
    """
    queryset = Usuario.objects.filter(rol='asesor')
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    
    def destroy(self, request, *args, **kwargs):
        """Desactivar en lugar de eliminar."""
        instance = self.get_object()
        success, error = UsuarioService.desactivar_usuario(instance.id, rol='asesor')
        
        if not success:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'message': 'Asesor desactivado exitosamente'})


class ToggleAsesorEstadoView(APIView):
    """
    POST /api/admin/asesores/<id>/toggle-estado/
    Activa/desactiva un asesor.
    """
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    
    def post(self, request, pk):
        usuario, error = UsuarioService.toggle_estado_usuario(pk, rol='asesor')
        
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        
        estado = 'activado' if usuario.is_active else 'desactivado'
        return Response({
            'message': f'Asesor {estado} exitosamente',
            'is_active': usuario.is_active
        })


class AdminEstadisticasView(APIView):
    """
    GET /api/admin/estadisticas/
    Estadísticas del sistema para el dashboard admin.
    """
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    
    def get(self, request):
        stats = AdminService.obtener_estadisticas()
        return Response(stats)
