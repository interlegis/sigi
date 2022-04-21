from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("convenios", "0004_auto_20210407_1928"),
    ]

    operations = [
        migrations.AddField(
            model_name="convenio",
            name="data_sigad",
            field=models.DateField(
                null=True, verbose_name="data de cadastro no SIGAD", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="convenio",
            name="data_sigi",
            field=models.DateField(
                auto_now_add=True,
                verbose_name="data de cadastro no SIGI",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
