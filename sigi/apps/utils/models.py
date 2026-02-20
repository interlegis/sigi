import io
from contextlib import redirect_stderr, redirect_stdout
from cron_converter import Cron
from pyexpat import model
from django.db import models
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.formats import localize
from django.utils.translation import gettext as _
from django_extensions.management.jobs import get_job, get_jobs
from tinymce.models import HTMLField
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from docutils.core import publish_string
from django.utils.html import format_html


class SigiAlert(models.Model):
    DESTINATARIOS_CHOICES = (
        ("A", _("Todo e qualquer usuário")),
        ("N", _("Usuários anônimos / não autenticados")),
        ("S", _("Membros da equipe Interlegis")),
        ("D", _("Administradores do sistema")),
    )
    caminho = models.CharField(_("caminho da tela"), max_length=200)
    destinatarios = models.CharField(
        _("destinatários"), max_length=1, choices=DESTINATARIOS_CHOICES
    )
    titulo = models.CharField(_("título"), max_length=60)
    mensagem = HTMLField(_("mensagem"))

    class Meta:
        ordering = ("caminho", "destinatarios")
        verbose_name = _("alerta SIGI")
        verbose_name_plural = _("alertas SIGI")

    def __str__(self):
        return self.titulo


class Config(models.Model):
    PARAMETRO_CHOICES = (
        ("ENCERRA_INSCRICAO", _("Encerra inscrições de oficinas no Portal")),
        ("EMAIL_JOBS", _("E-mail de jobs")),
    )
    DEFAULTS = {
        "ENCERRA_INSCRICAO": "30",
        "EMAIL_JOBS": "sigi@interlegis.leg.br",
    }
    parametro = models.CharField(
        _("parâmetro"), max_length=100, choices=PARAMETRO_CHOICES
    )
    valor = models.CharField(_("valor do parâmettro"), max_length=200)

    class Meta:
        ordering = ("parametro",)
        verbose_name = _("Parâmetro de configuração")
        verbose_name_plural = _("Parâmetros de configuração")

    def __str__(self):
        return f"{self.get_parametro_display()}: {self.valor}"

    @classmethod
    def get_param(cls, parametro):
        if parametro not in cls.DEFAULTS:
            raise cls.DoesNotExist(
                _(
                    f"Não existe o parâmetro '{parametro}'. "
                    f"As opções são {', '.join(cls.DEFAULTS.keys())}."
                )
            )
        valores = list(
            cls.objects.filter(parametro=parametro).values_list(
                "valor", flat=True
            )
        )
        if not valores:
            valores.append(cls.DEFAULTS[parametro])
        return valores
