# Generated by Django 4.1.2 on 2022-11-08 19:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("convenios", "0031_alter_projeto_modelo_minuta_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="gescon",
            name="palavras_excluir",
            field=models.TextField(
                default="DTCOM",
                help_text="Palavras que não podem aparecer no campo OBJETO dos dados do Gescon.<ul><li>Informe uma palavra por linha.</li><li>Ocorrendo qualquer uma das palavras, o contrato será ignorado.</li></ul>",
                verbose_name="palavras de exclusão",
            ),
        ),
    ]
