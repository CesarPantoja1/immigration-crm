# Generated migration for embassy decision fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudes', '0002_alter_solicitud_tipo_visa'),
    ]

    operations = [
        # Actualizar choices de estado para incluir nuevos estados de embajada
        migrations.AlterField(
            model_name='solicitud',
            name='estado',
            field=models.CharField(
                choices=[
                    ('borrador', 'Borrador'),
                    ('pendiente', 'Pendiente de Revision'),
                    ('en_revision', 'En Revision'),
                    ('aprobada', 'Aprobada'),
                    ('rechazada', 'Rechazada'),
                    ('enviada_embajada', 'Enviada a Embajada'),
                    ('esperando_decision_embajada', 'Esperando Decision de Embajada'),
                    ('aprobada_embajada', 'Aprobada por Embajada'),
                    ('rechazada_embajada', 'Rechazada por Embajada'),
                    ('entrevista_agendada', 'Entrevista Agendada'),
                    ('completada', 'Completada'),
                ],
                db_index=True,
                default='borrador',
                max_length=30,
                verbose_name='Estado'
            ),
        ),
        # Agregar campo fecha_decision_embajada
        migrations.AddField(
            model_name='solicitud',
            name='fecha_decision_embajada',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Fecha Decision Embajada'
            ),
        ),
        # Agregar campo motivo_rechazo_embajada
        migrations.AddField(
            model_name='solicitud',
            name='motivo_rechazo_embajada',
            field=models.TextField(
                blank=True,
                help_text='Motivo del rechazo si la embajada rechaza la solicitud',
                verbose_name='Motivo Rechazo Embajada'
            ),
        ),
    ]
