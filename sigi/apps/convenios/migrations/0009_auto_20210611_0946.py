from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('convenios', '0008_auto_20210422_1907'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projeto',
            options={'ordering': ('nome',)},
        ),
    ]
