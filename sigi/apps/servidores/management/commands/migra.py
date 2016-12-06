# coding= utf-8
import csv
import re
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from sigi.apps.contatos.models import Municipio
from sigi.apps.servidores.models import Servico, Servidor, Subsecretaria


# Funcao.objects.all().delete()
# Ferias.objects.all().delete()
# Licenca.objects.all().delete()
# for u in User.objects.filter(date_joined__gte=datetime(2011, 12, 9, 10, 58, 49, 83734)).all():
#    u.servidor_set.all().delete()
#    u.delete()


class MigrationError(Exception):
    pass


class Command(BaseCommand):
    help = _(u'Migra usuários do antigo Sistema de RH')

    def to_date(self, data):
        return datetime.strptime(data, "%Y-%m-%d 00:00:00")

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

            user = None
            if not p['email']:
                username = ''
                email = ''
            elif not ('@interlegis' in p['email']):
                username = p['email'].split('@')[0].strip().lower()
                email = ''
            else:
                username = p['email'].split('@')[0].strip().lower()
                email = username + '@interlegis.leg.br'

            # buscar usuário e servidor da linha atual
            try:
                # procuro o usuario por email do interlegis
                if email:
                    try:
                        user = User.objects.get(email=email)
                    except User.DoesNotExist:
                        email = username + '@interlegis.leg.br'
                        try:
                            user = User.objects.get(email=email)
                        except User.DoesNotExist:
                            pass

                if not user and username:
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        try:
                            user = User.objects.get(username=username + "__")
                        except User.DoesNotExist:
                            pass

                if not user:
                    if not username:
                        raise MigrationError

                    if not email:
                        # cria um username a partir do email sem
                        # colidir com os usuarios ldap
                        username = username + '__'

                    names = p['nome_completo'].split(' ')
                    first_name = names[0]
                    last_name = " ".join(names[1:])

                    user = User.objects.create(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name[:30],
                        is_active=False
                    )

                servidor = user.servidor
            except Servidor.DoesNotExist:
                servidor = Servidor.objects.create(
                    user=user,
                    nome_completo="%s %s" % (user.first_name, user.last_name)
                )
            except MigrationError as e:
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
                servidor.email_pessoal = p['email']

            if p['inativo'] == "-1":
                servidor.user.is_active = False
            else:
                servidor.user.is_active = True
            servidor.user.save()

            if p['de_fora'] == "-1":
                servidor.de_fora = True
            else:
                servidor.de_fora = False

            if p['sexo'].upper() == 'M':
                servidor.sexo = 'M'
            elif p['sexo'].upper() == 'F':
                servidor.sexo = 'F'

            if p['turno'] == "1":
                servidor.turno = 'M'
            elif p['turno'] == "2":
                servidor.turno = 'T'
            elif p['turno'] == "3":
                servidor.turno = 'N'

            if p['aniversario']:
                servidor.data_nascimento = self.to_date(p['aniversario'])

            if p['data_nomeacao']:
                servidor.data_nomeacao = self.to_date(p['data_nomeacao'])

            if p['secretaria_sigla']:
                if ' - ' in p['secretaria_nome']:
                    secretaria_nome = p['secretaria_nome'].split(' - ')[1]
                else:
                    secretaria_nome = p['secretaria_nome']

                secretaria = Subsecretaria.objects.get_or_create(
                    sigla=p['secretaria_sigla'],
                    nome=secretaria_nome
                )[0]

                if ' - ' in p['servico_nome']:
                    servico_nome = p['servico_nome'].split(' - ')[1]
                else:
                    servico_nome = p['servico_nome']

                servico = Servico.objects.get_or_create(
                    sigla=p['servico_sigla'],
                    nome=servico_nome
                )[0]

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
                e.bairro = p['cidade']  # bizarro mas é isso mesmo
                e.cep = re.sub("\D", "", p['cep'])
                e.save()

            servidor.apontamentos = p['apontamentos']
            servidor.obs = p['obs']

            if p['cargo'] or p['funcao']:
                funcao = servidor.funcao_set.get_or_create(
                    funcao=p['funcao'],
                    cargo=p['cargo'],
                )[0]

                if p['data_bap_entrada']:
                    funcao.data_bap_entrada = self.to_date(p['data_bap_entrada'])

                if p['data_bap_saida']:
                    funcao.data_bap_saida = self.to_date(p['data_bap_saida'])

                if p['data_entrada']:
                    funcao.inicio_funcao = self.to_date(p['data_entrada'])

                if p['data_saida']:
                    funcao.fim_funcao = self.to_date(p['data_saida'])

                funcao.bap_entrada = p['bap_entrada']
                funcao.bap_saida = p['bap_saida']
                funcao.save()

                if re.search(r'estagi.ri[o|a]', p['cargo'], re.I):  # XXX i18n
                    # TODO inserir dados de estagio
                    pass

            if p['inicio_ferias'] and p['final_ferias']:
                servidor.ferias_set.get_or_create(
                    inicio_ferias=self.to_date(p['inicio_ferias']),
                    fim_ferias=self.to_date(p['final_ferias']),
                    obs=p['obs_ferias']
                )

            if p['inicio_licenca'] and p['fim_licenca']:
                servidor.licenca_set.get_or_create(
                    inicio_licenca=self.to_date(p['inicio_licenca']),
                    fim_licenca=self.to_date(p['fim_licenca']),
                    obs=p['obs_licenca']
                )

            servidor.save()
