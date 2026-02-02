# Generated migration for adding propuesto_por field to Simulacro

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preparacion', '0005_add_configuracion_ia'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulacro',
            name='propuesto_por',
            field=models.CharField(
                choices=[('cliente', 'Cliente'), ('asesor', 'Asesor')],
                default='asesor',
                help_text='Indica quien inicio la propuesta del simulacro',
                max_length=20,
                verbose_name='Propuesto Por'
            ),
        ),
    ]
