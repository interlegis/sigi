def generate_instance_name(orgao):
    import re
    from sigi.apps.utils import to_ascii

    # Orgao deve ser uma instância de sigi.apps.casas.models.Orgao #
    if orgao.tipo.sigla == "CM":
        return (
            re.sub("\W+", "", to_ascii(orgao.municipio.nome)).lower()
            + "-"
            + orgao.municipio.uf.sigla.lower()
        )
    elif orgao.tipo.sigla == "CT":
        return "cl-df"
    elif orgao.tipo.sigla == "AL":
        return f"al-{orgao.municipio.uf.sigla.lower()}"
    elif orgao.tipo.sigla in ["CD", "SF"]:
        return re.sub("\W+", "", to_ascii(orgao.nome)).lower()
    else:
        return f"{orgao.tipo.sigla.lower()}-{orgao.municipio.uf.sigla.lower()}"
