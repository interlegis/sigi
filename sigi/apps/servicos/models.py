from django.utils import timezone
from django.db import models
from django.db.models import Q
from sigi.apps.casas.models import Orgao, Funcionario
from django.utils.translation import gettext as _


class TipoServico(models.Model):
    MODO_CHOICES = (("H", _("Hospedagem")), ("R", _("Registro")))
    email_help = "Use a marcação {url} para incluir a URL do serviço,<br/>"
    string_pesquisa_help = (
        "Parâmetros da pesquisa para averiguar a data da "
        "última atualização do serviço. Formato:<br/>"
        "<ul><li>/caminho/da/pesquisa/?parametros "
        "[xml|json] campo.de.data</li>"
    )
    nome = models.CharField(_("nome"), max_length=60)
    sigla = models.CharField(_("sigla"), max_length=12)
    modo = models.CharField(
        _("modo de prestação do serviço"), max_length=1, choices=MODO_CHOICES
    )
    tipo_rancher = models.CharField(
        _("tipo de objeto no Rancher"), max_length=100, blank=True
    )
    spec_rancher = models.CharField(
        _("spec do serviço no Rancher"), max_length=100, blank=True
    )
    arquivo_rancher = models.CharField(
        _("nome do arquivo gerado no rancher"), max_length=100, blank=True
    )
    prefixo_padrao = models.CharField(max_length=20, blank=True)
    string_pesquisa = models.TextField(
        _("string de pesquisa"), blank=True, help_text=string_pesquisa_help
    )
    template_email_ativa = models.TextField(
        _("template de email de ativação"), help_text=email_help, blank=True
    )
    template_email_altera = models.TextField(
        _("template de email de alteração"), help_text=email_help, blank=True
    )
    template_email_desativa = models.TextField(
        _("template de email de desativação"),
        help_text=email_help
        + _("<br/>{motivo} para incluir o motivo da desativação do serviço"),
        blank=True,
    )

    @property
    def qtde_casas_atendidas(self):
        """Quantidade de casas atendidas"""
        return self.servico_set.filter(data_desativacao=None).count()

    class Meta:
        verbose_name = _("tipo de serviço")
        verbose_name_plural = _("tipos de serviço")

    def __str__(self):
        return self.nome


