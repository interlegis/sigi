# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosticos', '0002_auto_20170407_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='escolha',
            name='schema_to_open',
            field=models.ForeignKey(related_name='abre_por', verbose_name='pergunta para abrir', blank=True, to='diagnosticos.Pergunta', null=True),
            preserve_default=True,
        ),
    ]
