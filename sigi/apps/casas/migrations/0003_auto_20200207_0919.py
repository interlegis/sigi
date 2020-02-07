# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0002_auto_20150710_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='casalegislativa',
            name='horario_funcionamento',
            field=models.CharField(max_length=100, verbose_name='Hor\xe1rio de funcionamento da Casa Legislativa', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='funcionario',
            name='data_nascimento',
            field=models.DateField(null=True, verbose_name='Data de nascimento', blank=True),
            preserve_default=True,
        ),
    ]
