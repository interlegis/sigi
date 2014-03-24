# -*- coding: utf8 -*-

from django.test import TestCase


class DiagnosticosViewsTest(TestCase):
    """Testes feitos para verificar o funcionamento
    do view de diagnósticos.
    """

    def test_diagnostico_list_success(self):

        response = self.client.get('/mobile/diagnosticos')
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, 'diagnosticos/diagnosticos_list.html')
