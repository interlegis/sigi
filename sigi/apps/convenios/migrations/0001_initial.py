from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import sigi.apps.utils


class Migration(migrations.Migration):
    dependencies = [
        ("inventario", "__first__"),
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
                        upload_to="apps/convenios/anexo/arquivo",
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
            ],
            options={
                "ordering": ("-data_pub",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Convenio",
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
                        field_names=["casa_legislativa"], editable=False
                    ),
                ),
                (
                    "num_processo_sf",
                    models.CharField(
                        help_text="Formatos:<br/>Antigo: <em>XXXXXX/XX-X</em>.<br/><em>SIGAD: XXXXX.XXXXXX/XXXX-XX</em>",
                        max_length=20,
                        verbose_name="n\xfamero do processo SF (Senado Federal)",
                        blank=True,
                    ),
                ),
                (
                    "num_convenio",
                    models.CharField(
                        max_length=10,
                        verbose_name="n\xfamero do conv\xeanio",
                        blank=True,
                    ),
                ),
                (
                    "data_adesao",
                    models.DateField(
                        null=True, verbose_name="Aderidas", blank=True
                    ),
                ),
                (
                    "data_retorno_assinatura",
                    models.DateField(
                        help_text="Conv\xeanio firmado.",
                        null=True,
                        verbose_name="Conveniadas",
                        blank=True,
                    ),
                ),
                (
                    "data_pub_diario",
                    models.DateField(
                        null=True,
                        verbose_name="data da publica\xe7\xe3o no Di\xe1rio Oficial",
                        blank=True,
                    ),
                ),
                (
                    "data_termo_aceite",
                    models.DateField(
                        help_text="Equipamentos recebidos.",
                        null=True,
                        verbose_name="Equipadas",
                        blank=True,
                    ),
                ),
                (
                    "data_devolucao_via",
                    models.DateField(
                        help_text="Data de devolu\xe7\xe3o da via do conv\xeanio \xe0 C\xe2mara Municipal.",
                        null=True,
                        verbose_name="data de devolu\xe7\xe3o da via",
                        blank=True,
                    ),
                ),
                (
                    "data_postagem_correio",
                    models.DateField(
                        null=True,
                        verbose_name="data postagem correio",
                        blank=True,
                    ),
                ),
                (
                    "data_devolucao_sem_assinatura",
                    models.DateField(
                        help_text="Data de devolu\xe7\xe3o por falta de assinatura",
                        null=True,
                        verbose_name="data de devolu\xe7\xe3o por falta de assinatura",
                        blank=True,
                    ),
                ),
                (
                    "data_retorno_sem_assinatura",
                    models.DateField(
                        help_text="Data do retorno do conv\xeanio sem assinatura",
                        null=True,
                        verbose_name="data do retorno sem assinatura",
                        blank=True,
                    ),
                ),
                (
                    "observacao",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ("conveniada", models.BooleanField(default=False)),
                ("equipada", models.BooleanField(default=False)),
                (
                    "casa_legislativa",
                    models.ForeignKey(
                        verbose_name="Casa Legislativa",
                        to="casas.CasaLegislativa",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
                "get_latest_by": "id",
                "verbose_name": "conv\xeanio",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="EquipamentoPrevisto",
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
                ("quantidade", models.PositiveSmallIntegerField(default=1)),
                (
                    "convenio",
                    models.ForeignKey(
                        verbose_name="conv\xeanio",
                        to="convenios.Convenio",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "equipamento",
                    models.ForeignKey(
                        to="inventario.Equipamento", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "verbose_name": "equipamento previsto",
                "verbose_name_plural": "equipamentos previstos",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Projeto",
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
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Tramitacao",
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
                ("data", models.DateField()),
                (
                    "observacao",
                    models.CharField(
                        max_length="512",
                        null=True,
                        verbose_name="observa\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "convenio",
                    models.ForeignKey(
                        verbose_name="conv\xeanio",
                        to="convenios.Convenio",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Tramita\xe7\xf5es",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="UnidadeAdministrativa",
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
                ("sigla", models.CharField(max_length="10")),
                ("nome", models.CharField(max_length="100")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="tramitacao",
            name="unid_admin",
            field=models.ForeignKey(
                verbose_name="Unidade Administrativa",
                to="convenios.UnidadeAdministrativa",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="convenio",
            name="projeto",
            field=models.ForeignKey(
                to="convenios.Projeto", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="anexo",
            name="convenio",
            field=models.ForeignKey(
                verbose_name="conv\xeanio",
                to="convenios.Convenio",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
