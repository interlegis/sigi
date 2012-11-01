# -*- coding: utf-8 -*-
from django.db import models

class Recurso(models.Model):
    nome = models.CharField(u'Nome', max_length=60)
    descricao = models.TextField(u'Descrição', help_text = 'Descrição detalhada do recurso', blank=True)
    quantidade = models.PositiveIntegerField(u'Quantidade', 'Quantidade disponível do recurso no Interlegis. Use 9999 para infinito')
    
    class Meta:
        verbose_name, verbose_name_plural = 'Recurso', 'Recursos' 
    
    def __unicode__(self):
        return self.nome;
    
    def qtde_disponivel(self, data_inicio, data_fim):
        """
        Given a date range, return the available quantity of recourse in that period.
        """
        #TODO: Write the code when Evento model is done
        return self.quantidade
    
    def reservar(self, evento, data_inicio, data_fim):
        """
        Lock a quantity of resource to an 'evento' in timeslice between 'data_inicio' and 'data_fim'
        Return True if successfull or False otherwise
        """
        # TODO: Write code when Evento model is done
        return True
