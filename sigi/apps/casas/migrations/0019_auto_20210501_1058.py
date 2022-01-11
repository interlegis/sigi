from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0018_orgao_sigla'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funcionario',
            name='email',
            field=models.CharField(max_length=250, verbose_name='e-mail', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='nota',
            field=models.CharField(max_length=250, null=True, verbose_name='Telefones', blank=True),
            preserve_default=True,
        ),
    ]
