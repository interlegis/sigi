import csv
import datetime
import re
from urllib.parse import urlparse
from sigi.apps.casas.models import Orgao


def run():
    f = open("/tmp/contato.csv", "r", encoding="iso8859-1")

    reader = csv.DictReader(f, delimiter=";")
    reader.fieldnames

    dados = {r["IDIBGE"]: r for r in reader}
    encontrados = list(
        filter(
            lambda x: dados[x]["CAIXA"] == "Encontrado"
            and dados[x]["ENDERECO"] != ""
            and dados[x]["TELEFONE"] != ""
            and dados[x]["SITE"] != ""
            and dados[x]["Email"] != "",
            dados,
        )
    )

    jan20 = datetime.date(2020, 1, 1)

    patterns = [
        re.compile(
            "(?P<logradouro>.+)- ?(?P<bairro>.+), ?(.+)- ?(.+), ?(?P<cep>\d{5}-\d{3})"
        ),
        re.compile(
            "(?P<logradouro>.+,.+), ?(.+)- ?(.+), ?(?P<cep>\d{5}-\d{3})"
        ),
        re.compile("(?P<logradouro>.+), ?(.+-.+), ?(?P<cep>\d{5}-\d{3})"),
        re.compile("(.+)- ?(.+), ?(?P<cep>\d{5}-\d{3})"),
        re.compile("(?P<logradouro>.+, ?\d*) ?- ?(?P<bairro>.+),(.+)-(.+)"),
    ]

    for id in encontrados:
        o = Orgao.objects.get(tipo__sigla="CM", municipio__codigo_ibge=id)
        salvar = False
        if (
            dados[id]["ENDERECO"] != ""
            and dados[id]["ENDERECO"] != o.logradouro
            and (o.ult_alt_endereco and o.ult_alt_endereco.date() < jan20)
        ):
            m = None
            for pattern in patterns:
                m = pattern.search(dados[id]["ENDERECO"])
                if m is not None:
                    break
            if m is not None:
                addr = m.groupdict()
                if "logradouro" in addr:
                    o.logradouro = addr["logradouro"]
                if "bairro" in addr:
                    o.bairro = addr["bairro"]
                if "cep" in addr:
                    o.cep = addr["cep"]
                salvar = True
            else:
                o.logradouro = dados[id]["ENDERECO"]
                salvar = True
        if (
            dados[id]["TELEFONE"] != ""
            and dados[id]["TELEFONE"] != o.telefone_geral
        ):
            o.telefone_geral = dados[id]["TELEFONE"]
            salvar = True
        if dados[id]["SITE"] != "" and dados[id]["SITE"] != o.pagina_web:
            parsed_url = urlparse(dados[id]["SITE"])
            url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
            o.pagina_web = url
            salvar = True
        if dados[id]["Email"] != "" and dados[id]["Email"] != o.email:
            o.email = dados[id]["Email"]
            salvar = True
        if salvar:
            if len(o.logradouro) > 100:
                o.logradouro = o.logradouro[:100]
            o.save()
            print(o.nome)
