from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.solicitudes.models import Solicitud, Documento
from apps.preparacion.simulacion.models import Simulacro
from apps.solicitudes.agendamiento.models import Entrevista
from apps.notificaciones.coordinacion.models import NotificacionCoordinacion

User = get_user_model()


class Command(BaseCommand):
    help = 'Limpia todos los datos de la base de datos excepto el usuario admin permanente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-admin',
            action='store_true',
            default=True,
            help='Mantener el usuario admin (por defecto: True)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando limpieza de base de datos...'))

        # Eliminar notificaciones
        try:
            count = NotificacionCoordinacion.objects.all().delete()[0]
            self.stdout.write(f'  - Eliminadas {count} notificaciones')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  - Error eliminando notificaciones: {e}'))

        # Eliminar simulacros
        try:
            count = Simulacro.objects.all().delete()[0]
            self.stdout.write(f'  - Eliminados {count} simulacros')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  - Error eliminando simulacros: {e}'))

        # Eliminar entrevistas
        try:
            count = Entrevista.objects.all().delete()[0]
            self.stdout.write(f'  - Eliminadas {count} entrevistas')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  - Error eliminando entrevistas: {e}'))

        # Eliminar documentos
        try:
            count = Documento.objects.all().delete()[0]
            self.stdout.write(f'  - Eliminados {count} documentos')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  - Error eliminando documentos: {e}'))

        # Eliminar solicitudes
        try:
            count = Solicitud.objects.all().delete()[0]
            self.stdout.write(f'  - Eliminadas {count} solicitudes')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  - Error eliminando solicitudes: {e}'))

        # Eliminar usuarios excepto admin
        try:
            users_to_delete = User.objects.exclude(email='admin@gmail.com')
            count = users_to_delete.delete()[0]
            self.stdout.write(f'  - Eliminados {count} usuarios (excepto admin)')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  - Error eliminando usuarios: {e}'))

        # Crear o verificar admin permanente
        admin_email = 'admin@gmail.com'
        admin_password = 'admin123'
        
        admin, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        
        if created:
            admin.set_password(admin_password)
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'  - Creado usuario admin: {admin_email}'))
        else:
            # Asegurar que tiene la configuración correcta
            admin.is_staff = True
            admin.is_superuser = True
            admin.is_active = True
            admin.rol = 'admin'
            admin.set_password(admin_password)
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'  - Usuario admin verificado: {admin_email}'))

        self.stdout.write(self.style.SUCCESS('\n¡Base de datos limpiada exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'\nCredenciales Admin:'))
        self.stdout.write(f'  Email: {admin_email}')
        self.stdout.write(f'  Password: {admin_password}')
