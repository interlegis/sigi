from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("convenios", "0016_auto_20210909_0732"),
    ]

    operations = [
        migrations.AddField(
            model_name="convenio",
            name="id_contrato_gescon",
            field=models.CharField(
                default="",
                verbose_name="ID do contrato no Gescon",
                max_length=20,
                editable=False,
                blank=True,
            ),
            preserve_default=True,
        ),
    ]
