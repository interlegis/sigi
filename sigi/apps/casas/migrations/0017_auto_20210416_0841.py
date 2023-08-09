from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("casas", "0016_auto_20210407_1559"),
    ]

    operations = [
        migrations.AlterField(
            model_name="funcionario",
            name="casa_legislativa",
            field=models.ForeignKey(
                verbose_name="\xf3rg\xe3o",
                to="casas.Orgao",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="municipio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="Municipio",
                blank=True,
                to="contatos.Municipio",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="orgao",
            name="municipio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Munic\xedpio",
                to="contatos.Municipio",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="orgao",
            name="pesquisador",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="Pesquisador",
                blank=True,
                to="servidores.Servidor",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="orgao",
            name="tipo",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Tipo",
                to="casas.TipoOrgao",
            ),
            preserve_default=True,
        ),
    ]
