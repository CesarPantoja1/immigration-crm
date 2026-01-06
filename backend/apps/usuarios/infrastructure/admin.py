"""
Django Admin (Presentation Layer)
"""
from django.contrib import admin
from .models import UsuarioModel


@admin.register(UsuarioModel)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'rol', 'created_at')
    list_filter = ('rol', 'created_at')
    search_fields = ('nombre', 'apellido')
    ordering = ('apellido', 'nombre')
    readonly_fields = ('created_at', 'updated_at')
