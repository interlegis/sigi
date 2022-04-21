from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("casas", "0005_casalegislativa_gerentes_interlegis"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="casalegislativa",
            name="gerente_contas",
        ),
    ]
