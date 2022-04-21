from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("contatos", "0002_auto_20151104_0810"),
        ("casas", "0007_auto_20201016_1632"),
    ]

    operations = [
        migrations.AddField(
            model_name="funcionario",
            name="bairro",
            field=models.CharField(
                max_length=100, verbose_name="Bairro", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="funcionario",
            name="cep",
            field=models.CharField(
                max_length=10, verbose_name="CEP", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="funcionario",
            name="endereco",
            field=models.CharField(
                max_length=100, verbose_name="Endere\xe7o", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="funcionario",
            name="municipio",
            field=models.ForeignKey(
                verbose_name="Municipio",
                to="contatos.Municipio",
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="funcionario",
            name="redes_sociais",
            field=models.TextField(
                help_text="Colocar um por linha",
                verbose_name="Redes sociais",
                blank=True,
            ),
            preserve_default=True,
        ),
    ]
