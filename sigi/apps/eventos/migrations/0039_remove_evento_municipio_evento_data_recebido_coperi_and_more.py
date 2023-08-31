# Generated by Django 4.2.4 on 2023-08-31 20:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0038_migra_pedidos"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="evento",
            name="municipio",
        ),
        migrations.AddField(
            model_name="evento",
            name="data_recebido_coperi",
            field=models.DateField(
                blank=True,
                help_text="Data em que o pedido chegou na COPERI",
                null=True,
                verbose_name="data de recebimento na COPERI",
            ),
        ),
        migrations.AddField(
            model_name="solicitacao",
            name="data_recebido_coperi",
            field=models.DateField(
                blank=True,
                help_text="Data em que o pedido chegou na COPERI",
                null=True,
                verbose_name="data de recebimento na COPERI",
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="data_pedido",
            field=models.DateField(
                blank=True,
                help_text="Data em que o pedido foi realizado",
                null=True,
                verbose_name="Data do pedido",
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="solicitante",
            field=models.CharField(
                max_length=100, verbose_name="senador(a) solicitante"
            ),
        ),
        migrations.AlterField(
            model_name="itemsolicitado",
            name="tipo_evento",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="eventos.tipoevento",
            ),
        ),
        migrations.AlterField(
            model_name="solicitacao",
            name="data_pedido",
            field=models.DateField(
                help_text="Data em que o pedido foi realizado",
                verbose_name="Data do pedido",
            ),
        ),
        migrations.AlterField(
            model_name="solicitacao",
            name="senador",
            field=models.CharField(
                max_length=100, verbose_name="senador(a) solicitante"
            ),
        ),
    ]
