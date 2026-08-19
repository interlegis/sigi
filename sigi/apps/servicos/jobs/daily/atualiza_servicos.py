from datetime import datetime
import requests
import sys
from django.conf import settings
from django.utils import timezone
from django.utils.formats import localize
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from url_normalize import url_normalize
from sigi.apps.servicos import generate_instance_name, nomeia_instancias
from sigi.apps.servicos.exceptions import MultipleServicesReturned
from sigi.apps.servicos.models import Servico, LogServico, TipoServico
from sigi.apps.casas.models import Orgao, TipoOrgao
from sigi.apps.utils import to_ascii
from sigi.apps.utils.management.jobs import AdminJobMixin


class Job(AdminJobMixin, DailyJob):
    help = _("Sincronização dos Serviços SEIT na infraestrutura")

    UPDATE_NOTHING = None
    UPDATE_DEACTIVATED = 0
    UPDATE_UPDATED = 1

    UPDATABLE_FIELDS = (
        ("url", "url"),
        ("versao", "version"),
    )

    nomes_gerados = None
    dados = None

    counter = 0
    erros = 0
    updates = 0
    desativados = 0
    novos = 0

    def __init__(self):
        super().__init__()
        self.nomes_gerados = {
            generate_instance_name(o): o
            for o in Orgao.objects.filter(tipo__legislativo=True)
        }

    def execute(self):
        if not self._retrieve_json_data():
            print(_("Processo abortado!"), file=sys.stderr)
            return

        hospedagens_ativas = Servico.objects.filter(
            tipo_servico__modo=TipoServico.MODO_HOSPEDAGEM,
            data_desativacao=None,
        ).exclude(tipo_servico__tipo_rancher="")

        nomeia_instancias(
            servicos=hospedagens_ativas.filter(instancia=""),
            user=self.get_sys_user(),
        )

        hospedagens_ativas.update(flag_confirmado=False)

        total = len(self.dados)
        self.erros = 0
        self.updates = 0
        self.desativados = 0
        self.novos = 0

        print(
            "\n\n",
            _("Processando {total} registros recebidos").format(total=total),
            "\n\n",
        )

        for rec in self.get_dados():
            tipo_servico = self.get_tipo_servico(rec)
            if not tipo_servico:
                self.erros += 1
                continue

            try:
                servico = self.get_servico(tipo_servico, rec)
            except MultipleServicesReturned as e:
                print("* ", str(e), file=sys.stderr)
                self.erros += 1
                continue

            if servico:
                self.atualiza_servico(servico, rec)
                continue

            # Tenta criar o serviço
            orgao = self.get_orgao(rec)
            if not orgao:
                self.erros += 1
                continue

            self.cria_servico(rec, tipo_servico, orgao)
            self.novos += 1

        # Desativar todos que não foram confirmados
        nao_confirmados = hospedagens_ativas.filter(flag_confirmado=False)
        self.desativados += self.bulk_desativa(nao_confirmados)

        print("\n\n", _("TOTAIS"))
        print("------", "\n\n")
        print("  * registros recebidos do webservice: ", total)
        print("  * registros com erro...............: ", self.erros)
        print("  * atualizações realizadas..........: ", self.updates)
        print("  * serviços desativados.............: ", self.desativados)
        print("  * novos serviços criados...........: ", self.novos)

    def _retrieve_json_data(self):
        if (not hasattr(settings, "HOSPEDAGEM_PATH")) or (
            not settings.HOSPEDAGEM_PATH
        ):
            print(
                _(
                    "Falta a configuração da URL de acesso aos serviços "
                    "instalados"
                ),
                file=sys.stderr,
            )
            return False

        print(
            _("Buscando dados no webservice {wsentry}...").format(
                wsentry=settings.HOSPEDAGEM_PATH
            ),
        )
        try:
            response = requests.get(settings.HOSPEDAGEM_PATH)
        except Exception as e:
            print(
                _("Ocorreu um erro ao acessar {url}: {error}").format(
                    url=settings.HOSPEDAGEM_PATH,
                    error=str(e),
                ),
                file=sys.stderr,
            )
            return False

        if response.status_code != 200:
            print(
                _(
                    "Problemas na resposta do webservice de serviços: "
                    "{code} - {reason}"
                ).format(code=response.status_code, reason=response.reason),
                file=sys.stderr,
            )
            return False

        if not "json" in response.headers["content-type"]:
            print(
                _("Tipo de conteúdo não é JSON: {contenttype}").format(
                    contenttype=response.headers["content-type"]
                ),
                file=sys.stderr,
            )
            return False

        result = response.json()

        if result["tipo"] != "SERVICES":
            print(
                _("Tipo de resultado inesperado: {tipo}").format(
                    tipo=result["tipo"]
                ),
                file=sys.stderr,
            )
            return False

        if result["status"] != "ok":
            print(
                _(
                    "O webservice respondeu com status {status}: logs: {logs}"
                ).format(status=result["status"], logs=result["logs"]),
                file=sys.stderr,
            )
            return False

        self.dados = result["result"]["servicos"]

        return True

    def get_dados(self):
        if self.dados is None:
            if not self._retrieve_json_data():
                return

        self.counter = 0

        for r in self.dados:
            self.counter += 1
            record = r.copy()

            record["url"] = url_normalize(record["url"])

            record["creationDate"] = (
                datetime.strptime(record["creationDate"], "%d/%m/%Y").date()
                if "creationDate" in record and record["creationDate"] != ""
                else None
            )
            record["suspendedDate"] = (
                datetime.strptime(record["suspendedDate"], "%d/%m/%Y").date()
                if "suspendedDate" in record and record["suspendedDate"] != ""
                else None
            )

            yield record

    def get_tipo_servico(self, rec):
        # Verificar se existe sub-serviço
        if rec["namespace"].count("-") > 1:
            subservico = rec["namespace"].split("-")[0]
            try:
                tipo_servico = TipoServico.objects.get(tipo_rancher=subservico)
                return tipo_servico
            except TipoServico.DoesNotExist:
                # Tenta encontrar o serviço principal
                pass
        try:
            tipo_servico = TipoServico.objects.get(tipo_rancher=rec["tipo"])
        except TipoServico.DoesNotExist:
            print(
                "* ",
                _(
                    "Erro ao processar {counter}º registro. Tipo de "
                    "serviço desconhecido: {tipo}. Registro: {r}"
                ).format(counter=self.counter, tipo=rec["tipo"], r=rec),
                file=sys.stderr,
            )
            return False
        return tipo_servico

    def get_orgao(self, rec):
        # Tenta achar pelo namespace, que é mais canônico

        namespace = rec["namespace"]
        if namespace.count("-") > 1:
            namespace = "-".join(namespace.split("-")[1:])
        if namespace in self.nomes_gerados:
            return self.nomes_gerados[namespace]

        # Senão, vamos buscar pelo tipo de órgão e nome
        try:
            tipo, nome_uf = rec["orgao"].split(" - ")
            if nome_uf.count("-") > 1:
                subproduto, nome, uf = nome_uf.split("-")
            else:
                nome, uf = nome_uf.split("-")
        except ValueError:
            print(
                "* ",
                _(
                    "Nome do órgão fora do padrão no {counter}º registro: {r}"
                ).format(counter=self.counter, r=rec),
                file=sys.stderr,
            )
            return False

        tipo = to_ascii(tipo).lower()
        nome = to_ascii(nome).lower()
        uf = to_ascii(uf).lower()
        cidade_uf = "-".join([nome, uf])

        try:
            tipo_orgao = TipoOrgao.objects.get(nome__unaccent__icontains=tipo)
        except TipoOrgao.DoesNotExist:
            print(
                "* ",
                _(
                    "Tipo de órgão desconhecido no {counter}º "
                    "registro. Nome do órgão: {orgao}, registro: {r}"
                ).format(counter=self.counter, orgao=rec["orgao"], r=rec),
                file=sys.stderr,
            )
            return False

        if cidade_uf in self.nomes_gerados:
            orgao = self.nomes_gerados[cidade_uf]
            if orgao.tipo != tipo_orgao:
                print(
                    "* ",
                    _(
                        "Encontrado um órgão para o municipio "
                        "{municipio} - {uf}, mas o tipo de órgão difere do "
                        "recebido do webservice. Registro: {rec}"
                    ).format(municipio=nome, uf=uf, rec=rec),
                    file=sys.stderr,
                )
                return False
            return orgao

        return False

    def get_servico(self, tipo_servico, rec):
        servicos = Servico.objects.filter(
            tipo_servico=tipo_servico,
            instancia=rec["namespace"],
            data_desativacao=None,
        ).order_by("-data_ativacao")
        # Nenhum serviço ativo nesse namespace. Podemos criar um novo
        if not servicos:
            return None
        if len(servicos) == 1:
            # Um único serviço ativo, deve ser esse
            return servicos[0]
        # Mais de um serviço ativo para este namespace.
        # Não tem como decidir qual atualizar
        raise MultipleServicesReturned(
            _(
                "Existem {qty} serviços ativos para o namespace {namespace}. "
                "Registro {r}"
            ).format(qty=len(servicos), namespace=rec["namespace"], r=rec)
        )

    def atualiza_servico(self, servico, rec):
        log_tit = []
        log_txt = []

        updated = False

        for attrname, recfield in self.UPDATABLE_FIELDS:
            old = getattr(servico, attrname)
            new = rec[recfield]
            if old != new:
                updated = True
                log_tit.append(
                    _(f"Mudança de {attrname}").format(
                        attrname=attrname.upper()
                    )
                )
                log_txt.append(
                    _(
                        "A {attrname} do serviço foi alterada na "
                        "infraestrutura de {old} para {new}."
                    ).format(attrname=attrname, old=old, new=new)
                )
                setattr(servico, attrname, new)

        if (
            rec["status"] == "suspenso" and servico.data_desativacao is None
        ) or (
            rec["suspendedDate"] is not None
            and servico.data_desativacao != rec["suspendedDate"]
        ):
            servico.data_desativacao = rec["suspendedDate"]
            servico.motivo_desativacao = _(
                "Serviço suspenso no SEIT e atualizado automaticamente "
                "pelo processo de cron."
            )
            log_tit.append(_("Serviço suspenso no SEIT"))
            log_txt.append(
                _(
                    "Serviço suspenso no SEIT e atualizado automaticamente "
                    "pelo processo de cron."
                )
            )
            print(
                "* ",
                _("{servico} de {orgao} desativado").format(
                    servico=servico.tipo_servico.nome,
                    orgao=servico.casa_legislativa.nome,
                ),
            )
            self.desativados += 1
        elif updated:
            self.updates += 1
            print(
                "* ",
                _("{servico} de {orgao} atualizado").format(
                    servico=servico.tipo_servico.nome,
                    orgao=servico.casa_legislativa.nome,
                ),
            )

        servico.flag_confirmado = True
        servico.save()
        if log_tit:
            log_tit = ", ".join(log_tit)
            log_txt = "\n\n".join(log_txt)
            servico.logservico_set.create(
                descricao=log_tit,
                data=timezone.localdate(),
                log=log_txt,
            )
            self.admin_log_change(servico, log_txt)

    def cria_servico(self, rec, tipo_servico, orgao):
        servico = Servico(
            casa_legislativa=orgao,
            tipo_servico=tipo_servico,
            url=rec["url"],
            versao=rec["version"],
            hospedagem_interlegis=True,
            instancia=rec["namespace"],
            data_ativacao=rec["creationDate"],
            data_desativacao=rec["suspendedDate"],
            motivo_desativacao=(
                "" if rec["suspendedDate"] is None else _("Suspenso no SEIT")
            ),
            flag_confirmado=True,
        )
        servico.save()
        servico.logservico_set.create(
            descricao=_("Serviço criado no SEIT"),
            data=timezone.localdate(),
            log=_(
                "Servico criado no SEIT e atualizado no SIGI "
                "automaticamente pelo processo de CRON"
            ),
        )
        self.admin_log_addition(
            servico,
            _(
                "Servico criado no SEIT e atualizado no SIGI "
                "automaticamente pelo processo de CRON"
            ),
        )
        print(
            "* ",
            _("{servico} criado para {orgao}").format(
                servico=servico.tipo_servico.nome,
                orgao=servico.casa_legislativa.nome,
            ),
        )

    def bulk_desativa(self, servicos):
        log_list = [
            LogServico(
                servico=s,
                descricao=_("Serviço desativado no SEIT"),
                data=timezone.localdate(),
                log=_(
                    "Desativado automaticamente pois não foi encontrado na "
                    "Infraestrutura do Interlegis"
                ),
            )
            for s in servicos
        ]
        LogServico.objects.bulk_create(log_list)
        self.admin_log_change(
            servicos,
            _(
                "Desativado automaticamente pois não foi encontrado na "
                "Infraestrutura do Interlegis"
            ),
        )
        print(
            *[
                _(
                    "* {servico} de {orgao} desativado porque não consta nos "
                    "dados do webservice do SEIT\n"
                ).format(
                    servico=s.tipo_servico.nome, orgao=s.casa_legislativa.nome
                )
                for s in servicos
            ],
        )
        return servicos.update(
            data_desativacao=timezone.localdate(),
            motivo_desativacao=_(
                "Desativado automaticamente pois não foi encontrado na "
                "Infraestrutura do Interlegis"
            ),
        )
