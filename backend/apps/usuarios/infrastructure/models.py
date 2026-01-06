"""
ORM Models (Infrastructure Layer)
Modelos de persistencia de Django
"""
from django.db import models


class UsuarioModel(models.Model):
    """Modelo ORM para Usuario"""
    
    ROLES = [
        ('admin', 'Administrador'),
        ('agente', 'Agente'),
        ('cliente', 'Cliente'),
    ]
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
