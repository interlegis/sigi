# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("casas", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bem",
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
                    "num_serie",
                    models.CharField(
                        help_text="N\xfamero fornecido pelo fabricante.",
                        unique=True,
                        max_length=64,
                        verbose_name="n\xfamero de s\xe9rie",
                    ),
                ),
                (
                    "recebido_por",
                    models.CharField(
                        help_text="Nome de quem recebeu o equipamento.",
                        max_length=64,
                        blank=True,
                    ),
                ),
                (
                    "observacoes",
                    models.TextField(
                        verbose_name="observa\xe7\xf5es", blank=True
                    ),
                ),
                (
                    "casa_legislativa",
                    models.ForeignKey(
                        to="casas.CasaLegislativa", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "bens",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Equipamento",
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
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Fabricante",
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
                ("nome", models.CharField(unique=True, max_length=40)),
            ],
            options={
                "ordering": ("nome",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Fornecedor",
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
                ("nome", models.CharField(max_length=40)),
                (
                    "email",
                    models.EmailField(
                        max_length=75, verbose_name="e-mail", blank=True
                    ),
                ),
                (
                    "pagina_web",
                    models.URLField(verbose_name="p\xe1gina web", blank=True),
                ),
            ],
            options={
                "ordering": ("nome",),
                "verbose_name_plural": "fornecedores",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ModeloEquipamento",
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
                ("modelo", models.CharField(max_length=30)),
            ],
            options={
                "ordering": ("modelo",),
                "verbose_name": "modelo de equipamento",
                "verbose_name_plural": "modelos de equipamentos",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TipoEquipamento",
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
                ("tipo", models.CharField(max_length=40)),
            ],
            options={
                "ordering": ("tipo",),
                "verbose_name": "tipo de equipamento",
                "verbose_name_plural": "tipos de equipamentos",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="modeloequipamento",
            name="tipo",
            field=models.ForeignKey(
                verbose_name="tipo de equipamento",
                to="inventario.TipoEquipamento",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="equipamento",
            name="fabricante",
            field=models.ForeignKey(
                to="inventario.Fabricante", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="equipamento",
            name="modelo",
            field=models.ForeignKey(
                to="inventario.ModeloEquipamento", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="equipamento",
            unique_together=set([("fabricante", "modelo")]),
        ),
        migrations.AddField(
            model_name="bem",
            name="equipamento",
            field=models.ForeignKey(
                to="inventario.Equipamento", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="bem",
            name="fornecedor",
            field=models.ForeignKey(
                to="inventario.Fornecedor", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
