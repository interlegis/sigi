# -*- coding: utf-8 -*-
from geraldo import Report, ReportBand, ObjectValue, DetailBand, Label
from reportlab.lib.units import cm
class CasasAderidasReport(object):
    pass

class CasasNaoAderidasReport(object):
    pass

class CasasComEquipamentosReport(object):
    pass

class SemEquipamentosReport(object):
    pass
class ConvenioReport(Report):
    title = u'Relatórios dos Convênios'
    author = u'Interlegis'
    class band_page_header(ReportBand):
        elements = [
            Label(
                text="ID", left=0.5*cm
            ),
            Label(
                text="Nº Processo", left=3*cm
            ),
            Label(
                text="Nome", left=5*cm
            ),
            Label(
                text="Data Adesão", left=10*cm
            ),
        ]
        #borders = {'bottom': True}
    class band_detail(DetailBand):
#        height = 0.5*cm
        elements=[
            ObjectValue(attribute_name='id', left=0.5*cm),
            ObjectValue(attribute_name='num_processo_sf', left=3*cm),
            ObjectValue(attribute_name='casa_legislativa', left=5*cm),
            ObjectValue(attribute_name='data_adesao', left=10*cm)
        ]
        border = {'bottom': True}
