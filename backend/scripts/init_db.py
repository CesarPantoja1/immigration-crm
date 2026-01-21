"""
Script para inicializar la base de datos con datos básicos.
Ejecutar con: python manage.py shell < scripts/init_db.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.solicitudes.agendamiento.infrastructure.models import ReglaEmbajada

# Crear reglas por defecto para embajadas
embajadas = [
    {'embajada': 'USA', 'max_reprogramaciones': 2, 'horas_minimas_cancelacion': 24},
    {'embajada': 'España', 'max_reprogramaciones': 2, 'horas_minimas_cancelacion': 48},
    {'embajada': 'Canadá', 'max_reprogramaciones': 2, 'horas_minimas_cancelacion': 72},
    {'embajada': 'Reino Unido', 'max_reprogramaciones': 1, 'horas_minimas_cancelacion': 48},
    {'embajada': 'Alemania', 'max_reprogramaciones': 2, 'horas_minimas_cancelacion': 72},
]

for embajada_data in embajadas:
    ReglaEmbajada.objects.get_or_create(
        embajada=embajada_data['embajada'],
        defaults={
            'max_reprogramaciones': embajada_data['max_reprogramaciones'],
            'horas_minimas_cancelacion': embajada_data['horas_minimas_cancelacion']
        }
    )

print("Base de datos inicializada correctamente!")
