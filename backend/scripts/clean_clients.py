"""
Script para limpiar datos de clientes.
Borra todos los usuarios clientes y sus datos asociados.
Mantiene los asesores, admins y superusers.

Ejecutar: python manage.py shell < scripts/clean_clients.py
"""
from django.contrib.auth import get_user_model
from apps.solicitudes.models import Solicitud
from apps.preparacion.models import Simulacro, Recomendacion, Practica
from apps.notificaciones.models import Notificacion, HistorialNotificaciones, PreferenciasNotificaciones

Usuario = get_user_model()

def clean_client_data():
    """Elimina todos los datos de clientes, manteniendo asesores y admins."""
    
    # Obtener los usuarios clientes
    clientes = Usuario.objects.filter(rol='cliente', is_deleted=False)
    
    if not clientes.exists():
        print("✓ No hay clientes para eliminar.")
        return
    
    print(f"Se van a eliminar {clientes.count()} cliente(s) y sus datos asociados...\n")
    
    for cliente in clientes:
        print(f"Limpiando datos de: {cliente.nombre_completo()} ({cliente.email})")
        
        # 1. Eliminar notificaciones del cliente
        notificaciones = Notificacion.objects.filter(usuario=cliente)
        notif_count = notificaciones.count()
        if notif_count > 0:
            notificaciones.delete()
            print(f"  ✓ Eliminadas {notif_count} notificacion(es)")
        
        # 2. Eliminar historial de notificaciones
        historial = HistorialNotificaciones.objects.filter(usuario=cliente)
        hist_count = historial.count()
        if hist_count > 0:
            historial.delete()
            print(f"  ✓ Eliminados {hist_count} historial(es) de notificaciones")
        
        # 3. Eliminar preferencias de notificaciones
        prefs = PreferenciasNotificaciones.objects.filter(usuario=cliente)
        if prefs.exists():
            prefs.delete()
            print(f"  ✓ Eliminadas preferencias de notificaciones")
        
        # 4. Eliminar recomendaciones del cliente
        recomendaciones = Recomendacion.objects.filter(cliente=cliente)
        rec_count = recomendaciones.count()
        if rec_count > 0:
            recomendaciones.delete()
            print(f"  ✓ Eliminadas {rec_count} recomendacion(es)")
        
        # 5. Eliminar práctica del cliente
        practica = Practica.objects.filter(cliente=cliente)
        prac_count = practica.count()
        if prac_count > 0:
            practica.delete()
            print(f"  ✓ Eliminadas {prac_count} práctica(s)")
        
        # 6. Eliminar simulacros del cliente
        simulacros = Simulacro.objects.filter(cliente=cliente)
        sim_count = simulacros.count()
        if sim_count > 0:
            simulacros.delete()
            print(f"  ✓ Eliminados {sim_count} simulacro(s)")
        
        # 7. Eliminar solicitudes del cliente (cascada eliminará documentos, entrevisas, etc.)
        solicitudes = Solicitud.objects.filter(cliente=cliente, is_deleted=False)
        sol_count = solicitudes.count()
        if sol_count > 0:
            solicitudes.delete()
            print(f"  ✓ Eliminadas {sol_count} solicitud(es) y sus documentos/entrevisas")
        
        # 8. Finalmente, eliminar el usuario cliente
        nombre = cliente.nombre_completo()
        email = cliente.email
        cliente.delete()
        print(f"  ✓ Usuario eliminado: {nombre} ({email})\n")
    
    print(f"✅ Limpieza completada exitosamente!")
    print(f"\nResumen:")
    print(f"  - Se eliminaron {clientes.count()} usuario(s) cliente(s)")
    print(f"  - Se mantuvieron todos los asesores, admins y superusers")
    print(f"  - Todos los datos asociados fueron eliminados en cascada")

if __name__ == '__main__':
    try:
        clean_client_data()
    except Exception as e:
        print(f"❌ Error durante la limpieza: {str(e)}")
        import traceback
        traceback.print_exc()
