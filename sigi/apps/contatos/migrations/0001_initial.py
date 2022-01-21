from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import sigi.apps.utils


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=120, verbose_name='nome completo')),
                ('nota', models.CharField(max_length=70, blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='e-mail', blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('nome',),
                'verbose_name': 'contato Interlegis',
                'verbose_name_plural': 'contatos Interlegis',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Endereco',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.CharField(max_length=15, choices=[('aeroporto', 'Aeroporto'), ('alameda', 'Alameda'), ('area', '\xc1rea'), ('avenida', 'Avenida'), ('campo', 'Campo'), ('chacara', 'Ch\xe1cara'), ('colonia', 'Col\xf4nia'), ('condominio', 'Condom\xednio'), ('conjunto', 'Conjunto'), ('distrito', 'Distrito'), ('esplanada', 'Esplanada'), ('estacao', 'Esta\xe7\xe3o'), ('estrada', 'Estrada'), ('favela', 'Favela'), ('fazenda', 'Fazenda'), ('feira', 'Feira'), ('jardim', 'Jardim'), ('ladeira', 'Ladeira'), ('lago', 'Lago'), ('lagoa', 'Lagoa'), ('largo', 'Largo'), ('loteamento', 'Loteamento'), ('morro', 'Morro'), ('nucleo', 'N\xfacleo'), ('parque', 'Parque'), ('passarela', 'Passarela'), ('patio', 'P\xe1tio'), ('praca', 'Pra\xe7a'), ('quadra', 'Quadra'), ('recanto', 'Recanto'), ('residencial', 'Residencial'), ('rodovia', 'Rodovia'), ('rua', 'Rua'), ('setor', 'Setor'), ('sitio', 'S\xedtio'), ('travessa', 'Travessa'), ('trecho', 'Trecho'), ('trevo', 'Trevo'), ('vale', 'Vale'), ('vereda', 'Vereda'), ('via', 'Via'), ('viaduto', 'Viaduto'), ('viela', 'Viela'), ('vila', 'Vila'), ('outro', 'Outro')])),
                ('logradouro', models.CharField(max_length=100)),
                ('numero', models.CharField(max_length=15, blank=True)),
                ('complemento', models.CharField(max_length=15, blank=True)),
                ('referencia', models.CharField(max_length=100, blank=True)),
                ('bairro', models.CharField(max_length=100, blank=True)),
                ('cep', models.CharField(help_text='Formato: <em>XXXXX-XXX</em>.', max_length=9, null=True, verbose_name='CEP', blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('logradouro', 'numero'),
                'verbose_name': 'endere\xe7o',
                'verbose_name_plural': 'endere\xe7os',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('codigo_ibge', models.PositiveIntegerField(help_text='C\xf3digo do munic\xedpio segundo IBGE.', unique=True, serialize=False, verbose_name='c\xf3digo IBGE', primary_key=True)),
                ('codigo_mesorregiao', models.PositiveIntegerField(null=True, verbose_name='c\xf3digo mesorregi\xe3o', blank=True)),
                ('codigo_microrregiao', models.PositiveIntegerField(null=True, verbose_name='c\xf3digo microrregi\xe3o', blank=True)),
                ('codigo_tse', models.PositiveIntegerField(help_text='C\xf3digo do munic\xedpio segundo TSE.', unique=True, null=True, verbose_name='c\xf3digo TSE')),
                ('nome', models.CharField(max_length=50)),
                ('search_text', sigi.apps.utils.SearchField(field_names=['nome', 'uf'], editable=False)),
                ('is_capital', models.BooleanField(default=False, verbose_name='capital')),
                ('populacao', models.PositiveIntegerField(verbose_name='popula\xe7\xe3o')),
                ('is_polo', models.BooleanField(default=False, verbose_name='p\xf3lo')),
                ('data_criacao', models.DateField(null=True, verbose_name='data de cria\xe7\xe3o do munic\xedpio', blank=True)),
                ('latitude', models.DecimalField(help_text='Exemplo: <em>-20,464</em>.', null=True, max_digits=10, decimal_places=8, blank=True)),
                ('longitude', models.DecimalField(help_text='Exemplo: <em>-45,426</em>.', null=True, max_digits=11, decimal_places=8, blank=True)),
                ('idh', models.DecimalField(help_text='\xcdndice de desenvolvimento Humano', verbose_name='IDH', max_digits=4, decimal_places=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('pib_total', models.DecimalField(null=True, verbose_name='PIB total', max_digits=18, decimal_places=3, blank=True)),
                ('pib_percapita', models.DecimalField(null=True, verbose_name='PIB per capita', max_digits=18, decimal_places=3, blank=True)),
                ('pib_ano', models.IntegerField(null=True, verbose_name='Ano de apura\xe7\xe3o do PIB', blank=True)),
            ],
            options={
                'ordering': ('nome', 'codigo_ibge'),
                'verbose_name': 'munic\xedpio',
                'verbose_name_plural': 'munic\xedpios',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Telefone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.CharField(help_text='Exemplo: <em>(31)8851-9898</em>.', max_length=64, verbose_name='n\xfamero')),
                ('tipo', models.CharField(default='I', max_length=1, choices=[('F', 'Fixo'), ('M', 'M\xf3vel'), ('X', 'Fax'), ('I', 'Indefinido')])),
                ('nota', models.CharField(max_length=70, null=True, blank=True)),
                ('ult_alteracao', models.DateTimeField(auto_now=True, verbose_name='\xdaltima altera\xe7\xe3o', null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('numero',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UnidadeFederativa',
            fields=[
                ('codigo_ibge', models.PositiveIntegerField(help_text='C\xf3digo do estado segundo IBGE.', unique=True, serialize=False, verbose_name='c\xf3digo IBGE', primary_key=True)),
                ('nome', models.CharField(max_length=25, verbose_name='Nome UF')),
                ('search_text', sigi.apps.utils.SearchField(field_names=['nome'], editable=False)),
                ('sigla', models.CharField(help_text='Exemplo: <em>MG</em>.', unique=True, max_length=2)),
                ('regiao', models.CharField(max_length=2, verbose_name='regi\xe3o', choices=[('SL', 'Sul'), ('SD', 'Sudeste'), ('CO', 'Centro-Oeste'), ('NE', 'Nordeste'), ('NO', 'Norte')])),
                ('populacao', models.PositiveIntegerField(verbose_name='popula\xe7\xe3o')),
            ],
            options={
                'ordering': ('nome',),
                'verbose_name': 'Unidade Federativa',
                'verbose_name_plural': 'Unidades Federativas',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='telefone',
            unique_together=set([('numero', 'tipo')]),
        ),
        migrations.AddField(
            model_name='municipio',
            name='uf',
            field=models.ForeignKey(verbose_name='UF', to='contatos.UnidadeFederativa', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='endereco',
            name='municipio',
            field=models.ForeignKey(verbose_name='munic\xedpio', blank=True, to='contatos.Municipio', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contato',
            name='municipio',
            field=models.ForeignKey(verbose_name='munic\xedpio', blank=True, to='contatos.Municipio', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
