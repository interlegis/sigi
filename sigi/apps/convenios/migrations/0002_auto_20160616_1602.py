# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('convenios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anexo',
            name='descricao',
            field=models.CharField(max_length=70, verbose_name='descri\xe7\xe3o'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tramitacao',
            name='observacao',
            field=models.CharField(max_length=512, null=True, verbose_name='observa\xe7\xe3o', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unidadeadministrativa',
            name='nome',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unidadeadministrativa',
            name='sigla',
            field=models.CharField(max_length=10),
            preserve_default=True,
        ),
    ]
