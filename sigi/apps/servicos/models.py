from datetime import date
from django.db import models
from sigi.apps.casas.models import Orgao, Funcionario
from django.utils.translation import gettext as _


class TipoServico(models.Model):
    MODO_CHOICES = (("H", _("Hospedagem")), ("R", _("Registro")))
    email_help = """Use:<br/>
                        {url} para incluir a URL do serviço,<br/>
                        {senha} para incluir a senha inicial do serviço"""
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
    string_pesquisa = models.TextField(
        _("string de pesquisa"), blank=True, help_text=string_pesquisa_help
    )
    template_email_ativa = models.TextField(
        _("Template de email de ativação"), help_text=email_help, blank=True
    )
    template_email_altera = models.TextField(
        _("Template de email de alteração"), help_text=email_help, blank=True
    )
    template_email_desativa = models.TextField(
        _("Template de email de desativação"),
        help_text=email_help
        + _("<br/>{motivo} para incluir o motivo da desativação do serviço"),
        blank=True,
    )

    @property
    def qtde_casas_atendidas(self):
        """Quantidade de casas atendidas"""
        return self.servico_set.filter(data_desativacao=None).count()

    class Meta:
        verbose_name = _("Tipo de serviço")
        verbose_name_plural = _("Tipos de serviço")

    def __str__(self):
        return self.nome


class Servico(models.Model):
    casa_legislativa = models.ForeignKey(
        Orgao, on_delete=models.PROTECT, verbose_name=_("Casa Legislativa")
    )
    tipo_servico = models.ForeignKey(
        TipoServico, on_delete=models.PROTECT, verbose_name=_("Tipo de serviço")
    )
    contato_tecnico = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        verbose_name=_("Contato técnico"),
        related_name="contato_tecnico",
    )
    contato_administrativo = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        verbose_name=_("Contato administrativo"),
        related_name="contato_administrativo",
    )
    url = models.URLField(_("URL do serviço"), blank=True)
    hospedagem_interlegis = models.BooleanField(
        _("Hospedagem no Interlegis?"), default=False
    )
    nome_servidor = models.CharField(
        _("Hospedado em"),
        max_length=60,
        blank=True,
        help_text=_(
            "Se hospedado no Interlegis, informe o nome do servidor."
            "<br/>Senão, informe o nome do provedor de serviços."
        ),
    )
    porta_servico = models.PositiveSmallIntegerField(
        _("Porta de serviço (instância)"), blank=True, null=True
    )
    senha_inicial = models.CharField(
        _("Senha inicial"), max_length=33, blank=True
    )
    data_ativacao = models.DateField(_("Data de ativação"), default=date.today)
    data_alteracao = models.DateField(
        _("Data da última alteração"), blank=True, null=True, auto_now=True
    )
    data_desativacao = models.DateField(
        _("Data de desativação"), blank=True, null=True
    )
    motivo_desativacao = models.TextField(
        _("Motivo da desativação"), blank=True
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

    @property
    def status_servico(self):
        if self.data_desativacao is None:
            return _("Ativo")
        else:
            return _("Inativo")

    def atualiza_data_uso(self):
        import requests
        from xml.dom.minidom import parseString

        def reset():
            if self.data_ultimo_uso is not None:
                self.data_ultimo_uso = None
                self.erro_atualizacao = ""
                self.save()
            return

        def ultimo_uso(url, string_pesquisa):
            param_pesquisa = string_pesquisa.split(" ")
            if len(param_pesquisa) != 3:
                return {
                    "data": "",
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
                        "erro": _("String de pesquisa mal configurada"),
                        "comment": "",
                    }

                for c in campos:
                    if isinstance(c, int):
                        if (len(data) - 1) < c:
                            return {
                                "data": "",
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
                    data = data.firstChild.nodeValue
                data = data[:10]
                data = data.replace("/", "-")
                return {"data": data, "erro": "", "comment": ""}
            except Exception as e:
                return {
                    "data": "",
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
            self.save()
            return

        if url[-1] != "/":
            url += "/"

        resultados = []

        for string_pesquisa in self.tipo_servico.string_pesquisa.splitlines():
            resultados.append(ultimo_uso(url, string_pesquisa))

        data = max([r["data"] for r in resultados])

        if data == "":
            # Nenhuma busca deu resultado, guardar log de erro
            self.data_ultimo_uso = None
            self.erro_atualizacao = "<br/>".join(
                set(
                    [
                        "{erro} ({comment})".format(
                            erro=r["erro"], comment=r["comment"]
                        )
                        for r in resultados
                        if r["erro"] != "" and r["comment"] != ""
                    ]
                )
            )
            self.save()
        else:
            # Atualiza a maior data de atualização
            self.data_ultimo_uso = data[:10]  # Apenas YYYY-MM-DD
            self.erro_atualizacao = ""
            self.save()

        return

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
            or self.contato_tecnico != original.contato_tecnico
            or self.url != original.url
            or self.nome_servidor != original.nome_servidor
            or self.senha_inicial != original.senha_inicial
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
        body = (
            body.replace("{url}", self.url)
            .replace("{senha}", self.senha_inicial)
            .replace("{motivo}", self.motivo_desativacao)
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
    data = models.DateField(_("Data da ação"), default=date.today)
    log = models.TextField(_("Log da ação"))

    def __str__(self):
        return f"{self.descricao} ({self.data})"

    class Meta:
        verbose_name = _("Log do serviço")
        verbose_name_plural = _("Logs do serviço")


class CasaAtendidaManager(models.Manager):
    def get_queryset(self):
        qs = super(CasaAtendidaManager, self).get_queryset()
        qs = qs.exclude(codigo_interlegis="")
        return qs


class CasaAtendida(Orgao):
    class Meta:
        proxy = True
        verbose_name_plural = _("Casas atendidas")

    objects = CasaAtendidaManager()


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
