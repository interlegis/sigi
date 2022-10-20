import datetime
import docutils.core
import json
from pathlib import Path
from django.conf import settings
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.servicos import generate_instance_name
from sigi.apps.servicos.models import Servico, TipoServico
from sigi.apps.casas.models import Orgao


class Job(DailyJob):
    help = _("Sincronização dos Serviços SEIT na infraestrutura")
    _nomes_gerados = None
    _errors = {}
    _infos = {}

    def execute(self):
        print(
            _(
                "Sincroniza os serviços SEIT a partir da infraestrutura."
                f" Início: {datetime.datetime.now(): %d/%m/%Y %H:%M:%S}"
            )
        )
        self._nomes_gerados = {
            generate_instance_name(o): o
            for o in Orgao.objects.filter(tipo__legislativo=True)
        }
        print(f"\t{len(self._nomes_gerados)} órgãos que podem ter instâncias.")

        for tipo in TipoServico.objects.filter(modo="H").exclude(
            tipo_rancher=""
        ):
            print(
                _(
                    f"\tProcessando {tipo.nome}."
                    f" Início: {datetime.datetime.now():%H:%M:%S}."
                ),
                end="",
            )
            self.process(tipo)
            print(f" Término: {datetime.datetime.now():%H:%M:%S}.")

        print("Relatório final:\n================")
        self.report()

        print(_(f"Término: {datetime.datetime.now(): %d/%m/%Y %H:%M:%S}"))

    def process(self, tipo):
        NAO_CONSTA = "*não-consta-no-rancher*"
        self._errors[tipo] = []
        self._infos[tipo] = []

        file_path = settings.HOSPEDAGEM_PATH / tipo.arquivo_rancher
        if not file_path.exists() or not file_path.is_file():
            self._errors[tipo].append(_(f"Arquivo {file_path} não encontado."))
            return

        with open(file_path, "r") as f:
            json_data = json.load(f)

        portais = [
            item
            for item in json_data["items"]
            if item["spec"]["chart"]["metadata"]["name"] == tipo.tipo_rancher
        ]

        encontrados = 0
        novos = 0
        desativados = 0

        self._infos[tipo].append(
            _(f"{len(portais)} {tipo.nome} encontrados no Rancher")
        )

        # Atualiza portais existentes e cria novos #
        for p in portais:
            iname = p["metadata"]["name"]
            if tipo.spec_rancher in p["spec"]["values"]:
                if "hostname" in p["spec"]["values"][tipo.spec_rancher]:
                    hostname = p["spec"]["values"][tipo.spec_rancher][
                        "hostname"
                    ]
                elif "domain" in p["spec"]["values"][tipo.spec_rancher]:
                    hostname = p["spec"]["values"][tipo.spec_rancher]["domain"]
                else:
                    hostname = NAO_CONSTA
                    self._errors[tipo].append(
                        _(
                            f"Instância {iname} de {tipo.nome} sem URL no "
                            "rancher"
                        )
                    )

                if "hostprefix" in p["spec"]["values"][tipo.spec_rancher]:
                    prefix = p["spec"]["values"][tipo.spec_rancher][
                        "hostprefix"
                    ]
                    hostname = f"{prefix}.{hostname}"
                elif tipo.prefixo_padrao != "":
                    hostname = f"{tipo.prefixo_padrao}.{hostname}"
            else:
                hostname = NAO_CONSTA
                self._errors[tipo].append(
                    _(f"Instância {iname} de {tipo.nome} sem URL no rancher")
                )

            try:
                portal = Servico.objects.get(instancia=iname, tipo_servico=tipo)
                encontrados += 1
            except Servico.DoesNotExist:
                if iname in self._nomes_gerados:
                    orgao = self._nomes_gerados[iname]
                    portal = Servico(
                        casa_legislativa=orgao,
                        tipo_servico=tipo,
                        instancia=iname,
                        data_ativacao=p["spec"]["info"]["firstDeployed"][:10],
                    )
                    self._infos[tipo].append(
                        _(
                            f"Criada instância {iname} de {tipo.nome} para "
                            f"{orgao.nome} ({orgao.municipio.uf.sigla})"
                        )
                    )
                    novos += 1
                else:
                    self._errors[tipo].append(
                        _(
                            f"{iname} ({hostname}) não parece pertencer a "
                            "nenhum órgão."
                        )
                    )
                    continue
            # atualiza o serviço no SIGI
            portal.versao = (
                p["spec"]["values"]["image"]["tag"]
                if "image" in p["spec"]["values"]
                else ""
            )
            if NAO_CONSTA in hostname:
                portal.url = ""
            else:
                portal.url = f"https://{hostname}/"
            portal.hospedagem_interlegis = True
            portal.save()

        # Desativa portais registrados no SIGI que não estão no Rancher #
        nomes_instancias = [p["metadata"]["name"] for p in portais]
        for portal in Servico.objects.filter(
            tipo_servico=tipo, data_desativacao=None, hospedagem_interlegis=True
        ):
            if (
                portal.instancia == ""
                or portal.instancia not in nomes_instancias
            ):
                portal.data_desativacao = timezone.localdate()
                portal.motivo_desativacao = _("Não encontrado no Rancher")
                portal.save()
                self._infos[tipo].append(
                    f"{portal.instancia} ({portal.url}) de "
                    f"{portal.casa_legislativa.nome} desativado pois não "
                    "foi encontrado no Rancher."
                )
                desativados += 1

        self._infos[tipo].append(
            _(f"{encontrados} {tipo.nome} do Rancher encontrados no SIGI")
        )
        self._infos[tipo].append(
            _(f"{novos} novos {tipo.nome} criados no SIGI")
        )
        self._infos[tipo].append(
            _(f"{desativados} {tipo.nome} desativados no SIGI")
        )

    def report(self):
        rst = render_to_string(
            "servicos/emails/report_sincroniza_rancher.rst",
            {
                "erros": self._errors,
                "infos": self._infos,
                "title": _("Resultado da sincronização do SIGI com o Rancher"),
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
