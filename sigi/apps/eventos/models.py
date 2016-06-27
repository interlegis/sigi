# -*- coding: utf-8 -*-
#
# sigi.apps.eventos.models
#
# Copyright (C) 2015  Interlegis
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import lazy
from django.utils.translation import ugettext as _

from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.contatos.models import Municipio
from sigi.apps.mdl.models import Course
from sigi.apps.servidores.models import Servidor
from sigi.apps.utils.moodle_ws_api import get_courses


class TipoEvento(models.Model):
    nome = models.CharField(_(u"Nome"), max_length=100)
    
    class Meta:
        ordering = ("nome",)
        verbose_name, verbose_name_plural = _(u"Tipo de evento"), _(u"Tipos de evento")
        
    def __unicode__(self):
        return self.nome

class Evento(models.Model):
    STATUS_CHOICES = (
        ('P', _(u"Previsão")),
        ('A', _(u"A confirmar")),
        ('O', _(u"Confirmado")),
        ('R', _(u"Realizado")),
        ('C', _(u"Cancelado"))
    )
    
#     def get_course_choices():
#         result = [(None, u'---------')]
#     
#         try:
#             courses = get_courses(sort_order='categorysortorder', idnumber__startswith='evento')
#             result = result + [(c['id'], c['fullname']) for c in courses]
#         except Exception as e:
#             result.append((None, _(u"Erro ao acessar o saberes: '%s'" % (e.message,))))
#     
#         return result

    def get_course_choices():
        from django.apps import apps
        if apps.models_ready:
            courses = Course.objects.filter(idnumber__startswith='evento')
        else:
            courses = []
        result = [(None, u'---------')] + [(c.id, c.fullname) for c in courses]
        return result

    tipo_evento = models.ForeignKey(TipoEvento)
    nome = models.CharField(_(u"Nome do evento"), max_length=100)
    descricao = models.TextField(_(u"Descrição do evento"))
    solicitante = models.CharField(_(u"Solicitante"), max_length=100)
    data_inicio = models.DateField(_(u"Data de início"))
    data_termino = models.DateField(_(u"Data de término"))
    casa_anfitria = models.ForeignKey(CasaLegislativa, verbose_name=_(u"Casa anfitriã"), blank=True, 
                                      null=True)
    municipio = models.ForeignKey(Municipio)
    local = models.TextField(_(u"Local do evento"), blank=True)
    publico_alvo = models.TextField(_(u"Público alvo"), blank=True)
    status = models.CharField(_(u"Status"), max_length=1, choices=STATUS_CHOICES)
    data_cancelamento = models.DateField(_(u"Data de cancelamento"), blank=True, null=True)
    motivo_cancelamento = models.TextField(_(u"Motivo do cancelamento"), blank=True)
    curso_moodle_id = models.IntegerField(_(u"Curso saberes"), blank=True, null=True, 
                                          choices=lazy(get_course_choices, list)())
    
    class Meta:
        ordering = ("-data_inicio",)
        verbose_name, verbose_name_plural = _(u"Evento"), _(u"Eventos")
        
    def __unicode__(self):
        return _("%(nome)s (%(tipo_evento)s): de %(data_inicio)s a %(data_termino)s") % dict(
                    nome=self.nome,
                    tipo_evento=unicode(self.tipo_evento),
                    data_inicio=self.data_inicio,
                    data_termino=self.data_termino)
        
    def save(self, *args, **kwargs): 
        if self.status != 'C':
            self.data_cancelamento = None
            self.motivo_cancelamento = ""
        if self.data_inicio > self.data_termino:
            raise ValidationError(_(u"Data de término deve ser posterior à data de início"))
        return super(Evento, self).save(*args, **kwargs)
        
class Funcao(models.Model):
    nome = models.CharField(_(u"Função na equipe de evento"), max_length=100)
    descricao = models.TextField(_(u"Descrição da função"))
    
    class Meta:
        ordering = ("nome",)
        verbose_name, verbose_name_plural = _(u"Função"), _(u"Funções")
        
    def __unicode__(self):
        return self.nome
    
class Equipe(models.Model):
    evento = models.ForeignKey(Evento)
    membro = models.ForeignKey(Servidor, related_name="equipe_evento")
    funcao = models.ForeignKey(Funcao, verbose_name=_(u"Função na equipe"))
    observacoes = models.TextField(_(u"Observações"), blank=True)
    
    class Meta:
        ordering = ('evento', 'funcao', 'membro',)
        verbose_name, verbose_name_plural = _(u"Membro da equipe"), _(u"Membros da equipe")
        
    def __unicode__(self):
        return u"%s (%s)" % (unicode(self.membro), unicode(self.funcao),)
    
class Convite(models.Model):
    evento = models.ForeignKey(Evento)
    casa = models.ForeignKey(CasaLegislativa, verbose_name=_(u"Casa convidada"))
    servidor = models.ForeignKey(Servidor, verbose_name=_(u"Servidor que convidou"))
    data_convite = models.DateField(_(u"Data do convite"))
    aceite = models.BooleanField(_("Aceitou o convite"), default=False)
    participou = models.BooleanField(_(u"Participou do evento"), default=False)
    
    class Meta:
        ordering = ('evento', 'casa', '-data_convite')
        unique_together = ('evento', 'casa')
        verbose_name, verbose_name_plural = _(u"Casa convidada"), _(u"Casas convidadas")
