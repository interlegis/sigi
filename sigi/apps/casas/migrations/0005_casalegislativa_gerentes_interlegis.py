from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servidores', '0001_initial'),
        ('casas', '0004_auto_20201015_0810'),
    ]

    operations = [
        migrations.AddField(
            model_name='casalegislativa',
            name='gerentes_interlegis',
            field=models.ManyToManyField(related_name='casas_que_gerencia', verbose_name=b'Gerentes Interlegis', to='servidores.Servidor'),
            preserve_default=True,
        ),
    ]
