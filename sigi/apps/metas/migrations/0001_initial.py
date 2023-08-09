# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("casas", "0001_initial"),
        ("convenios", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Meta",
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
                    "titulo",
                    models.CharField(
                        help_text="T\xedtulo da meta que aparecer\xe1 no dashboard",
                        max_length=40,
                        verbose_name="T\xedtulo",
                    ),
                ),
                (
                    "descricao",
                    models.TextField(verbose_name="Descri\xe7\xe3o"),
                ),
                (
                    "data_inicio",
                    models.DateField(
                        help_text="In\xedcio do per\xedodo de c\xf4mputo da meta",
                        verbose_name="Data inicial",
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(
                        help_text="Prazo final para cumprimento da meta",
                        verbose_name="Data final",
                    ),
                ),
                (
                    "algoritmo",
                    models.CharField(
                        max_length=10,
                        verbose_name="Algoritmo de c\xe1lculo",
                        choices=[
                            (b"SUM_GASTOS", "Soma dos desembolsos"),
                            (b"COUNT_EQUI", "Quantidade de casas equipadas"),
                            (b"COUNT_ADER", "Quantidade de casas aderidas"),
                            (
                                b"COUNT_DIAG",
                                "Quantidade de casas diagnosticadas",
                            ),
                            (b"COUNT_PDIR", "Quantidade de planos diretores"),
                            (b"COUNT_CONV", "Quantidade de casas conveniadas"),
                        ],
                    ),
                ),
                (
                    "valor_meta",
                    models.FloatField(
                        help_text="Valor que deve ser atingido at\xe9 o prazo final da meta",
                        verbose_name="Valor da meta",
                    ),
                ),
                (
                    "projeto",
                    models.ForeignKey(
                        verbose_name="Projeto",
                        to="convenios.Projeto",
                        help_text="Projeto ao qual a meta se refere",
                    ),
                ),
            ],
            options={
                "verbose_name": "Meta BID",
                "verbose_name_plural": "Metas BID",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PlanoDiretor",
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
                    "status",
                    models.CharField(
                        default=b"E",
                        max_length=1,
                        verbose_name="Status",
                        choices=[(b"E", "Entregue"), (b"I", "Implantado")],
                    ),
                ),
                (
                    "data_entrega",
                    models.DateField(
                        null=True, verbose_name="Data de entrega", blank=True
                    ),
                ),
                (
                    "data_implantacao",
                    models.DateField(
                        null=True,
                        verbose_name="Data de implanta\xe7\xe3o",
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
                    "projeto",
                    models.ForeignKey(
                        verbose_name="Projeto", to="convenios.Projeto"
                    ),
                ),
            ],
            options={
                "verbose_name": "Plano Diretor",
                "verbose_name_plural": "Planos Diretores",
            },
            bases=(models.Model,),
        ),
    ]
