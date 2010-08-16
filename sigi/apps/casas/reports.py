# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from geraldo import Report, DetailBand, Label, ObjectValue, ManyElements, \
                    ReportGroup, ReportBand, landscape

from sigi.apps.relatorios.reports import ReportDefault

def string_to_cm(texto):
    tamanho = 0
    minEspeciais = {
       'f':0.1,
       'i':0.05,
       'j':0.05,
       'l':0.05,
       'm':0.2,
       'r':0.1,
       't':0.15,
    }
    maiuEspeciais = {
       'I':0.05,
       'J':0.15,
       'L':0.15,
       'P':0.15,
    }
    for c in texto:
        if c > 'a' and c<'z':
            if c in minEspeciais:                
                tamanho += minEspeciais[c]                
            else:                
                tamanho += 0.17                
        else:
            if c in maiuEspeciais:                
                tamanho += maiuEspeciais[c]                
            else:                
                tamanho += 0.2                
    return tamanho



class CasasLegislativasLabels(Report):
    """
    Usage example::

      >>> from geraldo.generators import PDFGenerator
      >>> queryset = CasaLegislativa.objects.filter(municipio__uf__sigla='MG')
      >>> report = LabelsReport(queryset)
      >>> report.generate_by(PDFGenerator, filename='./inline-detail-report.pdf')

    """

    page_size = A4
    margin_top = 0.8*cm
    margin_bottom = 0.8*cm
    margin_left = 0.4*cm
    margin_right = 0.4*cm

    class band_detail(DetailBand):


        width  = 9.9*cm
        height = 5.6*cm
        margin_bottom = 0.0*cm
        margin_right  = 0.3*cm                

        # With this attribute as True, the band will try to align in
        # the same line.
        display_inline = True        

        default_style = {'fontName': 'Helvetica', 'fontSize': 11}        
       
        elements = [            
            Label(
                text='A Sua Excelência o(a) Senhor(a)',
                top=1*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='parlamentar',
                top=1.5*cm, left=0.5*cm, width=9.4*cm,                
            ),
            ObjectValue(
                attribute_name='nome',
                top=2*cm, left=0.5*cm, width=9.4*cm,
                get_value=lambda instance:
                    "Presidente da " + instance.nome
            ),
            ObjectValue(
                attribute_name='logradouro',
                top=2.5*cm, left=0.5*cm, width=9.4*cm,
                get_value=lambda instance:                    
                        (instance.logradouro +" - "+ instance.bairro)
                            if len(instance.bairro) != 0
                            else instance.logradouro                    
            ),
            ObjectValue(
                attribute_name='municipio',
                top=3*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='cep',
                top=3.5*cm, left=0.5*cm, width=9.4*cm,                
            ),            
        ]

class CasasLabelsNomeMaior(CasasLegislativasLabels):
    class band_detail(CasasLegislativasLabels.band_detail):        
        elements = [
            Label(
                text='A Sua Excelência o(a) Senhor(a)',
                top=1*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='parlamentar',
                top=1.5*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='nome',
                top=2*cm, left=0.5*cm, width=9.4*cm,
                get_value=lambda instance:
                    "Presidente da " + instance.nome
            ),
            ObjectValue(
                attribute_name='logradouro',
                top=3*cm, left=0.5*cm, width=9.4*cm,
                get_value=lambda instance:
                        instance.logradouro +" - "+ instance.bairro
                            if len(instance.bairro) != 0
                            else instance.logradouro
            ),
            ObjectValue(
                attribute_name='municipio',
                top=3.5*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='cep',
                top=4*cm, left=0.5*cm, width=9.4*cm,
            ),
        ]

class CasasLabelsEnderecoMaior(CasasLegislativasLabels):
    class band_detail(CasasLegislativasLabels.band_detail):
        elements = [
            Label(
                text='A Sua Excelência o(a) Senhor(a)',
                top=1*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='parlamentar',
                top=1.5*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='nome',
                top=2*cm, left=0.5*cm, width=9.4*cm,
                get_value=lambda instance:
                    "Presidente da " + instance.nome
            ),
            ObjectValue(
                attribute_name='logradouro',
                top=2.5*cm, left=0.5*cm, width=9.4*cm,
                get_value=lambda instance:
                        instance.logradouro +" - "+ instance.bairro
                            if len(instance.bairro) != 0
                            else instance.logradouro
            ),
            ObjectValue(
                attribute_name='municipio',
                top=3.5*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='cep',
                top=4*cm, left=0.5*cm, width=9.4*cm,
            ),
        ]

class CasasLabelsNomeMaiorEnderecoMaior(CasasLegislativasLabels):
    class band_detail(CasasLegislativasLabels.band_detail):
        elements = [
            Label(
                text='A Sua Excelência o(a) Senhor(a)',
                top=1*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='parlamentar',
                top=1.5*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='nome',
                top=2*cm, left=0.5*cm, width=9.4*cm,
                get_value=lambda instance:
                    "Presidente da " + instance.nome
            ),
            ObjectValue(
                attribute_name='logradouro',
                top=3*cm, left=0.5*cm, width=9.4*cm,
                get_value=lambda instance:
                        instance.logradouro +" - "+ instance.bairro
                            if len(instance.bairro) != 0
                            else instance.logradouro
            ),
            ObjectValue(
                attribute_name='municipio',
                top=4*cm, left=0.5*cm, width=9.4*cm,
            ),
            ObjectValue(
                attribute_name='cep',
                top=4.5*cm, left=0.5*cm, width=9.4*cm,
            ),
        ]




