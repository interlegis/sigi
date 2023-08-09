from django_extensions.management.jobs import MonthlyJob
from django.conf import settings
from django.contrib.admin.models import ADDITION, CHANGE
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from ibge.localidades import Estados, Municipios
from sigi.apps.contatos.models import (
    UnidadeFederativa,
    Mesorregiao,
    Microrregiao,
    Municipio,
)
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils.management.jobs import JobReportMixin


class Job(JobReportMixin, MonthlyJob):
    help = _(
        "Atualiza Unidades Federativas, mesorregiões, microrregiões e "
        "municípios com dados do IBGE"
    )
    report_template = "contatos/emails/report_atualiza_ibge.rst"

    uf_novas = []
    uf_atualizadas = []
    municipios_novos = []
    municipios_atualizados = []
    meso_novas = []
    meso_atualizadas = []
    micro_novas = []
    micro_atualizadas = []
    sigi_user = None

    def do_job(self):
        self.atualiza_ufs()
        self.atualiza_municipios()

        self.report_data = {
            "uf_novas": self.uf_novas,
            "uf_atualizadas": self.uf_atualizadas,
            "municipios_novos": self.municipios_novos,
            "municipios_atualizados": self.municipios_atualizados,
            "meso_novas": self.meso_novas,
            "meso_atualizadas": self.meso_atualizadas,
            "micro_novas": self.micro_novas,
            "micro_atualizadas": self.micro_atualizadas,
        }

    def atualiza_ufs(self):
        regioes_map = {
            "N": "NO",
            "NE": "NE",
            "SE": "SE",
            "S": "SL",
            "CO": "CO",
        }

        for ibge_uf in Estados().json():
            regiao = regioes_map[ibge_uf["regiao"]["sigla"]]
            try:
                sigi_uf = UnidadeFederativa.objects.get(
                    codigo_ibge=ibge_uf["id"]
                )
            except UnidadeFederativa.DoesNotExist:
                sigi_uf = UnidadeFederativa(
                    codigo_ibge=ibge_uf["id"],
                    nome=ibge_uf["nome"],
                    sigla=ibge_uf["sigla"],
                    regiao=regiao,
                    populacao=0,
                )
                sigi_uf.save()
                self.uf_novas.append(sigi_uf)
                self.admin_log_addition(sigi_uf, "Nova UF encontrada no IBGE")
            if (
                sigi_uf.nome != ibge_uf["nome"]
                or sigi_uf.sigla != ibge_uf["sigla"]
                or sigi_uf.regiao != regiao
            ):
                sigi_uf.nome = ibge_uf["nome"]
                sigi_uf.sigla = ibge_uf["sigla"]
                sigi_uf.regiao = regiao
                sigi_uf.save()
                self.uf_atualizadas.append(sigi_uf)
                self.admin_log_change(sigi_uf, "Atualizada pelo IBGE")

    def atualiza_municipios(self):
        for ibge_mun in Municipios().json():
            uf_id = ibge_mun["microrregiao"]["mesorregiao"]["UF"]["id"]
            cod_meso = ibge_mun["microrregiao"]["mesorregiao"]["id"]
            cod_micro = int(
                str(cod_meso) + str(ibge_mun["microrregiao"]["id"])[-3:]
            )
            # Atualiza ou cria mesorregião #
            try:
                meso = Mesorregiao.objects.get(codigo_ibge=cod_meso)
            except Mesorregiao.DoesNotExist:
                meso = Mesorregiao(
                    codigo_ibge=cod_meso,
                    uf_id=uf_id,
                    nome=ibge_mun["microrregiao"]["mesorregiao"]["nome"],
                )
                meso.save()
                self.meso_novas.append(meso)
                self.admin_log_addition(
                    meso, "Nova mesorregião encontrada no IBGE"
                )
            if meso.nome != ibge_mun["microrregiao"]["mesorregiao"]["nome"]:
                meso.nome = ibge_mun["microrregiao"]["mesorregiao"]["nome"]
                meso.save()
                self.meso_atualizadas.append(meso)
                self.admin_log_change(meso, "Atualizada pelo IBGE")
            # Atualiza ou cria a microrregião #
            try:
                micro = Microrregiao.objects.get(codigo_ibge=cod_micro)
            except Microrregiao.DoesNotExist:
                micro = Microrregiao(
                    codigo_ibge=cod_micro,
                    mesorregiao=meso,
                    nome=ibge_mun["microrregiao"]["nome"],
                )
                micro.save()
                self.micro_novas.append(micro)
                self.admin_log_addition(
                    micro, "Nova microrregião encontrada no IBGE"
                )
            if (
                micro.nome != ibge_mun["microrregiao"]["nome"]
                or micro.mesorregiao != meso
            ):
                micro.nome = ibge_mun["microrregiao"]["nome"]
                micro.mesorregiao = meso
                micro.save()
                self.micro_atualizadas.append(micro)
                self.admin_log_change(micro, "Atualizada pelo IBGE")
            # Atualiza ou cria o município #
            try:
                sigi_mun = Municipio.objects.get(codigo_ibge=ibge_mun["id"])
            except Municipio.DoesNotExist:
                sigi_mun = Municipio(
                    codigo_ibge=ibge_mun["id"],
                    microrregiao=micro,
                    nome=ibge_mun["nome"],
                    uf_id=uf_id,
                    populacao=0,
                    idh=0.0,
                )
                sigi_mun.save()
                self.municipios_novos.append(sigi_mun)
                self.admin_log_addition(
                    sigi_mun, "Novo município encontrado no IBGE"
                )
            if (
                sigi_mun.nome != ibge_mun["nome"]
                or sigi_mun.uf_id != uf_id
                or sigi_mun.microrregiao != micro
            ):
                sigi_mun.nome = ibge_mun["nome"]
                sigi_mun.uf_id = uf_id
                sigi_mun.microrregiao = micro
                sigi_mun.save()
                self.municipios_atualizados.append(sigi_mun)
                self.admin_log_change(sigi_mun, "Atualizada pelo IBGE")
