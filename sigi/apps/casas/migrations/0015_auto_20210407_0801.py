from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("casas", "0014_auto_20210406_1945"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="orgao",
            options={
                "ordering": ("nome",),
                "verbose_name": "\xd3rg\xe3o",
                "verbose_name_plural": "\xd3rg\xe3os",
            },
        ),
        migrations.AddField(
            model_name="tipoorgao",
            name="legislativo",
            field=models.BooleanField(
                default=False, verbose_name="Poder legislativo"
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="orgao",
            unique_together=set([]),
        ),
    ]
