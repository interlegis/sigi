# Generated by Django 4.2.4 on 2023-09-25 12:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0045_alter_evento_banner"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipoevento",
            name="gerar_turma",
            field=models.BooleanField(
                default=True,
                help_text="Se o campo 'turma' for deixado em branco, o sistema deve gerar um número de turma automaticamente, com base no ano da data de início do evento?",
                verbose_name="Gerar turma",
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="turma",
            field=models.CharField(
                blank=True,
                help_text="Se deixado em branco e o evento tiver status CONFIRMADO e data de início definida, o número da turma será gerado automaticamente.",
                max_length=100,
                validators=[
                    django.core.validators.RegexValidator(
                        "^\\d{2}/\\d{4}$",
                        "Formato inválido. Utilize nn/aaaa, onde 'nn' são dígitos numéricos e 'aaaa' o ano com quatro dígitos.",
                    )
                ],
                verbose_name="turma",
            ),
        ),
    ]
