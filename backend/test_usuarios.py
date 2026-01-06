import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Importar el modelo
from apps.usuarios.infrastructure.models import UsuarioModel

print("✓ Modelo cargado exitosamente")
print(f"✓ Nombre de la tabla: {UsuarioModel._meta.db_table}")
print(f"✓ App label: {UsuarioModel._meta.app_label}")

# Verificar si hay usuarios
count = UsuarioModel.objects.count()
print(f"✓ Total de usuarios en la BD: {count}")

if count > 0:
    usuarios = UsuarioModel.objects.all()[:5]
    print("\nPrimeros usuarios:")
    for u in usuarios:
        print(f"  - {u.nombre} {u.apellido} ({u.rol})")
else:
    print("\n⚠ No hay usuarios en la base de datos")
    print("Puedes crear uno con: python manage.py createsuperuser")

