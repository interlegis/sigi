from pyexpat import model
from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import gettext as _
from tinymce.models import HTMLField


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
