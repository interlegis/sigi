from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("convenios", "0010_auto_20210819_0833"),
    ]

    operations = [
        migrations.AddField(
            model_name="convenio",
            name="data_termino_vigencia",
            field=models.DateField(
                help_text="T\xe9rmino da vig\xeancia do conv\xeanio.",
                null=True,
                verbose_name="Data t\xe9rmino vig\xeancia",
                blank=True,
            ),
            preserve_default=True,
        ),
    ]
