# coding= utf-8
import sys
import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from sigi.apps.servidores.models import Servidor, Servico, Subsecretaria
from sigi.apps.contatos.models import Municipio

#print 'removendo...'
#for u in User.objects.filter(date_joined__gte=datetime(2011, 12, 9, 10, 58, 49, 83734)).all():
#    u.servidor_set.all().delete()
#    u.delete()

print 'iniciando...'
class MigrationError(Exception):
    pass

class Command(BaseCommand):
    help = 'Migra usuários do antigo Sistema de RH'

    def handle(self, *args, **options):
        reader = csv.reader(open("/tmp/pessoal.csv"), delimiter=',', quotechar="\"")

        BRASILIA = Municipio.objects.get(codigo_ibge=5300108)

        # Read the column names from the first line of the file
        fields = reader.next()
        for row in reader:
            # cria um dict com a primeira e a linha atual
            pessoa = zip(fields, row)
            p = {}
            for (name, value) in pessoa:
                p[name] = value.strip()

            # buscar usuário e servidor da linha atual
            try:
                # procuro o usuario por email se for interlegis
                if not p['email'] or not ('@interlegis' in p['email']):
                    raise MigrationError
                user = User.objects.get(email__startswith=p['email'])
                servidor = user.servidor
            except (MigrationError, User.DoesNotExist):
                try:
                    # se nao encontrar procura por nome
                    if not p['nome_completo']:
                        raise MigrationError
                    servidor = Servidor.objects.get(nome_completo=p['nome_completo'])
                except (MigrationError, Servidor.DoesNotExist):
                    try:
                        # Cria um usuario tratando os casos incompletos
                        # fulano@interlegis.
                        if not '@' in p['email']:
                            raise MigrationError
                        username = p['email'].split('@')[0].lower()
                        if '@interlegis' in p['email']:
                            # pode ser um antigo usuario do ad
                            email = username + '@interlegis.gov.br'
                        else:
                            # cria um username a partir do email sem
                            # colidir com os usuarios ldap
                            username = username + '__'
                            email = ''
                        if not username or username == '__':
                            raise MigrationError
                        names = p['nome_completo'].split(' ')
                        first_name = names[0]
                        last_name = " ".join(names[1:])
                        user = User.objects.create(
                                username = username,
                                email = email,
                                first_name = first_name,
                                last_name = last_name,
                                is_active= False
                            )
                        servidor = user.servidor
                    except Exception, e:
                        print ", ".join(row)
                        continue

            # mapeando dados simples
            servidor.nome_completo = p['nome_completo']
            servidor.cpf = p['cpf']
            servidor.rg = p['identidade']
            servidor.apelido = p['username']
            servidor.matricula = p['matricula']
            servidor.ato_exoneracao = p['ato_exoneracao']
            servidor.ato_numero = p['ato_numero']
            servidor.ramal = p['ramal']

            if p['email'] and not '@interlegis' in p['email']:
                servidor.email_pessoal= p['email']

            if p['inativo']=="-1":
                servidor.user.is_active = False
            else:
                servidor.user.is_active = True
            servidor.user.save()

            if p['de_fora']=="-1":
                servidor.de_fora = True
            else:
                servidor.de_fora = False

            if p['sexo'].upper() == 'M':
                servidor.sexo = 'M'
            elif p['sexo'].upper() == 'F':
                servidor.sexo = 'F'

            if p['turno']=="1":
                servidor.turno = 'M'
            elif p['turno']=="2":
                servidor.turno = 'T'
            elif p['turno']=="3":
                servidor.turno = 'N'

            if p['aniversario']:
                servidor.data_nascimento = datetime.strptime(p['aniversario'], "%Y-%m-%d 00:00:00")

            if p['data_nomeacao']:
                servidor.data_nomeacao = datetime.strptime(p['data_nomeacao'], "%Y-%m-%d 00:00:00")

            if p['secretaria']:
                secretaria = Subsecretaria.objects.get_or_create(sigla=p['secretaria'])[0]
                servico = Servico.objects.get_or_create(sigla=(p['servico'] or 'desconhecido'))[0]
                servico.subsecretaria = secretaria
                servico.save()
                servidor.servico = servico

            if p['telefone']:
              try:
                t = servidor.telefones.get(numero=p['telefone'])
              except:
                t = servidor.telefones.create(numero=p['telefone'])
              t.tipo = 'F'
              t.save()

            if p['celular']:
              try:
                t = servidor.telefones.get(numero=p['celular'])
              except:
                t = servidor.telefones.create(numero=p['celular'])
              t.tipo = 'M'
              t.save()

            if p['endereco']:
              try:
                e = servidor.endereco.get(logradouro=p['endereco'])
              except:
                e = servidor.endereco.create(logradouro=p['endereco'])
              e.municipio = BRASILIA
              e.bairro = p['cidade'] # bizarro mas é isso mesmo
              e.cep = p['cep']
              e.save()

            servidor.apontamentos = p['apontamentos']
            servidor.obs = p['obs']
            servidor.save()

