"""
Serializers para la API de Usuarios.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

Usuario = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para ver/listar usuarios."""
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'first_name', 'last_name', 'nombre_completo',
            'rol', 'telefono', 'foto_perfil', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_nombre_completo(self, obj):
        return obj.nombre_completo()


class RegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = Usuario
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'telefono', 'rol'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })

        # Solo admin puede crear otros admins/asesores
        request = self.context.get('request')
        rol = attrs.get('rol', 'cliente')

        if rol in ['admin', 'asesor']:
            if not request or not request.user.is_authenticated:
                attrs['rol'] = 'cliente'  # Forzar rol cliente si no está autenticado
            elif not request.user.es_admin():
                attrs['rol'] = 'cliente'

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = Usuario.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class CambiarPasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña."""
    password_actual = serializers.CharField(required=True, write_only=True)
    password_nuevo = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    password_confirmar = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['password_nuevo'] != attrs['password_confirmar']:
            raise serializers.ValidationError({
                'password_confirmar': 'Las contraseñas no coinciden.'
            })
        return attrs


class PerfilSerializer(serializers.ModelSerializer):
    """Serializer para actualizar perfil."""

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'telefono', 'foto_perfil']
