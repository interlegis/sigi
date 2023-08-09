from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("convenios", "0005_auto_20210409_0842"),
    ]

    operations = [
        migrations.AlterField(
            model_name="convenio",
            name="casa_legislativa",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="\xf3rg\xe3o conveniado",
                to="casas.Orgao",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="convenio",
            name="projeto",
            field=models.ForeignKey(
                to="convenios.Projeto",
                on_delete=django.db.models.deletion.PROTECT,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="tramitacao",
            name="unid_admin",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Unidade Administrativa",
                to="convenios.UnidadeAdministrativa",
            ),
            preserve_default=True,
        ),
    ]
