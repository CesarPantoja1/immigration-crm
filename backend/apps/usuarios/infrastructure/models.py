"""
Modelo de Usuario personalizado para autenticación.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from apps.core.models import TimeStampedModel


class UsuarioManager(BaseUserManager):
    """Manager personalizado para Usuario."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crea y guarda un usuario con email y password."""
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crea y guarda un superusuario."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado.
    Usa email como identificador único en lugar de username.
    """
    
    ROLES = [
        ('admin', 'Administrador'),
        ('asesor', 'Asesor'),
        ('cliente', 'Cliente'),
    ]
    
    # Removemos username y usamos email
    username = None
    email = models.EmailField('Correo electrónico', unique=True)
    
    # Campos adicionales
    rol = models.CharField(
        'Rol',
        max_length=20,
        choices=ROLES,
        default='cliente'
    )
    telefono = models.CharField(
        'Teléfono',
        max_length=20,
        blank=True
    )
    foto_perfil = models.ImageField(
        'Foto de perfil',
        upload_to='usuarios/fotos/',
        null=True,
        blank=True
    )
    
    # Para asesores: límite diario de solicitudes
    limite_solicitudes_diarias = models.PositiveIntegerField(
        'Límite de solicitudes diarias',
        default=10
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario."""
        return f"{self.first_name} {self.last_name}"
    
    def es_admin(self) -> bool:
        """Verifica si el usuario es administrador."""
        return self.rol == 'admin'
    
    def es_asesor(self) -> bool:
        """Verifica si el usuario es asesor."""
        return self.rol == 'asesor'
    
    def es_cliente(self) -> bool:
        """Verifica si el usuario es cliente."""
        return self.rol == 'cliente'
