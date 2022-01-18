# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CasaManifesta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_manifestacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('informante', models.CharField(max_length=100, verbose_name='Nome do informante', blank=True)),
                ('cargo', models.CharField(max_length=100, verbose_name='Cargo do informante', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='E-mail de contato', blank=True)),
                ('casa_legislativa', models.OneToOneField(to='casas.CasaLegislativa', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogServico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao', models.CharField(max_length=60, verbose_name='Breve descri\xe7\xe3o da a\xe7\xe3o')),
                ('data', models.DateField(default=datetime.date.today, verbose_name='Data da a\xe7\xe3o')),
                ('log', models.TextField(verbose_name='Log da a\xe7\xe3o')),
            ],
            options={
                'verbose_name': 'Log do servi\xe7o',
                'verbose_name_plural': 'Logs do servi\xe7o',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegistroServico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('produto', models.CharField(max_length=50)),
                ('versao', models.CharField(max_length=30)),
                ('url', models.URLField()),
                ('data_registro', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Registro de servi\xe7os',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(verbose_name='URL do servi\xe7o', blank=True)),
                ('hospedagem_interlegis', models.BooleanField(default=False, verbose_name='Hospedagem no Interlegis?')),
                ('nome_servidor', models.CharField(help_text='Se hospedado no Interlegis, informe o nome do servidor.<br/>Sen\xe3o, informe o nome do provedor de servi\xe7os.', max_length=60, verbose_name='Hospedado em', blank=True)),
                ('porta_servico', models.PositiveSmallIntegerField(null=True, verbose_name='Porta de servi\xe7o (inst\xe2ncia)', blank=True)),
                ('senha_inicial', models.CharField(max_length=33, verbose_name='Senha inicial', blank=True)),
                ('data_ativacao', models.DateField(default=datetime.date.today, verbose_name='Data de ativa\xe7\xe3o')),
                ('data_alteracao', models.DateField(auto_now=True, verbose_name='Data da \xfaltima altera\xe7\xe3o', null=True)),
                ('data_desativacao', models.DateField(null=True, verbose_name='Data de desativa\xe7\xe3o', blank=True)),
                ('motivo_desativacao', models.TextField(verbose_name='Motivo da desativa\xe7\xe3o', blank=True)),
                ('data_ultimo_uso', models.DateField(help_text='Data em que o servi\xe7o foi utilizado pela Casa Legislativa pela \xfaltima vez<br/><strong>N\xc3O \xc9 ATUALIZADO AUTOMATICAMENTE!</strong>', null=True, verbose_name='Data da \xfaltima utiliza\xe7\xe3o', blank=True)),
                ('erro_atualizacao', models.CharField(help_text='Erro ocorrido na \xfaltima tentativa de atualizar a data de \xfaltimo acesso', max_length=200, verbose_name='Erro na atualiza\xe7\xe3o', blank=True)),
                ('casa_legislativa', models.ForeignKey(verbose_name='Casa Legislativa', to='casas.CasaLegislativa', on_delete=models.CASCADE)),
                ('contato_administrativo', models.ForeignKey(related_name=b'contato_administrativo', verbose_name='Contato administrativo', to='casas.Funcionario', on_delete=models.CASCADE)),
                ('contato_tecnico', models.ForeignKey(related_name=b'contato_tecnico', verbose_name='Contato t\xe9cnico', to='casas.Funcionario', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServicoManifesto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(blank=True)),
                ('hospedagem_interlegis', models.BooleanField(default=False, verbose_name='Hospedagem no Interlegis?')),
                ('casa_manifesta', models.ForeignKey(to='servicos.CasaManifesta', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoServico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=60, verbose_name='Nome')),
                ('sigla', models.CharField(max_length=b'12', verbose_name='Sigla')),
                ('string_pesquisa', models.CharField(help_text='Sufixo para pesquisa RSS para averiguar a data da \xfaltima atualiza\xe7\xe3o do servi\xe7o', max_length=200, verbose_name='String de pesquisa', blank=True)),
                ('template_email_ativa', models.TextField(help_text='Use:<br/>\n                        {url} para incluir a URL do servi\xe7o,<br/>\n                        {senha} para incluir a senha inicial do servi\xe7o', verbose_name='Template de email de ativa\xe7\xe3o', blank=True)),
                ('template_email_altera', models.TextField(help_text='Use:<br/>\n                        {url} para incluir a URL do servi\xe7o,<br/>\n                        {senha} para incluir a senha inicial do servi\xe7o', verbose_name='Template de email de altera\xe7\xe3o', blank=True)),
                ('template_email_desativa', models.TextField(help_text='Use:<br/>\n                        {url} para incluir a URL do servi\xe7o,<br/>\n                        {senha} para incluir a senha inicial do servi\xe7o<br/>{motivo} para incluir o motivo da desativa\xe7\xe3o do servi\xe7o', verbose_name='Template de email de desativa\xe7\xe3o', blank=True)),
            ],
            options={
                'verbose_name': 'Tipo de servi\xe7o',
                'verbose_name_plural': 'Tipos de servi\xe7o',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='servicomanifesto',
            name='servico',
            field=models.ForeignKey(to='servicos.TipoServico', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='servicomanifesto',
            unique_together=set([('casa_manifesta', 'servico')]),
        ),
        migrations.AddField(
            model_name='servico',
            name='tipo_servico',
            field=models.ForeignKey(verbose_name='Tipo de servi\xe7o', to='servicos.TipoServico', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logservico',
            name='servico',
            field=models.ForeignKey(verbose_name='Servi\xe7o', to='servicos.Servico', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='CasaAtendida',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name_plural': 'Casas atendidas',
            },
            bases=('casas.casalegislativa',),
        ),
    ]
