"""
Configuración para el entorno de desarrollo.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres.lhbezpqwcolfccrwhfkl'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'da!@zBS.U.8cbDb'),
        'HOST': os.environ.get('DB_HOST', 'aws-0-us-west-2.pooler.supabase.com'),
        'PORT': os.environ.get('DB_PORT', '6543'),
    }
}

# CORS para desarrollo (si se usa DRF)
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

# Email backend para desarrollo (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache simple para desarrollo
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
