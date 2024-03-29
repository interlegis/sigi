import re
import requests
from hashlib import md5
from pathlib import Path
from django.db import models
from django.db.models import Q, fields
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator
from django.template import Template, Context
from django.template.exceptions import TemplateSyntaxError
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _
from django_weasyprint.utils import django_url_fetcher
from docx import Document
from tinymce.models import HTMLField
from weasyprint import HTML
from sigi.apps.contatos.models import Municipio, UnidadeFederativa
from sigi.apps.eventos.models import Evento
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.utils import to_ascii
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.servidores.models import Servidor, Servico
from sigi.apps.utils import editor_help


class Projeto(models.Model):
    OFICIO_HELP = editor_help(
        "texto_oficio",
        [
            ("casa", Orgao),
            ("presidente", Parlamentar),
            ("contato", Funcionario),
            ("casa.municipio", Municipio),
            ("casa.municipio.uf", UnidadeFederativa),
            ("data", _("Data atual")),
            ("doravante", _("CÂMARA ou ASSEMBLEIA")),
        ],
    )
    MINUTA_HELP = editor_help(
        "modelo_minuta",
        [
            ("casa", Orgao),
            ("presidente", Parlamentar),
            ("contato", Funcionario),
            ("casa.municipio", Municipio),
            ("casa.municipio.uf", UnidadeFederativa),
            ("data", _("Data atual")),
            ("ente", _("Ente da federação (município/estado)")),
            ("doravante", _("CÂMARA ou ASSEMBLEIA")),
        ],
    )
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)
    texto_oficio = HTMLField(
        _("texto do ofício"), blank=True, help_text=OFICIO_HELP
    )
    modelo_minuta = models.FileField(
        _("Modelo de minuta"),
        blank=True,
        help_text=MINUTA_HELP,
        upload_to="convenios/minutas/",
        validators=[
            FileExtensionValidator(
                [
                    "docx",
                ]
            ),
        ],
    )

    def __str__(self):
        return self.sigla

    class Meta:
        ordering = ("nome",)

    def gerar_oficio(self, file_object, casa, presidente, contato, path):
        texto = self.texto_oficio
        template_string = (
            '{% extends "convenios/oficio_padrao.html" %}'
            "{% load pdf %}"
            f"{{% block text_body %}}{texto}{{% endblock %}}"
        )
        context = Context(
            {
                "casa": casa,
                "presidente": presidente,
                "contato": contato,
                "data": timezone.localdate(),
                "doravante": casa.tipo.nome.split(" ")[0],
            }
        )
        string = Template(template_string).render(context)
        pdf = HTML(
            string=string,
            url_fetcher=django_url_fetcher,
            encoding="utf-8",
            base_url=path,
        )
        file_name = Path(file_object.path)
        if not file_name.parent.exists():
            file_name.parent.mkdir(parents=True, exist_ok=True)
        if file_object.closed:
            file_object.open(mode="wb")
        pdf.write_pdf(target=file_object)
        file_object.flush()

    def gerar_minuta(self, file_path, casa, presidente, contato):
        doc = Document(self.modelo_minuta.path)

        if casa.tipo.sigla == "CM":
            ente = (
                f"Município de {casa.municipio.nome}, "
                f"{casa.municipio.uf.sigla}"
            )
        else:
            ente = f"Estado de {casa.municipio.uf.nome}"

        doc_context = Context(
            {
                "casa": casa,
                "presidente": presidente,
                "contato": contato,
                "data": timezone.localdate(),
                "ente": ente,
                "doravante": casa.tipo.nome.split(" ")[0],
            }
        )

        self.processa_paragrafos(doc.paragraphs, doc_context)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    self.processa_paragrafos(
                        cell.paragraphs,
                        doc_context,
                    )
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.mkdir(parents=True, exist_ok=True)
        doc.save(file_path)

    def processa_paragrafos(self, paragrafos, context):
        for paragrafo in paragrafos:
            run_final = None
            for run in paragrafo.runs:
                if run_final is None:
                    run_final = run
                else:
                    run_final.text += run.text
                    run.text = ""
                if run_final.text.count("{{") != run_final.text.count("}}"):
                    continue
                try:
                    run_final.text = Template(run_final.text).render(context)
                    run_final = None
                except TemplateSyntaxError:
                    pass


