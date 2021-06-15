# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0006_auto_20210416_0841'),
    ]

    operations = [
        migrations.AddField(
            model_name='convite',
            name='nomes_participantes',
            field=models.TextField(help_text='Favor colocar um participante por linha', verbose_name='nome dos participantes', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='convite',
            name='qtde_participantes',
            field=models.PositiveIntegerField(default=0, verbose_name='n\xfamero de participantes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evento',
            name='carga_horaria',
            field=models.PositiveIntegerField(default=0, verbose_name='carga hor\xe1ria'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evento',
            name='virtual',
            field=models.BooleanField(default=False, verbose_name='Virtual'),
            preserve_default=True,
        ),
    ]
