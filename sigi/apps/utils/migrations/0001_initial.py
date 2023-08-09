# Generated by Django 4.0.6 on 2022-07-12 20:41

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SigiAlert",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "caminho",
                    models.CharField(
                        max_length=200, verbose_name="caminho da tela"
                    ),
                ),
                (
                    "destinatarios",
                    models.CharField(
                        choices=[
                            ("A", "Todo e qualquer usuário"),
                            ("N", "Usuários anônimos / não autenticados"),
                            ("S", "Membros da equipe Interlegis"),
                            ("D", "Administradores do sistema"),
                        ],
                        max_length=1,
                        verbose_name="destinatários",
                    ),
                ),
                (
                    "titulo",
                    models.CharField(max_length=60, verbose_name="título"),
                ),
                (
                    "mensagem",
                    tinymce.models.HTMLField(verbose_name="mensagem"),
                ),
            ],
            options={
                "verbose_name": "alerta SIGI",
                "verbose_name_plural": "alertas SIGI",
                "ordering": ("caminho", "destinatarios"),
            },
        ),
    ]
