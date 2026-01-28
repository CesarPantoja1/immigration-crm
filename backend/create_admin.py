#!/usr/bin/env python
"""
Script para crear el usuario administrador por defecto.

Credenciales por defecto:
    Email: admin@migrafacil.com
    Password: admin123

Uso:
    python create_admin.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.usuarios.models import Usuario


def create_default_admin():
    """Crea el usuario administrador por defecto."""
    
    print("\n" + "="*60)
    print("🔐 CREAR ADMINISTRADOR POR DEFECTO - MIGRAFÁCIL CRM")
    print("="*60)
    
    # Credenciales por defecto
    ADMIN_EMAIL = 'admin@migrafacil.com'
    ADMIN_PASSWORD = 'admin123'
    ADMIN_FIRST_NAME = 'Admin'
    ADMIN_LAST_NAME = 'MigraFácil'
    
    # Verificar si ya existe
    if Usuario.objects.filter(email=ADMIN_EMAIL).exists():
        print(f"\n⚠️  El usuario {ADMIN_EMAIL} ya existe.")
        
        update = input("¿Deseas resetear la contraseña? (s/n): ")
        if update.lower() == 's':
            admin = Usuario.objects.get(email=ADMIN_EMAIL)
            admin.set_password(ADMIN_PASSWORD)
            admin.save()
            print("✅ Contraseña reseteada exitosamente.")
        else:
            print("❌ Operación cancelada.")
        return
    
    # Crear administrador
    admin = Usuario.objects.create_superuser(
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        first_name=ADMIN_FIRST_NAME,
        last_name=ADMIN_LAST_NAME,
        rol='admin'
    )
    
    print("\n✅ ADMINISTRADOR CREADO EXITOSAMENTE")
    print("\n" + "-"*40)
    print("📧 Email:    " + ADMIN_EMAIL)
    print("🔑 Password: " + ADMIN_PASSWORD)
    print("👤 Nombre:   " + f"{ADMIN_FIRST_NAME} {ADMIN_LAST_NAME}")
    print("🎭 Rol:      admin")
    print("-"*40)
    print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login!")
    print("="*60 + "\n")


def create_test_advisor():
    """Crea un asesor de prueba."""
    
    ADVISOR_EMAIL = 'asesor@migrafacil.com'
    ADVISOR_PASSWORD = 'asesor123'
    
    if Usuario.objects.filter(email=ADVISOR_EMAIL).exists():
        print(f"⚠️  El asesor {ADVISOR_EMAIL} ya existe.")
        return
    
    asesor = Usuario.objects.create_user(
        email=ADVISOR_EMAIL,
        password=ADVISOR_PASSWORD,
        first_name='Asesor',
        last_name='Demo',
        rol='asesor',
        is_staff=True  # Para acceso al admin
    )
    
    print(f"✅ Asesor creado: {ADVISOR_EMAIL} / {ADVISOR_PASSWORD}")


def create_test_client():
    """Crea un cliente de prueba."""
    
    CLIENT_EMAIL = 'cliente@migrafacil.com'
    CLIENT_PASSWORD = 'cliente123'
    
    if Usuario.objects.filter(email=CLIENT_EMAIL).exists():
        print(f"⚠️  El cliente {CLIENT_EMAIL} ya existe.")
        return
    
    cliente = Usuario.objects.create_user(
        email=CLIENT_EMAIL,
        password=CLIENT_PASSWORD,
        first_name='Cliente',
        last_name='Demo',
        rol='cliente'
    )
    
    print(f"✅ Cliente creado: {CLIENT_EMAIL} / {CLIENT_PASSWORD}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Crear usuarios por defecto MigraFácil')
    parser.add_argument('--all', action='store_true',
                        help='Crear admin, asesor y cliente de prueba')
    parser.add_argument('--advisor', action='store_true',
                        help='También crear asesor de prueba')
    parser.add_argument('--client', action='store_true',
                        help='También crear cliente de prueba')
    
    args = parser.parse_args()
    
    create_default_admin()
    
    if args.all or args.advisor:
        create_test_advisor()
    
    if args.all or args.client:
        create_test_client()
    
    print("\n📋 USUARIOS EN EL SISTEMA:")
    for user in Usuario.objects.all():
        print(f"   • {user.email} ({user.rol})")
    print()
