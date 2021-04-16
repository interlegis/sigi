# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parlamentares', '0002_auto_20210406_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mandato',
            name='cargo',
            field=models.ForeignKey(to='parlamentares.Cargo', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='membromesadiretora',
            name='cargo',
            field=models.ForeignKey(to='parlamentares.Cargo', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sessaolegislativa',
            name='mesa_diretora',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Mesa Diretora', to='parlamentares.MesaDiretora'),
            preserve_default=True,
        ),
    ]
