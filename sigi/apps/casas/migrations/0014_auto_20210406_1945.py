from __future__ import unicode_literals

from django.db import models, migrations
import sigi.apps.utils


class Migration(migrations.Migration):

    dependencies = [
        ("contatos", "0002_auto_20151104_0810"),
        ("servidores", "0001_initial"),
        ("servicos", "0004_delete_casaatendida"),
        ("inventario", "0001_initial"),
        ("convenios", "0002_convenio_duracao"),
        ("ocorrencias", "0002_auto_20160308_0828"),
        ("eventos", "0004_remove_evento_curso_moodle_id"),
        ("casas", "0013_auto_20210406_1428"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="CasaLegislativa",
            new_name="Orgao",
        ),
    ]
