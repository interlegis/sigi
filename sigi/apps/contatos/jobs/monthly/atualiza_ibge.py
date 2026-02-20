import sys
from django_extensions.management.jobs import MonthlyJob
from django.conf import settings
from django.contrib.admin.models import ADDITION, CHANGE
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django.utils.translation import gettext as _, ngettext
from ibge.localidades import Estados, Municipios
from sigi.apps.contatos.models import (
    UnidadeFederativa,
    Mesorregiao,
    Microrregiao,
    Municipio,
)
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils.management.jobs import AdminJobMixin


class Job(AdminJobMixin, MonthlyJob):
    help = _(
        "Atualiza Unidades Federativas, mesorregiões, microrregiões e "
        "municípios com dados do IBGE"
    )

    def execute(self):
        self.atualiza_ufs()
        self.atualiza_municipios()

    def atualiza_ufs(self):
        regioes_map = {"N": "NO", "NE": "NE", "SE": "SE", "S": "SL", "CO": "CO"}
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
                self.admin_log_addition(
                    sigi_uf, _("Nova UF encontrada no IBGE")
                )
                print(
                    _("Nova UF encontrada no IBGE: {sigla}, {nome}").format(
                        sigla=sigi_uf.sigla, nome=sigi_uf.nome
                    )
                )
            if (
                sigi_uf.nome != ibge_uf["nome"]
                or sigi_uf.sigla != ibge_uf["sigla"]
                or sigi_uf.regiao != regiao
            ):
                print(
                    _(
                        "UF {codigo_ibge} atualizada pelo IBGE: "
                        "{regiao} => {nova_regiao}, {sigla} => {nova_sigla}, "
                        "{nome} => {novo_nome}"
                    ).format(
                        codigo_ibge=sigi_uf.codigo_ibge,
                        regiao=sigi_uf.regiao,
                        nova_regiao=regiao,
                        sigla=sigi_uf.sigla,
                        nova_sigla=ibge_uf["sigla"],
                        nome=sigi_uf.nome,
                        novo_nome=ibge_uf["nome"],
                    )
                )
                sigi_uf.nome = ibge_uf["nome"]
                sigi_uf.sigla = ibge_uf["sigla"]
                sigi_uf.regiao = regiao
                sigi_uf.save()
                self.admin_log_change(sigi_uf, _("Atualizada pelo IBGE"))

    def atualiza_municipios(self):
        for ibge_mun in Municipios().json():
            if ibge_mun["microrregiao"]:
                uf_id = ibge_mun["microrregiao"]["mesorregiao"]["UF"]["id"]
                uf_nome = ibge_mun["microrregiao"]["mesorregiao"]["UF"]["nome"]
            else:
                uf_id = ibge_mun["regiao-imediata"]["regiao-intermediaria"][
                    "UF"
                ]["id"]
                uf_nome = ibge_mun["regiao-imediata"]["regiao-intermediaria"][
                    "UF"
                ]["nome"]
            try:
                uf = UnidadeFederativa.objects.get(codigo_ibge=uf_id)
            except UnidadeFederativa.DoesNotExist:
                print(
                    _(
                        "* ERRO: UF {uf_id} - {uf_nome} não encontrada no SIGI"
                        " ao processar o município do IBGE {mun_id} {mun_nome}"
                    ).format(
                        uf_id=uf_id, uf_nome=uf_nome, mun_id=ibge_mun["id"]
                    )
                )
                continue
            meso = self.atualiza_meso(ibge_mun, uf)
            micro = self.atualiza_micro(ibge_mun, meso)
            # Atualiza ou cria o município #
            try:
                sigi_mun = Municipio.objects.get(codigo_ibge=ibge_mun["id"])
            except Municipio.DoesNotExist:
                sigi_mun = Municipio(
                    codigo_ibge=ibge_mun["id"],
                    microrregiao=micro,
                    nome=ibge_mun["nome"],
                    uf=uf,
                    populacao=0,
                    idh=0.0,
                )
                sigi_mun.save()
                print(
                    _(
                        "Novo município {nome} da UF {uf_nome} criado pelo IBGE"
                    ).format(nome=sigi_mun.nome, uf_nome=sigi_mun.uf.nome)
                )
                self.admin_log_addition(
                    sigi_mun, "Novo município encontrado no IBGE"
                )
            if (
                sigi_mun.nome != ibge_mun["nome"]
                or sigi_mun.uf_id != uf_id
                or sigi_mun.microrregiao != micro
            ):
                print(
                    _(
                        "Município {codigo_ibge} alterado no IBGE. "
                        "{old_name} => {new_name}, {old_uf} => {new_uf}, "
                        "{old_micro} => {new_micro}"
                    ).format(
                        codigo_ibge=sigi_mun.codigo_ibge,
                        old_name=sigi_mun.nome,
                        new_name=ibge_mun["nome"],
                        old_uf=sigi_mun.uf.nome,
                        new_uf=uf_nome,
                        old_micro=sigi_mun.microrregiao.nome,
                        new_micro=micro.nome,
                    )
                )
                sigi_mun.nome = ibge_mun["nome"]
                sigi_mun.uf_id = uf_id
                sigi_mun.microrregiao = micro
                sigi_mun.save()
                self.admin_log_change(sigi_mun, "Atualizada pelo IBGE")

    def atualiza_meso(self, ibge_mun, uf):
        # Atualiza ou cria mesorregião #
        if ibge_mun["microrregiao"]:
            cod_meso = ibge_mun["microrregiao"]["mesorregiao"]["id"]
            nome_meso = ibge_mun["microrregiao"]["mesorregiao"]["nome"]
        else:
            cod_meso = ibge_mun["regiao-imediata"]["regiao-intermediaria"]["id"]
            nome_meso = ibge_mun["regiao-imediata"]["regiao-intermediaria"][
                "nome"
            ]
        try:
            meso = Mesorregiao.objects.get(codigo_ibge=cod_meso)
        except Mesorregiao.DoesNotExist:
            meso = Mesorregiao(
                codigo_ibge=cod_meso,
                uf=uf,
                nome=nome_meso,
            )
            meso.save()
            print(
                _("Incluída nova mesorregião {nome} na UF {uf}").format(
                    nome=meso.nome, uf=uf.nome
                )
            )
            self.admin_log_addition(
                meso, _("Nova mesorregião encontrada no IBGE")
            )
        if meso.nome != nome_meso:
            print(
                _(
                    "Nome da mesorregião {codigo_ibge} mudou de {old_name} "
                    "para {new_name}"
                ).format(
                    codigo_ibge=meso.codigo_ibge,
                    old_name=meso.nome,
                    new_name=nome_meso,
                )
            )
            meso.nome = nome_meso
            meso.save()
            self.admin_log_change(meso, _("Atualizada pelo IBGE"))
        return meso

    def atualiza_micro(self, ibge_mun, meso):
        # Atualiza ou cria a microrregião #
        if ibge_mun["microrregiao"]:
            cod_micro = int(
                str(ibge_mun["microrregiao"]["mesorregiao"]["id"])
                + str(ibge_mun["microrregiao"]["id"])[-3:]
            )
            nome_micro = ibge_mun["microrregiao"]["nome"]
        else:
            cod_micro = int(
                str(ibge_mun["regiao-imediata"]["regiao-intermediaria"]["id"])
                + str(ibge_mun["regiao-imediata"]["id"])[-3:]
            )
            nome_micro = ibge_mun["regiao-imediata"]["nome"]

        try:
            micro = Microrregiao.objects.get(codigo_ibge=cod_micro)
        except Microrregiao.DoesNotExist:
            micro = Microrregiao(
                codigo_ibge=cod_micro,
                mesorregiao=meso,
                nome=nome_micro,
            )
            micro.save()
            print(
                _("Incluída nova microrregião {nome} na UF {uf}").format(
                    nome=micro.nome, uf=meso.uf.nome
                )
            )
            self.admin_log_addition(
                micro, _("Nova microrregião encontrada no IBGE")
            )
        if micro.nome != nome_micro or micro.mesorregiao != meso:
            print(
                _(
                    "Microrregião {codigo_ibge} atualizada pelo IBGE: "
                    "{old_name} => {new_name}, {old_meso} => {new_meso}"
                ).format(
                    codigo_ibge=micro.codigo_ibge,
                    old_name=micro.nome,
                    new_name=nome_micro,
                    old_meso=micro.mesorregiao.nome,
                    new_meso=meso.nome,
                )
            )
            micro.nome = nome_micro
            micro.mesorregiao = meso
            micro.save()
            self.admin_log_change(micro, _("Atualizada pelo IBGE"))
        return micro
