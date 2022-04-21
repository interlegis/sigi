# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ("eventos", "0014_auto_20211124_0736"),
    ]

    operations = [
        migrations.CreateModel(
            name="Anexo",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "arquivo",
                    models.FileField(
                        max_length=500, upload_to="apps/eventos/anexo/arquivo"
                    ),
                ),
                (
                    "descricao",
                    models.CharField(
                        max_length="70", verbose_name="descri\xe7\xe3o"
                    ),
                ),
                (
                    "data_pub",
                    models.DateTimeField(
                        default=datetime.datetime.now,
                        verbose_name="data da publica\xe7\xe3o do anexo",
                    ),
                ),
                (
                    "evento",
                    models.ForeignKey(
                        verbose_name="evento",
                        to="eventos.Evento",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("-data_pub",),
            },
            bases=(models.Model,),
        ),
    ]
