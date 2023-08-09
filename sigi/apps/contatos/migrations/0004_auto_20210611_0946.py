# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("contatos", "0003_auto_20210416_0841"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="microrregiao",
            options={
                "ordering": ("nome",),
                "verbose_name": "Microrregi\xe3o",
                "verbose_name_plural": "Microrregi\xf5es",
            },
        ),
        migrations.AlterField(
            model_name="unidadefederativa",
            name="regiao",
            field=models.CharField(
                max_length=2,
                verbose_name="regi\xe3o",
                choices=[
                    ("CO", "Centro-Oeste"),
                    ("NE", "Nordeste"),
                    ("NO", "Norte"),
                    ("SD", "Sudeste"),
                    ("SL", "Sul"),
                ],
            ),
            preserve_default=True,
        ),
    ]
