# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0007_auto_20210417_0744"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evento",
            name="data_inicio",
            field=models.DateTimeField(
                null=True, verbose_name="Data/hora do In\xedcio", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="evento",
            name="data_termino",
            field=models.DateTimeField(
                null=True, verbose_name="Data/hora do Termino", blank=True
            ),
            preserve_default=True,
        ),
    ]
