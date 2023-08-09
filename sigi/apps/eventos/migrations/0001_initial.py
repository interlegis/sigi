# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("servidores", "0001_initial"),
        ("contatos", "0001_initial"),
        ("casas", "0002_auto_20150710_1247"),
    ]

    operations = [
        migrations.CreateModel(
            name="Convite",
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
                    "data_convite",
                    models.DateField(verbose_name="Data do convite"),
                ),
                (
                    "aceite",
                    models.BooleanField(
                        default=False, verbose_name="Aceitou o convite"
                    ),
                ),
                (
                    "participou",
                    models.BooleanField(
                        default=False, verbose_name="Participou do evento"
                    ),
                ),
                (
                    "casa",
                    models.ForeignKey(
                        verbose_name="Casa convidada",
                        to="casas.CasaLegislativa",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("evento", "casa", "-data_convite"),
                "verbose_name": "Casa convidada",
                "verbose_name_plural": "Casas convidadas",
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
                    "observacoes",
                    models.TextField(
                        verbose_name="Observa\xe7\xf5es", blank=True
                    ),
                ),
            ],
            options={
                "ordering": ("evento", "funcao", "membro"),
                "verbose_name": "Membro da equipe",
                "verbose_name_plural": "Membros da equipe",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Evento",
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
                        max_length=100, verbose_name="Nome do evento"
                    ),
                ),
                (
                    "descricao",
                    models.TextField(verbose_name="Descri\xe7\xe3o do evento"),
                ),
                (
                    "solicitante",
                    models.CharField(
                        max_length=100, verbose_name="Solicitante"
                    ),
                ),
                (
                    "data_inicio",
                    models.DateField(verbose_name="Data de in\xedcio"),
                ),
                (
                    "data_termino",
                    models.DateField(verbose_name="Data de t\xe9rmino"),
                ),
                (
                    "local",
                    models.TextField(
                        verbose_name="Local do evento", blank=True
                    ),
                ),
                (
                    "publico_alvo",
                    models.TextField(
                        verbose_name="P\xfablico alvo", blank=True
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        max_length=1,
                        verbose_name="Status",
                        choices=[
                            ("P", "Previs\xe3o"),
                            ("A", "A confirmar"),
                            ("O", "Confirmado"),
                            ("R", "Realizado"),
                            ("C", "Cancelado"),
                        ],
                    ),
                ),
                (
                    "data_cancelamento",
                    models.DateField(
                        null=True,
                        verbose_name="Data de cancelamento",
                        blank=True,
                    ),
                ),
                (
                    "motivo_cancelamento",
                    models.TextField(
                        verbose_name="Motivo do cancelamento", blank=True
                    ),
                ),
                (
                    "casa_anfitria",
                    models.ForeignKey(
                        verbose_name="Casa anfitri\xe3",
                        blank=True,
                        to="casas.CasaLegislativa",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "municipio",
                    models.ForeignKey(
                        to="contatos.Municipio", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": ("-data_inicio",),
                "verbose_name": "Evento",
                "verbose_name_plural": "Eventos",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Funcao",
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
                        max_length=100,
                        verbose_name="Fun\xe7\xe3o na equipe de evento",
                    ),
                ),
                (
                    "descricao",
                    models.TextField(
                        verbose_name="Descri\xe7\xe3o da fun\xe7\xe3o"
                    ),
                ),
            ],
            options={
                "ordering": ("nome",),
                "verbose_name": "Fun\xe7\xe3o",
                "verbose_name_plural": "Fun\xe7\xf5es",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TipoEvento",
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
                    models.CharField(max_length=100, verbose_name="Nome"),
                ),
            ],
            options={
                "ordering": ("nome",),
                "verbose_name": "Tipo de evento",
                "verbose_name_plural": "Tipos de evento",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="evento",
            name="tipo_evento",
            field=models.ForeignKey(
                to="eventos.TipoEvento", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="equipe",
            name="evento",
            field=models.ForeignKey(
                to="eventos.Evento", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="equipe",
            name="funcao",
            field=models.ForeignKey(
                verbose_name="Fun\xe7\xe3o na equipe",
                to="eventos.Funcao",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="equipe",
            name="membro",
            field=models.ForeignKey(
                related_name="equipe_evento",
                to="servidores.Servidor",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="convite",
            name="evento",
            field=models.ForeignKey(
                to="eventos.Evento", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="convite",
            name="servidor",
            field=models.ForeignKey(
                verbose_name="Servidor que convido",
                to="servidores.Servidor",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="convite",
            unique_together=set([("evento", "casa")]),
        ),
    ]
