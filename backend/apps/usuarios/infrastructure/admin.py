"""
Admin para la app Usuarios.
Panel de administración para gestionar usuarios, asesores y clientes.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin personalizado para el modelo Usuario."""
    
    list_display = ['email', 'nombre_completo', 'rol_badge', 'telefono', 'is_active', 'created_at']
    list_filter = ['rol', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'telefono']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    list_per_page = 25
    
    fieldsets = (
        ('Credenciales', {'fields': ('email', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'telefono', 'foto_perfil')
        }),
        ('Rol y Permisos', {
            'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Configuración Asesor', {
            'fields': ('limite_solicitudes_diarias',),
            'classes': ('collapse',),
            'description': 'Solo aplica para usuarios con rol de asesor'
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Credenciales', {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'telefono'),
        }),
        ('Rol', {
            'classes': ('wide',),
            'fields': ('rol', 'is_active', 'is_staff'),
        }),
    )
    
    def nombre_completo(self, obj):
        """Muestra el nombre completo."""
        return f"{obj.first_name} {obj.last_name}"
    nombre_completo.short_description = 'Nombre'
    nombre_completo.admin_order_field = 'first_name'
    
    def rol_badge(self, obj):
        """Muestra el rol con un badge de color."""
        colors = {
            'admin': '#dc2626',    # Rojo
            'asesor': '#2563eb',   # Azul
            'cliente': '#16a34a',  # Verde
        }
        color = colors.get(obj.rol, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_rol_display()
        )
    rol_badge.short_description = 'Rol'
    rol_badge.admin_order_field = 'rol'
    
    # Acciones personalizadas
    actions = ['make_asesor', 'make_cliente', 'activate_users', 'deactivate_users']
    
    @admin.action(description='Convertir seleccionados en Asesor')
    def make_asesor(self, request, queryset):
        updated = queryset.update(rol='asesor', is_staff=True)
        self.message_user(request, f'{updated} usuario(s) convertidos a asesor.')
    
    @admin.action(description='Convertir seleccionados en Cliente')
    def make_cliente(self, request, queryset):
        updated = queryset.update(rol='cliente', is_staff=False)
        self.message_user(request, f'{updated} usuario(s) convertidos a cliente.')
    
    @admin.action(description='Activar usuarios seleccionados')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} usuario(s) activados.')
    
    @admin.action(description='Desactivar usuarios seleccionados')
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} usuario(s) desactivados.')
    
    def save_model(self, request, obj, form, change):
        """Al guardar, asegurar que asesores tengan is_staff=True."""
        if obj.rol == 'asesor':
            obj.is_staff = True
        elif obj.rol == 'admin':
            obj.is_staff = True
            obj.is_superuser = True
        super().save_model(request, obj, form, change)


# Personalizar título del admin
admin.site.site_header = '🌎 MigraFácil CRM - Administración'
admin.site.site_title = 'MigraFácil Admin'
admin.site.index_title = 'Panel de Control'