class Servico(models.Model):
    RESULTADO_CHOICES = (
        ("N", _("Não verificado")),
        ("F", _("Funcionando")),
        ("U", _("Nunca foi usado")),
        ("D", _("Acesso negado")),
        ("O", _("Fora do ar")),
        ("I", _("Dados imcompatíveis - não é serviço Interlegis")),
    )
    casa_legislativa = models.ForeignKey(
        Orgao, on_delete=models.PROTECT, verbose_name=_("Casa Legislativa")
    )
    tipo_servico = models.ForeignKey(
        TipoServico,
        on_delete=models.PROTECT,
        verbose_name=_("tipo de serviço"),
    )
    url = models.URLField(_("URL do serviço"), blank=True)
    versao = models.CharField(_("versão"), max_length=20, blank=True)
    hospedagem_interlegis = models.BooleanField(
        _("Hospedagem no Interlegis?"), default=False
    )
    instancia = models.CharField(
        _("nome da instância"), max_length=100, blank=True
    )
    apps = models.TextField(_("apps instaladas no DNS"), blank=True)
    data_ativacao = models.DateField(
        _("Data de ativação"), default=timezone.localdate
    )
    data_alteracao = models.DateField(
        _("Data da última alteração"), blank=True, null=True, auto_now=True
    )
    data_desativacao = models.DateField(
        _("Data de desativação"), blank=True, null=True
    )
    motivo_desativacao = models.TextField(
        _("Motivo da desativação"), blank=True
    )
    data_verificacao = models.DateTimeField(
        _("data da última verificação"), blank=True, null=True
    )
    resultado_verificacao = models.CharField(
        _("resultado da verificação"),
        choices=RESULTADO_CHOICES,
        default="N",
        max_length=1,
    )
    data_ultimo_uso = models.DateField(
        _("Data da última utilização"),
        blank=True,
        null=True,
        help_text=_(
            "Data em que o serviço foi utilizado pela Casa Legislativa"
            " pela última vez"
        ),
    )
    erro_atualizacao = models.TextField(
        _("Erro na atualização"),
        blank=True,
        help_text=_(
            "Erro ocorrido na última tentativa de verificar a data "
            "de última atualização do serviço"
        ),
    )
    flag_confirmado = models.BooleanField(
        _("indica se o registro foi confirmado"), default=False
    )

    @property
    def status_servico(self):
        if self.data_desativacao is None:
            return _("Ativo")
        else:
            return _("Inativo")

    def atualiza_data_uso(self):
        import requests
        from xml.dom.minidom import parseString

        requests.packages.urllib3.disable_warnings()

        def reset():
            if self.data_ultimo_uso is not None:
                self.data_verificacao = None
                self.resultado_verificacao = "N"
                self.data_ultimo_uso = None
                self.erro_atualizacao = ""
                self.save()
            return

        def ultimo_uso(url, string_pesquisa):
            param_pesquisa = string_pesquisa.split(" ")
            if len(param_pesquisa) != 3:
                return {
                    "data": "",
                    "resultado": "N",
                    "erro": _("String de pesquisa mal configurada"),
                    "comment": _("Corrija a string de pesquisa"),
                }
            campos = [
                int(s) if s.isdigit() else s
                for s in param_pesquisa[2].split(".")
            ]

            url += param_pesquisa[0]

            try:  # Captura erros de conexão
                req = requests.get(url, verify=False, allow_redirects=True)
            except Exception as e:
                return {
                    "data": "",
                    "resultado": "O",
                    "erro": str(e),
                    "comment": _(
                        "Não foi possível conectar com o servidor. "
                        "Pode estar fora do ar ou não ser "
                        "um {tipo}".format(tipo=self.tipo_servico.nome)
                    ),
                }

            if req.status_code != 200:
                return {
                    "data": "",
                    "resultado": "D",
                    "erro": req.reason,
                    "comment": _(
                        "Não foi possível receber os dados do "
                        "servidor. O acesso pode ter sido negado."
                    ),
                }

            try:
                if param_pesquisa[1] == "xml":
                    data = parseString(req.content)
                elif param_pesquisa[1] == "json":
                    data = req.json()
                else:
                    return {
                        "data": "",
                        "resultado": "N",
                        "erro": _("String de pesquisa mal configurada"),
                        "comment": "",
                    }

                for c in campos:
                    if isinstance(c, int):
                        if (len(data) - 1) < c:
                            return {
                                "data": "",
                                "resultado": "U",
                                "erro": _("Sem dados para verificação"),
                                "comment": _("Parece que nunca foi usado"),
                            }
                        data = data[c]
                    else:
                        if param_pesquisa[1] == "xml":
                            data = data.getElementsByTagName(c)
                        else:
                            data = data[c]

                if param_pesquisa[1] == "xml":
                    if data.hasChildNodes():
                        data = data.firstChild.nodeValue
                    else:
                        data = data.nodeValue
                if data is None or data == "":
                    return {
                        "data": "",
                        "resultado": "U",
                        "erro": _("Sem data da última atualização."),
                        "comment": _("Parece que nunca foi usado"),
                    }
                data = data[:10]
                data = data.replace("/", "-")
                return {
                    "data": data,
                    "resultado": "F",
                    "erro": "",
                    "comment": "",
                }
            except Exception as e:
                return {
                    "data": "",
                    "resultado": "I",
                    "erro": str(e),
                    "comment": _(
                        "Parece que não é um {tipo}".format(
                            tipo=self.tipo_servico.nome
                        )
                    ),
                }

        if self.tipo_servico.string_pesquisa == "":
            reset()
            return

        url = self.url

        if not url:
            reset()
            self.erro_atualizacao = _("Serviço sem URL")
            self.data_verificacao = timezone.localtime()
            self.save()
            return

        if url[-1] != "/":
            url += "/"

        resultados = []

        for string_pesquisa in self.tipo_servico.string_pesquisa.splitlines():
            resultados.append(ultimo_uso(url, string_pesquisa))

        data = max([r["data"] for r in resultados])
        resultado = {r["resultado"] for r in resultados}

        if "F" in resultado:
            self.resultado_verificacao = "F"
        else:
            self.resultado_verificacao = resultado.pop()

        if data == "":
            # Nenhuma busca deu resultado, guardar log de erro
            self.data_ultimo_uso = None
            self.erro_atualizacao = "<br/>".join(
                set(
                    [
                        f"{r['erro']} ({r['comment']})"
                        for r in resultados
                        if r["erro"] != "" and r["comment"] != ""
                    ]
                )
            )
        else:
            # Atualiza a maior data de atualização
            self.data_ultimo_uso = data[:10]  # Apenas YYYY-MM-DD
            self.erro_atualizacao = ""

        self.data_verificacao = timezone.localtime()
        self.save()

        return

    class Meta:
        verbose_name = _("serviço SEIT")
        verbose_name_plural = _("serviços SEIT")
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_servico", "instancia", "url"],
                condition=Q(data_desativacao=None) & ~Q(instancia=""),
                name="unique_instance",
            )
        ]

    def __str__(self):
        return f"{self.tipo_servico.nome} ({self.status_servico})"

    def save(self, *args, **kwargs):
        # Reter o objeto original para verificar mudanças

        if self.id is not None:
            original = Servico.objects.get(id=self.id)

        if self.id is None:
            # Novo serviço, email de ativação
            subject = _("INTERLEGIS - Ativação de serviço %s") % (
                self.tipo_servico.nome,
            )
            body = self.tipo_servico.template_email_ativa
        elif (
            self.data_desativacao is not None
            and original.data_desativacao is None
        ):
            # Serviço foi desativado. Email de desativação
            subject = _("INTERLEGIS - Desativação de serviço %s") % (
                self.tipo_servico.nome,
            )
            body = self.tipo_servico.template_email_desativa
        elif (
            self.tipo_servico != original.tipo_servico
            or self.url != original.url
        ):
            # Serviço foi alterado
            subject = _("INTERLEGIS - Alteração de serviço %s") % (
                self.tipo_servico.nome,
            )
            body = self.tipo_servico.template_email_altera
        else:
            # Salvar o Servico
            super(Servico, self).save(*args, **kwargs)
            return  # sem enviar email

        # Prepara e envia o email
        body = body.replace("{url}", self.url).replace(
            "{motivo}", self.motivo_desativacao
        )

        #        send_mail(subject, body, DEFAULT_FROM_EMAIL, \
        #                  (self.contato_tecnico.email,), fail_silently=False)

        # Salvar o Servico
        super(Servico, self).save(*args, **kwargs)

        return


