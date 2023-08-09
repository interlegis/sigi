from __future__ import unicode_literals

from django.db import models, migrations
import sigi.apps.utils


class Migration(migrations.Migration):
    dependencies = [
        ("servidores", "0001_initial"),
        ("contatos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CasaLegislativa",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "nome",
                    models.CharField(
                        help_text="Exemplo: <em>C\xc3\xa2mara Municipal de Pains</em>.",
                        max_length=60,
                    ),
                ),
                (
                    "search_text",
                    sigi.apps.utils.SearchField(
                        field_names=["nome"], editable=False
                    ),
                ),
                (
                    "cnpj",
                    models.CharField(
                        max_length=32, verbose_name="CNPJ", blank=True
                    ),
                ),
                (
                    "observacoes",
                    models.TextField(
                        verbose_name="observa\xe7\xf5es", blank=True
                    ),
                ),
                (
                    "codigo_interlegis",
                    models.CharField(
                        max_length=3,
                        verbose_name="C\xc3\xb3digo Interlegis",
                        blank=True,
                    ),
                ),
                (
                    "logradouro",
                    models.CharField(
                        help_text="Avenida, rua, pra\xc3\xa7a, jardim, parque...",
                        max_length=100,
                    ),
                ),
                ("bairro", models.CharField(max_length=100, blank=True)),
                ("cep", models.CharField(max_length=32)),
                (
                    "email",
                    models.EmailField(
                        max_length=128, verbose_name="e-mail", blank=True
                    ),
                ),
                (
                    "pagina_web",
                    models.URLField(
                        help_text=b"Exemplo: <em>http://www.camarapains.mg.gov.br</em>.",
                        verbose_name="p\xe1gina web",
                        blank=True,
                    ),
                ),
                (
                    "ult_alt_endereco",
                    models.DateTimeField(
                        null=True,
                        verbose_name="\xdaltima altera\xe7\xe3o do endere\xe7o",
                        blank=True,
                    ),
                ),
                (
                    "foto",
                    models.ImageField(
                        height_field="foto_altura",
                        width_field="foto_largura",
                        upload_to="imagens/casas",
                        blank=True,
                    ),
                ),
                ("recorte", models.CharField("foto", max_length=255)),
                (
                    "foto_largura",
                    models.SmallIntegerField(null=True, editable=False),
                ),
                (
                    "foto_altura",
                    models.SmallIntegerField(null=True, editable=False),
                ),
                (
                    "data_instalacao",
                    models.DateField(
                        null=True,
                        verbose_name="Data de instala\xe7\xe3o da Casa Legislativa",
                        blank=True,
                    ),
                ),
                (
                    "gerente_contas",
                    models.ForeignKey(
                        verbose_name="Gerente de contas",
                        blank=True,
                        to="servidores.Servidor",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "municipio",
                    models.ForeignKey(
                        verbose_name="munic\xc3\xadpio",
                        to="contatos.Municipio",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("nome",),
                "verbose_name": "Casa Legislativa",
                "verbose_name_plural": "Casas Legislativas",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Funcionario",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "nome",
                    models.CharField(
                        max_length=60, verbose_name="nome completo"
                    ),
                ),
                (
                    "sexo",
                    models.CharField(
                        default="M",
                        max_length=1,
                        choices=[("M", "Masculino"), ("F", "Feminino")],
                    ),
                ),
                (
                    "nota",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "email",
                    models.CharField(
                        max_length=75, verbose_name="e-mail", blank=True
                    ),
                ),
                (
                    "cargo",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "funcao",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="fun\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "setor",
                    models.CharField(
                        default="outros",
                        max_length=100,
                        choices=[
                            ("presidente", "Presidente"),
                            ("contato_interlegis", "Contato Interlegis"),
                            (
                                "infraestrutura_fisica",
                                "Infraestrutura F\xc3\xadsica",
                            ),
                            ("estrutura_de_ti", "Estrutura de TI"),
                            (
                                "organizacao_do_processo_legislativo",
                                "Organiza\xc3\xa7\xc3\xa3o do Processo Legislativo",
                            ),
                            (
                                "producao_legislativa",
                                "Produ\xc3\xa7\xc3\xa3o Legislativa",
                            ),
                            (
                                "estrutura_de_comunicacao_social",
                                "Estrutura de Comunica\xc3\xa7\xc3\xa3o Social",
                            ),
                            (
                                "estrutura_de_recursos_humanos",
                                "Estrutura de Recursos Humanos",
                            ),
                            ("gestao", "Gest\xc3\xa3o"),
                            ("outros", "Outros"),
                        ],
                    ),
                ),
                (
                    "tempo_de_servico",
                    models.CharField(
                        max_length=50,
                        null=True,
                        verbose_name="tempo de servi\xe7o",
                        blank=True,
                    ),
                ),
                (
                    "ult_alteracao",
                    models.DateTimeField(
                        null=True,
                        verbose_name="\xdaltima altera\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "casa_legislativa",
                    models.ForeignKey(
                        to="casas.CasaLegislativa", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": ("nome",),
                "verbose_name": "contato da Casa Legislativa",
                "verbose_name_plural": "contatos da Casa Legislativa",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TipoCasaLegislativa",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("sigla", models.CharField(max_length=5)),
                ("nome", models.CharField(max_length=100)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="casalegislativa",
            name="tipo",
            field=models.ForeignKey(
                verbose_name="Tipo",
                to="casas.TipoCasaLegislativa",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="casalegislativa",
            unique_together=set([("municipio", "tipo")]),
        ),
        migrations.CreateModel(
            name="Presidente",
            fields=[],
            options={
                "proxy": True,
            },
            bases=("casas.funcionario",),
        ),
    ]
