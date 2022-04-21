from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("servidores", "0001_initial"),
        ("convenios", "0003_auto_20210406_1945"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatusConvenio",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "cancela",
                    models.BooleanField(
                        default=False, verbose_name="Cancela o conv\xeanio"
                    ),
                ),
            ],
            options={
                "ordering": ("nome",),
                "verbose_name": "Estado de convenios",
                "verbose_name_plural": "Estados de convenios",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="convenio",
            name="acompanha",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="acompanhado por",
                blank=True,
                to="servidores.Servidor",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="convenio",
            name="status",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="estado atual",
                blank=True,
                to="convenios.StatusConvenio",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="convenio",
            name="casa_legislativa",
            field=models.ForeignKey(
                verbose_name="\xf3rg\xe3o conveniado",
                to="casas.Orgao",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="convenio",
            name="data_adesao",
            field=models.DateField(
                null=True, verbose_name="aderidas", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="convenio",
            name="data_retorno_assinatura",
            field=models.DateField(
                help_text="Conv\xeanio firmado.",
                null=True,
                verbose_name="conveniadas",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="convenio",
            name="data_termo_aceite",
            field=models.DateField(
                help_text="Equipamentos recebidos.",
                null=True,
                verbose_name="equipadas",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="convenio",
            name="duracao",
            field=models.PositiveIntegerField(
                help_text="Deixar em branco caso a dura\xe7\xe3o seja indefinida",
                null=True,
                verbose_name="dura\xe7\xe3o (meses)",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="convenio",
            name="observacao",
            field=models.TextField(
                null=True, verbose_name="observa\xe7\xf5es", blank=True
            ),
            preserve_default=True,
        ),
    ]
