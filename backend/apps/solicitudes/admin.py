"""
Admin para la app Solicitudes.
"""
from django.contrib import admin
from .models import Solicitud, Documento, Entrevista


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'cliente', 'tipo_visa', 'embajada', 'estado',
        'asesor', 'created_at'
    ]
    list_filter = ['estado', 'tipo_visa', 'embajada', 'created_at']
    search_fields = ['cliente__email', 'cliente__first_name', 'cliente__last_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['cliente', 'asesor']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información General', {
            'fields': ('cliente', 'tipo_visa', 'embajada', 'estado')
        }),
        ('Asignación', {
            'fields': ('asesor', 'fecha_asignacion')
        }),
        ('Datos', {
            'fields': ('datos_personales', 'documentos', 'observaciones', 'notas_asesor')
        }),
        ('Fechas', {
            'fields': ('fecha_revision', 'fecha_envio_embajada', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'solicitud', 'estado', 'created_at']
    list_filter = ['estado', 'created_at']
    search_fields = ['nombre', 'solicitud__id']
    raw_id_fields = ['solicitud', 'revisado_por']


@admin.register(Entrevista)
class EntrevistaAdmin(admin.ModelAdmin):
    list_display = ['id', 'solicitud', 'fecha', 'hora', 'estado', 'veces_reprogramada']
    list_filter = ['estado', 'fecha']
    search_fields = ['solicitud__id']
    raw_id_fields = ['solicitud']
    date_hierarchy = 'fecha'
