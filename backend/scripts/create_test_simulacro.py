"""
Script para crear un simulacro de prueba para probar Jitsi Meet.
Ejecutar: python manage.py shell < scripts/create_test_simulacro.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.usuarios.models import Usuario
from apps.solicitudes.models import Solicitud
from apps.preparacion.models import Simulacro

def create_test_simulacro():
    """Crea un simulacro de prueba en estado confirmado."""
    
    # Obtener cliente y asesor
    try:
        cliente = Usuario.objects.filter(rol='cliente').first()
        asesor = Usuario.objects.filter(rol='asesor').first()
        
        if not cliente:
            print("❌ No hay clientes registrados. Ejecuta primero el script de usuarios.")
            return
        
        if not asesor:
            print("❌ No hay asesores registrados. Ejecuta primero el script de usuarios.")
            return
        
        # Obtener o crear una solicitud
        solicitud = Solicitud.objects.filter(cliente=cliente).first()
        if not solicitud:
            solicitud = Solicitud.objects.create(
                cliente=cliente,
                tipo_visa='turismo',
                pais_destino='Estados Unidos',
                estado='en_proceso'
            )
            print(f"✅ Solicitud creada: #{solicitud.id}")
        
        # Crear simulacro para hoy/ahora (para poder probarlo de inmediato)
        ahora = timezone.now()
        fecha_hoy = ahora.date()
        hora_actual = ahora.time()
        
        # Verificar si ya existe un simulacro activo
        simulacro_existente = Simulacro.objects.filter(
            cliente=cliente,
            estado__in=['confirmado', 'en_sala_espera', 'en_progreso']
        ).first()
        
        if simulacro_existente:
            print(f"ℹ️  Ya existe un simulacro activo: #{simulacro_existente.id} (estado: {simulacro_existente.estado})")
            print(f"   URL Cliente: http://localhost:5173/simulacros/{simulacro_existente.id}/room")
            print(f"   URL Asesor: http://localhost:5173/asesor/simulacros/{simulacro_existente.id}/room")
            return simulacro_existente
        
        simulacro = Simulacro.objects.create(
            cliente=cliente,
            asesor=asesor,
            solicitud=solicitud,
            fecha=fecha_hoy,
            hora=hora_actual,
            fecha_propuesta=fecha_hoy,
            hora_propuesta=hora_actual.strftime('%H:%M'),
            modalidad='virtual',
            estado='confirmado',
            tipo_entrevista='inicial'
        )
        
        print(f"✅ Simulacro creado exitosamente!")
        print(f"   ID: #{simulacro.id}")
        print(f"   Cliente: {cliente.email}")
        print(f"   Asesor: {asesor.email}")
        print(f"   Estado: {simulacro.estado}")
        print(f"   Fecha: {fecha_hoy}")
        print(f"   Hora: {hora_actual.strftime('%H:%M')}")
        print()
        print("🎥 URLs para probar Jitsi Meet:")
        print(f"   Cliente: http://localhost:5173/simulacros/{simulacro.id}/room")
        print(f"   Asesor:  http://localhost:5173/asesor/simulacros/{simulacro.id}/room")
        print()
        print("💡 Instrucciones:")
        print("   1. Abre dos ventanas/pestañas del navegador")
        print("   2. En una, logéate como cliente e ingresa a la URL del cliente")
        print("   3. En otra, logéate como asesor e ingresa a la URL del asesor")
        print("   4. Desde el panel del asesor, haz clic en 'Iniciar Sesión'")
        print("   5. Ambos se conectarán a la misma sala de Jitsi Meet")
        
        return simulacro
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    create_test_simulacro()
