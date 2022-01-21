from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe


class Categoria(models.Model):
    nome = models.CharField(_("Categoria"), max_length=50)
    descricao = models.TextField(_('descrição'), blank=True, null=True)
    setor_responsavel = models.ForeignKey(
        'servidores.Servico',
        on_delete=models.PROTECT,
        verbose_name=_("Setor responsável")
    )

    class Meta:
        verbose_name = _('Categoria')
        verbose_name_plural = _('Categorias')
        ordering = ('nome',)

    def __str__(self):
        return self.nome

class TipoContato(models.Model):
    descricao = models.CharField(_("Descrição"), max_length=50)

    class Meta:
        verbose_name = _("Tipo de contato")
        verbose_name_plural = _("Tipos de contato")

    def __str__(self):
        return self.descricao

class Ocorrencia(models.Model):
    STATUS_ABERTO    = 1
    STATUS_REABERTO  = 2
    STATUS_RESOLVIDO = 3
    STATUS_FECHADO   = 4
    STATUS_DUPLICADO = 5

    STATUS_CHOICES = (
        (STATUS_ABERTO   , _('Aberto')),
        (STATUS_REABERTO , _('Reaberto')),
        (STATUS_RESOLVIDO, _('Resolvido')),
        (STATUS_FECHADO  , _('Fechado')),
        (STATUS_DUPLICADO, _('Duplicado')),
    )

    PRIORITY_CHOICES = (
        (1, _('Altíssimo')),
        (2, _('Alto')),
        (3, _('Normal')),
        (4, _('Baixo')),
        (5, _('Baixíssimo')),
    )

    casa_legislativa = models.ForeignKey(
        'casas.Orgao',
        on_delete=models.CASCADE,
        verbose_name=_('Casa Legislativa')
    )
    data_criacao = models.DateField(
        _('Data de criação'),
        null=True,
        blank=True,
        auto_now_add=True
    )
    data_modificacao = models.DateField(
        _('Data de modificação'),
        null=True,
        blank=True,
        auto_now=True
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        verbose_name=_('Categoria')
    )
    tipo_contato = models.ForeignKey(
        TipoContato,
        on_delete=models.PROTECT,
        verbose_name=_("Tipo de contato")
    )
    assunto = models.CharField(_('Assunto'), max_length=200)
    status = models.IntegerField(
        _('Status'),
        choices=STATUS_CHOICES,
        default=1
    )
    prioridade = models.IntegerField(
        _('Prioridade'),
        choices=PRIORITY_CHOICES,
        default=3
    )
    descricao = models.TextField(_('descrição'), blank=True,)
    resolucao = models.TextField(_('resolução'), blank=True,)
    servidor_registro = models.ForeignKey(
        'servidores.Servidor',
        on_delete=models.PROTECT,
        verbose_name=_("Servidor que registrou a ocorrência")
    )
    setor_responsavel = models.ForeignKey(
        'servidores.Servico',
        on_delete=models.PROTECT,
        verbose_name=_("Setor responsável")
    )
    ticket = models.PositiveIntegerField(
        _('Número do ticket'),
        blank=True,
        null=True,
        help_text=_("Número do ticket no osTicket")
    )

    class Meta:
        verbose_name = _('ocorrência')
        verbose_name_plural = _('ocorrências')
        ordering = ['prioridade', 'data_modificacao', 'data_criacao', ]

    def __str__(self):
        return _(f"{self.casa_legislativa}: {self.assunto}")

    def clean(self):
        if (self.ticket is not None
            and Ocorrencia.objects.exclude(pk=self.pk).filter(
                ticket=self.ticket).exists()
        ):
            raise ValidationError({'ticket': _("Já existe ocorrência "
                                               "registrada para este ticket")})
        return super(Ocorrencia, self).clean()

    def get_ticket_url(self):
        return mark_safe(settings.OSTICKET_URL % self.ticket)

class Comentario(models.Model):
    ocorrencia = models.ForeignKey(
        Ocorrencia,
        on_delete=models.CASCADE,
        verbose_name=_('Ocorrência'),
        related_name='comentarios'
    )
    data_criacao = models.DateTimeField(
        _('Data de criação'),
        null=True,
        blank=True,
        auto_now_add=True
    )
    descricao = models.TextField(_('Descrição'), blank=True, null=True)
    usuario = models.ForeignKey(
        'servidores.Servidor',
        on_delete=models.PROTECT,
        verbose_name=_('Usuário')
    )
    novo_status = models.IntegerField(
        _('Novo status'),
        choices=Ocorrencia.STATUS_CHOICES,
        blank=True,
        null=True
    )
    encaminhar_setor = models.ForeignKey(
        'servidores.Servico',
        on_delete=models.PROTECT,
        verbose_name=_('Encaminhar para setor'),
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        if (self.encaminhar_setor
            and (self.encaminhar_setor != self.ocorrencia.setor_responsavel)
        ):
            self.ocorrencia.setor_responsavel = self.encaminhar_setor
            self.ocorrencia.save()
        if self.novo_status and (self.novo_status != self.ocorrencia.status):
            self.ocorrencia.status = self.novo_status
            self.ocorrencia.save()
        super(Comentario, self).save(*args, **kwargs)

class Anexo(models.Model):
    ocorrencia = models.ForeignKey(
        Ocorrencia,
        on_delete=models.CASCADE,
        verbose_name=_('ocorrência')
    )
    arquivo = models.FileField(
        _('Arquivo anexado'),
        upload_to='apps/ocorrencia/anexo/arquivo',
        max_length=500
    )
    descricao = models.CharField(
        _('descrição do anexo'),
        max_length=70
    )
    data_pub = models.DateTimeField(
        _('data da publicação do anexo'),
        null=True,
        blank=True,
        auto_now_add=True
    )

    class Meta:
        ordering = ('-data_pub',)
        verbose_name =  _('Anexo')
        verbose_name_plural =_('Anexos')

    def __str__(self):
        return _(f"{self.arquivo.name}: {self.descricao}")
