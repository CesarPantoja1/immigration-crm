"""
Views para la API de Usuarios y Autenticación.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate

from .serializers import (
    UsuarioSerializer,
    RegistroSerializer,
    LoginSerializer,
    CambiarPasswordSerializer,
    PerfilSerializer,
)

Usuario = get_user_model()


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

        # Generar tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'mensaje': 'Usuario registrado exitosamente',
            'usuario': UsuarioSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
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

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'error': 'Usuario inactivo'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Generar tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'mensaje': 'Login exitoso',
            'usuario': UsuarioSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Invalida el refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({'mensaje': 'Logout exitoso'})
        except Exception:
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

        user = request.user
        if not user.check_password(serializer.validated_data['password_actual']):
            return Response({
                'error': 'Contraseña actual incorrecta'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['password_nuevo'])
        user.save()

        return Response({'mensaje': 'Contraseña actualizada exitosamente'})


# =====================================================
# GESTIÓN DE USUARIOS (Admin)
# =====================================================

class UsuarioListView(generics.ListAPIView):
    """
    GET /api/usuarios/
    Lista todos los usuarios.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Usuario.objects.all()

        # Filtros opcionales
        rol = self.request.query_params.get('rol')
        if rol:
            queryset = queryset.filter(rol=rol)

        activo = self.request.query_params.get('activo')
        if activo is not None:
            queryset = queryset.filter(is_active=activo.lower() == 'true')

        return queryset


class AsesoresListView(generics.ListAPIView):
    """
    GET /api/usuarios/asesores/
    Lista todos los asesores activos.
    """
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Usuario.objects.filter(rol='asesor', is_active=True)


class UsuarioDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/usuarios/<id>/
    PATCH /api/usuarios/<id>/
    Detalle y actualización de usuario.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
