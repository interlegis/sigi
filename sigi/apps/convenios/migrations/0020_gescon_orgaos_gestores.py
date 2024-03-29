# Generated by Django 4.0.3 on 2022-04-20 13:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "convenios",
            "0019_alter_anexo_arquivo_alter_anexo_descricao_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="gescon",
            name="orgaos_gestores",
            field=models.TextField(
                default="SCCO",
                help_text="Siglas de órgãos gestores que devem aparecer no campoORGAOSGESTORESTITULARES<ul><li>Informe um sigla por linha.</li><li>Ocorrendo qualquer uma das siglas, o contrato será importado.</li></ul>",
                verbose_name="Órgãos gestores",
            ),
        ),
    ]
