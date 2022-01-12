from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('convenios', '0006_auto_20210416_0841'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoSolicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('nome',),
                'verbose_name': 'tipo de solicita\xe7\xe3o',
                'verbose_name_plural': 'Tipos de solicita\xe7\xe3o',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='convenio',
            name='data_solicitacao',
            field=models.DateField(null=True, verbose_name='data do e-mail de solicita\xe7\xe3o', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='convenio',
            name='tipo_solicitacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='tipo de solicita\xe7\xe3o', blank=True, to='convenios.TipoSolicitacao', null=True),
            preserve_default=True,
        ),
    ]
