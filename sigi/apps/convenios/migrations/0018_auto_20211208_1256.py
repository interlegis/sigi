from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('convenios', '0017_convenio_id_contrato_gescon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convenio',
            name='projeto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Tipo de Convenio', to='convenios.Projeto'),
            preserve_default=True,
        ),
    ]
