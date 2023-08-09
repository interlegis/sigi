from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("convenios", "0013_remove_convenio_duracao"),
    ]

    operations = [
        migrations.CreateModel(
            name="Gescon",
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
                    "url_gescon",
                    models.URLField(
                        default="https://adm.senado.gov.br/gestao-contratos/api/contratos/busca?especie={s}",
                        help_text="Informe o ponto de consulta do webservice do Gescon, inclusive com a querystring. No ponto onde deve ser inserida a sigla da subespecie do contrato, use a marca\xe7\xe3o {s}.<br/><strong>Por exemplo:</strong> https://adm.senado.gov.br/gestao-contratos/api/contratos/busca?especie=<strong>{s}</strong>",
                        verbose_name="Webservice Gescon",
                    ),
                ),
                (
                    "subespecies",
                    models.TextField(
                        default="AC=ACT\nPI=PI\nCN=PML\nTA=PML",
                        help_text="Informe as siglas das subesp\xe9cies de contratos que devem ser pesquisados no Gescon com a sigla correspondente do projeto no SIGI. Coloque um par de siglas por linha, no formato SIGLA_GESTON=SIGLA_SIGI. As siglas n\xe3o encontradas ser\xe3o ignoradas.",
                        verbose_name="Subesp\xe9cies",
                    ),
                ),
                (
                    "palavras",
                    models.TextField(
                        default="ILB\nINTERLEGIS",
                        help_text="Palavras que devem aparecer no campo OBJETO dos dados do Gescon para identificar se o contrato pertence ao ILB. <ul><li>Informe uma palavra por linha.</li><li>Ocorrendo qualquer uma das palavras, o contrato ser\xe1 importado.</li></ul>",
                        verbose_name="Palavras de filtro",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Caixa de e-mail para onde o relat\xf3rio di\xe1rio de importa\xe7\xe3o ser\xe1 enviado.",
                        max_length=75,
                        verbose_name="E-mail",
                    ),
                ),
                (
                    "ultima_importacao",
                    models.TextField(
                        verbose_name="Resultado da \xfaltima importa\xe7\xe3o",
                        blank=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Configura\xe7\xe3o do Gescon",
                "verbose_name_plural": "Configura\xe7\xf5es do Gescon",
            },
            bases=(models.Model,),
        ),
    ]
