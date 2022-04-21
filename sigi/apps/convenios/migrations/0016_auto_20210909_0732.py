from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("convenios", "0015_remove_convenio_search_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="convenio",
            name="atualizacao_gescon",
            field=models.DateTimeField(
                null=True,
                verbose_name="Data de atualiza\xe7\xe3o pelo Gescon",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="convenio",
            name="observacao_gescon",
            field=models.TextField(
                verbose_name="Observa\xe7\xf5es da atualiza\xe7\xe3o do Gescon",
                blank=True,
            ),
            preserve_default=True,
        ),
    ]
