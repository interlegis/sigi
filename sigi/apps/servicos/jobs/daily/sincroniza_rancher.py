import json
import shutil
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from django_extensions.management.jobs import DailyJob
from sigi.apps.servicos import generate_instance_name, nomeia_instancias
from sigi.apps.servicos.models import Servico, TipoServico
from sigi.apps.casas.models import Orgao
from sigi.apps.utils.management.jobs import JobReportMixin


class Job(JobReportMixin, DailyJob):
    help = _("Sincronização dos Serviços SEIT na infraestrutura")
    report_template = "servicos/emails/report_sincroniza_rancher.rst"
    nomes_gerados = None
    errors = {}
    infos = {}

    def do_job(self):
        self.nomes_gerados = {
            generate_instance_name(o): o
            for o in Orgao.objects.filter(tipo__legislativo=True)
        }

        for tipo in TipoServico.objects.filter(modo="H").exclude(
            tipo_rancher=""
        ):
            self.process(tipo)

        try:
            shutil.rmtree(settings.HOSPEDAGEM_PATH)
        except Exception as e:
            pass

        self.report_data = {
            "erros": self.errors,
            "infos": self.infos,
        }

    def process(self, tipo):
        nomeia_instancias(
            servicos=Servico.objects.filter(
                tipo_servico=tipo, data_desativacao=None, instancia=""
            ),
            user=self.sys_user,
        )
        NAO_CONSTA = "*não-consta-no-rancher*"
        self.errors[tipo] = []
        self.infos[tipo] = []

        file_path = settings.HOSPEDAGEM_PATH / tipo.arquivo_rancher
        if not file_path.exists() or not file_path.is_file():
            self.errors[tipo].append(_(f"Arquivo {file_path} não encontado."))
            return

        json_data = json.loads(file_path.read_text())

        portais = [
            item
            for item in json_data["items"]
            if item["kind"].lower() == "app"
            and item["spec"]["chart"]["metadata"]["name"] == tipo.tipo_rancher
        ]
        namespaces = [
            item
            for item in json_data["items"]
            if item["kind"].lower() == "namespace"
        ]

        encontrados = 0
        novos = 0
        desativados = 0

        self.infos[tipo].append(
            _(f"{len(portais)} {tipo.nome} encontrados no Rancher")
        )

        # Atualiza portais existentes e cria novos #
        for p in portais:
            namespace = p["metadata"]["namespace"]
            name = p["metadata"]["name"]
            if tipo.spec_rancher in p["spec"]["values"]:
                if "hostname" in p["spec"]["values"][tipo.spec_rancher]:
                    hostname = p["spec"]["values"][tipo.spec_rancher][
                        "hostname"
                    ]
                elif "domain" in p["spec"]["values"][tipo.spec_rancher]:
                    hostname = p["spec"]["values"][tipo.spec_rancher]["domain"]
                else:
                    hostname = NAO_CONSTA
                    self.errors[tipo].append(
                        _(
                            f"Instância {namespace} de {tipo.nome} sem URL no "
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
                self.errors[tipo].append(
                    _(
                        f"Instância {namespace} de {tipo.nome} sem URL no rancher"
                    )
                )

            nova_versao = (
                p["spec"]["values"]["image"]["tag"]
                if "image" in p["spec"]["values"]
                else ""
            )
            if NAO_CONSTA in hostname:
                nova_url = ""
            else:
                nova_url = f"https://{hostname}/"

            # Identificar registro de suspensão do namespace
            suspenso = [
                ns["metadata"]["annotations"]["suspenso"]
                for ns in namespaces
                if ns["metadata"]["name"] == namespace
                and "suspenso" in ns["metadata"]["annotations"]
            ]

            try:
                portal = Servico.objects.get(
                    instancia=namespace,
                    tipo_servico=tipo,
                    data_desativacao=None,
                )
                encontrados += 1
            except Servico.MultipleObjectsReturned:
                self.errors[tipo].append(
                    _(
                        f"Existe mais de um registro ativo da instância "
                        f"{namespace} de {tipo}."
                    )
                )
                continue
            except Servico.DoesNotExist:
                # Se a instância está suspensa, não precisa criar o registro
                # no SIGI.

                if suspenso:
                    continue

                if (
                    namespace in self.nomes_gerados
                    or name in self.nomes_gerados
                ):
                    orgao = (
                        self.nomes_gerados[namespace]
                        if namespace in self.nomes_gerados
                        else self.nomes_gerados[name]
                    )
                    portal = Servico(
                        casa_legislativa=orgao,
                        tipo_servico=tipo,
                        instancia=namespace,
                        url=nova_url,
                        versao=nova_versao,
                        data_ativacao=p["spec"]["info"]["firstDeployed"][:10],
                        hospedagem_interlegis=True,
                    )
                    portal.save()
                    self.admin_log_addition(portal, "Criado no Rancher")
                    novos += 1
                    self.infos[tipo].append(
                        _(
                            f"Criada instância {namespace} de {tipo.nome} para "
                            f"{orgao.nome} ({orgao.municipio.uf.sigla})"
                        )
                    )
                else:
                    self.errors[tipo].append(
                        _(
                            f"{namespace} ({hostname}) não parece pertencer a "
                            "nenhum órgão."
                        )
                    )
                    continue
            # se tem registro de suspensão do namespace
            if suspenso:
                # Desativar o portal no SIGI
                portal.data_desativacao = timezone.localdate()
                portal.motivo_desativacao = (
                    "Suspenso no Rancher com os seguintes apontamentos:"
                    + ", ".join([f'"{s}"' for s in suspenso])
                )
                portal.save()
                self.admin_log_change(portal, portal.motivo_desativacao)
            # atualiza o serviço no SIGI
            if (
                nova_versao != portal.versao
                or nova_url != portal.url
                or not portal.hospedagem_interlegis
            ):
                message = (
                    "Atualizado no Rancher: "
                    + (
                        f"Versão: de '{portal.versao}' para '{nova_versao}' "
                        if portal.versao != nova_versao
                        else ""
                    )
                    + (
                        f"Url: de '{portal.url}' para '{nova_url}' "
                        if portal.url != nova_url
                        else ""
                    )
                    + (
                        "hospedagem interlegis"
                        if not portal.hospedagem_interlegis
                        else ""
                    )
                )
                portal.versao = nova_versao
                portal.url = nova_url
                portal.hospedagem_interlegis = True
                portal.save()
                self.admin_log_change(portal, message)

        # Desativa portais registrados no SIGI que não estão no Rancher #
        nomes_instancias = [p["metadata"]["name"] for p in portais]
        for portal in Servico.objects.filter(
            tipo_servico=tipo,
            data_desativacao=None,
            hospedagem_interlegis=True,
        ):
            if (
                portal.instancia == ""
                or portal.instancia not in nomes_instancias
            ):
                portal.data_desativacao = timezone.localdate()
                portal.motivo_desativacao = _("Não encontrado no Rancher")
                portal.save()
                self.admin_log_change(portal, "Desativado no Rancher")
                self.infos[tipo].append(
                    f"{portal.instancia} ({portal.url}) de "
                    f"{portal.casa_legislativa.nome} desativado pois não "
                    "foi encontrado no Rancher."
                )
                desativados += 1

        self.infos[tipo].append(
            _(f"{encontrados} {tipo.nome} do Rancher encontrados no SIGI")
        )
        self.infos[tipo].append(
            _(f"{novos} novos {tipo.nome} criados no SIGI")
        )
        self.infos[tipo].append(
            _(f"{desativados} {tipo.nome} desativados no SIGI")
        )
