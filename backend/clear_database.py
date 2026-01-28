#!/usr/bin/env python
"""
Script para limpiar TODOS los datos de la base de datos.
⚠️  ADVERTENCIA: Este script elimina TODOS los datos!

Uso:
    python clear_database.py          # Limpia todo
    python clear_database.py --keep-admin  # Mantiene usuarios admin
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection
from django.apps import apps


def clear_all_data(keep_admin=False):
    """Elimina todos los datos de todas las tablas."""
    
    print("\n" + "="*60)
    print("⚠️  LIMPIEZA DE BASE DE DATOS - MIGRAFÁCIL CRM")
    print("="*60)
    
    if not keep_admin:
        confirm = input("\n¿Estás seguro de que quieres ELIMINAR TODOS los datos? (escribe 'SI' para confirmar): ")
        if confirm != 'SI':
            print("❌ Operación cancelada.")
            return
    
    # Obtener todos los modelos
    all_models = apps.get_models()
    
    # Orden de eliminación (dependencias primero)
    delete_order = [
        # Notificaciones
        'notificaciones.Notificacion',
        'notificaciones.PreferenciaNotificacion',
        'notificaciones.ConfiguracionRecordatorio',
        
        # Preparación
        'preparacion.Practica',
        'preparacion.Recomendacion', 
        'preparacion.Simulacro',
        
        # Solicitudes
        'solicitudes.Entrevista',
        'solicitudes.Documento',
        'solicitudes.Solicitud',
        
        # Usuarios (al final si no keep_admin)
        'usuarios.Usuario',
    ]
    
    print("\n🗑️  Eliminando datos...\n")
    
    # Eliminar en orden
    for model_name in delete_order:
        try:
            app_label, model_label = model_name.split('.')
            model = apps.get_model(app_label, model_label)
            
            if keep_admin and model_label == 'Usuario':
                # Mantener admins
                count = model.objects.exclude(rol='admin').count()
                model.objects.exclude(rol='admin').delete()
                print(f"   ✓ {model_name}: {count} registros eliminados (admins conservados)")
            else:
                count = model.objects.count()
                model.objects.all().delete()
                print(f"   ✓ {model_name}: {count} registros eliminados")
                
        except LookupError:
            print(f"   ⚠ {model_name}: modelo no encontrado (saltando)")
        except Exception as e:
            print(f"   ✗ {model_name}: Error - {e}")
    
    # Resetear secuencias SQLite
    if 'sqlite' in connection.vendor:
        print("\n🔄 Reseteando secuencias de ID...")
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence;")
        print("   ✓ Secuencias reseteadas")
    
    print("\n" + "="*60)
    print("✅ BASE DE DATOS LIMPIADA EXITOSAMENTE")
    print("="*60 + "\n")


def show_stats():
    """Muestra estadísticas actuales de la BD."""
    print("\n📊 ESTADÍSTICAS ACTUALES DE LA BD:\n")
    
    models_to_check = [
        ('usuarios', 'Usuario'),
        ('solicitudes', 'Solicitud'),
        ('solicitudes', 'Documento'),
        ('solicitudes', 'Entrevista'),
        ('preparacion', 'Simulacro'),
        ('preparacion', 'Recomendacion'),
        ('preparacion', 'Practica'),
        ('notificaciones', 'Notificacion'),
    ]
    
    for app, model_name in models_to_check:
        try:
            model = apps.get_model(app, model_name)
            count = model.objects.count()
            print(f"   {model_name}: {count} registros")
        except:
            pass
    
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Limpiar base de datos MigraFácil')
    parser.add_argument('--keep-admin', action='store_true', 
                        help='Mantener usuarios administradores')
    parser.add_argument('--stats', action='store_true',
                        help='Solo mostrar estadísticas sin eliminar')
    
    args = parser.parse_args()
    
    if args.stats:
        show_stats()
    else:
        clear_all_data(keep_admin=args.keep_admin)
