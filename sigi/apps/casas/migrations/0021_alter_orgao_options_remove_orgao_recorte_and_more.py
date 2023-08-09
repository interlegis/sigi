# Generated by Django 4.0.1 on 2022-01-11 18:44

from django.db import migrations, models
import django.db.models.deletion
import sigi.apps.utils


class Migration(migrations.Migration):
    dependencies = [
        ("servidores", "0008_alter_servico_id_alter_servidor_foto_and_more"),
        (
            "contatos",
            "0005_alter_mesorregiao_options_alter_microrregiao_options_and_more",
        ),
        ("casas", "0020_auto_20210611_0946"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="orgao",
            options={
                "ordering": ("nome",),
                "verbose_name": "órgão",
                "verbose_name_plural": "órgãos",
            },
        ),
        migrations.RemoveField(
            model_name="orgao",
            name="recorte",
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="bairro",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="bairro"
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="cargo",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="cargo"
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="data_nascimento",
            field=models.DateField(
                blank=True, null=True, verbose_name="data de nascimento"
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="desativado",
            field=models.BooleanField(
                default=False, verbose_name="desativado"
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="endereco",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="endereço"
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="municipio",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="contatos.municipio",
                verbose_name="municipio",
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="nome",
            field=models.CharField(
                max_length=60, verbose_name="nome completo"
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="nota",
            field=models.CharField(
                blank=True, max_length=250, null=True, verbose_name="telefones"
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="observacoes",
            field=models.TextField(blank=True, verbose_name="observações"),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="redes_sociais",
            field=models.TextField(
                blank=True,
                help_text="Colocar um por linha",
                verbose_name="redes sociais",
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="setor",
            field=models.CharField(
                choices=[
                    ("presidente", "Presidente"),
                    ("contato_interlegis", "Contato Interlegis"),
                    ("infraestrutura_fisica", "Infraestrutura Física"),
                    ("estrutura_de_ti", "Estrutura de TI"),
                    (
                        "organizacao_do_processo_legislativo",
                        "Organização do Processo Legislativo",
                    ),
                    ("producao_legislativa", "Produção Legislativa"),
                    (
                        "estrutura_de_comunicacao_social",
                        "Estrutura de Comunicação Social",
                    ),
                    (
                        "estrutura_de_recursos_humanos",
                        "Estrutura de Recursos Humanos",
                    ),
                    ("gestao", "Gestão"),
                    ("outros", "Outros"),
                ],
                default="outros",
                max_length=100,
                verbose_name="setor",
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="sexo",
            field=models.CharField(
                choices=[("M", "Masculino"), ("F", "Feminino")],
                default="M",
                max_length=1,
                verbose_name="sexo",
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="tempo_de_servico",
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                verbose_name="tempo de serviço",
            ),
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="ult_alteracao",
            field=models.DateTimeField(
                auto_now=True, null=True, verbose_name="última alteração"
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="bairro",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="bairro"
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="cnpj",
            field=models.CharField(
                blank=True, max_length=32, verbose_name="CNPJ"
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="codigo_interlegis",
            field=models.CharField(
                blank=True, max_length=3, verbose_name="código Interlegis"
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="data_instalacao",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="data de instalação da Casa Legislativa",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="data_levantamento",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="data/hora da pesquisa"
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="email",
            field=models.EmailField(
                blank=True, max_length=128, verbose_name="e-mail"
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="foto",
            field=models.ImageField(
                blank=True,
                height_field="foto_altura",
                upload_to="imagens/casas",
                verbose_name="foto",
                width_field="foto_largura",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="horario_funcionamento",
            field=models.CharField(
                blank=True,
                max_length=100,
                verbose_name="horário de funcionamento da Casa Legislativa",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="inclusao_digital",
            field=models.CharField(
                choices=[
                    ("NAO PESQUISADO", "Não pesquisado"),
                    ("NAO POSSUI PORTAL", "Não possui portal"),
                    ("PORTAL MODELO", "Possui Portal Modelo"),
                    ("OUTRO PORTAL", "Possui outro portal"),
                ],
                default="NAO PESQUISADO",
                max_length=30,
                verbose_name="inclusão digital",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="logradouro",
            field=models.CharField(
                help_text="Avenida, rua, praça, jardim, parque...",
                max_length=100,
                verbose_name="logradouro",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="municipio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="contatos.municipio",
                verbose_name="município",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="nome",
            field=models.CharField(
                help_text="Exemplo: <em>Câmara Municipal de Pains</em>.",
                max_length=60,
                verbose_name="nome",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="obs_pesquisa",
            field=models.TextField(
                blank=True, verbose_name="observações do pesquisador"
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="pagina_web",
            field=models.URLField(
                blank=True,
                help_text="Exemplo: <em>http://www.camarapains.mg.gov.br</em>.",
                verbose_name="página web",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="pesquisador",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="servidores.servidor",
                verbose_name="pesquisador",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="search_text",
            field=sigi.apps.utils.SearchField(
                editable=False, field_names=["nome"]
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="tipo",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="casas.tipoorgao",
                verbose_name="tipo",
            ),
        ),
        migrations.AlterField(
            model_name="orgao",
            name="ult_alt_endereco",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="última alteração do endereço",
            ),
        ),
        migrations.AlterField(
            model_name="tipoorgao",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
    ]
