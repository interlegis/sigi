from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servidores', '0001_initial'),
        ('casas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='casalegislativa',
            name='data_levantamento',
            field=models.DateTimeField(null=True, verbose_name='Data/hora da pesquisa', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='casalegislativa',
            name='inclusao_digital',
            field=models.CharField(default=b'NAO PESQUISADO', max_length=30, choices=[(b'NAO PESQUISADO', 'N\xe3o pesquisado'), (b'NAO POSSUI PORTAL', 'N\xe3o possui portal'), (b'PORTAL MODELO', 'Possui Portal Modelo'), (b'OUTRO PORTAL', 'Possui outro portal')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='casalegislativa',
            name='obs_pesquisa',
            field=models.TextField(verbose_name='Observa\xe7\xf5es do pesquisador', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='casalegislativa',
            name='pesquisador',
            field=models.ForeignKey(verbose_name='Pesquisador', blank=True, to='servidores.Servidor', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='gerente_contas',
            field=models.ForeignKey(related_name='casas_que_gerencia', verbose_name=b'Gerente de contas', blank=True, to='servidores.Servidor', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='ult_alteracao',
            field=models.DateTimeField(auto_now=True, verbose_name='\xdaltima altera\xe7\xe3o', null=True),
            preserve_default=True,
        ),
    ]