class CasasLegislativasReport(ReportDefault):
    title = u'Relatório de Casas Legislativas'

    class band_page_header(ReportDefault.band_page_header):

        label_top = ReportDefault.band_page_header.label_top
        label_left = [0.3,1,5.5,11]
        elements = list(ReportDefault.band_page_header.elements)

        elements += [
            Label(
                text="UF",
                left=label_left[0]*cm,
                top=label_top,
            ),
            Label(
                text="Municipio",
                left=label_left[1]*cm,
                top=label_top,
            ),            
            Label(
                text="Presidente",
                left=label_left[2]*cm,
                top=label_top,                
            ),
            Label(
                text="Logradouro",
                left=label_left[3]*cm,
                top=label_top,                
            ),
            
        ]



    class band_page_footer(ReportDefault.band_page_footer):
        pass

    class band_detail(ReportDefault.band_detail):

        label_left = [0.3,1,5.5,11]

        elements=[
            ObjectValue(
                attribute_name='municipio.uf.sigla',
                left=label_left[0]*cm,
            ),
            ObjectValue(
                attribute_name='municipio.nome',
                left=label_left[1]*cm,
            ),            
            ObjectValue(
                attribute_name='parlamentar',
                left=label_left[2]*cm,
            ),
            ObjectValue(
                attribute_name='logradouro',
                left=label_left[3]*cm,
                get_value=lambda instance: instance.logradouro + ' - '+ instance.bairro,                
            ),
        ]

    groups = [
        ReportGroup(attribute_name='municipio.uf',
            band_header=ReportBand(
                height=0.7*cm,
                elements= [
                    ObjectValue(attribute_name='municipio.uf')
                ],
                borders={'top': True},
            )
        )
    ]


class CasasSemConvenioReport(CasasLegislativasReport):
    title = u'Relatório de Casas Legislativas sem Convênio'

class InfoCasaLegislativa(ReportDefault):    
    class band_detail(ReportDefault.band_detail):
        
        posicao_left = [
            0,1.8,       #Regiao
            5.5,6.8,     #U.F.
            12,13.3,           #Tipo
            0,2.3,       #Municipio
            0,2.8,       #Logradouro
            0,1.6,         #Bairro
            0,1.3,         #CEP
        ]
        posicao_top = [
            0.5,         #Regiao
            0.5,         #U.F.
            0.5,         #Tipo
            1.3,         #Municipio
            2.1,         #Logradouro
            2.9,         #Bairro
            3.7,         #CEP
        ]

        display_inline = True
        REGIAO_CHOICES = {'SL': 'Sul','SD': 'Sudeste','CO': 'Centro-Oeste','NE': 'Nordeste','NO': 'Norte',}
        default_style = {'fontName': 'Helvetica', 'fontSize':14}


        elements = [

            # Linha 1
            Label(
                text="Região: ",
                left=posicao_left[0]*cm,
                top=posicao_top[0]*cm,
            ),            
            ObjectValue(
                attribute_name='municipio.uf.regiao',
                left=posicao_left[1]*cm,
                top=posicao_top[0]*cm,
                get_value=lambda instance:
                      {'SL': 'Sul','SD': 'Sudeste','CO': 'Centro-Oeste','NE': 'Nordeste','NO': 'Norte',}
                      [instance.municipio.uf.regiao]
            ),
            Label(
                text="U.F.: ",
                left=posicao_left[2]*cm,
                top=posicao_top[1]*cm,
            ),
            ObjectValue(
                attribute_name='municipio.uf',
                left=posicao_left[3]*cm,
                top=posicao_top[1]*cm,
            ),
            Label(
                text="Tipo: ",
                left=posicao_left[4]*cm,
                top=posicao_top[2]*cm,
            ),
            ObjectValue(
                attribute_name='tipo.nome',
                left=posicao_left[5]*cm,
                top=posicao_top[2]*cm,
                width=6*cm,
            ),
            # Linha 2
            Label(
                text="Município: ",
                left=posicao_left[6]*cm,
                top=posicao_top[3]*cm,
            ),
            ObjectValue(
                attribute_name='municipio.nome',
                left=posicao_left[7]*cm,
                top=posicao_top[3]*cm,
                width=20*cm,
            ),
            # Linha 3
            Label(
                text="Logradouro: ",
                left=posicao_left[8]*cm,
                top=posicao_top[4]*cm,
            ),
            ObjectValue(
                attribute_name='logradouro',
                left=posicao_left[9]*cm,
                top=posicao_top[4]*cm,
                width=20*cm,
            ),
            Label(
                text="Bairro: ",
                left=posicao_left[10]*cm,
                top=posicao_top[5]*cm,
            ),
            ObjectValue(
                attribute_name='bairro',
                left=posicao_left[11]*cm,
                top=posicao_top[5]*cm,
            ),
            Label(
                text="CEP: ",
                left=posicao_left[12]*cm,
                top=posicao_top[6]*cm,
            ),
            ObjectValue(
                attribute_name='cep',
                left=posicao_left[13]*cm,
                top=posicao_top[6]*cm,
            ),

            
        ]