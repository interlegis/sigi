# Generated by Django 4.0.6 on 2022-07-16 02:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0022_alter_anexo_data_pub"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cronograma",
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
                    "etapa",
                    models.CharField(
                        max_length=10, verbose_name="sigla da etapa"
                    ),
                ),
                (
                    "nome",
                    models.CharField(
                        max_length=100, verbose_name="nome da etapa"
                    ),
                ),
                (
                    "descricao",
                    models.TextField(
                        help_text="Descrição detalhada das atividades realizadas na etapa",
                        verbose_name="descrição da etapa",
                    ),
                ),
                (
                    "duracao",
                    models.PositiveBigIntegerField(
                        verbose_name="duração (em dias)"
                    ),
                ),
                (
                    "data_prevista_inicio",
                    models.DateField(
                        blank=True,
                        null=True,
                        verbose_name="data prevista de início",
                    ),
                ),
                (
                    "data_prevista_termino",
                    models.DateField(
                        blank=True,
                        null=True,
                        verbose_name="data prevista de término",
                    ),
                ),
                (
                    "data_inicio",
                    models.DateField(
                        blank=True, null=True, verbose_name="data de início"
                    ),
                ),
                (
                    "data_termino",
                    models.DateField(
                        blank=True, null=True, verbose_name="data de término"
                    ),
                ),
                (
                    "dependencia",
                    models.CharField(
                        blank=True,
                        help_text="Sigla da etapa que precisa ser concluída para que esta seja iniciada",
                        max_length=200,
                        verbose_name="depende da etapa",
                    ),
                ),
                (
                    "responsaveis",
                    models.TextField(
                        blank=True,
                        help_text="Pessoas, setores, órgãos.",
                        verbose_name="responsáveis pela tarefa",
                    ),
                ),
                (
                    "comunicar_inicio",
                    models.TextField(
                        blank=True,
                        help_text="Lista de pessoas/órgãos para comunicar quando a tarefa for iniciada. Coloque um por linha.",
                        verbose_name="comunicar inicio para",
                    ),
                ),
                (
                    "comunicar_termino",
                    models.TextField(
                        blank=True,
                        help_text="Lista de pessoas/órgãos para comunicar quando a tarefa for concluída. Coloque um por linha.",
                        verbose_name="comunicar término para",
                    ),
                ),
                (
                    "recursos",
                    models.TextField(
                        help_text="Lista de recursos necessários para desenvolver a tarefa",
                        verbose_name="recursos necessários",
                    ),
                ),
                (
                    "evento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eventos.evento",
                    ),
                ),
            ],
            options={
                "verbose_name": "cronograma",
                "verbose_name_plural": "cronogramas",
            },
        ),
        migrations.CreateModel(
            name="Checklist",
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
                    "etapa",
                    models.CharField(
                        max_length=10, verbose_name="sigla da etapa"
                    ),
                ),
                (
                    "nome",
                    models.CharField(
                        max_length=100, verbose_name="nome da etapa"
                    ),
                ),
                (
                    "descricao",
                    models.TextField(
                        help_text="Descrição detalhada das atividades realizadas na etapa",
                        verbose_name="descrição da etapa",
                    ),
                ),
                (
                    "duracao",
                    models.PositiveBigIntegerField(
                        verbose_name="duração (em dias)"
                    ),
                ),
                (
                    "dependencia",
                    models.CharField(
                        blank=True,
                        help_text="Siglas das etapas que precisam ser concluídas para que esta seja iniciada. Separe cada uma com um espaço.",
                        max_length=200,
                        verbose_name="depende da etapa",
                    ),
                ),
                (
                    "responsaveis",
                    models.TextField(
                        blank=True,
                        help_text="Pessoas, setores, órgãos.",
                        verbose_name="responsáveis pela tarefa",
                    ),
                ),
                (
                    "comunicar_inicio",
                    models.TextField(
                        blank=True,
                        help_text="Lista de e-mails para comunicar quando a tarefa for iniciada",
                        verbose_name="comunicar inicio para",
                    ),
                ),
                (
                    "comunicar_termino",
                    models.TextField(
                        blank=True,
                        help_text="Lista de e-mails para comunicar quando a tarefa for concluída",
                        verbose_name="comunicar término para",
                    ),
                ),
                (
                    "recursos",
                    models.TextField(
                        help_text="Lista de recursos necessários para desenvolver a tarefa",
                        verbose_name="recursos necessários",
                    ),
                ),
                (
                    "tipo_evento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eventos.tipoevento",
                    ),
                ),
            ],
            options={
                "verbose_name": "checklist",
                "verbose_name_plural": "checklists",
            },
        ),
    ]
