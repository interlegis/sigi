from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("convenios", "0009_auto_20210611_0946"),
    ]

    operations = [
        migrations.AlterField(
            model_name="convenio",
            name="data_retorno_assinatura",
            field=models.DateField(
                help_text="Conv\xeanio firmado.",
                null=True,
                verbose_name="data in\xedcio vig\xeancia",
                blank=True,
            ),
            preserve_default=True,
        ),
    ]
