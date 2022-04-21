# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sigi.apps.utils


class Migration(migrations.Migration):

    dependencies = [
        ("contatos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Mesorregiao",
            fields=[
                (
                    "codigo_ibge",
                    models.PositiveIntegerField(
                        help_text="C\xf3digo da mesorregi\xe3o segundo o IBGE",
                        unique=True,
                        serialize=False,
                        verbose_name="C\xf3digo IBGE",
                        primary_key=True,
                    ),
                ),
                (
                    "nome",
                    models.CharField(
                        max_length=100, verbose_name="Nome mesorregi\xe3o"
                    ),
                ),
                (
                    "search_text",
                    sigi.apps.utils.SearchField(
                        field_names=["nome"], editable=False
                    ),
                ),
                (
                    "uf",
                    models.ForeignKey(
                        verbose_name="UF",
                        to="contatos.UnidadeFederativa",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("uf", "nome"),
                "verbose_name": "Mesorregi\xe3o",
                "verbose_name_plural": "Mesorregi\xf5es",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Microrregiao",
            fields=[
                (
                    "codigo_ibge",
                    models.PositiveIntegerField(
                        help_text="C\xf3digo da microrregi\xe3o segundo o IBGE",
                        unique=True,
                        serialize=False,
                        verbose_name="C\xf3digo IBGE",
                        primary_key=True,
                    ),
                ),
                (
                    "nome",
                    models.CharField(
                        max_length=100, verbose_name="Nome microrregi\xe3o"
                    ),
                ),
                (
                    "search_text",
                    sigi.apps.utils.SearchField(
                        field_names=["nome"], editable=False
                    ),
                ),
                (
                    "mesorregiao",
                    models.ForeignKey(
                        to="contatos.Mesorregiao", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": ("mesorregiao", "nome"),
                "verbose_name": "Microrregi\xe3o",
                "verbose_name_plural": "Microrregi\xf5es",
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name="municipio",
            name="codigo_mesorregiao",
        ),
        migrations.RemoveField(
            model_name="municipio",
            name="codigo_microrregiao",
        ),
        migrations.AddField(
            model_name="municipio",
            name="microrregiao",
            field=models.ForeignKey(
                verbose_name="Microrregi\xe3o",
                blank=True,
                to="contatos.Microrregiao",
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
