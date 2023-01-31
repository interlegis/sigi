import datetime
import docutils.core
import json
import shutil
from django.conf import settings
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.servicos import generate_instance_name
from sigi.apps.servicos.models import Servico, TipoServico
from sigi.apps.casas.models import Orgao
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.utils.mixins import JobReportMixin

LOG_GERAL = _("Mensagens gerais")
IGNORES = ["_psl", "k8s", "www.", "sapl."]

get_iname = lambda d: "-".join(d.split(".")[:-2])
get_sigla_serv = lambda d: "".join(d.split(".")[-2:]).upper()
get_sigla_uf = lambda d: "".join(d.split(".")[-3:-2]).upper()


def get_log_entry():
    return {
        "sumario": {
            "total": 0,
            "novos": 0,
            "atualizados": 0,
            "desativados": 0,
            "ignorados": 0,
        },
        "infos": [],
        "erros": [],
    }


class Job(JobReportMixin, DailyJob):
    help = _("Sincronização dos registros de DNS da infraestrutura")
    report_template = "servicos/emails/report_sincroniza_dns.rst"
    nomes_gerados = None
    report_data = {}

    def do_job(self):
        # TODO: Resolver
        raise Exception(
            "Este CRON está desativado até resolvermos questões internas"
        )

        self.report_data[LOG_GERAL] = get_log_entry()
        self.report_data["reativados"] = get_log_entry()  # TODO: Remover
        self.info("id,nome do orgao,instancia,tipo,url", "reativados")

        if (
            not settings.REGISTRO_PATH.exists()
            or not settings.REGISTRO_PATH.is_dir()
        ):
            self.error(_(f"Arquivos de DNS não encontrados."))
            return

        self.nomes_gerados = {
            generate_instance_name(o): o
            for o in Orgao.objects.filter(tipo__legislativo=True)
        }

        Servico.objects.filter(
            tipo_servico__modo="R", data_desativacao=None
        ).update(flag_confirmado=False)

        for uf in UnidadeFederativa.objects.all():
            self.report_data[uf] = get_log_entry()
            self.processa_uf(uf)

        self.processa_zones()
        self.processa_files()

        try:
            shutil.rmtree(settings.REGISTRO_PATH)
        except Exception as e:
            self.info(_(f"Erro ao excluir diretório {settings.REGISTRO_PATH}"))

    def processa_rec(self, dns_rec, log_entry=LOG_GERAL):
        dominio = dns_rec["name"][:-1]
        nivel = dominio.count(".") + 1
        iname = get_iname(dominio)
        sigla_srv = get_sigla_serv(dominio)

        if log_entry == LOG_GERAL:
            try:
                log_entry = UnidadeFederativa.objects.get(
                    sigla=get_sigla_uf(dominio)
                )
            except:
                pass

        if any([i in dominio for i in IGNORES]):
            # Ignorar esses registros sem fazer log #
            return

        apps = []
        if "rrsets" in dns_rec:
            apps = [
                r["name"].split(".")[0]
                for r in dns_rec["rrsets"]
                if r["type"] != "TXT" and r["name"][:-1].count(".") + 1 > nivel
            ]
        else:
            detail_file = settings.REGISTRO_PATH / f"{dominio}."
            if detail_file.exists() and detail_file.is_file():
                detail_data = json.loads(detail_file.read_text())
                if "rrsets" in detail_data:
                    apps = [
                        r["name"].split(".")[0]
                        for r in detail_data["rrsets"]
                        if r["type"] != "TXT"
                        and r["name"][:-1].count(".") + 1 > nivel
                    ]

        try:
            tipo = TipoServico.objects.get(sigla=sigla_srv, modo="R")
        except TipoServico.DoesNotExist:
            self.log_ignore(
                dominio,
                _("não coincide com nenhum tipo de serviço de registro SEIT"),
                log_entry,
            )
            return

        try:
            servico = Servico.objects.get(
                tipo_servico=tipo, instancia=iname, data_desativacao=None
            )
            self.log_update(servico)
        except Servico.MultipleObjectsReturned:
            self.log_ignore(
                dominio,
                _(
                    "existe mais de um registro no SIGI para a instância "
                    f"{iname}"
                ),
                log_entry,
            )
            return
        except Servico.DoesNotExist:
            # Tenta encontrar um registro desativado para esta instância #
            servico = Servico.objects.filter(
                tipo_servico=tipo, instancia=iname
            ).first()
            if servico is not None:
                # Reativa o servico #
                servico.data_desativacao = None
                servico.instancia = iname
                self.log_reativa(servico)
            else:
                servico = None
                # Tenta encontrar um registro ativo com mesmo domínio #
                servico = Servico.objects.filter(
                    tipo_servico=tipo, url=dominio, data_desativacao=None
                ).first()
                if servico is not None:
                    servico.instancia = iname
                    self.log_update(servico)
                else:
                    # Tenta encontrar um registro desativado com mesmo domínio #
                    servico = Servico.objects.filter(
                        tipo_servico=tipo, url=dominio
                    ).first()
                    if servico is not None:
                        servico.data_desativacao = None
                        servico.instancia = iname
                        self.log_reativa(servico)

            if servico is None:
                # Tenta criar o registro #
                if iname in self.nomes_gerados:
                    orgao = self.nomes_gerados[iname]
                    log_entry = orgao.municipio.uf
                    servico = Servico(
                        casa_legislativa=orgao,
                        tipo_servico=tipo,
                        instancia=iname,
                        data_ativacao=timezone.localdate(),
                        flag_confirmado=True,
                    )
                    self.log_novo(servico)

            if servico is None:
                if nivel > 3:
                    # Loga registro não encontrado apenas para 4º+ nível #
                    self.log_ignore(
                        dominio,
                        _("não parece pertencer a nenhum órgão"),
                        log_entry,
                    )
            else:
                # atualiza o serviço no SIGI
                servico.url = dominio
                servico.instancia = iname
                servico.apps = "\n".join(apps)
                servico.hospedagem_interlegis = True
                servico.data_verificacao = timezone.localtime()
                servico.resultado_verificacao = "F"  # Funcionando
                servico.flag_confirmado = True
                servico.save()

    def processa_uf(self, uf):
        file_path = settings.REGISTRO_PATH / f"{uf.sigla.lower()}.leg.br."
        if not file_path.exists() or not file_path.is_file():
            self.error(_(f"Arquivo {file_path} não encontado."), uf)
            return

        registros = json.loads(file_path.read_text())["rrsets"]
        self.report_data[uf]["sumario"]["total"] = len(registros)

        # Atualiza registros existentes e cria novos #
        for rec in registros:
            dominio = rec["name"][:-1]
            self.processa_rec(rec, uf)
            # Remove arquivo de detalhe, se existente #
            detail_file = settings.REGISTRO_PATH / f"{dominio}."
            if (
                detail_file != file_path
                and detail_file.exists()
                and detail_file.is_file()
            ):
                detail_file.unlink()

        # Remove arquivo da UF #
        file_path.unlink()

    def processa_zones(self):
        zones_file = settings.REGISTRO_PATH / "ZONES"
        if not zones_file.exists() or not zones_file.is_file():
            self.error(
                _(
                    f"Arquivo de zonas {zones_file} não encontrado ou "
                    "não é arquivo"
                )
            )
            return
        data = json.loads(zones_file.read_text())
        for rec in data:
            dominio = rec["name"][:-1]
            self.processa_rec(rec)
            detail_file = settings.REGISTRO_PATH / f"{dominio}."
            if (
                detail_file != zones_file
                and detail_file.exists()
                and detail_file.is_file()
            ):
                detail_file.unlink()

        zones_file.unlink()

    def processa_files(self):
        file_list = list(settings.REGISTRO_PATH.iterdir())
        self.report_data[LOG_GERAL]["sumario"]["total"] = len(file_list)
        for file_path in file_list:
            if not file_path.is_file():
                self.report_data[LOG_GERAL]["sumario"]["total"] -= 1
                continue
            data = json.loads(file_path.read_text())
            self.processa_rec(data)
            file_path.unlink()

    def remove_sigi(self):
        # Desativa registros no SIGI que não estão no DNS #
        for servico in Servico.objects.filter(
            tipo_servico__modo="R",
            data_desativacao=None,
            hospedagem_interlegis=True,
            flag_confirmado=False,
        ):
            servico.data_desativacao = timezone.localdate()
            servico.motivo_desativacao = _("Não encontrado no DNS")
            servico.save()
            self.log_remove(servico)

    def error(self, message, log_entry=LOG_GERAL):
        self.report_data[log_entry]["erros"].append(message)

    def info(self, message, log_entry=LOG_GERAL):
        self.report_data[log_entry]["infos"].append(message)

    def log_novo(self, srv):
        orgao = srv.casa_legislativa
        uf = orgao.municipio.uf
        msg = _(
            f"Criada instância {srv.instancia} de {srv.tipo_servico.nome} "
            f"para {orgao.nome} ({uf.sigla})"
        )
        self.info(msg, uf)
        self.report_data[uf]["sumario"]["novos"] += 1

    def log_ignore(self, dominio, motivo, log_entry=LOG_GERAL):
        self.error(_(f"Registro {dominio} ignorado pois {motivo}"), log_entry)
        self.report_data[log_entry]["sumario"]["ignorados"] += 1

    def log_update(self, srv):
        uf = srv.casa_legislativa.municipio.uf
        self.report_data[uf]["sumario"]["atualizados"] += 1

    def log_reativa(self, srv):
        orgao = srv.casa_legislativa
        uf = orgao.municipio.uf
        msg = _(
            f"Instância {srv.instancia} de {srv.tipo_servico.nome} "
            f"para {orgao.nome} ({uf.sigla}) reativada no SIGI"
        )
        self.report_data[uf]["sumario"]["atualizados"] += 1
        self.info(msg, uf)
        msg = f"{srv.id},{orgao.nome},{srv.instancia},{srv.tipo_servico.nome},{srv.url}"
        self.info(msg, "reativados")

    def log_remove(self, srv):
        orgao = srv.casa_legislativa
        uf = orgao.municipio.uf
        self.report_data[uf]["sumario"]["desativados"] += 1
        self.info(
            _(
                f"Registro {srv.tipo_servico.sigla} {srv.instancia} ({srv.url})"
                f" de {orgao.nome} desativado pois não foi encontrado no DNS."
            ),
            uf,
        )
