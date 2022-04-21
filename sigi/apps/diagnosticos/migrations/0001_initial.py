# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import datetime
import sigi.apps.utils


class Migration(migrations.Migration):

    dependencies = [
        ("servidores", "0001_initial"),
        ("contenttypes", "0001_initial"),
        ("casas", "0001_initial"),
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
                        max_length=500,
                        upload_to=b"apps/diagnostico/anexo/arquivo",
                    ),
                ),
                (
                    "descricao",
                    models.CharField(
                        max_length=b"70", verbose_name="descri\xe7\xe3o"
                    ),
                ),
                (
                    "data_pub",
                    models.DateTimeField(
                        default=datetime.datetime.now,
                        verbose_name="data da publica\xe7\xe3o do anexo",
                    ),
                ),
            ],
            options={
                "ordering": ("-data_pub",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Categoria",
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
                ("nome", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ("nome",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Diagnostico",
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
                    "search_text",
                    sigi.apps.utils.SearchField(
                        field_names=[b"casa_legislativa"], editable=False
                    ),
                ),
                (
                    "data_visita_inicio",
                    models.DateField(
                        null=True,
                        verbose_name="data inicial da visita",
                        blank=True,
                    ),
                ),
                (
                    "data_visita_fim",
                    models.DateField(
                        null=True,
                        verbose_name="data final da visita",
                        blank=True,
                    ),
                ),
                ("publicado", models.BooleanField(default=False)),
                (
                    "data_publicacao",
                    models.DateField(
                        null=True,
                        verbose_name="data de publica\xe7\xe3o do diagn\xf3stico",
                        blank=True,
                    ),
                ),
                (
                    "casa_legislativa",
                    models.ForeignKey(
                        verbose_name="Casa Legislativa",
                        to="casas.CasaLegislativa",
                    ),
                ),
                (
                    "responsavel",
                    models.ForeignKey(
                        verbose_name="respons\xe1vel", to="servidores.Servidor"
                    ),
                ),
            ],
            options={
                "verbose_name": "diagn\xf3stico",
                "verbose_name_plural": "diagn\xf3sticos",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Equipe",
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
                    "diagnostico",
                    models.ForeignKey(to="diagnosticos.Diagnostico"),
                ),
                ("membro", models.ForeignKey(to="servidores.Servidor")),
            ],
            options={
                "verbose_name": "equipe",
                "verbose_name_plural": "equipe",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Escolha",
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
                ("title", models.CharField(max_length=100)),
                ("ordem", models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                "ordering": ("schema", "ordem"),
                "verbose_name": "escolha",
                "verbose_name_plural": "escolhas",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Pergunta",
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
                    "title",
                    models.CharField(
                        help_text="user-friendly attribute name",
                        max_length=250,
                        verbose_name="title",
                    ),
                ),
                (
                    "name",
                    autoslug.fields.AutoSlugField(
                        max_length=250, verbose_name="name", blank=True
                    ),
                ),
                (
                    "help_text",
                    models.CharField(
                        help_text="short description for administrator",
                        max_length=250,
                        verbose_name="help text",
                        blank=True,
                    ),
                ),
                (
                    "datatype",
                    models.CharField(
                        max_length=5,
                        verbose_name="data type",
                        choices=[
                            (b"text", "text"),
                            (b"float", "number"),
                            (b"date", "date"),
                            (b"bool", "boolean"),
                            (b"one", "choice"),
                            (b"many", "multiple choices"),
                            (b"range", "numeric range"),
                        ],
                    ),
                ),
                (
                    "required",
                    models.BooleanField(default=False, verbose_name="required"),
                ),
                (
                    "searched",
                    models.BooleanField(
                        default=False, verbose_name="include in search"
                    ),
                ),
                (
                    "filtered",
                    models.BooleanField(
                        default=False, verbose_name="include in filters"
                    ),
                ),
                (
                    "sortable",
                    models.BooleanField(
                        default=False, verbose_name="allow sorting"
                    ),
                ),
                (
                    "categoria",
                    models.ForeignKey(
                        related_name=b"perguntas", to="diagnosticos.Categoria"
                    ),
                ),
            ],
            options={
                "ordering": ("title",),
                "verbose_name": "pergunta",
                "verbose_name_plural": "perguntas",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Resposta",
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
                ("entity_id", models.IntegerField()),
                ("value_text", models.TextField(null=True, blank=True)),
                ("value_float", models.FloatField(null=True, blank=True)),
                ("value_date", models.DateField(null=True, blank=True)),
                ("value_bool", models.NullBooleanField()),
                ("value_range_min", models.FloatField(null=True, blank=True)),
                ("value_range_max", models.FloatField(null=True, blank=True)),
                (
                    "choice",
                    models.ForeignKey(
                        verbose_name="escolha",
                        blank=True,
                        to="diagnosticos.Escolha",
                        null=True,
                    ),
                ),
                (
                    "entity_type",
                    models.ForeignKey(to="contenttypes.ContentType"),
                ),
                (
                    "schema",
                    models.ForeignKey(
                        related_name=b"attrs",
                        verbose_name="pergunta",
                        to="diagnosticos.Pergunta",
                    ),
                ),
            ],
            options={
                "verbose_name": "resposta",
                "verbose_name_plural": "respostas",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="escolha",
            name="schema",
            field=models.ForeignKey(
                related_name=b"choices",
                verbose_name="pergunta",
                to="diagnosticos.Pergunta",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="escolha",
            name="schema_to_open",
            field=models.ForeignKey(
                related_name=b"",
                verbose_name="pergunta para abrir",
                blank=True,
                to="diagnosticos.Pergunta",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="anexo",
            name="diagnostico",
            field=models.ForeignKey(
                verbose_name="diagn\xf3stico", to="diagnosticos.Diagnostico"
            ),
            preserve_default=True,
        ),
    ]
