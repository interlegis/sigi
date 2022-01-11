from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0008_auto_20210218_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funcionario',
            name='municipio',
            field=models.ForeignKey(verbose_name='Municipio', blank=True, to='contatos.Municipio', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
