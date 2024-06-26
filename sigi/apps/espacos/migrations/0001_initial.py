# Generated by Django 4.2.4 on 2023-11-08 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("eventos", "0053_visita_anfitria_senado_oficina_remove_convite")
    ]

    operations = [
        migrations.CreateModel(
            name="Espaco",
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
                    "nome",
                    models.CharField(max_length=100, verbose_name="nome"),
                ),
                (
                    "sigla",
                    models.CharField(max_length=20, verbose_name="sigla"),
                ),
                (
                    "descricao",
                    models.TextField(blank=True, verbose_name="descrição"),
                ),
                (
                    "local",
                    models.CharField(
                        help_text="Indique o prédio/bloco/sala onde este espaço está localizado.",
                        max_length=100,
                        verbose_name="local",
                    ),
                ),
            ],
            options={
                "verbose_name": "espaço",
                "verbose_name_plural": "espaços",
                "ordering": ("nome",),
            },
        ),
        migrations.CreateModel(
            name="Recurso",
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
                    "nome",
                    models.CharField(max_length=100, verbose_name="nome"),
                ),
                (
                    "sigla",
                    models.CharField(max_length=20, verbose_name="sigla"),
                ),
                (
                    "descricao",
                    models.TextField(blank=True, verbose_name="descrição"),
                ),
            ],
            options={
                "verbose_name": "recurso",
                "verbose_name_plural": "recursos",
                "ordering": ("nome",),
            },
        ),
        migrations.CreateModel(
            name="Reserva",
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
                    "status",
                    models.CharField(
                        choices=[("A", "Ativo"), ("C", "Cancelado")],
                        default="A",
                        editable=False,
                        max_length=1,
                        verbose_name="Status",
                    ),
                ),
                (
                    "proposito",
                    models.CharField(
                        help_text="Indique o propósito da reserva (nome do evento, indicativo da reunião, aula, apresentação, etc.)",
                        max_length=100,
                        verbose_name="propósito",
                    ),
                ),
                (
                    "inicio",
                    models.DateTimeField(verbose_name="Data/hora de início"),
                ),
                (
                    "termino",
                    models.DateTimeField(verbose_name="Data/hora de término"),
                ),
                (
                    "informacoes",
                    models.TextField(
                        blank=True,
                        help_text="Utilize para anotar informações adicionais e demais detalhes sobre a reserva",
                        verbose_name="informações adicionais",
                    ),
                ),
                (
                    "solicitante",
                    models.CharField(
                        help_text="indique o nome da pessoa ou setor solicitante da reserva",
                        max_length=100,
                        verbose_name="solicitante",
                    ),
                ),
                (
                    "contato",
                    models.CharField(
                        blank=True,
                        help_text="Indique o nome da(s) pessoa(s) de contato para tratar assuntos da reserva.",
                        max_length=100,
                        verbose_name="pessoa de contato",
                    ),
                ),
                (
                    "telefone_contato",
                    models.CharField(
                        blank=True,
                        help_text="Indique o telefone/ramal da pessoa responsável pela reserva.",
                        max_length=100,
                        verbose_name="telefone de contato",
                    ),
                ),
                (
                    "espaco",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="espacos.espaco",
                        verbose_name="espaço",
                    ),
                ),
            ],
            options={
                "verbose_name": "reserva",
                "verbose_name_plural": "reservas",
                "ordering": ("inicio", "espaco", "proposito"),
            },
        ),
        migrations.CreateModel(
            name="RecursoSolicitado",
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
                    "quantidade",
                    models.FloatField(default=0.0, verbose_name="quantidade"),
                ),
                (
                    "observacoes",
                    models.TextField(blank=True, verbose_name="observações"),
                ),
                (
                    "recurso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="espacos.recurso",
                        verbose_name="recurso",
                    ),
                ),
                (
                    "reserva",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="espacos.reserva",
                        verbose_name="reserva",
                    ),
                ),
            ],
            options={
                "verbose_name": "recurso solicitado",
                "verbose_name_plural": "recursos solicitados",
                "ordering": ("recurso",),
            },
        ),
    ]
