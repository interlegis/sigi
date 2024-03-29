# Generated by Django 4.2.4 on 2023-09-19 11:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0043_alter_solicitacao_estimativa_casas_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="chave_inscricao",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="chave de inscrição"
            ),
        ),
        migrations.AddField(
            model_name="evento",
            name="contato_inscricao",
            field=models.CharField(
                blank=True,
                help_text="pessoa ou setor responsável por dar suporte aos alunos no processo de inscrição",
                max_length=100,
                verbose_name="contato para inscrição",
            ),
        ),
        migrations.AddField(
            model_name="evento",
            name="observacao_inscricao",
            field=models.TextField(
                blank=True,
                help_text="Mais detalhes para ajudar o aluno a se inscrever no curso",
                verbose_name="Observações para inscrição",
            ),
        ),
        migrations.AddField(
            model_name="evento",
            name="perfil_aluno",
            field=models.URLField(
                blank=True,
                help_text="Link completo da página de perfil do aluno deste curso no Saberes",
                verbose_name="Link do perfil do aluno",
            ),
        ),
        migrations.AddField(
            model_name="evento",
            name="telefone_inscricao",
            field=models.CharField(
                blank=True,
                help_text="telefone da pessoa ou setor responsável por dar suporte aos alunos no processo de inscrição",
                max_length=30,
                verbose_name="telefone do contato",
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="contato",
            field=models.CharField(
                blank=True,
                help_text="pessoa de contato na casa anfitriã",
                max_length=100,
                verbose_name="contato",
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="telefone",
            field=models.CharField(
                blank=True,
                help_text="telefone da pessoa de contato na casa anfitriã",
                max_length=30,
                verbose_name="tefone de contato",
            ),
        ),
    ]
