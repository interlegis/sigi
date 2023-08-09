from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("servidores", "0004_auto_20210422_1907"),
        ("convenios", "0007_auto_20210416_0918"),
    ]

    operations = [
        migrations.AddField(
            model_name="convenio",
            name="servico_gestao",
            field=models.ForeignKey(
                related_name="convenios_geridos",
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="servi\xe7o de gest\xe3o",
                blank=True,
                to="servidores.Servico",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="convenio",
            name="servidor_gestao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="servidor de gest\xe3o",
                blank=True,
                to="servidores.Servidor",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="convenio",
            name="acompanha",
            field=models.ForeignKey(
                related_name="convenios_acompanhados",
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="acompanhado por",
                blank=True,
                to="servidores.Servidor",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
