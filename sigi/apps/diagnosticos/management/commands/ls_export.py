# -*- coding: utf-8 -*-

import csv
from collections import OrderedDict
from django.core.management.base import BaseCommand, CommandError
from sigi.apps.casas.models import Funcionario
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.diagnosticos.models import Categoria, Diagnostico, Resposta

DATATYPES = {"text": "T", "float": "N", "date": "D", "one": "L", "many": "M"}


class Command(BaseCommand):
    help = """Exporta dados do diagnóstico para o formato Tab-Separated-Values
    do LimeSurvey, conforme documentado em
    https://manual.limesurvey.org/Tab_Separated_Value_survey_structure"""

    def handle(self, *args, **options):
        def normalize(l):
            return [s.encode("utf-8") for s in l]

        nonum = lambda s: s[s.index(" ") + 1 :]
        avalue = lambda e: (
            "Y" if e.title == "Sim" else "N" if e.title == "Não" else e.id
        )

        setores = [
            (i + 1, s[0], s[1])
            for i, s in enumerate(Funcionario.SETOR_CHOICES)
        ]

        if len(args) < 2:
            raise CommandError("Use: ls_export survey_id struct.txt data.csv")

        survey_id = args[0]

        lsf = csv.writer(
            open(args[1], "wb+"), delimiter="\t", quoting=csv.QUOTE_MINIMAL
        )

        struct = [
            "id",
            "token",
            "submitdate",
            "lastpage",
            "startlanguage",
            "seed",
        ]

        self.stdout.write("Exporting survey structure: ")
        # Structure headers #
        self.stdout.write("\tStructure headers...", ending=" ")
        lsf.writerow(
            [
                "id",
                "related_id",
                "class",
                "type/scale",
                "name",
                "relevance",
                "text",
                "help",
                "language",
                "validation",
                "mandatory",
                "other",
                "default",
                "same_default",
            ]
        )
        lsf.writerows(
            [
                ["", "", "S", "", "sid", "", survey_id],
                ["", "", "S", "", "format", "", "G"],
                ["", "", "S", "", "language", "", "pt-BR"],
                [
                    "",
                    "",
                    "SL",
                    "",
                    "surveyls_survey_id",
                    "",
                    survey_id,
                    "",
                    "pt-BR",
                ],
                [
                    "",
                    "",
                    "SL",
                    "",
                    "surveyls_language",
                    "",
                    "pt-BR",
                    "",
                    "pt-BR",
                ],
                [
                    "",
                    "",
                    "SL",
                    "",
                    "surveyls_title",
                    "",
                    "Diagnóstico PML".encode("utf-8"),
                    "",
                    "pt-BR",
                ],
            ]
        )
        self.stdout.write("Done!")

        # Identificação da Casa Legislativa e sua equipe #
        self.stdout.write("\tIdentificação da Casa...", ending=" ")
        lsf.writerow(
            normalize(
                [
                    "1000",
                    "",
                    "G",
                    "",
                    "Identificação da Casa",
                    "",
                    "",
                    "",
                    "pt-BR",
                ]
            )
        )
        lsf.writerow(
            normalize(
                [
                    "1001",
                    "",
                    "Q",
                    "L",
                    "c001q001",
                    "1",
                    "Região",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q001")
        lsf.writerows(
            [
                normalize(["1001", "", "A", "0", sigla, "", nome, "", "pt-BR"])
                for sigla, nome in UnidadeFederativa.REGIAO_CHOICES
            ]
        )
        lsf.writerow(
            normalize(
                [
                    "1002",
                    "",
                    "Q",
                    "!",
                    "c001q002",
                    "1",
                    "Estado (UF)",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q002")
        lsf.writerows(
            [
                normalize(
                    ["1002", "", "A", "0", u.sigla, "", u.nome, "", "pt-BR"]
                )
                for u in UnidadeFederativa.objects.all()
            ]
        )
        lsf.writerow(
            normalize(
                [
                    "1003",
                    "",
                    "Q",
                    "S",
                    "c001q003",
                    "1",
                    "Município",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q003")
        lsf.writerow(
            normalize(
                [
                    "1004",
                    "",
                    "Q",
                    "D",
                    "c001q004",
                    "1",
                    "Data de criação do município",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q004")
        lsf.writerow(
            normalize(
                [
                    "1005",
                    "",
                    "Q",
                    "S",
                    "c001q005",
                    "1",
                    "Nome da Casa",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q005")
        lsf.writerow(
            normalize(
                [
                    "1006",
                    "",
                    "Q",
                    "D",
                    "c001q006",
                    "1",
                    "Data de instalação do legislativo",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q006")
        lsf.writerow(
            normalize(
                [
                    "1007",
                    "",
                    "Q",
                    "T",
                    "c001q007",
                    "1",
                    "Endereço",
                    "",
                    "pt-BR",
                    "",
                    "N",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q007")
        lsf.writerow(
            normalize(
                [
                    "1008",
                    "",
                    "Q",
                    "S",
                    "c001q008",
                    "1",
                    "CNPJ",
                    "",
                    "pt-BR",
                    "",
                    "N",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q008")
        lsf.writerow(
            normalize(
                [
                    "1009",
                    "",
                    "Q",
                    "S",
                    "c001q009",
                    "1",
                    "E-mail principal",
                    "",
                    "pt-BR",
                    "",
                    "N",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q009")
        lsf.writerow(
            normalize(
                [
                    "1010",
                    "",
                    "Q",
                    "S",
                    "c001q010",
                    "1",
                    "Endereço Web",
                    "",
                    "pt-BR",
                    "",
                    "N",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c001q010")
        lsf.writerow(
            normalize(
                [
                    "1011",
                    "",
                    "Q",
                    ";",
                    "c001q011",
                    "1",
                    "Pessoas de contato",
                    "",
                    "pt-BR",
                    "",
                    "N",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        lsf.writerow(
            normalize(
                [
                    "101198",
                    "",
                    "SQ",
                    "1",
                    "SQ00101",
                    "",
                    "Nome",
                    "",
                    "pt-BR",
                    "",
                    "",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        lsf.writerow(
            normalize(
                [
                    "101199",
                    "",
                    "SQ",
                    "1",
                    "SQ00102",
                    "",
                    "E-mail",
                    "",
                    "pt-BR",
                    "",
                    "",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        for i, k, v in setores:
            lsf.writerow(
                normalize(
                    [
                        "10110{0}".format(i),
                        "",
                        "SQ",
                        "",
                        "SQ1010{0}".format(i),
                        "1",
                        v,
                        "",
                        "pt-BR",
                        "",
                        "",
                        "N",
                        "",
                        "0",
                    ]
                )
            )
            struct.extend(
                [
                    "c001q011_SQ1010{0}_SQ00101".format(i),
                    "c001q011_SQ1010{0}_SQ00102".format(i),
                ]
            )

        self.stdout.write("Done!")
        # Equipe de diagnóstico #
        self.stdout.write("\tEquipe de diagnóstico...", ending=" ")
        lsf.writerow(
            normalize(
                [
                    "2000",
                    "",
                    "G",
                    "",
                    "Equipe de diagnóstico",
                    "",
                    "",
                    "",
                    "pt-BR",
                ]
            )
        )
        lsf.writerow(
            normalize(
                [
                    "2001",
                    "",
                    "Q",
                    "D",
                    "c002q001",
                    "1",
                    "Data de início da visita",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c002q001")
        lsf.writerow(
            normalize(
                [
                    "2002",
                    "",
                    "Q",
                    "D",
                    "c002q002",
                    "1",
                    "Data de término da visita",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c002q002")
        lsf.writerow(
            normalize(
                [
                    "2003",
                    "",
                    "Q",
                    "S",
                    "c002q003",
                    "1",
                    "Líder da equipe",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c002q003")
        lsf.writerow(
            normalize(
                [
                    "2004",
                    "",
                    "Q",
                    "T",
                    "c002q004",
                    "1",
                    "Membros da equipe",
                    "",
                    "pt-BR",
                    "",
                    "Y",
                    "N",
                    "",
                    "0",
                ]
            )
        )
        struct.append("c002q004")
        self.stdout.write("Done!")

        for c in Categoria.objects.all():
            self.stdout.write(
                "\t{0}...".format(nonum(c.nome).encode("utf-8")), ending=" "
            )
            lsf.writerow(
                normalize(
                    [
                        str(c.id),
                        "",
                        "G",
                        "",
                        nonum(c.nome),
                        "",
                        nonum(c.nome),
                        "",
                        "pt-BR",
                    ]
                )
            )
            perguntas = sorted([(p.title, p) for p in c.perguntas.all()])
            for t, p in perguntas:
                lstype = DATATYPES[p.datatype]
                # Hack para perguntas SIM/NÃO que foram cadastradas como Choice
                if lstype == "L":
                    if "".join([e.title for e in p.choices.all()]) in [
                        "SimNão",
                        "NãoSim",
                    ]:
                        lstype = "Y"
                ########
                relevance = "1"
                if p.abre_por.exists():
                    relevance = (
                        "("
                        + " or ".join(
                            [
                                '({sid}X{gid}X{qid}.NAOK == "{value}")'.format(
                                    sid=survey_id,
                                    gid=e.schema.categoria.id,
                                    qid=e.schema.id,
                                    value=avalue(e),
                                )
                                for e in p.abre_por.all()
                            ]
                        )
                        + ")"
                    )

                lsf.writerow(
                    normalize(
                        [
                            str(p.id),
                            "",
                            "Q",
                            lstype,
                            "c{0:03}q{1:03}".format(c.id, p.id),
                            relevance,
                            nonum(p.title),
                            p.help_text,
                            "pt-BR",
                            "",
                            "NY"[p.required],
                            "N",
                            "",
                            "0",
                        ]
                    )
                )
                if lstype == "L":
                    lsf.writerows(
                        [
                            normalize(
                                [
                                    str(p.id),
                                    "",
                                    "A",
                                    "0",
                                    str(e.id),
                                    "",
                                    e.title,
                                    "",
                                    "pt-BR",
                                ]
                            )
                            for e in p.choices.all()
                        ]
                    )
                if lstype == "M":
                    lsf.writerows(
                        [
                            normalize(
                                [
                                    str(p.id * 1000 + e.id),
                                    "",
                                    "SQ",
                                    "",
                                    str(e.id),
                                    "1",
                                    e.title,
                                    "",
                                    "pt-BR",
                                ]
                            )
                            for e in p.choices.all()
                        ]
                    )
                    struct.extend(
                        [
                            "c{0:03}q{1:03}_{2}".format(c.id, p.id, e.id)
                            for e in p.choices.all()
                        ]
                    )
                else:
                    struct.extend(["c{0:03}q{1:03}".format(c.id, p.id)])
            self.stdout.write("Done!")

        if len(args) < 3:  # No data export
            return

        self.stdout.write("Exporting survey data: ")

        dtf = csv.writer(
            open(args[2], "wb+"), delimiter="\t", quoting=csv.QUOTE_MINIMAL
        )

        dtf.writerow(struct)

        for d in Diagnostico.objects.all():
            self.stdout.write("\t{0}".format(d.casa_legislativa.nome))

            form = OrderedDict.fromkeys(struct, "{question_not_shown}")

            form["id"] = str(d.id)
            if d.data_publicacao:
                form["submitdate"] = d.data_publicacao.isoformat()
            # form['lastpage'] = '8'
            form["startlanguage"] = "pt-BR"
            # form['seed'] = '123456'

            # Identificação da Casa Legislativa e sua equipe #
            form["c001q001"] = d.casa_legislativa.municipio.uf.regiao
            form["c001q002"] = d.casa_legislativa.municipio.uf.sigla
            form["c001q003"] = d.casa_legislativa.municipio.nome
            if d.casa_legislativa.municipio.data_criacao:
                form[
                    "c001q004"
                ] = d.casa_legislativa.municipio.data_criacao.isoformat()
            form["c001q005"] = d.casa_legislativa.nome
            if d.casa_legislativa.data_instalacao:
                form[
                    "c001q006"
                ] = d.casa_legislativa.data_instalacao.isoformat()
            form["c001q007"] = (
                "{logradouro}{{cr}}{{newline}}"
                "{bairro}{{cr}}{{newline}}"
                "{cep} - {municipio} - {uf}".format(
                    logradouro=d.casa_legislativa.logradouro,
                    bairro=d.casa_legislativa.bairro,
                    cep=d.casa_legislativa.cep,
                    municipio=d.casa_legislativa.municipio.nome,
                    uf=d.casa_legislativa.municipio.uf.sigla,
                )
            )
            form["c001q008"] = d.casa_legislativa.cnpj
            form["c001q009"] = d.casa_legislativa.email
            form["c001q010"] = d.casa_legislativa.pagina_web

            for i, k, v in setores:
                q = d.casa_legislativa.funcionario_set.filter(setor=k)
                if q.exists():
                    f = q.first()
                    knome = "c001q011_SQ1010{0}_SQ00101".format(i)
                    kmail = "c001q011_SQ1010{0}_SQ00102".format(i)
                    form[knome] = f.nome
                    form[kmail] = f.email

            if d.data_visita_inicio:
                form["c002q001"] = d.data_visita_inicio.isoformat()
            if d.data_visita_fim:
                form["c002q002"] = d.data_visita_fim.isoformat()
            form["c002q003"] = d.responsavel.nome_completo
            form["c002q004"] = "{cr}{newline}".join(
                [e.membro.nome_completo for e in d.equipe_set.all()]
            )

            for r in Resposta.objects.filter(entity_id=d.id):
                if r.schema.datatype == "many":
                    key = "c{cid:03}q{qid:03}_{sqid}".format(
                        cid=r.schema.categoria.id,
                        qid=r.schema.id,
                        sqid=r.value.id,
                    )
                    value = "Y"
                else:
                    key = "c{cid:03}q{qid:03}".format(
                        cid=r.schema.categoria.id, qid=r.schema.id
                    )
                    value = r.value
                    if r.schema.datatype == "one":
                        if value is None:
                            value = "{question_not_shown}"
                        elif value.title == "Sim":
                            value = "Y"
                        elif value.title == "Não":
                            value = "N"
                        else:
                            value = r.value.id
                    elif r.schema.datatype == "text":
                        value = (
                            value.replace("\r\n", "{cr}{newline}")
                            .replace("\r", "{cr}{newline}")
                            .replace("\n", "{cr}{newline}")
                            .replace("\t", " ")
                        )

                if value is None:
                    value = "{question_not_shown}"
                form[key] = "{0}".format(value)
            dtf.writerow(normalize(form.values()))

        self.stdout.write("Done!")
