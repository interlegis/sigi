# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext as _

from sigi.apps.casas.models import Orgao


class Partido(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)

    class Meta:
        ordering = ("nome",)

    def __unicode__(self):
        return "%s (%s)" % (unicode(self.nome), unicode(self.sigla))


class Parlamentar(models.Model):
    SEXO_CHOICES = (
        ("M", _("Masculino")),
        ("F", _("Feminino")),
    )
    nome_completo = models.CharField(max_length=128)
    nome_parlamentar = models.CharField(max_length=35, blank=True)
    foto = models.ImageField(
        upload_to="fotos/parlamentares",
        width_field="foto_largura",
        height_field="foto_altura",
        blank=True,
    )
    foto_largura = models.SmallIntegerField(editable=False, null=True)
    foto_altura = models.SmallIntegerField(editable=False, null=True)
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
    )
    data_nascimento = models.DateField(
        _("data de nascimento"),
        blank=True,
        null=True,
    )
    email = models.EmailField(_("e-mail"), blank=True)
    pagina_web = models.URLField(_("página web"), blank=True)

    class Meta:
        ordering = ("nome_completo",)
        verbose_name_plural = _("parlamentares")

    def __unicode__(self):
        if self.nome_parlamentar:
            return self.nome_parlamentar
        return self.nome_completo


class Mandato(models.Model):
    SUPLENCIA_CHOICES = (
        ("T", _("Titular")),
        ("S", _("Suplente")),
    )
    parlamentar = models.ForeignKey(Parlamentar, on_delete=models.CASCADE)
    legislatura = models.ForeignKey(
        "parlamentares.Legislatura", on_delete=models.CASCADE
    )
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    cargo = models.ForeignKey("parlamentares.Cargo", on_delete=models.PROTECT)
    inicio_mandato = models.DateField(_("início de mandato"))
    fim_mandato = models.DateField(_("fim de mandato"))
    is_afastado = models.BooleanField(
        _("afastado"),
        default=False,
        help_text=_("Marque caso parlamentar não esteja ativo."),
    )

    #    suplencia = models.CharField(
    #        _('suplência'),
    #        max_length=1,
    #        choices=SUPLENCIA_CHOICES,
    #    )

    def __unicode__(self):
        return str(self.id)


class Legislatura(models.Model):
    casa_legislativa = models.ForeignKey(Orgao, on_delete=models.CASCADE)
    numero = models.PositiveSmallIntegerField(_("número legislatura"))
    data_inicio = models.DateField(_("início"))
    data_fim = models.DateField(_("fim"))
    data_eleicao = models.DateField(_("data da eleição"))
    total_parlamentares = models.PositiveIntegerField(
        _("Total de parlamentares")
    )

    casa_legislativa.convenio_uf_filter = True
    casa_legislativa.convenio_cl_tipo_filter = True

    class Meta:
        unique_together = ("casa_legislativa", "numero")
        ordering = ["casa_legislativa__municipio__uf__sigla", "-data_inicio"]

    def __unicode__(self):
        return _(
            "%(number)sª legislatura da %(parliament)s (%(initial_year)s-%(final_year)s)"
        ) % dict(
            number=self.numero,
            parliament=self.casa_legislativa.__unicode__(),
            initial_year=self.data_inicio.year,
            final_year=self.data_fim.year,
        )


class Coligacao(models.Model):
    nome = models.CharField(max_length=50)
    legislatura = models.ForeignKey(Legislatura, on_delete=models.CASCADE)
    numero_votos = models.PositiveIntegerField(
        _("número de votos"),
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("legislatura", "nome")
        verbose_name = _("coligação")
        verbose_name_plural = _("coligações")

    def __unicode__(self):
        return self.nome


class ComposicaoColigacao(models.Model):
    coligacao = models.ForeignKey(
        Coligacao, on_delete=models.CASCADE, verbose_name=_("coligação")
    )
    partido = models.ForeignKey(
        "parlamentares.Partido", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("composição da coligação")
        verbose_name_plural = _("composições das coligações")

    def __unicode__(self):
        return str(self.id)


class SessaoLegislativa(models.Model):
    SESSAO_CHOICES = (
        ("O", _("Ordinária")),
        ("E", _("Extraordinária")),
    )
    numero = models.PositiveSmallIntegerField(
        _("número da sessão"), unique=True
    )
    mesa_diretora = models.ForeignKey(
        "MesaDiretora",
        on_delete=models.PROTECT,
        verbose_name=_("Mesa Diretora"),
    )
    legislatura = models.ForeignKey(Legislatura, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=SESSAO_CHOICES, default="O")
    data_inicio = models.DateField(_("início"))
    data_fim = models.DateField(_("fim"))
    data_inicio_intervalo = models.DateField(
        _("início de intervalo"), blank=True, null=True
    )
    data_fim_intervalo = models.DateField(
        _("fim de intervalo"), blank=True, null=True
    )

    class Meta:
        ordering = ("legislatura", "numero")
        verbose_name = _("Sessão Legislativa")
        verbose_name_plural = _("Sessões Legislativas")

    def __unicode__(self):
        return str(self.numero)


class MesaDiretora(models.Model):
    casa_legislativa = models.ForeignKey(
        "casas.Orgao",
        on_delete=models.CASCADE,
        verbose_name=_("Casa Legislativa"),
    )

    class Meta:
        verbose_name = _("Mesa Diretora")
        verbose_name_plural = _("Mesas Diretoras")

    def __unicode__(self):
        return _("Mesa Diretora da %s") % unicode(self.casa_legislativa)


class Cargo(models.Model):
    descricao = models.CharField(_("descrição"), max_length=30)

    class Meta:
        ordering = ("descricao",)

    def __unicode__(self):
        return self.descricao


class MembroMesaDiretora(models.Model):
    parlamentar = models.ForeignKey(
        "parlamentares.Parlamentar", on_delete=models.CASCADE
    )
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT)
    mesa_diretora = models.ForeignKey(MesaDiretora, on_delete=models.CASCADE)

    class Meta:
        ordering = ("parlamentar",)
        unique_together = ("cargo", "mesa_diretora")
        verbose_name = _("membro de Mesa Diretora")
        verbose_name_plural = _("membros de Mesa Diretora")

    def __unicode__(self):
        return "%s (%s)" % (unicode(self.parlamentar), unicode(self.cargo))