class LogServico(models.Model):
    servico = models.ForeignKey(
        Servico, on_delete=models.CASCADE, verbose_name=_("Serviço")
    )
    descricao = models.CharField(_("Breve descrição da ação"), max_length=60)
    data = models.DateField(_("Data da ação"), default=timezone.localdate)
    log = models.TextField(_("Log da ação"))

    def __str__(self):
        return f"{self.descricao} ({self.data})"

    class Meta:
        verbose_name = _("Log do serviço")
        verbose_name_plural = _("Logs do serviço")


class CasaManifesta(models.Model):
    casa_legislativa = models.OneToOneField(Orgao, on_delete=models.CASCADE)
    data_manifestacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    informante = models.CharField(
        _("Nome do informante"), max_length=100, blank=True
    )
    cargo = models.CharField(
        _("Cargo do informante"), max_length=100, blank=True
    )
    email = models.EmailField(_("E-mail de contato"), blank=True)


class ServicoManifesto(models.Model):
    casa_manifesta = models.ForeignKey(CasaManifesta, on_delete=models.CASCADE)
    servico = models.ForeignKey(TipoServico, on_delete=models.CASCADE)
    url = models.URLField(blank=True)
    hospedagem_interlegis = models.BooleanField(
        _("Hospedagem no Interlegis?"), default=False
    )

    class Meta:
        unique_together = ("casa_manifesta", "servico")


class RegistroServico(models.Model):
    produto = models.CharField(max_length=50)
    versao = models.CharField(max_length=30)
    url = models.URLField()
    data_registro = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("Registro de serviços")
