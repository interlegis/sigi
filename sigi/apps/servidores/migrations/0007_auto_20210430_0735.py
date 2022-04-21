# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("servidores", "0006_auto_20210429_0822"),
    ]

    operations = [
        migrations.AddField(
            model_name="servidor",
            name="externo",
            field=models.BooleanField(
                default=False, verbose_name="colaborador externo"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="servidor",
            name="orgao_origem",
            field=models.CharField(
                max_length=100,
                verbose_name="\xf3rg\xe3o de origem, ",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="servidor",
            name="qualificacoes",
            field=models.TextField(
                verbose_name="qualifica\xe7\xf5es", blank=True
            ),
            preserve_default=True,
        ),
    ]
