"""
Configuración para el entorno de testing (pruebas con Behave y pytest).

TIPOS DE TESTS:
1. Tests de lógica pura (ej: seguimiento_solicitud.feature)
   - Usan entidades en memoria (business_logic/)
   - NO requieren base de datos
   - Son muy rápidos (~0.04s)

2. Tests de integración (ej: alertas_entrevista.feature)
   - Usan Django ORM y BD real
   - Requieren SQLite con archivo (no :memory:) para persistir migraciones
   - Son más lentos pero validan integración completa
"""
from .base import *
import os

DEBUG = True

# Permitir testserver para Django Test Client
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Base de datos para tests BDD - archivo temporal compartido
# NOTA: Usamos archivo SQLite (no :memory:) porque Behave ejecuta múltiples
# escenarios en el mismo proceso y las migraciones deben persistir.
# Para tests de lógica pura, esta BD no se usa (ver environment.py)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_testing.sqlite3',
        'TEST': {
            'NAME': BASE_DIR / 'db_testing.sqlite3',
        }
    }
}

# CORS permitir todo en testing
CORS_ALLOW_ALL_ORIGINS = True

# Password hashers más rápidos para tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Email backend para testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cache dummy para testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Desactivar migraciones en tests para mayor velocidad
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

# MIGRATION_MODULES = DisableMigrations()
