from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("casas", "0015_auto_20210407_0801"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orgao",
            name="gerentes_interlegis",
            field=models.ManyToManyField(
                related_name="casas_que_gerencia",
                verbose_name="Gerentes Interlegis",
                to="servidores.Servidor",
                blank=True,
            ),
            preserve_default=True,
        ),
    ]
