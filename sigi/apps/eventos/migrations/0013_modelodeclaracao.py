# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ("eventos", "0012_auto_20211117_0657"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModeloDeclaracao",
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
                    "nome",
                    models.CharField(
                        max_length=100, verbose_name="Nome do modelo"
                    ),
                ),
                (
                    "formato",
                    models.CharField(
                        default="A4 portrait",
                        max_length=30,
                        verbose_name="Formato da p\xe1gina",
                        choices=[
                            ("A4 portrait", "A4 retrato"),
                            ("A4 landscape", "A4 paisagem"),
                            ("letter portrait", "Carta retrato"),
                            ("letter landscape", "Carta paisagem"),
                        ],
                    ),
                ),
                (
                    "margem",
                    models.PositiveIntegerField(
                        default=4,
                        help_text="Margem da p\xe1gina em cent\xedmetros",
                        verbose_name="Margem",
                    ),
                ),
                (
                    "texto",
                    tinymce.models.HTMLField(
                        help_text="Use as seguintes marca\xe7\xf5es:<ul><li>{{ casa }} para o nome da Casa Legislativa / \xf3rg\xe3o</li><li>{{ nome }} para o nome do visitante</li><li>{{ data }} para a data de emiss\xe3o da declara\xe7\xe3o</li><li>{{ evento.data_inicio }} para a data/hora do in\xedcio da visita</li><li>{{ evento.data_termino }} para a data/hora do t\xe9rmino da visita</li><li>{{ evento.nome }} para o nome do evento</li><li>{{ evento.descricao }} para a descri\xe7\xe3o do evento</li></ul>",
                        verbose_name="Texto da declara\xe7\xe3o",
                    ),
                ),
            ],
            options={
                "verbose_name": "modelo de declara\xe7\xe3o",
                "verbose_name_plural": "modelos de declara\xe7\xe3o",
            },
            bases=(models.Model,),
        ),
    ]
