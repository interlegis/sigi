import requests
import datetime
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.formats import localize
from django.utils.translation import gettext as _
from django_extensions.management.jobs import HourlyJob
from sigi.apps.utils.management.jobs import JobReportMixin
from sigi.apps.espacos.models import (
    Espaco,
    Recurso,
    Reserva,
)

DEPARA_SITUACAO = {
    "Aguardando análise": Reserva.STATUS_ATIVO,
    "Excluída": None,  # Será tratado como caso especial
    "Reserva aprovada": Reserva.STATUS_ATIVO,
    "Reserva cancelada": Reserva.STATUS_CANCELADO,
    "Reserva rejeitada": Reserva.STATUS_CANCELADO,
}


class Job(JobReportMixin, HourlyJob):
    help = "Sincroniza dados do sistema de reserva de salas"
    report_data = []
    resumo = []
    infos = []
    erros = []

    @property
    def auth_data(self):
        return (
            settings.RESERVA_SALA_API_USER,
            settings.RESERVA_SALA_API_PASSWORD,
        )

    def do_job(self):
        self.resumo = []
        self.infos = []
        self.erros = []

        if (
            settings.RESERVA_SALA_BASE_URL is None
            or settings.RESERVA_SALA_API_USER is None
            or settings.RESERVA_SALA_API_PASSWORD is None
        ):
            # Acesso ao sistema não configurado. Não fazer nada
            return

        self.carrega_salas()
        self.carrega_recursos()
        self.carrega_reservas()

    def carrega_salas(self):
        tit = ["", "\t*Carga de salas*", ""]
        self.infos.extend(tit)
        self.erros.extend(tit)
        self.resumo.extend(tit)

        tot_novas = 0
        tot_erros = 0
        tot_atualizadas = 0
        req = requests.get(
            settings.RESERVA_SALA_BASE_URL + "salas", auth=self.auth_data
        )
        if not req.ok:
            self.erros.append(
                _(
                    "\t* Erro de autenticação na API do sistema de reserva "
                    f"de salas, com a mensagem *{req.reason}*"
                )
            )
            return
        for sala in req.json():
            try:
                espaco = Espaco.objects.get(id_sala=sala["id"])
            except Espaco.DoesNotExist:
                # Criar espaço
                espaco = Espaco(
                    nome=sala["nome"],
                    sigla=sala["nome"][:20],
                    descricao=sala["nome"],
                    local=sala["local"],
                    capacidade=sala["capacidade"],
                    id_sala=sala["id"],
                )
                espaco.save()
                self.infos.append(
                    _(
                        f"\t* Criado espaço *{espaco.id}* para a "
                        f"sala *{sala['id']} - {sala['nome']}*"
                    )
                )
                tot_novas += 1
                continue
            except Espaco.MultipleObjectsReturned:
                self.erros.append(
                    _(
                        "\t* Existe mais de um espaço com o mesmo ID de sala. "
                        "Isso deve ser corrigido manualmente no SIGI. "
                        f"id_sala={sala['id']}"
                    )
                )
                tot_erros += 1
                continue
            # verifica se precisa atualizar os dados do espaço
            jespaco = {
                "id": espaco.id_sala,
                "nome": espaco.nome,
                "local": espaco.local,
                "capacidade": espaco.capacidade,
            }
            if sorted(sala) != sorted(jespaco):
                # Atualizar o espaço
                espaco.sala_id = sala["id"]
                espaco.nome = sala["nome"]
                espaco.local = sala["local"]
                espaco.capacidade = sala["capacidade"]
                espaco.save()
                self.infos.append(
                    _(
                        f"\t* Espaço *{espaco.id}* atualizado com novos dados "
                        f"da sala *{sala['id']}*"
                    )
                )
                tot_atualizadas += 1
        self.resumo.append(
            _(f"\t* Total de salas processadas: {len(req.json())}")
        )
        self.resumo.append(_(f"\t* Novos espaços criados: {tot_novas}"))
        self.resumo.append(_(f"\t* Espaços atualizados: {tot_atualizadas}"))
        self.resumo.append(_(f"\t* Erros encontrados nas salas: {tot_erros}"))

    def carrega_recursos(self):
        tit = ["", "\t*Carga de recursos*", ""]
        self.infos.extend(tit)
        self.erros.extend(tit)
        self.resumo.extend(tit)

        tot_novas = 0
        tot_erros = 0
        tot_atualizadas = 0

        req = requests.get(
            settings.RESERVA_SALA_BASE_URL + "equipamentos",
            auth=self.auth_data,
        )
        if not req.ok:
            self.erros.append(
                _(
                    "\t* Erro na API do sistema de reserva ao ler "
                    f"equipamentos, com a mensagem *{req.reason}*"
                )
            )
            return

        for equipamento in req.json():
            if equipamento["status"] == "Não":
                # Não importar
                continue
            try:
                recurso = Recurso.objects.get(id_equipamento=equipamento["id"])
            except Recurso.DoesNotExist:
                recurso = Recurso(
                    nome=equipamento["nome"],
                    sigla=equipamento["nome"][:20],
                    descricao=equipamento["nome"],
                    id_equipamento=equipamento["id"],
                )
                recurso.save()
                self.infos.append(
                    f"\t* Recurso *{recurso}* criado a partir do equipamento *{equipamento['id']} - {equipamento['nome']}*"
                )
                tot_novas += 1
                continue
            except Recurso.MultipleObjectsReturned:
                lista = ", ".join(
                    [
                        str(r)
                        for r in Recurso.objects.filter(
                            id_equipamento=equipamento["id"]
                        )
                    ]
                )
                self.erros.append(
                    f"\t* O equipamento *{equipamento['id']} - "
                    f"{equipamento['nome']}* possui os seguintes recursos "
                    f"com mesmo ID no SIGI: *{lista}*"
                )
                tot_erros += 1
                continue
            if equipamento["nome"] != recurso.nome:
                recurso.nome = equipamento["nome"]
                recurso.save()
                self.infos.append(
                    f"\t* Recurso *{str(recurso)}* atualizado com as alterações "
                    f"do equipamento *{equipamento['id']}*"
                )
                tot_atualizadas += 1

        self.resumo.append(
            _(f"\t* Total de equipamentos processados: {len(req.json())}")
        )
        self.resumo.append(_(f"\t* Novos recursos criados: {tot_novas}"))
        self.resumo.append(_(f"\t* Recursos atualizados: {tot_atualizadas}"))
        self.resumo.append(
            _(f"\t* Erros encontrados nos equipamentos: {tot_erros}")
        )

    def carrega_reservas(
        self,
        ontem=(timezone.localdate() - timezone.timedelta(days=1)).isoformat(),
    ):
        tit = ["", "\t*Carga de reservas*", ""]
        self.infos.extend(tit)
        self.erros.extend(tit)
        self.resumo.extend(tit)

        tot_processadas = 0
        tot_novas = 0
        tot_excluidas = 0
        tot_erros = 0
        tot_atualizadas = 0

        for espaco in Espaco.objects.exclude(id_sala=None):
            req = requests.get(
                settings.RESERVA_SALA_BASE_URL
                + f"salas/{espaco.id_sala}/reservas/datas?dataInicio={ontem}",
                auth=self.auth_data,
            )
            if not req.ok:
                self.erros.append(
                    _(
                        "\t* Erro na API do sistema de reserva ao ler "
                        f"reservas da sala *{espaco.id_sala}*, com data de "
                        f"início maior que *{ontem}*, "
                        f"com a mensagem *{req.reason}*"
                    )
                )
                continue
            tot_processadas += len(req.json())
            for reserva in req.json():
                # Hack sujo para campos igual a None
                if reserva["horaInicio"] is None:
                    reserva["horaInicio"] = "00:00:00"
                if reserva["horaFim"] is None:
                    reserva["horaFim"] = "23:59:59"
                if reserva["descricao"] is None:
                    reserva["descricao"] = ""
                if reserva["informacao"] is None:
                    reserva["informacao"] = ""
                if reserva["ramal"] is None:
                    reserva["ramal"] = ""
                # Hack sujo para strings muito grandes
                reserva["evento"] = reserva["evento"][:100]
                reserva["coordenador"] = reserva["coordenador"][:100]
                reserva["ramal"] = reserva["ramal"][:100]

                data_inicio = datetime.date.fromisoformat(
                    reserva["dataInicio"]
                )
                hora_inicio = datetime.time.fromisoformat(
                    reserva["horaInicio"]
                )
                data_termino = datetime.date.fromisoformat(reserva["dataFim"])
                hora_termino = datetime.time.fromisoformat(reserva["horaFim"])
                status = DEPARA_SITUACAO[reserva["situacao"]]
                # Tratar reservas excluídas no sistema de reservas
                if reserva["situacao"] == "Excluída":
                    res = Reserva.objects.filter(
                        id_reserva=reserva["id"]
                    ).delete()[1]
                    if "espacos.Reserva" in res:
                        tot_excluidas += res["espacos.Reserva"]
                    continue
                # Tratar os demais casos
                try:
                    reserva_sigi = Reserva.objects.get(
                        id_reserva=reserva["id"]
                    )
                except Reserva.DoesNotExist:
                    conflitos = self.verifica_conflito(
                        espaco,
                        data_inicio,
                        data_termino,
                        hora_inicio,
                        hora_termino,
                    )
                    if conflitos:
                        # Verificar se existe um conflitante com as mesmas
                        # datas/horas e que tenha sido cadastrado diretamente
                        # no SIGI (id_reserva = None)
                        reserva_sigi = Reserva.objects.filter(
                            espaco=espaco,
                            id_reserva=None,
                            data_inicio=data_inicio,
                            data_termino=data_termino,
                            hora_inicio=hora_inicio,
                            hora_termino=hora_termino,
                        ).first()
                        if reserva_sigi:
                            # Se existe, então é a mesma, bastando vincular
                            reserva_sigi.id_reserva = reserva["id"]
                            reserva_sigi.save()
                            # Deixa seguir para atualizar outros campos
                        else:
                            # Criar a reserva conflitante
                            if status != Reserva.STATUS_CANCELADO:
                                status = Reserva.STATUS_CONFLITO
                            reserva_sigi = self.cria_reserva(
                                reserva,
                                espaco,
                                status,
                                data_inicio,
                                data_termino,
                                hora_inicio,
                                hora_termino,
                            )
                            if reserva_sigi.status == Reserva.STATUS_CONFLITO:
                                # Reportar como erro se a reserva é conflitante
                                lista = ", ".join([str(c) for c in conflitos])
                                self.erros.append(
                                    f"\t* A reserva *{reserva['id']} - "
                                    f"{reserva['evento']}"
                                    "* do sistema de reservas conflita com "
                                    "a(s) seguinte(s) reserva(s) do SIGI: "
                                    f"*{lista}*. e foi copiada para o SIGI "
                                    "como conflitante."
                                )
                                tot_erros += 1
                            else:
                                # Reportar como nova se o status for cancelada
                                self.infos.append(
                                    f"\t* Reserva *{str(reserva_sigi)}* "
                                    "criada no SIGI a partir da reserva "
                                    f"*{reserva['descricao']}* "
                                    "do sistema de reservas"
                                )
                                tot_novas += 1
                            continue
                    else:  # Não há conflitos, basta criar a reserva
                        reserva_sigi = self.cria_reserva(
                            reserva,
                            espaco,
                            status,
                            data_inicio,
                            data_termino,
                            hora_inicio,
                            hora_termino,
                        )
                        self.infos.append(
                            f"\t* Reserva *{str(reserva_sigi)}* criada no SIGI"
                            f" a partir da reserva *{reserva['descricao']}* "
                            "do sistema de reservas"
                        )
                        tot_novas += 1
                        continue
                except Reserva.MultipleObjectsReturned:
                    # Esse erro nunca poderia acontecer, mas ...
                    self.erros.append(
                        _(
                            "\t* Existe mais de uma reserva no SIGI com o "
                            "mesmo ID de reserva do sistema de reservas. "
                            "Isso deve ser corrigido manualmente no SIGI. "
                            f"id_reserva=*{reserva['id']}*"
                        )
                    )
                    tot_erros += 1
                    continue
                # Reserva foi encontrada no SIGI. Podemos atualizar
                atualizou = False
                if (
                    reserva_sigi.data_inicio != data_inicio
                    or reserva_sigi.data_termino != data_termino
                    or reserva_sigi.hora_inicio != hora_inicio
                    or reserva_sigi.hora_termino != hora_termino
                ):
                    # Se mudou de data/hora, pode ocorrer conflitos
                    conflitos = self.verifica_conflito(
                        espaco,
                        data_inicio,
                        data_termino,
                        hora_inicio,
                        hora_termino,
                        reserva_sigi,
                    )
                    if not conflitos:
                        # Nenhum conflito, podemos alterar as datas de boa
                        reserva_sigi.data_inicio = data_inicio
                        reserva_sigi.data_termino = data_termino
                        reserva_sigi.hora_inicio = hora_inicio
                        reserva_sigi.hora_termino = hora_termino
                        self.infos.append(
                            f"\t* *{str(reserva_sigi)}* mudou para o período "
                            f"de *{localize(data_inicio)} "
                            f"{localize(hora_inicio)}* a "
                            f"*{localize(data_termino)} "
                            f"{localize(hora_termino)}*"
                        )
                        atualizou = True
                    else:
                        lista = ", ".join([str(c) for c in conflitos])
                        self.erros.append(
                            f"\t* A reserva *{reserva['evento']}* no sistema "
                            "de reservas mudou de data, mas esta mudança não "
                            "pode ser aplicada no SIGI pois gera conflito "
                            "com a(s) seguinte(s) outra(s) reserva(s): "
                            f"*{lista}*"
                        )
                        tot_erros += 1
                        continue
                # Verificar outras atualizações
                if reserva_sigi.status != status:
                    reserva_sigi.status = status
                    self.infos.append(
                        f"\t* A reserva SIGI *{str(reserva_sigi)}* mudou de "
                        f"status para *{reserva_sigi.get_status_display()}*"
                    )
                    atualizou = True
                rr = (
                    reserva["evento"],
                    reserva["quantidadeAlunos"],
                    "\n".join(
                        [reserva["descricao"], str(reserva["informacao"])]
                    ),
                    reserva["coordenador"],
                    reserva["coordenador"],
                    reserva["ramal"],
                )
                rs = (
                    reserva_sigi.proposito,
                    reserva_sigi.total_participantes,
                    reserva_sigi.informacoes,
                    reserva_sigi.solicitante,
                    reserva_sigi.contato,
                    reserva_sigi.telefone_contato,
                )
                if rr != rs:
                    # Campos descritivos foram alterados
                    reserva_sigi.proposito = reserva["evento"]
                    reserva_sigi.total_participantes = reserva[
                        "quantidadeAlunos"
                    ]
                    reserva_sigi.informacoes = "\n".join(
                        [reserva["descricao"], str(reserva["informacao"])]
                    )
                    reserva_sigi.solicitante = reserva["coordenador"]
                    reserva_sigi.contato = reserva["coordenador"]
                    reserva_sigi.telefone_contato = reserva["ramal"]
                    reserva_sigi.save()
                    self.infos.append(
                        f"\t* A reserva SIGI *{str(reserva_sigi)}* foi "
                        "atualizada com as alterações da "
                        f"reserva *{reserva['id']}*"
                    )
                    atualizou = True
                if self.recursos_solicitados(
                    reserva_sigi, reserva["equipamentos"]
                ):
                    self.infos.append(
                        "\t* Os recursos solicitados da reserva SIGI "
                        f"*{str(reserva_sigi)}* foram atualizados"
                    )
                    atualizou = True
                if atualizou:
                    tot_atualizadas += 1
        self.resumo.append(
            _(f"\t* Total de reservas processadas: {tot_processadas}")
        )
        self.resumo.append(_(f"\t* Novas reservas criadas: {tot_novas}"))
        self.resumo.append(_(f"\t* Reservas atualizados: {tot_atualizadas}"))
        self.resumo.append(_(f"\t* Reservas excluídas: {tot_excluidas}"))
        self.resumo.append(
            _(f"\t* Erros encontrados nas reservas: {tot_erros}")
        )

    def verifica_conflito(
        self,
        espaco,
        data_inicio,
        data_termino,
        hora_inicio,
        hora_termino,
        reserva_sigi=None,
    ):
        # Verifica se existe alguma reserva do espaço que conflita com o
        # período desejado
        reservas_conflitantes = Reserva.objects.exclude(
            status=Reserva.STATUS_CANCELADO
        ).filter(
            espaco=espaco,
            data_inicio__lte=data_termino,
            data_termino__gte=data_inicio,
            hora_inicio__lte=hora_termino,
            hora_termino__gte=hora_inicio,
        )
        if reserva_sigi:
            reservas_conflitantes = reservas_conflitantes.exclude(
                id=reserva_sigi.id
            )

        if not reservas_conflitantes.exists():
            return None
        else:
            return reservas_conflitantes.all()

    def cria_reserva(
        self,
        reserva,
        espaco,
        status,
        data_inicio,
        data_termino,
        hora_inicio,
        hora_termino,
    ):
        data_pedido = min(timezone.localdate(), data_inicio)
        reserva_sigi = Reserva(
            status=status,
            espaco=espaco,
            proposito=reserva["evento"],
            virtual=False,
            total_participantes=reserva["quantidadeAlunos"],
            data_pedido=data_pedido,
            data_inicio=data_inicio,
            data_termino=data_termino,
            hora_inicio=hora_inicio,
            hora_termino=hora_termino,
            informacoes="\n".join(
                [
                    reserva["descricao"],
                    str(reserva["informacao"]),
                ]
            ),
            solicitante=reserva["coordenador"],
            contato=reserva["coordenador"],
            telefone_contato=reserva["ramal"],
            id_reserva=reserva["id"],
            data_ult_atualizacao=timezone.localtime(),
        )
        reserva_sigi.save()
        self.recursos_solicitados(reserva_sigi, reserva["equipamentos"])
        return reserva_sigi

    def recursos_solicitados(self, reserva_sigi, equipamentos_solicitados):
        atualizou = False
        for equipamento in equipamentos_solicitados:
            recurso = Recurso.objects.filter(
                id_equipamento=equipamento["id"]
            ).first()
            if not recurso:
                # Cria um novo recurso na tabela de recursos
                recurso = Recurso(
                    nome=equipamento["nome"],
                    sigla=equipamento["nome"][:20],
                    descricao=equipamento["nome"],
                    id_equipamento=equipamento["id"],
                )
                recurso.save()
                atualizou = True
                continue

            if not reserva_sigi.recursosolicitado_set.filter(
                recurso=recurso
            ).exists():
                reserva_sigi.recursosolicitado_set.create(
                    recurso=recurso, quantidade=1
                )
                atualizou = True
        return atualizou

    def report(self, start_time, end_time):
        self.report_data = [
            "",
            "",
            "RESUMO",
            "------",
            "",
            "",
        ]
        self.report_data.extend(self.resumo)
        self.report_data.extend(
            [
                "",
                "",
                "ERROS ENCONTRADOS",
                "-----------------",
                "",
                "",
            ]
        )
        self.report_data.extend(self.erros)
        self.report_data.extend(
            [
                "",
                "",
                "MAIS INFORMAÇÕES",
                "----------------",
                "",
                "",
            ]
        )
        self.report_data.extend(self.infos)
        super().report(start_time, end_time)
