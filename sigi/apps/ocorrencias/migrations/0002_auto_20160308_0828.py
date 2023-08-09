# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ocorrencias", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ocorrencia",
            name="ticket",
            field=models.PositiveIntegerField(
                help_text="N\xfamero do ticket no osTicket",
                null=True,
                verbose_name="N\xfamero do ticket",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="comentario",
            name="ocorrencia",
            field=models.ForeignKey(
                related_name="comentarios",
                verbose_name="Ocorr\xeancia",
                to="ocorrencias.Ocorrencia",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
