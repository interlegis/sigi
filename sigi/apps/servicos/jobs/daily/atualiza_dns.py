import requests
import sys
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from url_normalize import url_normalize
from sigi.apps.casas.models import Orgao, TipoOrgao
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.servicos import generate_instance_name, nomeia_instancias
from sigi.apps.servicos.exceptions import MultipleServicesReturned
from sigi.apps.servicos.models import Servico, LogServico, TipoServico
from sigi.apps.utils.management.jobs import AdminJobMixin


class Job(AdminJobMixin, DailyJob):
    help = _("Atualiza registros de DNS")

    nomes_gerados = None
    dados = None

    counter = 0
    ignorados = 0
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

        registros_ativos = Servico.objects.filter(
            tipo_servico__modo=TipoServico.MODO_REGISTRO, data_desativacao=None
        )

        nomeia_instancias(
            servicos=registros_ativos.filter(instancia=""),
            user=self.get_sys_user(),
        )

        registros_ativos.update(flag_confirmado=False)

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
                servico = self.get_registro(tipo_servico, rec)
            except MultipleServicesReturned as e:
                print("* ", str(e), file=sys.sys.stderr)
                self.erros += 1
                continue

            if servico:
                self.atualiza_registro(servico, rec)
                continue

            # Tenta criar o registro
            orgao = self.get_orgao(rec)
            if not orgao:
                self.erros += 1
                continue

            self.cria_registro(rec, tipo_servico, orgao)
            self.novos += 1

        # Desativar todos que não foram confirmados
        nao_confirmados = registros_ativos.filter(flag_confirmado=False)
        self.desativados += self.bulk_desativa(nao_confirmados)

        print("\n\n", _("TOTAIS"))
        print("------", "\n")
        print(
            _("  * registros recebidos do webservice: {total}").format(
                total=total
            )
        )
        print(
            _("  * registros ignorados..............: {ignorados}").format(
                ignorados=self.ignorados
            )
        )
        print(
            _("  * registros com erro...............: {erros}").format(
                erros=self.erros
            )
        )
        print(
            _("  * atualizações realizadas..........: {updates}").format(
                updates=self.updates
            )
        )
        print(
            _("  * registros desativados............: {desativados}").format(
                desativados=self.desativados
            )
        )
        print(
            _("  * novos registros criados..........: {novos}").format(
                novos=self.novos
            )
        )

    def _retrieve_json_data(self):
        if (not hasattr(settings, "REGISTRO_PATH")) or (
            not settings.REGISTRO_PATH
        ):
            print(
                _(
                    "Falta a configuração da URL de acesso aos registros de "
                    "DNS instalados"
                ),
                file=sys.stderr,
            )
            return False

        print(
            _("Buscando dados no webservice {wsentry}...").format(
                wsentry=settings.REGISTRO_PATH
            ),
        )
        try:
            response = requests.get(settings.REGISTRO_PATH)
        except Exception as e:
            print(
                _("Ocorreu um erro ao acessar {url}: {error}").format(
                    url=settings.REGISTRO_PATH, error=str(e)
                ),
                file=sys.stderr,
            )
            return False

        if response.status_code != 200:
            print(
                _(
                    "Problemas na resposta do webservice de DNS: "
                    "{code} - {reason}"
                ).format(code=response.status_code, reason=response.reason),
                file=sys.stderr,
            )
            return False

        if "json" not in response.headers["content-type"]:
            print(
                _("Tipo de conteúdo não é JSON: {contenttype}").format(
                    contenttype=response.headers["content-type"]
                ),
                file=sys.stderr,
            )
            return False

        result = response.json()

        if result["tipo"] != "DNS":
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

        self.dados = result["result"]["dominios"]

        return True

    def get_dados(self):
        if self.dados is None:
            if not self._retrieve_json_data():
                return

        self.ignorados = 0
        self.counter = 0

        for record in self.dados:
            self.counter += 1
            if (
                "interlegis" in record["url"].lower()
                or "interlegis" in record["orgao"].lower()
            ):
                self.ignorados += 1
                continue
            yield record

    def get_tipo_servico(self, rec):
        try:
            tipo_servico = TipoServico.objects.get(tipo_rancher=rec["tipo"])
        except TipoServico.DoesNotExist:
            print(
                "* ",
                _(
                    "Erro ao processar {counter}º registro. Tipo de "
                    "registro desconhecido: {tipo}. Registro: {r}"
                ).format(counter=self.counter, tipo=rec["tipo"], r=rec),
                file=sys.stderr,
            )
            return None
        if tipo_servico.modo != TipoServico.MODO_REGISTRO:
            print(
                "* ",
                _(
                    "O {counter}º registro de DNS {rec} indica um tipo de "
                    "serviço que não é de registro de DNS."
                ).format(counter=self.counter, rec=rec),
                file=sys.stderr,
            )
            return None
        return tipo_servico

    def get_orgao(self, rec):
        # tenta achar pelo órgão dado no registro
        if rec["orgao"] in self.nomes_gerados:
            return self.nomes_gerados[rec["orgao"]]

        # Senão, vamos buscar pelo nome do domínio na URL

        partes = rec["url"].split(".")
        # A UF deve ser o 2º nível e o domínio, o último
        uf = partes[-3]
        dominio = partes[0].replace("https://", "")

        if not UnidadeFederativa.objects.filter(sigla=uf).exists():
            print(
                "* ",
                _(
                    "Impossível identificar o órgão dono do registro {url}, "
                    "no {counter}º registro: {rec}"
                ).format(url=rec["url"], counter=self.counter, rec=rec),
                file=sys.stderr,
            )
            return None

        nome_orgao = f"{dominio}-{uf}"
        if nome_orgao in self.nomes_gerados:
            return self.nomes_gerados[nome_orgao]

        return None

    def get_registro(self, tipo_servico, rec):
        servicos = Servico.objects.filter(
            tipo_servico=tipo_servico,
            instancia=rec["orgao"],
            data_desativacao=None,
        ).order_by("-data_ativacao")
        if not servicos:
            # Nenhum registro ativo, podemos criar um
            return None
        if len(servicos) == 1:
            # Um único registro ativo, deve ser esse
            return servicos[0]
        # Mais de um registro ativo para este órgão.
        # Não tem como decidir qual atualizar
        raise MultipleServicesReturned(
            _(
                "Existem {qty} registros ativos para o órgão {orgao}. "
                "Registro {r}"
            ).format(qty=len(servicos), orgao=rec["orgao"], r=rec)
        )

    def atualiza_registro(self, registro, rec):
        old = registro.url
        new = rec["url"]

        if old != new:
            registro.url = new
            self.updates += 1
            log = _(
                "A URL do {tipo} de {orgao} atualizado de {old} para {new}"
            ).format(
                tipo=registro.tipo_servico.sigla,
                orgao=registro.casa_legislativa.nome,
                old=old,
                new=new,
            )
            print("* ", log)
            registro.logservico_set.create(
                descricao=_("URL atualizada"),
                data=timezone.localdate(),
                log=log,
            )
            self.admin_log_change(registro, log)
        registro.flag_confirmado = True
        registro.save()

    def cria_registro(self, rec, tipo_servico, orgao):
        registro = Servico(
            casa_legislativa=orgao,
            tipo_servico=tipo_servico,
            url=rec["url"],
            hospedagem_interlegis=rec["hospedagem"] == "Interlegis",
            instancia=rec["orgao"],
            data_ativacao=timezone.localdate(),
            flag_confirmado=True,
        )
        registro.save()
        registro.logservico_set.create(
            descricao=_("Serviço criado no SEIT"),
            data=timezone.localdate(),
            log=_(
                "Servico criado no SEIT e atualizado no SIGI "
                "automaticamente pelo processo de CRON"
            ),
        )
        self.admin_log_addition(
            registro,
            _(
                "Servico criado no SEIT e atualizado no SIGI "
                "automaticamente pelo processo de CRON"
            ),
        )
        print(
            "* ",
            _("{servico} criado para {orgao}").format(
                servico=registro.tipo_servico.nome,
                orgao=registro.casa_legislativa.nome,
            ),
        )

    def bulk_desativa(self, registros):
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
            for s in registros
        ]
        LogServico.objects.bulk_create(log_list)
        self.admin_log_change(
            registros,
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
                for s in registros
            ],
        )
        return registros.update(
            data_desativacao=timezone.localdate(),
            motivo_desativacao=_(
                "Desativado automaticamente pois não foi encontrado na "
                "Infraestrutura do Interlegis"
            ),
        )
