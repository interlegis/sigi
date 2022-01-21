from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0006_remove_casalegislativa_gerente_contas'),
    ]

    operations = [
        migrations.AddField(
            model_name='funcionario',
            name='desativado',
            field=models.BooleanField(default=False, verbose_name='Desativado'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='funcionario',
            name='observacoes',
            field=models.TextField(verbose_name='Observa\xe7\xf5es', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='bairro',
            field=models.CharField(max_length=100, verbose_name='Bairro', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='cep',
            field=models.CharField(max_length=32, verbose_name='CEP'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='codigo_interlegis',
            field=models.CharField(max_length=3, verbose_name='C\xf3digo Interlegis', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='email',
            field=models.EmailField(max_length=128, verbose_name='E-mail', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='foto',
            field=models.ImageField(upload_to='imagens/casas', width_field='foto_largura', height_field='foto_altura', blank=True, verbose_name='Foto'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='inclusao_digital',
            field=models.CharField(default='NAO PESQUISADO', max_length=30, verbose_name='Inclus\xe3o digital', choices=[('NAO PESQUISADO', 'N\xe3o pesquisado'), ('NAO POSSUI PORTAL', 'N\xe3o possui portal'), ('PORTAL MODELO', 'Possui Portal Modelo'), ('OUTRO PORTAL', 'Possui outro portal')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='logradouro',
            field=models.CharField(help_text='Avenida, rua, pra\xe7a, jardim, parque...', max_length=100, verbose_name='Logradouro'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='municipio',
            field=models.ForeignKey(verbose_name='Munic\xedpio', to='contatos.Municipio', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='nome',
            field=models.CharField(help_text='Exemplo: <em>C\xe2mara Municipal de Pains</em>.', max_length=60, verbose_name='Nome'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='casalegislativa',
            name='pagina_web',
            field=models.URLField(help_text='Exemplo: <em>http://www.camarapains.mg.gov.br</em>.', verbose_name='P\xe1gina web', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='cargo',
            field=models.CharField(max_length=100, null=True, verbose_name='Cargo', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='nota',
            field=models.CharField(max_length=70, null=True, verbose_name='Telefones', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='setor',
            field=models.CharField(default='outros', max_length=100, verbose_name='Setor', choices=[('presidente', 'Presidente'), ('contato_interlegis', 'Contato Interlegis'), ('infraestrutura_fisica', 'Infraestrutura F\xedsica'), ('estrutura_de_ti', 'Estrutura de TI'), ('organizacao_do_processo_legislativo', 'Organiza\xe7\xe3o do Processo Legislativo'), ('producao_legislativa', 'Produ\xe7\xe3o Legislativa'), ('estrutura_de_comunicacao_social', 'Estrutura de Comunica\xe7\xe3o Social'), ('estrutura_de_recursos_humanos', 'Estrutura de Recursos Humanos'), ('gestao', 'Gest\xe3o'), ('outros', 'Outros')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='sexo',
            field=models.CharField(default='M', max_length=1, verbose_name='Sexo', choices=[('M', 'Masculino'), ('F', 'Feminino')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='funcionario',
            name='tempo_de_servico',
            field=models.CharField(max_length=50, null=True, verbose_name='Tempo de servi\xe7o', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tipocasalegislativa',
            name='nome',
            field=models.CharField(max_length=100, verbose_name='Nome'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tipocasalegislativa',
            name='sigla',
            field=models.CharField(max_length=5, verbose_name='Sigla'),
            preserve_default=True,
        ),
    ]
