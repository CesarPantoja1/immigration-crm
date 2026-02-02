from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.solicitudes.models import Solicitud
from apps.preparacion.models import Simulacro, Recomendacion, Practica
from apps.notificaciones.models import Notificacion, PreferenciaNotificacion

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Elimina todos los usuarios clientes y sus datos asociados, manteniendo asesores y admins'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmar la eliminación sin pedir confirmación',
        )

    def handle(self, *args, **options):
        # Obtener los usuarios clientes
        clientes = Usuario.objects.filter(rol='cliente')

        if not clientes.exists():
            self.stdout.write(self.style.SUCCESS('✓ No hay clientes para eliminar.'))
            return

        self.stdout.write(f'\nSe van a eliminar {clientes.count()} cliente(s) y sus datos asociados...\n')

        if not options['confirm']:
            confirmacion = input('¿Estás seguro? (escribe "sí" para confirmar): ')
            if confirmacion.lower() != 'sí':
                self.stdout.write(self.style.WARNING('Operación cancelada.'))
                return

        total_solicitudes = 0
        total_notificaciones = 0
        total_simulacros = 0
        total_recomendaciones = 0
        total_practica = 0

        for cliente in clientes:
            self.stdout.write(f'\nLimpiando datos de: {cliente.nombre_completo()} ({cliente.email})')

            # 1. Eliminar notificaciones del cliente
            notificaciones = Notificacion.objects.filter(usuario=cliente)
            notif_count = notificaciones.count()
            if notif_count > 0:
                notificaciones.delete()
                total_notificaciones += notif_count
                self.stdout.write(f'  ✓ Eliminadas {notif_count} notificacion(es)')

            # 2. Eliminar preferencias de notificaciones
            prefs = PreferenciaNotificacion.objects.filter(usuario=cliente)
            if prefs.exists():
                prefs.delete()
                self.stdout.write(f'  ✓ Eliminadas preferencias de notificaciones')

            # 3. Eliminar recomendaciones del cliente
            # Las recomendaciones están asociadas a simulacros
            simulacros_cliente = Simulacro.objects.filter(cliente=cliente)
            recomendaciones = Recomendacion.objects.filter(simulacro__in=simulacros_cliente)
            rec_count = recomendaciones.count()
            if rec_count > 0:
                recomendaciones.delete()
                total_recomendaciones += rec_count
                self.stdout.write(f'  ✓ Eliminadas {rec_count} recomendacion(es)')

            # 4. Eliminar práctica del cliente
            practica = Practica.objects.filter(cliente=cliente)
            prac_count = practica.count()
            if prac_count > 0:
                practica.delete()
                total_practica += prac_count
                self.stdout.write(f'  ✓ Eliminadas {prac_count} práctica(s)')

            # 5. Eliminar simulacros del cliente
            simulacros = Simulacro.objects.filter(cliente=cliente)
            sim_count = simulacros.count()
            if sim_count > 0:
                simulacros.delete()
                total_simulacros += sim_count
                self.stdout.write(f'  ✓ Eliminados {sim_count} simulacro(s)')

            # 6. Eliminar solicitudes del cliente (cascada eliminará documentos, entrevisas, etc.)
            solicitudes = Solicitud.objects.filter(cliente=cliente)
            sol_count = solicitudes.count()
            if sol_count > 0:
                solicitudes.delete()
                total_solicitudes += sol_count
                self.stdout.write(
                    f'  ✓ Eliminadas {sol_count} solicitud(es) y sus documentos/entrevisas'
                )

            # 7. Finalmente, eliminar el usuario cliente
            nombre = cliente.nombre_completo()
            email = cliente.email
            cliente.delete()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Usuario eliminado: {nombre} ({email})'))

        self.stdout.write(self.style.SUCCESS('\n✅ Limpieza completada exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'\nResumen:'))
        self.stdout.write(self.style.SUCCESS(f'  - Se eliminaron {clientes.count()} usuario(s) cliente(s)'))
        self.stdout.write(self.style.SUCCESS(f'  - Se eliminaron {total_solicitudes} solicitud(es)'))
        self.stdout.write(
            self.style.SUCCESS(f'  - Se eliminaron {total_notificaciones} notificacion(es)')
        )
        self.stdout.write(self.style.SUCCESS(f'  - Se eliminaron {total_simulacros} simulacro(s)'))
        self.stdout.write(
            self.style.SUCCESS(f'  - Se eliminaron {total_recomendaciones} recomendacion(es)')
        )
        self.stdout.write(
            self.style.SUCCESS(f'  - Se eliminaron {total_practica} práctica(s) individual(es)')
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'  - Se mantuvieron todos los asesores, admins y superusers'
            )
        )
