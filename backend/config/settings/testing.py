"""
Configuración para el entorno de testing (pruebas con Behave y pytest).
"""
from .base import *

DEBUG = True

# Base de datos en memoria para tests rápidos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
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
