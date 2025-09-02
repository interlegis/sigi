import lxml
from difflib import SequenceMatcher
from moodle import Moodle
from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from sigi.apps.utils import to_ascii
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.casas.models import Orgao


CAR_ESP = {x: " " for x in range(33, 65) if x < 48 or x > 58}
CONECTIVOS = ["a", "e", "o", "da", "de", "do", "na", "no", "em"]


def canonize_full(s):
    """canoniza uma string removendo símbolos, artigos e outros conectivos

    Args:
        s (str): A string a ser canonizada

    Returns:
        (str, list): a string canonizada e a lista de palavras
    """
    s = to_ascii(s.lower()).strip().translate(CAR_ESP)
    palavras = [
        p.strip()
        for p in s.split(" ")
        if p.strip() != "" and p.strip() not in CONECTIVOS
    ]
    s = " ".join(palavras)
    return (s, palavras)


def canonize(s):
    """canoniza uma string retornando apenas a string canonizada

    Args:
        s (str): A string a ser canonizada

    Returns:
        str: a string canonizada
    """
    return canonize_full(s)[0]


class SaberesSyncException(Exception):
    @property
    def message(self):
        return str(self)


class EventoSaberes(Moodle):
    _inscritos = None
    _participantes = None
    _aprovados = None
    evento = None
    _ufs = None

    def __init__(self, evento):
        url = f"{settings.MOODLE_BASE_URL}/webservice/rest/server.php"
        super().__init__(url, settings.MOODLE_API_TOKEN)
        self.evento = evento
        self._inscritos = None
        self._participantes = None
        self._aprovados = None
        self._ufs = {
            canonize(uf.nome): uf for uf in UnidadeFederativa.objects.all()
        }

    def get_inscritos(self):
        if self.evento.moodle_courseid is None:
            raise SaberesSyncException(
                _(
                    f"O evento {self.evento} não tem curso associado no Saberes"
                ),
            )

        if self._inscritos is None:
            try:
                self._inscritos = self.post(
                    "core_enrol_get_enrolled_users",
                    courseid=self.evento.moodle_courseid,
                )
            except Exception as e:
                raise SaberesSyncException(
                    _(
                        "Ocorreu um erro ao acessar o curso no Saberes com "
                        f"a mensagem {e.message}"
                    ),
                )
            for i in self._inscritos:
                if "customfields" in i:
                    i["dictcustomfields"] = {
                        f["shortname"]: canonize(
                            lxml.html.fromstring(f["value"]).text_content()
                        )
                        for f in i["customfields"]
                    }
                    uf_nome = (
                        i["dictcustomfields"][settings.MOODLE_UF_CUSTOMFIELD]
                        if settings.MOODLE_UF_CUSTOMFIELD
                        in i["dictcustomfields"]
                        else None
                    )
                    i["uf"] = (
                        self._ufs[uf_nome] if uf_nome in self._ufs else None
                    )
        return self._inscritos

    def get_participantes(self):
        if self._participantes is None:
            self._participantes = list(
                filter(
                    lambda u: any(
                        r["roleid"] in settings.MOODLE_STUDENT_ROLES
                        for r in u["roles"]
                    ),
                    self.get_inscritos(),
                )
            )
        return self._participantes

    def get_aprovados(self):
        if self._aprovados is None:
            for participante in self.get_participantes():
                try:
                    participante["completion_data"] = self.post(
                        "core_completion_get_course_completion_status",
                        courseid=self.evento.moodle_courseid,
                        userid=participante["id"],
                    )
                except Exception:
                    participante["completed"] = False
                    participante["completion_data"] = None
                    continue
                participante["completed"] = participante["completion_data"][
                    "completionstatus"
                ]["completed"] or any(
                    filter(
                        lambda c: c["type"]
                        == settings.MOODLE_COMPLETE_CRITERIA_TYPE
                        and c["complete"],
                        participante["completion_data"]["completionstatus"][
                            "completions"
                        ],
                    )
                )
            self._aprovados = list(
                filter(lambda p: p["completed"], self.get_participantes())
            )
        return self._aprovados

    def identifica_orgaos(self):
        obj_list = (
            Orgao.objects.all()
            .order_by()
            .annotate(uf_sigla=models.F("municipio__uf__sigla"))
        )
        assembleias = obj_list.filter(tipo__sigla="AL")
        orgaos = [(o, canonize(f"{o.nome} {o.uf_sigla}")) for o in obj_list]
        siglados = {canonize(o.sigla): o for o in obj_list if o.sigla != ""}
        siglados.update({canonize(f"ALE{o.uf_sigla}"): o for o in assembleias})
        siglados.update({canonize(f"AL{o.uf_sigla}"): o for o in assembleias})
        kcm = ["camara", "municipal", "vereadores"]
        kal = ["assembleia", "legislativa", "estado"]
        ufs = self._ufs
        try:
            senado = Orgao.objects.get(nome__iexact="senado federal")
        except Exception:
            senado = None

        def get_names(name, uf, municipio):
            municipio = canonize(municipio)
            uf_sigla = canonize(uf.sigla) if uf else None
            name, palavras = canonize_full(name)
            names = [name]
            # Acrescenta uma versão com a sigla do estado se já não tiver #
            if uf_sigla and uf_sigla not in palavras:
                names.insert(0, f"{name} {uf_sigla}")  # Coloca como primeiro
            # Corrige grafia das palavras-chave para Câmara
            matches = {
                s: [
                    p
                    for p in palavras
                    if SequenceMatcher(a=s, b=p).ratio() > 0.8
                ]
                for s in kcm
            }
            for kw in matches:
                for s in matches[kw]:
                    name = name.replace(s, kw)
            # Elimina o termo vereadores
            if "vereadores" in name:
                if "municipal" in name:
                    name = name.replace("vereadores", "")  # Só elimina
                else:
                    name = name.replace(
                        "vereadores", "municipal"
                    )  # troca por municipal
            names.append(canonize(name))
            if "camara" in name:
                if "municipal" not in name:
                    name = name.replace("camara", "camara municipal")
                    names.append(canonize(name))
                # Cria versão canonica com o nome do municipio e a UF
                if uf_sigla:
                    names.append(
                        canonize(f"camara municipal {municipio} {uf_sigla}")
                    )
            # Corrige grafia das palavras-chave para Assembleia
            matches = {
                s: [
                    p
                    for p in palavras
                    if SequenceMatcher(a=s, b=p).ratio() > 0.8
                ]
                for s in kal
            }
            for kw in matches:
                for s in matches[kw]:
                    name = name.replace(s, kw)
            if "assembleia" in name:
                name = name.replace("estado", "")  # Elimina o termo "estado"
                # Adiciona "legislativa" se necessário
                if "legislativa" not in name:
                    name = name.replace("assembleia", "assembleia legislativa")
                names.append(canonize(name))
                # Cria versão canonica com o nome e sigla da UF
                if uf_sigla:
                    names.append(
                        canonize(f"assembleia legislativa {uf} {uf_sigla}")
                    )
            # remove duplicados sem mudar a ordem
            names = list(dict.fromkeys(names))
            return names

        for p in self.get_participantes():
            if (
                "dictcustomfields" in p
                and settings.MOODLE_ORGAO_CUSTOMFIELD in p["dictcustomfields"]
                and p["dictcustomfields"][
                    settings.MOODLE_ORGAO_CUSTOMFIELD
                ].strip()
                != ""
            ):
                nome_orgao = p["dictcustomfields"][
                    settings.MOODLE_ORGAO_CUSTOMFIELD
                ]
                municipio = (
                    p["dictcustomfields"][
                        settings.MOODLE_MUNICIPIO_CUSTOMFIELD
                    ]
                    if settings.MOODLE_MUNICIPIO_CUSTOMFIELD
                    in p["dictcustomfields"]
                    else p["city"] if "city" in p else ""
                )
                nomes_possiveis = get_names(nome_orgao, p["uf"], municipio)
                for nome in nomes_possiveis:
                    semelhantes = Orgao.get_semelhantes(nome, orgaos)
                    if len(semelhantes) > 0:
                        p["orgao"] = semelhantes[-1][0]
                        break
                if "orgao" not in p:
                    # Buscar por sigla
                    nome, palavras = canonize_full(nome_orgao)
                    for nome in palavras:
                        if nome in siglados:
                            p["orgao"] = siglados[nome]
                            break
            # Pode ser servidor do Senado - última chance ;D
            if (
                "orgao" not in p
                and senado is not None
                and settings.MOODLE_SERVSENADO_CUSTOMFIELD
                in p["dictcustomfields"]
                and not p["dictcustomfields"][
                    settings.MOODLE_SERVSENADO_CUSTOMFIELD
                ].startswith("nao ")
            ):
                p["orgao"] = senado
