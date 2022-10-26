import datetime
from typing import TypedDict
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

LOG_GERAL = _("Mensagens gerais")

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


class Job(DailyJob):
    help = _("Sincronização dos registros de DNS da infraestrutura")
    _nomes_gerados = None
    _log = {}

    def execute(self):
        print(
            _(
                "Sincroniza os registros de domínio a partir do DNS."
                f" Início: {datetime.datetime.now(): %d/%m/%Y %H:%M:%S}"
            )
        )

        self._nomes_gerados = {
            generate_instance_name(o): o
            for o in Orgao.objects.filter(tipo__legislativo=True)
        }

        Servico.objects.filter(
            tipo_servico__modo="R", data_desativacao=None
        ).update(flag_confirmado=False)

        self._log[LOG_GERAL] = get_log_entry()

        for uf in UnidadeFederativa.objects.all():
            self._log[uf] = get_log_entry()
            self.processa_uf(uf)

        self.processa_zones()
        self.processa_files()

        try:
            shutil.rmtree(settings.REGISTRO_PATH)
        except Exception as e:
            print(_(f"Erro ao excluir diretório {settings.REGISTRO_PATH}"))

        print("Relatório final:\n================")
        self.report()
        print(_(f" Término: {datetime.datetime.now():%H:%M:%S}."))

    def processa_rec(self, dns_rec, log_entry=LOG_GERAL):
        dominio = dns_rec["name"][:-1]
        nivel = len(dominio.split("."))
        iname = get_iname(dominio)
        sigla_srv = get_sigla_serv(dominio)

        if log_entry == LOG_GERAL:
            try:
                log_entry = UnidadeFederativa.objects.get(
                    sigla=get_sigla_uf(dominio)
                )
            except:
                pass

        if "_psl" in dominio:
            # Ignorar registros _PSL sem fazer log #
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
            if iname in self._nomes_gerados:
                orgao = self._nomes_gerados[iname]
                log_entry = orgao.municipio.uf
                servico = Servico(
                    casa_legislativa=orgao,
                    tipo_servico=tipo,
                    instancia=iname,
                    data_ativacao=timezone.localdate(),
                    flag_confirmado=True,
                )
                self.log_novo(servico)
            else:
                if nivel < 4:
                    # Ignora registros de 3º nível ou abaixo, sem logar #
                    return
                try:
                    servico = Servico.objects.get(
                        tipo_servico=tipo,
                        url__icontains=dominio,
                        data_desativacao=None,
                    )
                    self.log_update(servico)
                except Servico.MultipleObjectsReturned:
                    self.log_ignore(
                        dominio,
                        _("existe mais de um registro no SIGI deste domínio."),
                        log_entry,
                    )
                    return
                except Servico.DoesNotExist:
                    self.log_ignore(
                        dominio,
                        _("não parece pertencer a nenhum órgão"),
                        log_entry,
                    )
                    return
        # atualiza o serviço no SIGI
        servico.url = dominio
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
        self._log[uf]["sumario"]["total"] = len(registros)

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
        self._log[LOG_GERAL]["sumario"]["total"] = len(file_list)
        for file_path in file_list:
            if not file_path.is_file():
                self._log[LOG_GERAL]["sumario"]["total"] -= 1
                continue
            print(file_path)
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

    def report(self):
        rst = render_to_string(
            "servicos/emails/report_sincroniza_dns.rst",
            {
                "log": self._log,
                "title": _("Resultado da sincronização do SIGI com o DNS"),
            },
        )

        html = docutils.core.publish_string(
            rst,
            writer_name="html5",
            settings_overrides={
                "input_encoding": "unicode",
                "output_encoding": "unicode",
            },
        )
        mail_admins(
            subject=self.help,
            message=rst,
            html_message=html,
            fail_silently=True,
        )
        print(rst)

    def error(self, message, log_entry=LOG_GERAL):
        self._log[log_entry]["erros"].append(message)

    def info(self, message, log_entry=LOG_GERAL):
        self._log[log_entry]["infos"].append(message)

    def log_novo(self, srv):
        orgao = srv.casa_legislativa
        uf = orgao.municipio.uf
        msg = _(
            f"Criada instância {srv.instancia} de {srv.tipo_servico.nome} "
            f"para {orgao.nome} ({uf.sigla})"
        )
        self.info(msg, uf)
        self._log[uf]["sumario"]["novos"] += 1

    def log_ignore(self, dominio, motivo, log_entry=LOG_GERAL):
        self.error(_(f"Registro {dominio} ignorado pois {motivo}"), log_entry)
        self._log[log_entry]["sumario"]["ignorados"] += 1

    def log_update(self, srv):
        uf = srv.casa_legislativa.municipio.uf
        self._log[uf]["sumario"]["atualizados"] += 1

    def log_remove(self, srv):
        orgao = srv.casa_legislativa
        uf = orgao.municipio.uf
        self._log[uf]["sumario"]["desativados"] += 1
        self.info(
            _(
                f"Registro {srv.tipo_servico.sigla} {srv.instancia} ({srv.url})"
                f" de {orgao.nome} desativado pois não foi encontrado no DNS."
            ),
            uf,
        )
