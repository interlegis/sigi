# -*- coding: utf-8 -*-
from geraldo import Report, ReportBand, ObjectValue, DetailBand, Label, FIELD_ACTION_SUM, FIELD_ACTION_COUNT
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

class ConvenioReportRegiao(Report):
    title = u'Relatório dos Convênios por Região'
    author = u'Interlegis'
    class band_page_header(ReportBand):
        elements = [
            Label(
                text="Região", left=0*cm
            ),
            Label(
                text="Quantidade Casas", left=3*cm,
            ),
            Label(
                text="Quantidade Casas Conveniadas", left=6*cm
            ),
            Label(
                text="Porcentagem Casas Conveniadas", left=15*cm
            ),
        ]
    class band_detail(DetailBand):
        height = 0.5*cm
        elements=[
            ObjectValue(attribute_name='regiao', left=0*cm, ),
            ObjectValue(attribute_name='casas', left=3*cm,),
            ObjectValue(attribute_name='casas_conveniadas', left=6*cm),
            ObjectValue(attribute_name='porc_casas_conveniadas', left=15*cm),
        ]
        border = {'bottom': True}
    class band_summary(ReportBand):
        elements = [
            Label(text="Total", top=0.1*cm, left=0),
            ObjectValue(attribute_name='casas', action=FIELD_ACTION_SUM, left=3*cm, top=0.1*cm),
            ObjectValue(attribute_name='casas_conveniadas', left=6*cm, action=FIELD_ACTION_SUM),
                    ]
        borders = {'top':True}
        child_bands = [
            ReportBand(
                height = 0.6*cm, 
                elements = [
                    Label(text="Total",),
                    ObjectValue(attribute_name='casas', action=FIELD_ACTION_COUNT,)
                    ]
                ),
            ]
