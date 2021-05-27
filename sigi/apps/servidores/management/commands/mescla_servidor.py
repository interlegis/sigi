# coding: utf-8
from django.contrib.auth.models import User, Group
from sigi.apps.servidores.models import Servidor
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = u'Transfere os dados do servidor OLD para o servidor NEW.'
    args = u'old_id new_id'

    def handle(self, *args, **options):
        if len(args) != 2:
            self.stderr.write(u"Informe old_id e new_id")
            return

        old_id = args[0]
        new_id = args[1]

        old = Servidor.objects.get(id=old_id)
        new = Servidor.objects.get(id=new_id)

        self.stdout.write(self.style.WARNING(
            u"Transferir dados de {old_name} para {new_name}".format(
                old_name=old.nome_completo,
                new_name=new.nome_completo
            )
        ))

        self.stdout.write(u"\t* Transferindo a carteira de atendimento...")
        for casa in old.casas_que_gerencia.all():
            new.casas_que_gerencia.add(casa)
            old.casas_que_gerencia.remove(casa)

        self.stdout.write(u"\t* Transferindo ocorrências registradas...")
        old.ocorrencia_set.all().update(servidor_registro=new)

        self.stdout.write(u"\t* Transferindo comentários de ocorrências...")
        old.comentario_set.all().update(usuario=new)

        self.stdout.write(u"\t* Transferindo convênios geridos...")
        old.convenio_set.all().update(servidor_gestao=new)

        self.stdout.write(u"\t* Transferindo convênios acompanhados...")
        old.convenio_set.all().update(acompanha=new)

        self.stdout.write(u"\t* Transferindo participação em eventos...")
        old.equipe_evento.all().update(membro=new)

        self.stdout.write(u"\t* Transferindo convites para eventos...")
        old.convite_set.all().update(servidor=new)

        self.stdout.write(u"\t* Transferindo diagnósticos...")
        old.diagnostico_set.all().update(responsavel=new)

        self.stdout.write(u"\t* Transferindo participação em diagnósticos...")
        old.equipe_set.all().update(membro=new)

        self.stdout.write(u"\t* Transferindo dados de autenticação...")

        if new.user:
            old.user.logentry_set.all().update(user=new)
            old.user.delete()
        else:
            new.user = old.user
            new.save()
            old.user = None
            old.save()

        self.stdout.write(u"Concluído!")