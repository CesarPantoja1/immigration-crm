"""
Configuración de settings según el entorno.
Importa automáticamente el settings correspondiente según DJANGO_SETTINGS_MODULE.
"""
import os

# Por defecto, usa development
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
elif env == 'testing':
    from .testing import *
else:
    from .development import *
