import csv
import zipfile
from datetime import datetime
import json
import logging
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django_extensions.management.jobs import MinutelyJob
from sigi.apps.casas.models import Orgao
from sigi.apps.parlamentares.jobs import import_path, json_path
from sigi.apps.parlamentares.models import Parlamentar, Partido


class Job(MinutelyJob):
    help = "Importa parlamentares de arquivo do TSE"

    def execute(self):
        json_data = self.get_json_data()
        if json_data is None:
            return
        json_data["inicio_processamento"] = str(datetime.now())
        print(
            f"Start importing parlamentares at {json_data['inicio_processamento']}: Details: {json_data}"
        )
        result_final = []
        # Importa parlamentares #
        if "resultados" in json_data:
            result = self.importa_parlamentares(
                import_path / json_data["resultados"], json_data
            )
            if result["erros"]:
                self.remove_files(json_data)
                self.send_mail(result["erros"], json_data)
                return
            result_final.append(_("* IMPORTAÇÃO DOS PARLAMENTARES *"))
            result_final.extend(result["infos"])
        if "redes_sociais" in json_data:
            result = self.importa_redes(
                import_path / json_data["redes_sociais"],
                json_data["codificacao"],
            )
            result_final.append(_("* IMPORTAÇÃO DAS REDES SOCIAIS *"))
            result_final.extend(result["infos"])
            result_final.append(_("* IMPORTAÇÃO DAS REDES SOCIAIS - ERROS *"))
            result_final.extend(result["erros"])

        if "fotos" in json_data:
            result = self.importa_fotos(import_path / json_data["fotos"])
            result_final.append(_("* IMPORTAÇÃO DAS FOTOS *"))
            result_final.extend(result["infos"])
            result_final.append(_("* IMPORTAÇÃO DAS FOTOS - ERROS *"))
            result_final.extend(result["erros"])
        self.remove_files(json_data)
        self.send_mail(result_final, json_data)
        print(f"Finish import parlamentares. Final result: {result_final}")
        return

    def get_json_data(self):
        if json_path.is_file():
            data = json.loads(json_path.read_text())
            json_path.unlink(missing_ok=True)
            return data
        return None

    def remove_files(self, json_data):
        if "resultados" in json_data:
            (import_path / json_data["resultados"]).unlink(missing_ok=True)
        if "redes_sociais" in json_data:
            (import_path / json_data["redes_sociais"]).unlink(missing_ok=True)
        if "fotos" in json_data:
            (import_path / json_data["fotos"]).unlink(missing_ok=True)

    def send_mail(self, result, json_data):
        user = get_user_model().objects.get(id=int(json_data["user_id"]))
        json_data["fim_processamento"] = str(datetime.now())
        json_data["user"] = user.get_full_name()
        del json_data["user_id"]
        result = list(dict.fromkeys(result))
        txt_message = "\n".join(result)
        html_message = render_to_string(
            "parlamentares/import_email.html",
            {"result": result, "json_data": json_data},
        )
        recipient_list = [a[1] for a in settings.ADMINS].append(user.email)
        result_file = import_path / "result.html"
        result_file.write_text(html_message, encoding="utf-8")
        send_mail(
            subject="Resultados da importação de dados de parlamentares",
            message=txt_message,
            recipient_list=recipient_list,
            html_message=html_message,
        )

    def importa_parlamentares(self, file_name, json_data):
        def limpa_flag():
            # Limpa o flag de importação para garantir que nada seja apagado #
            # indevidamente                                                  #
            Parlamentar.objects.all().update(flag_importa="")

        def marcar_antigos():
            if json_data["sigla_uf"] == "BR":
                Parlamentar.objects.filter(
                    casa_legislativa__tipo__sigla__in=tipo_casa
                ).update(flag_importa="E")
            else:
                Parlamentar.objects.filter(
                    casa_legislativa__municipio__uf__sigla=json_data[
                        "sigla_uf"
                    ],
                    casa_legislativa__tipo__sigla__in=tipo_casa,
                ).update(flag_importa="E")

        def apagar_antigos():
            Parlamentar.objects.filter(flag_importa="E").delete()

        def apagar_novos():
            Parlamentar.objects.filter(flag_importa="N").delete()

        if json_data["tipo_candidatos"] == "D":
            tipo_casa = ["AL", "CT"]
            cargos = ["7", "8"]  # Deputado Estadual e Distrital
        else:
            tipo_casa = ["CM"]
            cargos = ["13"]

        cod_situacao = ["1", "2", "3"]  # Eleito, por qp, por média
        if json_data["suplentes"]:
            cod_situacao.append("5")  # suplente

        result = {"infos": [], "erros": []}

        with open(file_name, "r", encoding=json_data["codificacao"]) as f:
            if f.encoding != json_data["codificacao"]:
                result["erros"].append(
                    f"Codificação de caracteres do arquivo {file_name} é "
                    f"{f.encoding}. Precisa converter para "
                    f"{json_data['codificacao']}."
                )
            reader = csv.DictReader(f, delimiter=";")
            fields = {
                "ANO_ELEICAO",
                "SG_UE",
                "NM_UE",
                "CD_CARGO",
                "SQ_CANDIDATO",
                "NM_CANDIDATO",
                "NM_URNA_CANDIDATO",
                "NR_PARTIDO",
                "NM_PARTIDO",
                "CD_SIT_TOT_TURNO",
            }
            try:
                fieldnames = reader.fieldnames
            except Exception as e:
                result["erros"].append(str(e))
                fieldnames = []

            if not fields.issubset(set(fieldnames)):
                result["erros"].append(
                    "Nao foram encontrados todos os campos necessários no "
                    "arquivo. São esperados os seguintes campos: "
                    + ", ".join(fields)
                )

            if result["erros"]:
                return result

            limpa_flag()
            marcar_antigos()

            skiped = 0
            imported = 0
            total = 0

            apenas_verificar = False

            for row in reader:
                total += 1
                if not (
                    row["CD_CARGO"] in cargos
                    and row["CD_SIT_TOT_TURNO"] in cod_situacao
                ):
                    skiped += 1
                    continue
                cod_tse = row["SG_UE"]
                legenda = int(row["NR_PARTIDO"])
                # Hack para 2022 - fusão de partidos #
                if legenda in [17, 25]:
                    legenda = 44
                try:
                    if json_data["tipo_candidatos"] == "V":
                        casa = Orgao.objects.get(
                            municipio__codigo_tse=int(cod_tse),
                            tipo__sigla__in=tipo_casa,
                        )
                    else:
                        casa = Orgao.objects.get(
                            municipio__uf__sigla=cod_tse,
                            tipo__sigla__in=tipo_casa,
                        )
                except:
                    # De agora em diante apenas procura erros, sem criar
                    # novos parlamentares, para agilizar o processo
                    apenas_verificar = True
                    result["erros"].append(
                        "Não foi encontrada a Casa Legislativa com "
                        f"o código TSE {cod_tse}. O nome do "
                        f"ente da federação é {row['NM_UE']}. "
                        "Corrija o cadastro do SIGI e tente novamente."
                    )
                try:
                    partido = Partido.objects.get(legenda=legenda)
                except:
                    # De agora em diante apenas procura erros, sem criar
                    # novos parlamentares, para agilizar o processo
                    apenas_verificar = True
                    result["erros"].append(
                        f"O partido {row['NM_PARTIDO']} de legenda "
                        f"{legenda} não foi encontrado no SIGI."
                    )

                if not apenas_verificar:
                    Parlamentar.objects.update_or_create(
                        flag_importa="N",
                        sequencial_tse=row["SQ_CANDIDATO"],
                        ano_eleicao=row["ANO_ELEICAO"],
                        nome_completo=row["NM_CANDIDATO"],
                        nome_parlamentar=row["NM_URNA_CANDIDATO"],
                        partido=partido,
                        casa_legislativa=casa,
                        status_mandato="S"
                        if row["CD_SIT_TOT_TURNO"] == "5"
                        else "E",
                    )
                    imported += 1
            if result["erros"]:
                apagar_novos()
                result["infos"] = []
            else:
                apagar_antigos()

        limpa_flag()

        result["infos"].append(f"Total de registros lidos: {total}")
        result["infos"].append(f"Total de registros ignorados: {skiped}")
        result["infos"].append(f"Total de registros importados: {imported}")

        return result

    def importa_redes(self, file_name, codificacao):
        result = {"infos": [], "erros": []}
        with open(file_name, "r", encoding=codificacao) as f:
            if f.encoding != codificacao:
                result["erros"].append(
                    f"Codificação de caracteres do arquivo {file_name} é "
                    f"{f.encoding}. Precisa converter para {codificacao}."
                )
            reader = csv.DictReader(f, delimiter=";")
            fields = {
                "SQ_CANDIDATO",
                "DS_URL",
            }
            try:
                fieldnames = reader.fieldnames
            except Exception as e:
                result["erros"].append(str(e))
                fieldnames = []

            if not fields.issubset(set(fieldnames)):
                result["erros"].append(
                    "Nao foram encontrados todos os campos necessários no "
                    "arquivo. São esperados os seguintes campos: "
                    + ", ".join(fields)
                )

            if result["erros"]:
                return result

            skiped = 0
            imported = 0
            total = 0

            for row in reader:
                total += 1
                try:
                    parlamentar = Parlamentar.objects.get(
                        sequencial_tse=row["SQ_CANDIDATO"]
                    )
                    if (
                        row["DS_URL"]
                        not in parlamentar.redes_sociais.splitlines()
                    ):
                        parlamentar.redes_sociais += "\n" + row["DS_URL"]
                        parlamentar.save()
                        imported += 1
                    else:
                        skiped += 1
                except Parlamentar.DoesNotExist:
                    skiped += 1
        result["infos"].append(f"Total de registros lidos: {total}")
        result["infos"].append(f"Total de registros ignorados: {skiped}")
        result["infos"].append(f"Total de registros importados: {imported}")
        return result

    def importa_fotos(self, file_name):
        result = {"erros": [], "infos": []}
        if not zipfile.is_zipfile(file_name):
            result["erros"].append("Arquivo de fotos deve ser um ZIP")
            return result

        with zipfile.ZipFile(file_name, mode="r") as zip_file:
            if zip_file.testzip() is not None:
                result["erros"].append("Arquivo de fotos está corrompido")
                return result

            sequenciais = {n[3:14]: n for n in zip_file.namelist()}
            parlamentares = Parlamentar.objects.filter(
                sequencial_tse__in=sequenciais.keys()
            )

            total = len(zip_file.namelist())
            imported = parlamentares.count()
            skiped = total - imported

            if imported <= 0:
                result["erros"].append(
                    "Nenhuma das fotos corresponde a algum parlamentar"
                )
                return result

            relative_path = Parlamentar.foto.field.upload_to
            foto_folder = settings.MEDIA_ROOT / relative_path

            for parlamentar in parlamentares:
                foto_nome = sequenciais[parlamentar.sequencial_tse]
                try:
                    zip_file.extract(foto_nome, foto_folder)
                    parlamentar.foto.name = str(f"{relative_path}/{foto_nome}")
                    parlamentar.save()
                except Exception as e:
                    result["erros"].append(str(e))

            result["infos"].extend(
                [
                    f"Total de fotos no arquivo: {total}",
                    f"Número de fotos importadas: {imported}",
                    f"Número de fotos ignoradas: {skiped}",
                ]
            )

            return result
