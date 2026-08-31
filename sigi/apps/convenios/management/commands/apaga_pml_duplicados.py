import re
import requests
from django.core.management.base import BaseCommand

from sigi.apps.convenios.models import Convenio


class Command(BaseCommand):
    help = "Apaga convênios PML que são duplicatas de ACTs."

    def handle(self, *args, **options):
        cprint = self.stdout.write
        sSuccess = self.style.SUCCESS
        sError = self.style.ERROR

        cprint("Buscando dados de ACTS no Gescon...")
        response = requests.get(
            "https://adm.senado.gov.br/gestao-contratos/api/contratos/busca"
            "?subespecie=AC"
        )
        if response.status_code != 200:
            cprint(
                sError(f"Erro HTTP: {response.status_code}: {response.reason}")
            )
            return
        if "json" not in response.headers["content-type"]:
            cprint(
                sError(
                    f"Response não é json: {response.headers['content-type']}"
                )
            )
            return
        jdata = response.json()
        cprint(sSuccess(f"{len(jdata)} registros recebidos do Gescon!"))

        cprint("Identificando ACTs duplicados no SIGI...")
        acts = {
            c.num_processo_sf: [c]
            for c in Convenio.objects.filter(projeto__sigla="ACT").exclude(
                num_processo_sf=""
            )
        }
        for c in Convenio.objects.exclude(num_processo_sf=""):
            if c.num_processo_sf in acts and not any(
                [a.id == c.id for a in acts[c.num_processo_sf]]
            ):
                acts[c.num_processo_sf].append(c)
        duplicados = [(k, v) for k, v in acts.items() if len(v) > 1]
        cprint(sSuccess(f"{len(duplicados)} processos com duplicidade"))

        cprint("Tratando duplas ACT x outro tipo de projeto...")
        duplas = [
            (k, v)
            for k, v in duplicados
            if len(v) == 2 and any([c.projeto.sigla == "ACT" for c in v])
        ]
        cprint(f"{len(duplas)} duplas idenfiticadas...")

        for k, v in duplas:
            act = [c for c in v if c.projeto.sigla == "ACT"][0]
            processo = re.sub(r"\D", "", k)
            recs = list(filter(lambda d: d["processo"] in processo, jdata))
            if len(recs) == 0:
                cprint(sError(f"Processo {k} não aparece no gescon"))
                continue
            elif len(recs) > 1:
                cprint(
                    sError(
                        f"Processo {k} ocorre {len(recs)} vezes no gescon:"
                        + ", ".join([d["processo"] for d in recs])
                    )
                )
                continue
            rec = recs[0]
            if rec["numero"] != re.sub(r"\D", "", act.num_convenio):
                cprint(
                    sError(f"Número: {rec['numero']} <=> {act.num_convenio}")
                )
                continue
            if rec["cnpjCpfFornecedor"] != re.sub(
                r"\D", "", act.casa_legislativa.cnpj
            ):
                cprint(
                    sError(
                        f"Nome: {rec['cnpjCpfFornecedor']} <=> "
                        f"{act.casa_legislativa.cnpj}"
                    )
                )
                continue
            if act.observacao != rec["objeto"]:
                cprint(sError(f"Objeto: {rec['objeto']} <=> {act.observacao}"))
                continue
            for c in v:
                if c.projeto.sigla != "ACT":
                    cprint(sSuccess(f"Excluído {c}"))
                    c.delete()
