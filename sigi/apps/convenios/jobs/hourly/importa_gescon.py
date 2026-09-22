import re
import sys
from django.forms.models import model_to_dict
import requests
from appconfig import config
from hashlib import md5
from url_normalize import url_normalize
from django.db.models import Q, F
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django_extensions.management.jobs import HourlyJob
from sigi.apps.utils import mask_cnpj, to_ascii
from sigi.apps.casas.models import Orgao
from sigi.apps.convenios.models import Projeto, Convenio


class Job(HourlyJob):
    help = "Carga de dados do Gescon."

    gescon = None
    dominio = None
    subespecies = None
    todos_orgaos = None

    novos = 0
    erros = 0
    atualizados = 0

    def execute(self):
        print(
            "Importação iniciada em {timezone.localtime():%d/%m/%Y %H:%M:%S}\n"
            "==========================================================\n"
        )

        if not self.setup():
            return

        for sigla_gescon, sigla_sigi in self.subespecies:
            print(
                _("\n**Importando subespécie {sigla_gescon}**").format(
                    sigla_gescon=sigla_gescon
                )
            )
            try:
                projeto = Projeto.objects.get(sigla=sigla_sigi)
            except Projeto.DoesNotExist:
                print(
                    _(
                        "Projeto com a sigla {sigla_sigi} não existe no SIGI"
                    ).format(sigla_sigi=sigla_sigi),
                    file=sys.stderr,
                )
                continue
            except Projeto.MultipleObjectsReturned:
                print(
                    _(
                        "A sigla {sigla_sigi} foi cadastrada com duplicidade "
                        "no SIGI"
                    ).format(sigla_sigi=sigla_sigi),
                    file=sys.stderr,
                )
                continue

            nossos = self.get_contratos_gescon(sigla_gescon)
            if not nossos:
                print(
                    _(
                        "Nenhum contrato do tipo {sigla_gescon} pertence ao "
                        "ILB / Interlegis"
                    ).format(sigla_gescon=sigla_gescon)
                )
                continue

            # Desmarca erros de importações passadas
            Convenio.objects.filter(projeto=projeto).update(erro_gescon=False)

            for contrato in nossos:
                if contrato["numero"] is None:
                    print(
                        _(
                            "\t* O contrato de id {id} subespécie {sub} foi "
                            "cadastrado no Gescon sem número e não será "
                            "importado."
                        ).format(id=contrato["id"], sub=contrato["subEspecie"]),
                        file=sys.stderr,
                    )
                    continue
                numero = re.sub(
                    r"(\d{4})(\d{4})", r"\1/\2", contrato["numero"].zfill(8)
                )
                sigad = re.sub(
                    r"(\d{5})(\d{6})(\d{4})(\d{2})",
                    r"\1.\2/\3-\4",
                    contrato["processo"].zfill(17),
                )

                if contrato["cnpjCpfFornecedor"]:
                    cnpj = contrato["cnpjCpfFornecedor"].zfill(14)
                    cnpj_masked = mask_cnpj(cnpj)
                else:
                    cnpj = None
                    cnpj_masked = None

                if contrato["nomeFornecedor"]:
                    nome = to_ascii(
                        contrato["nomeFornecedor"]
                        .replace("VEREADORES DE", "")
                        .replace("DO ESTADO", "")
                        .split("-")[0]
                        .split("/")[0]
                        .strip()
                        .replace("  ", " ")
                    )
                else:
                    nome = None

                convenio = self.get_convenio(
                    contrato, projeto, sigad, numero, cnpj_masked
                )

                if convenio:
                    # Encontrou um único convênio, basta atualizar seus dados
                    self.update_convenio(
                        convenio, contrato, projeto, sigad, numero
                    )
                    self.update_orgao(convenio.casa_legislativa, cnpj_masked)
                else:
                    # Não encontrou o convênio. Um novo convênio precisa ser
                    # criado. Primeiro, é preciso identificar qual órgão
                    # consta no contrato do Gescon
                    orgao = self.get_orgao(
                        contrato, cnpj, cnpj_masked, nome, numero, sigad
                    )

                    if orgao is None:
                        # Não encontrou o órgão... bora reportar o erro
                        print(
                            _(
                                "\t* Órgão não encontrado no SIGI ou mais de "
                                "um órgão encontrado com o mesmo CNPJ ou nome. "
                                "Favor regularizar o cadastro: \n"
                                "\t * CNPJ: {cnpj}\n"
                                "\t * Nome: {nome}"
                            ).format(
                                cnpj=contrato["cnpjCpfFornecedor"],
                                nome=contrato["nomeFornecedor"],
                            ),
                            file=sys.stderr,
                        )
                        self.erros += 1
                    else:
                        # Bora criar o convênio
                        self.create_convenio(
                            orgao, contrato, projeto, sigad, numero
                        )
                        self.update_orgao(orgao, cnpj_masked)
                        self.novos += 1

        print("\n\nRESUMO DA IMPORTAÇÃO")
        print("--------------------\n\n")
        print(
            "Novos convenios adicionados ao SIGI: {novos}".format(
                novos=self.novos
            )
        )
        print(
            "Convênios atualizados..............: {atualizados}".format(
                atualizados=self.atualizados
            )
        )
        print(
            "Erros encontrados..................: {erros}".format(
                erros=self.erros
            )
        )

    def setup(self):
        self.novos = 0
        self.erros = 0
        self.atualizados = 0

        self.gescon = config.convenios
        self.gescon.ultima_importacao = None
        if self.gescon.checksums is None:
            self.gescon.checksums = {}

        self.dominio = get_current_site(None).domain

        if self.gescon.palavras == "":
            print(
                _("Nenhuma palavra de pesquisa definida - processo abortado."),
                file=sys.stderr,
            )
            return False

        if self.gescon.orgaos_gestores == "":
            print(
                _("Nenhum órgão gestor definido - processo abortado"),
                file=sys.stderr,
            )
            return False

        if self.gescon.subespecies == "":
            print(
                _("Nenhuma subespécie definida - processo abortado."),
                file=sys.stderr,
            )
            return False

        if "{s}" not in self.gescon.url_gescon:
            print(
                _(
                    "Falta a marcação {s} na URL para indicar o local onde "
                    "inserir a sigla da subespécia na consulta ao webservice "
                    "- processo abortado."
                ),
                file=sys.stderr,
            )
            return False

        self.subespecies = {
            tuple(s.split("=")) for s in self.gescon.subespecies.split()
        }
        self.todos_orgaos = [
            (o, f"{to_ascii(o.nome)} - {o.uf_sigla}".lower())
            for o in Orgao.objects.all()
            .order_by()
            .annotate(uf_sigla=F("municipio__uf__sigla"))
        ]

        self.palavras = self.gescon.palavras.splitlines()
        self.orgaos = self.gescon.orgaos_gestores.splitlines()
        self.excludentes = self.gescon.palavras_excluir.splitlines()

        return True

    def get_contratos_gescon(self, sigla_gescon):
        requests.packages.urllib3.disable_warnings()

        url = self.gescon.url_gescon.format(s=sigla_gescon)

        try:
            response = requests.get(url, verify=False)
        except Exception as e:
            print(
                _("\tErro ao acessar {url}: {message}").format(
                    url=url, message=e.message
                ),
                file=sys.stderr,
            )
            return None

        if response.status_code != 200:
            print(
                _(
                    "\tErro na leitura dos dados de {url}: "
                    "[{status_code}] {reason}"
                ).format(
                    url=url,
                    status_code=response.status_code,
                    reason=response.reason,
                ),
                file=sys.stderr,
            )
            return None

        if "application/json" not in response.headers.get("Content-Type", ""):
            print(
                _(
                    "\tResultado da consulta à {url} não retornou dados "
                    "em formato json: {content_type}"
                ).format(
                    url=url,
                    content_type=response.headers.get("Content-Type", ""),
                ),
                file=sys.stderr,
            )
            return None

        md5sum = md5(response.text.encode(response.encoding)).hexdigest()
        if (
            sigla_gescon in self.gescon.checksums
            and self.gescon.checksums[sigla_gescon] == md5sum
        ):
            print(
                _(
                    "\tDados da subespécie {sigla_gescon} inalterados no "
                    "Gescon. Processamento desnecessário."
                ).format(sigla_gescon=sigla_gescon)
            )
            return None
        self.gescon.checksums[sigla_gescon] = md5sum

        contratos = response.json()

        # Pegar só os contratos que possuem alguma das palavras-chave
        nossos = [
            c
            for c in contratos
            if (
                any(palavra in c["objeto"] for palavra in self.palavras)
                or any(
                    orgao in c["orgaosGestoresTitulares"]
                    for orgao in self.orgaos
                    if c["orgaosGestoresTitulares"] is not None
                )
            )
            and not any(palavra in c["objeto"] for palavra in self.excludentes)
        ]

        print(
            _("\t{qty} contratos encontrados no Gescon").format(qty=len(nossos))
        )

        return nossos

    def get_convenio(self, contrato, projeto, sigad, numero, cnpj_masked):
        # Buscar o convenio pelo ID do Gescon
        try:
            convenio = Convenio.objects.get(id_gescon=contrato["id"])
            return convenio
        except Convenio.DoesNotExist:
            # Não existe, mas vamos buscar com outras chaves candidatas
            pass

        # Buscar o Convenio pelo NUP #
        convenios = Convenio.objects.filter(
            projeto=projeto, num_processo_sf=sigad
        )
        num_convenios = convenios.count()
        if num_convenios == 0:
            # Nenhum convênio. Vamos continuar buscando em todos convenios
            # desse tipo de projeto
            convenios = Convenio.objects.filter(projeto=projeto)
        elif num_convenios == 1:
            # Encontrou um único, então deve ser ele
            return convenios.get()

        # Se chegou aqui, é porque encontrou vários ou nenhum.
        # Vamos tentar diferenciar pelas outras chaves candidatas

        convenios = convenios.filter(
            Q(Q(num_convenio=numero) | Q(num_processo_sf=numero))
        )
        num_convenios = convenios.count()

        if num_convenios == 0:
            # Nenhum encontrado. Já finaliza como não encontrado
            return None
        elif num_convenios == 1:
            # Achou um. Deve ser ele
            return convenios.get()

        # Encontrou N: Marcamos todos como erro e reportamos
        urls = []
        for c in convenios:
            uri = reverse("admin:convenios_convenio_change", args=[c.id])
            url = url_normalize(f"{self.dominio}{uri}")
            urls.append(f'<a href="{url}">{c.id}</a>')
        urls = ", ".join(urls)
        convenios.update(
            erro_gescon=True,
            observacao_gescon=_(
                "Este convênio possui o mesmo número dos convenios {urls}"
            ).format(urls=urls),
        )
        print(
            _(
                "\t* O contrato {numero} no Gescon pode "
                "ser relacionado aos seguintes convênios "
                "do SIGI: {urls}"
            ).format(numero=numero, urls=urls),
            file=sys.stderr,
        )
        self.erros += 1

        # Porém, talvez seja possível ser desambiguado pelo CNPJ do
        # fornecedor
        if cnpj_masked is not None:
            convenios = convenios.filter(casa_legislativa__cnpj=cnpj_masked)
        if convenios.count() == 1:
            # Achou exatamente o único que deveria existir.
            return convenios.get()
        # Continua ambíguo. Não dá pra fazer nada.
        return None

    def get_orgao(self, contrato, cnpj, cnpj_masked, nome, numero, sigad):
        if (cnpj is None) and (nome is None):
            print(
                _(
                    "\t* O contrato {numero} no Gescon não informa nem o CNPJ "
                    "nem o nome do órgão, então não é possível importar "
                    "para o SIGI."
                ).format(numero=numero),
                file=sys.stderr,
            )
            self.erros += 1
            return None
        # Vamos tentar primeiro com o CNPJ
        if cnpj is not None:
            try:
                orgao = Orgao.objects.get(cnpj=cnpj_masked)
                return orgao
            except Orgao.MultipleObjectsReturned:
                # Pode acontecer de uma câmara usar o mesmo CNPJ da prefeitura,
                # e ambos terem convênio com o ILB. Podemos tentar desambiguar
                # pelo nome mais semelhante.
                orgaos = Orgao.get_semelhantes(
                    to_ascii(contrato["nomeFornecedor"]).lower(),
                    [
                        (
                            o,
                            f"{to_ascii(o.nome)} - {o.uf_sigla}".lower(),
                        )
                        for o in Orgao.objects.filter(cnpj=cnpj_masked)
                        .order_by()
                        .annotate(uf_sigla=F("municipio__uf__sigla"))
                    ],
                    min_ratio=0,
                )
                if orgaos:
                    # Retorna o mais semelhante
                    return orgaos[0][0]
            except Orgao.DoesNotExist:
                # Não encontrou nenhum. Vamos seguir sem órgao e tentar
                # encontrar pelo nome logo abaixo
                pass
        # Não achou pelo CNPJ. Bora ver se acha por similaridade do nome
        if nome is None:
            # Também não tem nome... então temos que reportar erro
            print(
                _(
                    "\t* O contrato {numero} no Gescon com NUP sigad {sigad}, "
                    "fornecedor {cnpj_masked} não pode ser imortado porque "
                    "não é possível identificar o órgão no SIGI. Cadastre um "
                    "órgão com o CNPJ desse fornecedor, que na próxima "
                    "importação este contrato será importado."
                ).format(numero=numero, sigad=sigad, cnpj_masked=cnpj_masked),
                file=sys.stderr,
            )
            self.erros += 1
            return None
        # Tentar primeiro com o nome igual veio do GESCON
        semelhantes = Orgao.get_semelhantes(
            to_ascii(contrato["nomeFornecedor"]).lower(),
            self.todos_orgaos,
        )
        if not semelhantes:
            # Não achou, então vamos tentar com o nome limpado
            semelhantes = Orgao.get_semelhantes(
                to_ascii(nome).lower(),
                self.todos_orgaos,
            )
        if len(semelhantes) > 0:
            # Encontrou algo semelhante.... bora usar.
            return semelhantes[0][0]
        # Não encontrou nada parecido. Bora reportar como erro
        print(
            _(
                "\t* O contrato {numero} no Gescon com NUP Sigad {sigad}, "
                "indica o fornecedor com CNPJ {cnpj_masked} e com o nome "
                "{nome}, que não tem correspondência no SIGI. Este convênio "
                "precisa ser cadastrado manualmente no SIGI para este erro "
                "parar de acontecer."
            ).format(
                numero=numero,
                sigad=sigad,
                cnpj_masked=cnpj_masked,
                nome=contrato["nomeFornecedor"],
            ),
            file=sys.stderr,
        )
        self.erros += 1
        return None

    def update_convenio(self, convenio, contrato, projeto, sigad, numero):
        antes = model_to_dict(convenio)
        convenio.projeto = projeto
        convenio.num_processo_sf = sigad
        convenio.num_convenio = numero
        convenio.data_sigad = contrato["assinatura"]
        convenio.observacao = contrato["objeto"]
        convenio.data_retorno_assinatura = contrato["inicioVigencia"]
        convenio.data_termino_vigencia = contrato["terminoVigencia"]
        convenio.data_pub_diario = contrato["publicacao"]
        convenio.atualizacao_gescon = timezone.localtime()
        convenio.erro_gescon = False
        convenio.observacao_gescon = ""
        convenio.id_contrato_gescon = contrato["codTextoContrato"] or ""
        convenio.id_gescon = contrato["id"]
        if antes != model_to_dict(convenio):
            convenio.save()
            self.atualizados += 1

    def create_convenio(self, orgao, contrato, projeto, sigad, numero):
        convenio = Convenio(
            casa_legislativa=orgao,
            projeto=projeto,
            num_processo_sf=sigad,
            num_convenio=numero,
            data_sigi=timezone.localdate(),
            data_sigad=contrato["assinatura"],
            observacao=contrato["objeto"],
            data_retorno_assinatura=contrato["inicioVigencia"],
            data_termino_vigencia=contrato["terminoVigencia"],
            data_pub_diario=contrato["publicacao"],
            atualizacao_gescon=timezone.localtime(),
            observacao_gescon=_("Importado integralmente do Gescon"),
            id_contrato_gescon=(contrato["codTextoContrato"] or ""),
            id_gescon=contrato["id"],
        )
        convenio.save()

    def update_orgao(self, orgao, cnpj_masked):
        # Corrigir o CNPJ do órgão se estiver diferente do
        # Gescon. O gescon é um pouquinho mais confiável,
        # por enquanto.
        if cnpj_masked and orgao.cnpj != cnpj_masked:
            orgao.cnpj = cnpj_masked
            orgao.save()
