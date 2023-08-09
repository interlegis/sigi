from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("convenios", "0014_gescon"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="convenio",
            name="search_text",
        ),
    ]
