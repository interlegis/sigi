import re
import requests
from hashlib import md5
from pathlib import Path
from url_normalize import url_normalize
from django.db import models
from django.db.models import Q, F
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator
from django.template import Template, Context
from django.template.exceptions import TemplateSyntaxError
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_weasyprint.utils import DjangoURLFetcher
from docx import Document
from tinymce.models import HTMLField
from weasyprint import HTML
from sigi.apps.contatos.models import Municipio, UnidadeFederativa
from sigi.apps.parlamentares.models import Parlamentar
from sigi.apps.utils import to_ascii
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.servidores.models import Servidor, Servico
from sigi.apps.utils import editor_help, mask_cnpj, get_sigad_url


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
    termino_indefinido = models.BooleanField(
        _("Término indefinido"),
        default=True,
        help_text=_(
            "Indica se os convênios deste tipo podem estar vigentes sem ter "
            "uma data de término de vigência."
        ),
    )
    extinto = models.BooleanField(
        _("extinto"),
        default=False,
        help_text=_(
            "Indica se este projeto foi extinto e todos os convênios dele devem ser extintos também."
        ),
    )
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
            url_fetcher=DjangoURLFetcher(),
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
    id_gescon = models.IntegerField(
        _("ID do convênio no Gescon"), blank=True, null=True
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
        help_text=_("Data de devolução da via do convênio à Câmara Municipal."),
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
    data_extincao = models.DateField(
        _("data de extinção/desistência"), null=True, blank=True
    )
    motivo_extincao = models.TextField(
        _("motivo da extinção/desistência"), blank=True
    )
    conveniada = models.BooleanField(default=False)
    equipada = models.BooleanField(default=False)
    atualizacao_gescon = models.DateTimeField(
        _("Data de atualização pelo Gescon"), blank=True, null=True
    )
    erro_gescon = models.BooleanField(
        _("erro no Gescon"),
        max_length=1,
        default=False,
    )
    observacao_gescon = models.TextField(
        _("Observações da atualização do Gescon"), blank=True
    )

    def get_status(self):
        if self.status and self.status.cancela:
            return _("Cancelado")

        if self.data_extincao:
            return _("Extinto")

        if self.projeto.extinto:
            return _("Descontinuado")

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
        return mark_safe(get_sigad_url(self.num_processo_sf, display_type))

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

    def clean(self):
        # Gertiq #184827
        if self.num_convenio:
            if not self.projeto.termino_indefinido and (
                self.data_retorno_assinatura is None
                or self.data_termino_vigencia is None
            ):
                errors = {
                    NON_FIELD_ERRORS: ValidationError(
                        _(
                            "Um convênio vigente precisa ter as datas de "
                            "início e término de vigência"
                        )
                    )
                }
                raise ValidationError(errors)
        else:
            if (
                self.data_retorno_assinatura is not None
                or self.data_termino_vigencia is not None
            ):
                errors = {
                    NON_FIELD_ERRORS: ValidationError(
                        _(
                            "Um convênio pendente não pode ter datas de "
                            "início e término de vigência"
                        )
                    )
                }
                raise ValidationError(errors)
        return super().clean()

    def save(self, *args, **kwargs):
        self.conveniada = self.data_retorno_assinatura is not None
        self.equipada = self.data_termo_aceite is not None
        super().save(*args, **kwargs)

    class Meta:
        get_latest_by = "id"
        ordering = ("id",)
        verbose_name = _("convênio")
        verbose_name_plural = _("convênios")
        constraints = [
            models.UniqueConstraint(
                fields=["id_gescon"],
                condition=models.Q(id_gescon__isnull=False),
                name="unique_id_gescon_if_not_null",
            )
        ]

    def __str__(self):
        SDF = "SHORT_DATE_FORMAT"
        number = self.num_convenio
        project = self.projeto.sigla
        if self.data_extincao:
            date = date_format(self.data_extincao, SDF)
            return _(f"{project} nº {number} extinto em {date}")
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
