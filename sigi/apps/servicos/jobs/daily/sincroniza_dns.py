import json
import shutil
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.servicos import generate_instance_name, nomeia_instancias
from sigi.apps.servicos.models import Servico, TipoServico
from sigi.apps.casas.models import Orgao
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.utils.mixins import JobReportMixin

LOG_GERAL = _("Mensagens gerais")
IGNORES = ["_psl", "k8s", "www.", "sapl.", "addr.arpa"]

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
        self.report_data[LOG_GERAL] = get_log_entry()

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

        nomeia_instancias(
            servicos=Servico.objects.filter(
                tipo_servico__modo="R", data_desativacao=None, instancia=""
            ),
            user=self.sys_user,
        )

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

        if any([i in dominio for i in IGNORES]):
            # Ignorar esses registros sem fazer log #
            return

        try:
            tipo = TipoServico.objects.get(sigla=sigla_srv, modo="R")
        except TipoServico.DoesNotExist:
            self.log_ignore(
                dominio,
                _("não coincide com nenhum tipo de serviço de registro SEIT"),
                log_entry,
            )
            return

        if log_entry == LOG_GERAL:
            try:
                log_entry = UnidadeFederativa.objects.get(
                    sigla=get_sigla_uf(dominio)
                )
            except:
                pass

        detail_file = settings.REGISTRO_PATH / f"{dominio}."
        hospedado_interlegis = detail_file.exists() and detail_file.is_file()

        filtro_base = Q(instancia=iname) | Q(url=dominio)
        if iname in self.nomes_gerados:
            filtro_base = filtro_base | Q(
                casa_legislativa=self.nomes_gerados[iname]
            )
        filtro_base = filtro_base & Q(tipo_servico=tipo)

        servico = None
        novo = False

        try:
            servico = Servico.objects.get(
                filtro_base & Q(data_desativacao=None)
            )
        except Servico.MultipleObjectsReturned:
            self.log_ignore(
                dominio,
                _(
                    "existe mais de um registro no SIGI para a instância "
                    f"{iname}, domínio {dominio}"
                ),
                log_entry,
            )
            return
        except Servico.DoesNotExist:
            # Tenta encontrar um registro desativado para esta instância #
            servico = Servico.objects.filter(
                filtro_base & ~Q(data_desativacao=None)
            ).first()
            if servico is not None:
                # Reativa o servico #
                self.log_reativa(servico)
                servico.data_desativacao = None
                servico.motivo_desativacao = ""
                servico.instancia = iname
                self.admin_log_change(servico, _("Reativado pelo DNS Rancher"))
            else:
                # Tenta criar o registro #
                if iname in self.nomes_gerados:
                    orgao = self.nomes_gerados[iname]
                    log_entry = orgao.municipio.uf
                    servico = Servico(
                        casa_legislativa=orgao,
                        tipo_servico=tipo,
                        url=dominio,
                        instancia=iname,
                        hospedagem_interlegis=hospedado_interlegis,
                        data_ativacao=timezone.localdate(),
                        flag_confirmado=True,
                        resultado_verificacao="N",  # Não verificado
                    )
                    servico.save()
                    novo = True
                    self.log_novo(servico)
                    self.admin_log_addition(servico, "Criado pelo DNS Rancher")

        if servico is None:
            if nivel > 3:
                # Loga registro não encontrado apenas para 4º+ nível #
                self.log_ignore(
                    dominio,
                    _("não parece pertencer a nenhum órgão"),
                    log_entry,
                )
        elif not novo:
            # atualiza o serviço no SIGI
            updates = []
            if servico.url != dominio:
                updates.append(_(f"Url de '{servico.url}' para '{dominio}'"))
            if servico.instancia != iname:
                updates.append(
                    _(f"Instância de '{servico.instancia}' para '{iname}'")
                )
            if servico.hospedagem_interlegis != hospedado_interlegis:
                updates.append(
                    "Veio para hospedagem no Interlegis"
                    if hospedado_interlegis
                    else "Passou a ser delegado"
                )
            servico.url = dominio
            servico.instancia = iname
            servico.hospedagem_interlegis = hospedado_interlegis
            servico.flag_confirmado = True
            servico.save()
            if updates:
                self.log_update(servico)
                self.admin_log_change(
                    servico,
                    "Atualizado pelo DNS Rancher: " + ", ".join(updates),
                )

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
            flag_confirmado=False,
        ):
            servico.data_desativacao = timezone.localdate()
            servico.motivo_desativacao = _("Não encontrado no DNS")
            servico.save()
            self.log_remove(servico)
            self.admin_log_change(
                servico, _("Desativado: não encontrado no DNS Rancher")
            )

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