class StatusConvenio(models.Model):
    nome = models.CharField(max_length=100)
    cancela = models.BooleanField(_("Cancela o convênio"), default=False)

    class Meta:
        ordering = ("nome",)
        verbose_name = _("Estado de convenios")
        verbose_name_plural = _("Estados de convenios")

    def __str__(self):
        return self.nome


class TipoSolicitacao(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        ordering = ("nome",)
        verbose_name = _("tipo de solicitação")
        verbose_name_plural = _("Tipos de solicitação")

    def __str__(self):
        return self.nome


class Convenio(models.Model):
    casa_legislativa = models.ForeignKey(
        "casas.Orgao",
        on_delete=models.PROTECT,
        verbose_name=_("órgão conveniado"),
    )
    projeto = models.ForeignKey(
        Projeto, on_delete=models.PROTECT, verbose_name=_("Tipo de Convenio")
    )
    # numero designado pelo Senado Federal para o convênio
    num_processo_sf = models.CharField(
        _("número do processo SF (Senado Federal)"),
        max_length=20,
        blank=True,
        help_text=_(
            "Formatos:<br/>Antigo: <em>XXXXXX/XX-X</em>.<br/><em>SIGAD: XXXXX.XXXXXX/XXXX-XX</em>"
        ),
    )
    # link_processo_stf = ('get_sigad_url')
    num_convenio = models.CharField(
        _("número do convênio"), max_length=10, blank=True
    )
    id_contrato_gescon = models.CharField(
        _("ID do contrato no Gescon"),
        max_length=20,
        blank=True,
        default="",
        editable=False,
    )
    data_sigi = models.DateField(
        _("data de cadastro no SIGI"), blank=True, null=True, auto_now_add=True
    )
    data_sigad = models.DateField(
        _("data de cadastro no SIGAD"), null=True, blank=True
    )
    data_solicitacao = models.DateField(
        _("data do e-mail de solicitação"), null=True, blank=True
    )
    tipo_solicitacao = models.ForeignKey(
        TipoSolicitacao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("tipo de solicitação"),
    )
    status = models.ForeignKey(
        StatusConvenio,
        on_delete=models.SET_NULL,
        verbose_name=_("estado atual"),
        null=True,
        blank=True,
    )
    acompanha = models.ForeignKey(
        Servidor,
        on_delete=models.SET_NULL,
        related_name="convenios_acompanhados",
        verbose_name=_("acompanhado por"),
        null=True,
        blank=True,
    )
    observacao = models.TextField(
        _("observações"),
        null=True,
        blank=True,
    )
    servico_gestao = models.ForeignKey(
        Servico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="convenios_geridos",
        verbose_name=_("serviço de gestão"),
    )
    servidor_gestao = models.ForeignKey(
        Servidor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("servidor de gestão"),
    )
    data_adesao = models.DateField(
        _("aderidas"),
        null=True,
        blank=True,
    )
    data_retorno_assinatura = models.DateField(
        _("data início vigência"),
        null=True,
        blank=True,
        help_text=_("Convênio firmado."),
    )
    data_termino_vigencia = models.DateField(
        _("Data término vigência"),
        null=True,
        blank=True,
        help_text=_("Término da vigência do convênio."),
    )
    data_pub_diario = models.DateField(
        _("data da publicação no Diário Oficial"), null=True, blank=True
    )
    data_termo_aceite = models.DateField(
        _("equipadas"),
        null=True,
        blank=True,
        help_text=_("Equipamentos recebidos."),
    )
    data_devolucao_via = models.DateField(
        _("data de devolução da via"),
        null=True,
        blank=True,
        help_text=_(
            "Data de devolução da via do convênio à Câmara Municipal."
        ),
    )
    data_postagem_correio = models.DateField(
        _("data postagem correio"),
        null=True,
        blank=True,
    )
    data_devolucao_sem_assinatura = models.DateField(
        _("data de devolução por falta de assinatura"),
        null=True,
        blank=True,
        help_text=_("Data de devolução por falta de assinatura"),
    )
    data_retorno_sem_assinatura = models.DateField(
        _("data do retorno sem assinatura"),
        null=True,
        blank=True,
        help_text=_("Data do retorno do convênio sem assinatura"),
    )
    conveniada = models.BooleanField(default=False)
    equipada = models.BooleanField(default=False)
    atualizacao_gescon = models.DateTimeField(
        _("Data de atualização pelo Gescon"), blank=True, null=True
    )
    observacao_gescon = models.TextField(
        _("Observações da atualização do Gescon"), blank=True
    )

    def get_status(self):
        if self.status and self.status.cancela:
            return _("Cancelado")

        if self.data_retorno_assinatura is not None:
            if self.data_termino_vigencia is not None:
                if timezone.localdate() >= self.data_termino_vigencia:
                    return _("Vencido")
            return _("Vigente")

        if (
            self.data_retorno_assinatura is None
            and self.data_devolucao_sem_assinatura is None
            and self.data_retorno_sem_assinatura is None
        ):
            return _("Pendente")
        if (
            self.data_devolucao_sem_assinatura is not None
            or self.data_retorno_sem_assinatura is not None
        ):
            return _("Desistência")

        return _("Indefinido")

    def link_sigad(self, obj):
        if obj.pk is None:
            return ""
        return obj.get_sigad_url()

    def get_sigad_url(self, display_type="numero"):
        m = re.match(
            r"(?P<orgao>00100|00200)\.(?P<sequencial>\d{6})/(?P<ano>\d{4})-\d{2}",
            self.num_processo_sf,
        )
        if m:
            orgao, sequencial, ano = m.groups()
            if display_type == "numero":
                display = self.num_processo_sf
            else:
                display = "<i class='material-icons'>visibility</i>"
            return (
                f'<a href="https://intra.senado.leg.br/sigad/novo/protocolo/'
                f"impressao.asp?area=processo&txt_numero_orgao={orgao}"
                f'&txt_numero_sequencial={sequencial}&txt_numero_ano={ano}" '
                f'target="_blank">{display}</a>'
            )
        if display_type == "numero":
            return self.num_processo_sf
        else:
            return "<i class='material-icons'>visibility_off</i>"

    def get_url_gescon(self):
        if not self.id_contrato_gescon:
            return ""
        return (
            "https://adm.senado.gov.br/gestao-contratos/api/contratos"
            f"/buscaTexto/{self.id_contrato_gescon}"
        )

    def get_url_minuta(self):
        if self.id_contrato_gescon:
            return self.get_link_gescon()
        if self.anexo_set.exists():
            return self.anexo_set.first().arquivo.url
        return ""

    def save(self, *args, **kwargs):
        self.conveniada = self.data_retorno_assinatura is not None
        self.equipada = self.data_termo_aceite is not None
        super(Convenio, self).save(*args, **kwargs)

    class Meta:
        get_latest_by = "id"
        ordering = ("id",)
        verbose_name = _("convênio")

    def __str__(self):
        from django.conf import settings

        SDF = settings.SHORT_DATE_FORMAT
        number = self.num_convenio
        project = self.projeto.sigla
        if (self.data_retorno_assinatura is None) and (
            self.equipada and self.data_termo_aceite is not None
        ):
            date = date_format(self.data_termo_aceite, SDF)
            return _(f"{project} nº {number} - equipada em {date}")
        elif self.data_retorno_assinatura is None:
            date = (
                date_format(self.data_adesao, SDF) if self.data_adesao else ""
            )
            return _(f"{project}, nº {number}, início em {date}")
        if (self.data_retorno_assinatura is not None) and not (
            self.equipada and self.data_termo_aceite is not None
        ):
            date = date_format(self.data_retorno_assinatura, SDF)
            status = self.get_status()
            return _(
                f"{project}, nº {number}, inicio em {date}. Status: {status}"
            )
        if (self.data_retorno_assinatura is not None) and (
            self.equipada and self.data_termo_aceite is not None
        ):
            date = date_format(self.data_retorno_assinatura, SDF)
            equipped_date = date_format(self.data_termo_aceite, SDF)
            return _(
                f"{project}, nº {number}, início em {date} e equipada em "
                f"{equipped_date}. Status: {self.get_status()}"
            )


class EquipamentoPrevisto(models.Model):
    convenio = models.ForeignKey(
        Convenio, on_delete=models.CASCADE, verbose_name=_("convênio")
    )
    equipamento = models.ForeignKey(
        "inventario.Equipamento", on_delete=models.CASCADE
    )
    quantidade = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = _("equipamento previsto")
        verbose_name_plural = _("equipamentos previstos")

    def __str__(self):
        return _(f"{self.quantidade} {self.equipamento}(s)")


class Anexo(models.Model):
    convenio = models.ForeignKey(
        Convenio, on_delete=models.CASCADE, verbose_name=_("convênio")
    )
    # caminho no sistema para o documento anexo
    arquivo = models.FileField(
        upload_to="apps/convenios/anexo/arquivo", max_length=500
    )
    descricao = models.CharField(_("descrição"), max_length=70)
    data_pub = models.DateTimeField(
        _("data da publicação do anexo"), default=timezone.localtime
    )

    class Meta:
        ordering = ("-data_pub",)

    def __str__(self):
        return _(f"{self.descricao} publicado em {self.data_pub}")


class UnidadeAdministrativa(models.Model):
    sigla = models.CharField(max_length=10)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.sigla


class Tramitacao(models.Model):
    convenio = models.ForeignKey(
        Convenio, on_delete=models.CASCADE, verbose_name=_("convênio")
    )
    unid_admin = models.ForeignKey(
        UnidadeAdministrativa,
        on_delete=models.PROTECT,
        verbose_name=_("Unidade Administrativa"),
    )
    data = models.DateField()
    observacao = models.CharField(
        _("observação"),
        max_length=512,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = _("Tramitações")

    def __str__(self):
        in_date = _(f"em {self.data}")  # for focused translation
        result = f"{self.unid_admin} {in_date}"
        if self.observacao:
            result = f"{result} ({self.observacao})"
        return result


class Gescon(models.Model):
    url_gescon = models.URLField(
        _("Webservice Gescon"),
        default=(
            "https://adm.senado.gov.br/gestao-contratos/api/contratos"
            "/busca?especie={s}"
        ),
        help_text=_(
            "Informe o ponto de consulta do webservice do Gescon, "
            "inclusive com a querystring. No ponto onde deve ser "
            "inserida a sigla da subespecie do contrato, use a "
            "marcação {s}.<br/><strong>Por exemplo:</strong> "
            "https://adm.senado.gov.br/gestao-contratos/api/contratos"
            "/busca?especie=<strong>{s}</strong>"
        ),
    )
    subespecies = models.TextField(
        _("Subespécies"),
        default="AC=ACT\nPI=PI\nCN=PML\nTA=PML",
        help_text=_(
            "Informe as siglas das subespécies de contratos que "
            "devem ser pesquisados no Gescon com a sigla "
            "correspondente do projeto no SIGI. Coloque um par de "
            "siglas por linha, no formato SIGLA_GESTON=SIGLA_SIGI. "
            "As siglas não encontradas serão ignoradas."
        ),
    )
    palavras = models.TextField(
        _("Palavras de filtro"),
        default="ILB\nINTERLEGIS",
        help_text=_(
            "Palavras que devem aparecer no campo OBJETO dos dados do "
            "Gescon para identificar se o contrato pertence ao ILB. "
            "<ul><li>Informe uma palavra por linha.</li>"
            "<li>Ocorrendo qualquer uma das palavras, o contrato será "
            "importado.</li></ul>"
        ),
    )
    palavras_excluir = models.TextField(
        _("palavras de exclusão"),
        default="DTCOM",
        help_text=_(
            "Palavras que não podem aparecer no campo OBJETO dos dados do "
            "Gescon."
            "<ul><li>Informe uma palavra por linha.</li>"
            "<li>Ocorrendo qualquer uma das palavras, o contrato será "
            "ignorado.</li></ul>"
        ),
    )
    orgaos_gestores = models.TextField(
        _("Órgãos gestores"),
        default="SCCO",
        help_text=_(
            "Siglas de órgãos gestores que devem aparecer no campo"
            "ORGAOSGESTORESTITULARES"
            "<ul><li>Informe um sigla por linha.</li>"
            "<li>Ocorrendo qualquer uma das siglas, o contrato será "
            "importado.</li></ul>"
        ),
    )
    email = models.EmailField(
        _("E-mail"),
        help_text=_(
            "Caixa de e-mail para onde o relatório diário de "
            "importação será enviado."
        ),
    )
    ultima_importacao = models.TextField(
        _("Resultado da última importação"), blank=True
    )
    checksums = models.JSONField(null=True)

    class Meta:
        verbose_name = _("Configuração do Gescon")
        verbose_name_plural = _("Configurações do Gescon")

    def __str__(self):
        return self.url_gescon

    def save(self, *args, **kwargs):
        self.pk = 1  # Highlander (singleton pattern)
        return super(Gescon, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Highlander is immortal

    def add_message(self, msg, save=False):
        self.ultima_importacao += msg + "\n"
        if save:
            self.save()
            self.email_report()

    def email_report(self):
        if self.email:
            send_mail(
                subject=_("Relatório de importação GESCON"),
                message=self.ultima_importacao,
                recipient_list=self.email,
                fail_silently=True,
            )
        else:
            self.ultima_importacao += _(
                "\n\n*Não foi definida uma caixa de e-mail nas configurações "
                "do Gescon*"
            )
            self.save()

    def importa_contratos(self):
        """Importa dados de convênios do GESCON

        Returns:
            boolean: Indica se há o que reportar ao usuário (erro ou dados
                     importados/atualizados)
        """
        self.ultima_importacao = ""
        if self.checksums is None:
            self.checksums = {}
        self.add_message(
            _(
                f"Importação iniciada em {timezone.localtime():%d/%m/%Y %H:%M:%S}\n"
                "==========================================================\n"
            )
        )

        if self.palavras == "" or self.orgaos_gestores == "":
            self.add_message(
                _(
                    "Nenhuma palavra de pesquisa ou orgãos "
                    "gestores definidos - processo abortado."
                ),
                True,
            )
            return True

        if self.subespecies == "":
            self.add_message(
                _("Nenhuma subespécie definida - processo " "abortado."), True
            )
            return True

        if "{s}" not in self.url_gescon:
            self.add_message(
                _(
                    "Falta a marcação {s} na URL para indicar o local onde "
                    "inserir a sigla da subespécia na consulta ao webservice "
                    "- processo abortado."
                ),
                True,
            )
            return True

        palavras = self.palavras.splitlines()
        excludentes = self.palavras_excluir.splitlines()
        orgaos = self.orgaos_gestores.split()
        subespecies = {tuple(s.split("=")) for s in self.subespecies.split()}
        lista_cnpj = {
            re.sub("[^\d]", "", o.cnpj).zfill(14): o
            for o in Orgao.objects.exclude(cnpj="")
            if re.sub("[^\d]", "", o.cnpj) != ""
        }

        requests.packages.urllib3.disable_warnings()
        report_user = False

        for sigla_gescon, sigla_sigi in subespecies:
            self.add_message(_(f"\n**Importando subespécie {sigla_gescon}**"))
            url = self.url_gescon.format(s=sigla_gescon)

            projeto = Projeto.objects.get(sigla=sigla_sigi)

            try:
                response = requests.get(url, verify=False)
            except Exception as e:
                self.add_message(_(f"\tErro ao acessar {url}: {e.message}"))
                report_user = True
                continue

            if not response.ok:
                self.add_message(
                    _(f"\tErro ao acessar {url}: {response.reason}")
                )
                report_user = True
                continue

            if not "application/json" in response.headers.get("Content-Type"):
                self.add_message(
                    _(
                        f"\tResultado da consulta à {url} não "
                        "retornou dados em formato json"
                    )
                )
                report_user = True
                continue

            md5sum = md5(response.text.encode(response.encoding)).hexdigest()
            if (
                sigla_gescon in self.checksums
                and self.checksums[sigla_gescon] == md5sum
            ):
                self.add_message(
                    f"Dados da subespécie {sigla_gescon} inalterados no Gescon."
                    " Processamento desnecessário."
                )
                continue

            contratos = response.json()

            # Pegar só os contratos que possuem alguma das palavras-chave

            nossos = [
                c
                for c in contratos
                if (
                    any(palavra in c["objeto"] for palavra in palavras)
                    or any(
                        orgao in c["orgaosGestoresTitulares"]
                        for orgao in orgaos
                        if c["orgaosGestoresTitulares"] is not None
                    )
                )
                and not any(palavra in c["objeto"] for palavra in excludentes)
            ]

            self.add_message(
                _(f"\t{len(nossos)} contratos encontrados no Gescon")
            )

            novos = 0
            erros = 0
            alertas = 0
            atualizados = 0

            for contrato in nossos:
                numero = contrato["numero"].zfill(8)
                numero = f"{numero[:4]}/{numero[4:]}"
                sigad = contrato["processo"].zfill(17)
                sigad = (
                    f"{sigad[:5]}.{sigad[5:11]}/{sigad[11:15]}-{sigad[15:]}"
                )

                if contrato["cnpjCpfFornecedor"]:
                    cnpj = contrato["cnpjCpfFornecedor"].zfill(14)
                    cnpj_masked = (
                        f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/"
                        f"{cnpj[8:12]}-{cnpj[12:]}"
                    )
                else:
                    cnpj = None

                if contrato["nomeFornecedor"]:
                    nome = contrato["nomeFornecedor"]
                    nome = nome.replace("VEREADORES DE", "")
                    nome = nome.split("-")[0]
                    nome = nome.split("/")[0]
                    nome = nome.strip()
                    nome = nome.replace("  ", " ")
                    nome = to_ascii(nome)
                else:
                    nome = None

                if (cnpj is None) and (nome is None):
                    self.add_message(
                        _(
                            f"\tO contrato {numero} no Gescon não informa o CNPJ"
                            "nem o nome do órgão."
                        )
                    )
                    erros += 1
                    continue

                orgao = None

                if cnpj is not None:
                    if cnpj in lista_cnpj:
                        orgao = lista_cnpj[cnpj]
                    else:
                        try:
                            orgao = Orgao.objects.get(cnpj=cnpj_masked)
                        except (
                            Orgao.DoesNotExist,
                            Orgao.MultipleObjectsReturned,
                        ) as e:
                            orgao = None
                            pass

                if (orgao is None) and (nome is not None):
                    try:
                        orgao = Orgao.objects.get(search_text__iexact=nome)
                    except (
                        Orgao.DoesNotExist,
                        Orgao.MultipleObjectsReturned,
                    ) as e:
                        orgao = None
                        pass

                if orgao is None:
                    self.add_message(
                        _(
                            f"\tÓrgão não encontrado no SIGI ou mais de um "
                            f"órgão encontrado com o mesmo CNPJ ou nome. Favor "
                            f"regularizar o cadastro: "
                            f"CNPJ: {contrato['cnpjCpfFornecedor']}, "
                            f"Nome: {contrato['nomeFornecedor']}"
                        )
                    )
                    erros += 1
                    continue

                # O mais seguro é o NUP sigad
                convenios = Convenio.objects.filter(num_processo_sf=sigad)
                chk = convenios.count()

                if chk == 0:
                    # NUP não encontrado, talvez exista apenas com o número
                    # do GESCON
                    convenios = Convenio.objects.filter(
                        Q(num_convenio=numero) | Q(num_processo_sf=numero)
                    )
                    chk = convenios.count()
                    if chk > 1:
                        # Pode ser que existam vários contratos de subespécies
                        # diferentes com o mesmo número Gescon. Neste caso, o
                        # ideal é filtrar pelo tipo de projeto. Existindo, é
                        # ele mesmo. Se não existir, então segue com os
                        # múltiplos para registrar o problema mais adiante
                        if convenios.filter(projeto=projeto).count() == 1:
                            convenios = convenios.filter(projeto=projeto)
                            chk = 1

                if chk == 0:
                    convenio = Convenio(
                        casa_legislativa=orgao,
                        projeto=projeto,
                        num_processo_sf=sigad,
                        num_convenio=numero,
                        data_sigi=timezone.localdate(),
                        data_sigad=contrato["assinatura"],
                        observacao=contrato["objeto"],
                        data_retorno_assinatura=contrato["inicioVigencia"],
                        data_termino_vigencia=contrato["terminoVigencia"],
                        data_pub_diario=contrato["publicacao"],
                        atualizacao_gescon=timezone.localtime(),
                        observacao_gescon=_(
                            "Importado integralmente do" "Gescon"
                        ),
                    )
                    convenio.save()
                    novos += 1
                    continue
                elif chk == 1:
                    convenio = convenios.get()
                    convenio.atualizacao_gescon = timezone.localtime()
                    convenio.observacao_gescon = ""
                    if convenio.casa_legislativa != orgao:
                        self.add_message(
                            _(
                                f"\tO órgao no convênio {convenio.id} diverge do "
                                f"que consta no Gescon ({cnpj}, "
                                f"{contrato['nomeFornecedor']})"
                            )
                        )
                        convenio.observacao_gescon = _(
                            "ERRO: Órgão diverge do Gescon. Não atualizado!"
                        )
                        convenio.save()
                        erros += 1
                        continue

                    if convenio.num_processo_sf != sigad:
                        self.add_message(
                            _(
                                f"\tO contrato Gescon nº {numero} corresponde"
                                f" ao convênio SIGI {convenio.id}, mas o NUP "
                                f"sigad diverge (Gescon: {sigad}, "
                                f"SIGI: {convenio.num_processo_sf}). "
                                "CORRIGIDO!"
                            )
                        )
                        convenio.num_processo_sf = sigad
                        convenio.observacao_gescon += _(
                            "Número do SIGAD atualizado.\n"
                        )
                        alertas += 1

                    if convenio.num_convenio != numero:
                        self.add_message(
                            _(
                                f"\tO contrato Gescon ID {contrato['id']} "
                                f"corresponde ao convênio SIGI {convenio.id}, "
                                "mas o número do convênio diverge ("
                                f"Gescon: {numero}, SIGI: {convenio.num_convenio}"
                                "). CORRIGIDO!"
                            )
                        )
                        convenio.num_convenio = numero
                        convenio.observacao_gescon += _(
                            "Número do convênio atualizado.\n"
                        )
                        alertas += 1

                    if contrato["objeto"] not in convenio.observacao:
                        convenio.observacao += "\n" + contrato["objeto"]
                        convenio.observacao_gescon += _(
                            "Observação atualizada.\n"
                        )

                    convenio.data_sigad = contrato["assinatura"]
                    convenio.data_retorno_assinatura = contrato[
                        "inicioVigencia"
                    ]
                    convenio.data_termino_vigencia = contrato[
                        "terminoVigencia"
                    ]
                    convenio.data_pub_diario = contrato["publicacao"]
                    if contrato["codTextoContrato"]:
                        convenio.id_contrato_gescon = contrato[
                            "codTextoContrato"
                        ]
                    else:
                        convenio.id_contrato_gescon = ""

                    try:
                        convenio.save()
                    except Exception as e:
                        self.add_message(
                            _(
                                "Ocorreu um erro ao salvar o convênio "
                                f"{convenio.id} no SIGI. Alguma informação do "
                                "Gescon pode ter quebrado o sistema. Informe ao "
                                f"suporte. Erro: {e.message}"
                            )
                        )
                        erros += 1
                        continue

                    atualizados += 1
                else:
                    self.add_message(
                        _(
                            f"\tExistem {chk} convênios no SIGI que "
                            "correspondem ao mesmo contrato no Gescon (contrato "
                            f"{numero}, sigad {sigad})"
                        )
                    )
                    erros += 1
                    continue

            if novos or erros or alertas or atualizados:
                report_user = True

            self.add_message(
                _(
                    f"\t{novos} novos convenios adicionados ao SIGI, "
                    f"{atualizados} atualizados, sendo {alertas} com alertas, e "
                    f"{erros} reportados com erro."
                )
            )
            self.checksums[sigla_gescon] = md5sum

        self.save()
        return report_user

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
