"""
Views para la API de Usuarios y Autenticación.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.db import models

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


# =====================================================
# VISTAS DE ADMINISTRACIÓN
# =====================================================

class EsAdmin(permissions.BasePermission):
    """Permiso que verifica si el usuario es administrador."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'


class CrearAsesorView(generics.CreateAPIView):
    """
    POST /api/admin/asesores/crear/
    Crea un nuevo asesor (solo admin).
    """
    serializer_class = RegistroSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context
    
    def create(self, request, *args, **kwargs):
        # Forzar rol asesor
        data = request.data.copy()
        data['rol'] = 'asesor'
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Asesor creado exitosamente',
            'asesor': {
                'id': user.id,
                'email': user.email,
                'nombre': user.nombre_completo(),
                'telefono': user.telefono
            }
        }, status=status.HTTP_201_CREATED)


class AdminAsesoresListView(generics.ListAPIView):
    """
    GET /api/admin/asesores/
    Lista todos los asesores (activos e inactivos) - solo admin.
    """
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    
    def get_queryset(self):
        queryset = Usuario.objects.filter(rol='asesor')
        
        # Filtro por estado activo
        activo = self.request.query_params.get('activo')
        if activo is not None:
            queryset = queryset.filter(is_active=activo.lower() == 'true')
        
        # Búsqueda por nombre o email
        busqueda = self.request.query_params.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                models.Q(first_name__icontains=busqueda) |
                models.Q(last_name__icontains=busqueda) |
                models.Q(email__icontains=busqueda)
            )
        
        return queryset.order_by('-created_at')


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
        instance.is_active = False
        instance.save()
        return Response({'message': 'Asesor desactivado exitosamente'}, status=status.HTTP_200_OK)


class ToggleAsesorEstadoView(APIView):
    """
    POST /api/admin/asesores/<id>/toggle-estado/
    Activa/desactiva un asesor.
    """
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    
    def post(self, request, pk):
        try:
            asesor = Usuario.objects.get(pk=pk, rol='asesor')
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Asesor no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        asesor.is_active = not asesor.is_active
        asesor.save()
        
        estado = 'activado' if asesor.is_active else 'desactivado'
        return Response({
            'message': f'Asesor {estado} exitosamente',
            'is_active': asesor.is_active
        })


class AdminEstadisticasView(APIView):
    """
    GET /api/admin/estadisticas/
    Estadísticas del sistema para el dashboard admin.
    """
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    
    def get(self, request):
        from apps.solicitudes.models import Solicitud
        from apps.preparacion.models import Simulacro
        from django.utils import timezone
        from datetime import timedelta
        
        hoy = timezone.now().date()
        
        stats = {
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
        
        return Response(stats)