# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("casas", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cargo",
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
                        max_length=30, verbose_name="descri\xe7\xe3o"
                    ),
                ),
            ],
            options={
                "ordering": ("descricao",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Coligacao",
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
                ("nome", models.CharField(max_length=50)),
                (
                    "numero_votos",
                    models.PositiveIntegerField(
                        null=True, verbose_name="n\xfamero de votos", blank=True
                    ),
                ),
            ],
            options={
                "ordering": ("legislatura", "nome"),
                "verbose_name": "coliga\xe7\xe3o",
                "verbose_name_plural": "coliga\xe7\xf5es",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ComposicaoColigacao",
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
                    "coligacao",
                    models.ForeignKey(
                        verbose_name="coliga\xe7\xe3o",
                        to="parlamentares.Coligacao",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "composi\xe7\xe3o da coliga\xe7\xe3o",
                "verbose_name_plural": "composi\xe7\xf5es das coliga\xe7\xf5es",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Legislatura",
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
                    "numero",
                    models.PositiveSmallIntegerField(
                        verbose_name="n\xfamero legislatura"
                    ),
                ),
                ("data_inicio", models.DateField(verbose_name="in\xedcio")),
                ("data_fim", models.DateField(verbose_name="fim")),
                (
                    "data_eleicao",
                    models.DateField(verbose_name="data da elei\xe7\xe3o"),
                ),
                (
                    "total_parlamentares",
                    models.PositiveIntegerField(
                        verbose_name="Total de parlamentares"
                    ),
                ),
                (
                    "casa_legislativa",
                    models.ForeignKey(
                        to="casas.Orgao", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": [
                    "casa_legislativa__municipio__uf__sigla",
                    "-data_inicio",
                ],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Mandato",
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
                    "inicio_mandato",
                    models.DateField(verbose_name="in\xedcio de mandato"),
                ),
                (
                    "fim_mandato",
                    models.DateField(verbose_name="fim de mandato"),
                ),
                (
                    "is_afastado",
                    models.BooleanField(
                        default=False,
                        help_text="Marque caso parlamentar n\xe3o esteja ativo.",
                        verbose_name="afastado",
                    ),
                ),
                (
                    "cargo",
                    models.ForeignKey(
                        to="parlamentares.Cargo", on_delete=models.CASCADE
                    ),
                ),
                (
                    "legislatura",
                    models.ForeignKey(
                        to="parlamentares.Legislatura", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MembroMesaDiretora",
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
                    "cargo",
                    models.ForeignKey(
                        to="parlamentares.Cargo", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": ("parlamentar",),
                "verbose_name": "membro de Mesa Diretora",
                "verbose_name_plural": "membros de Mesa Diretora",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MesaDiretora",
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
                    "casa_legislativa",
                    models.ForeignKey(
                        verbose_name="Casa Legislativa",
                        to="casas.Orgao",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "Mesa Diretora",
                "verbose_name_plural": "Mesas Diretoras",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Parlamentar",
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
                (
                    "nome_parlamentar",
                    models.CharField(max_length=35, blank=True),
                ),
                (
                    "foto",
                    models.ImageField(
                        height_field=b"foto_altura",
                        width_field=b"foto_largura",
                        upload_to=b"fotos/parlamentares",
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
                        max_length=1,
                        choices=[(b"M", "Masculino"), (b"F", "Feminino")],
                    ),
                ),
                (
                    "data_nascimento",
                    models.DateField(
                        null=True, verbose_name="data de nascimento", blank=True
                    ),
                ),
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
                "ordering": ("nome_completo",),
                "verbose_name_plural": "parlamentares",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Partido",
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
                ("nome", models.CharField(max_length=50)),
                ("sigla", models.CharField(max_length=10)),
            ],
            options={
                "ordering": ("nome",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="SessaoLegislativa",
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
                    "numero",
                    models.PositiveSmallIntegerField(
                        unique=True, verbose_name="n\xfamero da sess\xe3o"
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        default=b"O",
                        max_length=1,
                        choices=[
                            (b"O", "Ordin\xe1ria"),
                            (b"E", "Extraordin\xe1ria"),
                        ],
                    ),
                ),
                ("data_inicio", models.DateField(verbose_name="in\xedcio")),
                ("data_fim", models.DateField(verbose_name="fim")),
                (
                    "data_inicio_intervalo",
                    models.DateField(
                        null=True,
                        verbose_name="in\xedcio de intervalo",
                        blank=True,
                    ),
                ),
                (
                    "data_fim_intervalo",
                    models.DateField(
                        null=True, verbose_name="fim de intervalo", blank=True
                    ),
                ),
                (
                    "legislatura",
                    models.ForeignKey(
                        to="parlamentares.Legislatura", on_delete=models.CASCADE
                    ),
                ),
                (
                    "mesa_diretora",
                    models.ForeignKey(
                        verbose_name="Mesa Diretora",
                        to="parlamentares.MesaDiretora",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("legislatura", "numero"),
                "verbose_name": "Sess\xe3o Legislativa",
                "verbose_name_plural": "Sess\xf5es Legislativas",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="membromesadiretora",
            name="mesa_diretora",
            field=models.ForeignKey(
                to="parlamentares.MesaDiretora", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="membromesadiretora",
            name="parlamentar",
            field=models.ForeignKey(
                to="parlamentares.Parlamentar", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="membromesadiretora",
            unique_together=set([("cargo", "mesa_diretora")]),
        ),
        migrations.AddField(
            model_name="mandato",
            name="parlamentar",
            field=models.ForeignKey(
                to="parlamentares.Parlamentar", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="mandato",
            name="partido",
            field=models.ForeignKey(
                to="parlamentares.Partido", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="legislatura",
            unique_together=set([("casa_legislativa", "numero")]),
        ),
        migrations.AddField(
            model_name="composicaocoligacao",
            name="partido",
            field=models.ForeignKey(
                to="parlamentares.Partido", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="coligacao",
            name="legislatura",
            field=models.ForeignKey(
                to="parlamentares.Legislatura", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
