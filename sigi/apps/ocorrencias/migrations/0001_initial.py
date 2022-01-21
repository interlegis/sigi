# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0001_initial'),
        ('servidores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anexo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('arquivo', models.FileField(upload_to=b'apps/ocorrencia/anexo/arquivo', max_length=500, verbose_name='Arquivo anexado')),
                ('descricao', models.CharField(max_length=b'70', verbose_name='descri\xe7\xe3o do anexo')),
                ('data_pub', models.DateTimeField(auto_now_add=True, verbose_name='data da publica\xe7\xe3o do anexo', null=True)),
            ],
            options={
                'ordering': ('-data_pub',),
                'verbose_name': 'Anexo',
                'verbose_name_plural': 'Anexos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50, verbose_name='Categoria')),
                ('descricao', models.TextField(null=True, verbose_name='descri\xe7\xe3o', blank=True)),
                ('setor_responsavel', models.ForeignKey(verbose_name='Setor respons\xe1vel', to='servidores.Servico', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de cria\xe7\xe3o', null=True)),
                ('descricao', models.TextField(null=True, verbose_name='Descri\xe7\xe3o', blank=True)),
                ('novo_status', models.IntegerField(blank=True, null=True, verbose_name='Novo status', choices=[(1, 'Aberto'), (2, 'Reaberto'), (3, 'Resolvido'), (4, 'Fechado'), (5, 'Duplicado')])),
                ('encaminhar_setor', models.ForeignKey(verbose_name='Encaminhar para setor', blank=True, to='servidores.Servico', null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ocorrencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateField(auto_now_add=True, verbose_name='Data de cria\xe7\xe3o', null=True)),
                ('data_modificacao', models.DateField(auto_now=True, verbose_name='Data de modifica\xe7\xe3o', null=True)),
                ('assunto', models.CharField(max_length=200, verbose_name='Assunto')),
                ('status', models.IntegerField(default=1, verbose_name='Status', choices=[(1, 'Aberto'), (2, 'Reaberto'), (3, 'Resolvido'), (4, 'Fechado'), (5, 'Duplicado')])),
                ('prioridade', models.IntegerField(default=3, verbose_name='Prioridade', choices=[(1, 'Alt\xedssimo'), (2, 'Alto'), (3, 'Normal'), (4, 'Baixo'), (5, 'Baix\xedssimo')])),
                ('descricao', models.TextField(verbose_name='descri\xe7\xe3o', blank=True)),
                ('resolucao', models.TextField(verbose_name='resolu\xe7\xe3o', blank=True)),
                ('casa_legislativa', models.ForeignKey(verbose_name='Casa Legislativa', to='casas.CasaLegislativa', on_delete=models.CASCADE)),
                ('categoria', models.ForeignKey(verbose_name='Categoria', to='ocorrencias.Categoria', on_delete=models.CASCADE)),
                ('servidor_registro', models.ForeignKey(verbose_name='Servidor que registrou a ocorr\xeancia', to='servidores.Servidor', on_delete=models.CASCADE)),
                ('setor_responsavel', models.ForeignKey(verbose_name='Setor respons\xe1vel', to='servidores.Servico', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['prioridade', 'data_modificacao', 'data_criacao'],
                'verbose_name': 'ocorr\xeancia',
                'verbose_name_plural': 'ocorr\xeancias',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoContato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao', models.CharField(max_length=50, verbose_name='Descri\xe7\xe3o')),
            ],
            options={
                'verbose_name': 'Tipo de contato',
                'verbose_name_plural': 'Tipos de contato',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ocorrencia',
            name='tipo_contato',
            field=models.ForeignKey(verbose_name='Tipo de contato', to='ocorrencias.TipoContato', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comentario',
            name='ocorrencia',
            field=models.ForeignKey(verbose_name='Ocorr\xeancia', to='ocorrencias.Ocorrencia', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comentario',
            name='usuario',
            field=models.ForeignKey(verbose_name='Usu\xe1rio', to='servidores.Servidor', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='anexo',
            name='ocorrencia',
            field=models.ForeignKey(verbose_name='ocorr\xeancia', to='ocorrencias.Ocorrencia', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
