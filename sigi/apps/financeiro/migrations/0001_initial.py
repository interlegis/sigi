# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("convenios", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Desembolso",
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
                    "descricao",
                    models.CharField(
                        max_length=100,
                        verbose_name="Descri\xe7\xe3o da despesa",
                    ),
                ),
                ("data", models.DateField(verbose_name="Data do desembolso")),
                (
                    "valor_reais",
                    models.DecimalField(
                        verbose_name="Valor em R$",
                        max_digits=18,
                        decimal_places=2,
                    ),
                ),
                (
                    "valor_dolar",
                    models.DecimalField(
                        verbose_name="Valor em US$",
                        max_digits=18,
                        decimal_places=2,
                    ),
                ),
                (
                    "projeto",
                    models.ForeignKey(
                        verbose_name="Projeto", to="convenios.Projeto"
                    ),
                ),
            ],
            options={
                "verbose_name": "Desembolso",
                "verbose_name_plural": "Desembolsos",
            },
            bases=(models.Model,),
        ),
    ]
