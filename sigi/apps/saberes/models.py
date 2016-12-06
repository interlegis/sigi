# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _

from sigi.apps.mdl.models import (Course, CourseCategories, CourseCompletions,
                                  UserEnrolments)


class CategoriasInteresse(models.Model):
    prefixo = models.CharField(_(u"Prefixo das categorias no Moodle"), max_length=100,
                               help_text=_(u"Identifica as categorias no Moodle (campo idnumber) relacionadas a este interesse"))
    descricao = models.CharField(_(u"Descrição"), max_length=100)
    sigla = models.CharField(_(u"Sigla"), max_length=20)
    coorte = models.BooleanField(_(u"Usa Cohorte"), default=False, help_text=_(u"Usa cohorte para calcular o número de matrículas/alunos"))
    apurar_alunos = models.BooleanField(_(u"Apurar alunos"), default=False, help_text=_(u"Indica que deve-se verificar o perfil da"
                                                                                        + " inscrição para saber se é um aluno ou se a matrícula foi rejeitada"))
    apurar_conclusao = models.BooleanField(_(u"Apurar conclusão"), default=False, help_text=_(u"Indica se o dashboard mostrará o "
                                                                                              + "número de alunos aprovados, reprovados e desistentes"))

    class Meta:
        verbose_name = _(u'Categorias de interesse')

    def __unicode__(self):
        return self.descricao

    def categorias(self, subcategorias=False):
        def get_sub_categorias(categorias):
            result = CourseCategories.objects.none()
            for c in categorias:
                c_children = CourseCategories.objects.filter(parent=c)
                result = result | c_children | get_sub_categorias(c_children)
            return result

        q = CourseCategories.objects.filter(idnumber__startswith=self.prefixo)

        if subcategorias:
            q = q | get_sub_categorias(q)

        return q

    def get_all_courses(self, only_visible=False):
        q = Course.objects.none()
        for categoria in self.categorias():
            q = q | categoria.get_all_courses(only_visible=only_visible)
        return q

    def get_all_completions(self):
        q = CourseCompletions.objects.none()
        for c in self.get_all_courses():
            q = q | c.coursecompletions_set.all()
        return q

    def get_all_enrolments(self):
        q = UserEnrolments.objects.none()
        for c in self.get_all_courses():
            q = q | c.get_matriculas()
        return q

    def total_alunos_coorte(self):
        return sum(c.total_alunos_cohort() for c in self.categorias())

# A temporary model to store Moodle processed data by management command (called from CRON)


class PainelItem(models.Model):
    painel = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    help_text = models.CharField(max_length=255)
    valor = models.IntegerField()
    percentual = models.FloatField(null=True)

    class Meta:
        ordering = ['pk']
