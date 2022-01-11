from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0019_auto_20210501_1058'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tipoorgao',
            options={'ordering': ('nome',), 'verbose_name': 'Tipo de \xf3rg\xe3o', 'verbose_name_plural': 'Tipos de \xf3rg\xe3o'},
        ),
    ]
