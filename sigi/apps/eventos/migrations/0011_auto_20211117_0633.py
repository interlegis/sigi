# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0010_modulo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modulo',
            options={'ordering': ('inicio',), 'verbose_name': 'M\xf3dulo do evento', 'verbose_name_plural': 'M\xf3dulos do evento'},
        ),
        migrations.AddField(
            model_name='evento',
            name='total_participantes',
            field=models.PositiveIntegerField(default=0, help_text='Se informar quantidade de participantes na aba de convites, este campo ser\xe1 ajustado com a somat\xf3ria dos participantes naquela aba.', verbose_name='Total de participantes'),
            preserve_default=True,
        ),
    ]
