def generate_instance_name(orgao):
    import re
    from sigi.apps.utils import to_ascii

    # Orgao deve ser uma instância de sigi.apps.casas.models.Orgao #
    if orgao.tipo.sigla == "CM":
        return (
            re.sub(r"\W+", "", to_ascii(orgao.municipio.nome)).lower()
            + "-"
            + orgao.municipio.uf.sigla.lower()
        )
    elif orgao.tipo.sigla == "CT":
        return "cl-df"
    elif orgao.tipo.sigla == "AL":
        return f"al-{orgao.municipio.uf.sigla.lower()}"
    elif orgao.tipo.sigla in ["CD", "SF"]:
        return re.sub(r"\W+", "", to_ascii(orgao.nome)).lower()
    else:
        return f"{orgao.tipo.sigla.lower()}-{orgao.municipio.uf.sigla.lower()}"


def nomeia_instancias(servicos, user=None):
    from django.contrib.admin.models import LogEntry, CHANGE
    from django.contrib.contenttypes.models import ContentType
    from django.utils.translation import gettext as _

    for s in servicos.filter(instancia=""):
        s.instancia = generate_instance_name(s.casa_legislativa)
        s.save()
        if user:
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(type(s)).pk,
                object_id=s.id,
                object_repr=str(s),
                action_flag=CHANGE,
                change_message=_("Adicionado nome automático da instância"),
            )
