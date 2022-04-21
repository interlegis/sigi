# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Ferias",
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
                    "inicio_ferias",
                    models.DateField(verbose_name="in\xedcio das f\xe9rias"),
                ),
                (
                    "fim_ferias",
                    models.DateField(verbose_name="fim das f\xe9rias"),
                ),
                (
                    "obs",
                    models.TextField(
                        null=True, verbose_name="observa\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "verbose_name": "f\xe9rias",
                "verbose_name_plural": "f\xe9rias",
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
                ("funcao", models.CharField(max_length=250, null=True)),
                ("cargo", models.CharField(max_length=250, null=True)),
                (
                    "inicio_funcao",
                    models.DateField(
                        null=True, verbose_name="in\xedcio da fun\xe7\xe3o"
                    ),
                ),
                (
                    "fim_funcao",
                    models.DateField(
                        null=True,
                        verbose_name="fim da fun\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="descri\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "bap_entrada",
                    models.CharField(
                        max_length=50,
                        null=True,
                        verbose_name="BAP de entrada",
                        blank=True,
                    ),
                ),
                (
                    "data_bap_entrada",
                    models.DateField(
                        null=True,
                        verbose_name="data BAP de entrada",
                        blank=True,
                    ),
                ),
                (
                    "bap_saida",
                    models.CharField(
                        max_length=50,
                        null=True,
                        verbose_name="BAP de sa\xedda",
                        blank=True,
                    ),
                ),
                (
                    "data_bap_saida",
                    models.DateField(
                        null=True,
                        verbose_name="data BAP de sa\xedda",
                        blank=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "fun\xe7\xe3o",
                "verbose_name_plural": "fun\xe7\xf5es",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Licenca",
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
                    "inicio_licenca",
                    models.DateField(verbose_name="in\xedcio da licen\xe7a"),
                ),
                (
                    "fim_licenca",
                    models.DateField(verbose_name="fim da licen\xe7a"),
                ),
                (
                    "obs",
                    models.TextField(
                        null=True, verbose_name="observa\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "verbose_name": "licen\xe7a",
                "verbose_name_plural": "licen\xe7as",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Servico",
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
                        max_length=250, null=True, verbose_name="Setor"
                    ),
                ),
                ("sigla", models.CharField(max_length=10, null=True)),
            ],
            options={
                "ordering": ("nome",),
                "verbose_name": "servi\xe7o",
                "verbose_name_plural": "servi\xe7os",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Servidor",
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
                ("nome_completo", models.CharField(max_length=128)),
                ("apelido", models.CharField(max_length=50, blank=True)),
                (
                    "foto",
                    models.ImageField(
                        height_field="foto_altura",
                        width_field="foto_largura",
                        upload_to="fotos/servidores",
                        blank=True,
                    ),
                ),
                (
                    "foto_largura",
                    models.SmallIntegerField(null=True, editable=False),
                ),
                (
                    "foto_altura",
                    models.SmallIntegerField(null=True, editable=False),
                ),
                (
                    "sexo",
                    models.CharField(
                        blank=True,
                        max_length=1,
                        null=True,
                        choices=[("M", "Masculino"), ("F", "Feminino")],
                    ),
                ),
                (
                    "data_nascimento",
                    models.DateField(
                        null=True, verbose_name="data de nascimento", blank=True
                    ),
                ),
                (
                    "matricula",
                    models.CharField(
                        max_length=25,
                        null=True,
                        verbose_name="matr\xedcula",
                        blank=True,
                    ),
                ),
                (
                    "turno",
                    models.CharField(
                        blank=True,
                        max_length=1,
                        null=True,
                        choices=[
                            ("M", "Manh\xe3"),
                            ("T", "Tarde"),
                            ("N", "Noite"),
                        ],
                    ),
                ),
                ("de_fora", models.BooleanField(default=False)),
                (
                    "data_nomeacao",
                    models.DateField(
                        null=True,
                        verbose_name="data de nomea\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "ato_exoneracao",
                    models.CharField(
                        max_length=150,
                        null=True,
                        verbose_name="ato de exonera\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "ato_numero",
                    models.CharField(
                        max_length=150,
                        null=True,
                        verbose_name="ato de exonera\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "cpf",
                    models.CharField(
                        max_length=11, null=True, verbose_name="CPF", blank=True
                    ),
                ),
                (
                    "rg",
                    models.CharField(
                        max_length=25, null=True, verbose_name="RG", blank=True
                    ),
                ),
                (
                    "obs",
                    models.TextField(
                        null=True, verbose_name="observa\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "apontamentos",
                    models.TextField(
                        null=True, verbose_name="apontamentos", blank=True
                    ),
                ),
                (
                    "email_pessoal",
                    models.EmailField(
                        max_length=75,
                        null=True,
                        verbose_name="email pessoal",
                        blank=True,
                    ),
                ),
                (
                    "ramal",
                    models.CharField(max_length=25, null=True, blank=True),
                ),
                (
                    "servico",
                    models.ForeignKey(
                        blank=True,
                        to="servidores.Servico",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        unique=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("nome_completo",),
                "verbose_name_plural": "servidores",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Subsecretaria",
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
                ("nome", models.CharField(max_length=250, null=True)),
                ("sigla", models.CharField(max_length=10, null=True)),
                (
                    "responsavel",
                    models.ForeignKey(
                        related_name="diretor",
                        to="servidores.Servidor",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("nome",),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="servico",
            name="responsavel",
            field=models.ForeignKey(
                related_name="chefe",
                to="servidores.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="servico",
            name="subsecretaria",
            field=models.ForeignKey(
                to="servidores.Subsecretaria",
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="licenca",
            name="servidor",
            field=models.ForeignKey(
                to="servidores.Servidor", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="funcao",
            name="servidor",
            field=models.ForeignKey(
                to="servidores.Servidor", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="ferias",
            name="servidor",
            field=models.ForeignKey(
                to="servidores.Servidor", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
