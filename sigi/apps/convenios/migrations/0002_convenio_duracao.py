from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('convenios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='convenio',
            name='duracao',
            field=models.PositiveIntegerField(help_text='Deixar em branco caso a dura\xe7\xe3o seja indefinida', null=True, verbose_name='Dura\xe7\xe3o (meses)', blank=True),
            preserve_default=True,
        ),
    ]
