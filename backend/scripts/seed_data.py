"""
Script para poblar la base de datos con datos de prueba.
Ejecutar con: python manage.py shell < scripts/seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from datetime import datetime, timedelta
from apps.preparacion.simulacion.infrastructure.models import CuestionarioPractica, PreguntaPractica

# Crear cuestionarios de práctica
cuestionarios = [
    {
        'tipo_visado': 'Estudiante',
        'titulo': 'Cuestionario para Visa de Estudiante',
        'descripcion': 'Preguntas frecuentes en entrevistas de visa de estudiante'
    },
    {
        'tipo_visado': 'Turismo',
        'titulo': 'Cuestionario para Visa de Turismo',
        'descripcion': 'Preguntas frecuentes en entrevistas de visa de turismo'
    },
    {
        'tipo_visado': 'Trabajo',
        'titulo': 'Cuestionario para Visa de Trabajo',
        'descripcion': 'Preguntas frecuentes en entrevistas de visa de trabajo'
    }
]

for cuest_data in cuestionarios:
    cuestionario, created = CuestionarioPractica.objects.get_or_create(
        tipo_visado=cuest_data['tipo_visado'],
        titulo=cuest_data['titulo'],
        defaults={'descripcion': cuest_data['descripcion']}
    )

    if created:
        print(f"Creado cuestionario: {cuestionario.titulo}")

# Crear preguntas de ejemplo para Estudiante
cuest_estudiante = CuestionarioPractica.objects.get(tipo_visado='Estudiante')

preguntas_estudiante = [
    {
        'texto_pregunta': '¿Cómo financiarás tus estudios en el extranjero?',
        'opcion_a': 'Con ahorros personales y apoyo familiar',
        'opcion_b': 'Con un préstamo estudiantil',
        'opcion_c': 'Con una beca completa',
        'opcion_d': 'Trabajando durante mis estudios',
        'respuesta_correcta': 'A',
        'explicacion': 'La opción A es la más completa y realista, mostrando recursos claros.'
    },
    {
        'texto_pregunta': '¿Por qué elegiste esta universidad en particular?',
        'opcion_a': 'Porque es la más barata',
        'opcion_b': 'Por su excelente reputación en mi campo de estudio y sus programas de investigación',
        'opcion_c': 'Porque mis amigos estudian ahí',
        'opcion_d': 'Es la única que me aceptó',
        'respuesta_correcta': 'B',
        'explicacion': 'Muestra investigación previa y motivación genuina por la institución.'
    }
]

for pregunta_data in preguntas_estudiante:
    PreguntaPractica.objects.get_or_create(
        cuestionario=cuest_estudiante,
        texto_pregunta=pregunta_data['texto_pregunta'],
        defaults=pregunta_data
    )

print("Datos de prueba cargados correctamente!")
