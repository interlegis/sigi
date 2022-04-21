from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("convenios", "0012_auto_20210831_0844"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="convenio",
            name="duracao",
        ),
    ]
