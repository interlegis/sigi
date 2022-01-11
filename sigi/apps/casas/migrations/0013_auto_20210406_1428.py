from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0012_auto_20210406_1420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tipoorgao',
            options={'verbose_name': 'Tipo de \xf3rg\xe3o', 'verbose_name_plural': 'Tipos de \xf3rg\xe3o'},
        ),
    ]
