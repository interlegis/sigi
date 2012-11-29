# -*- coding: utf8 -*-

import new
from django.http import HttpResponse, QueryDict
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from geraldo.generators import PDFGenerator

from sigi.apps.diagnosticos.urls import LOGIN_REDIRECT_URL
from sigi.apps.utils.decorators import login_required
from sigi.apps.diagnosticos.decorators import validate_diagnostico
from sigi.apps.diagnosticos.models import Diagnostico, Categoria, Pergunta
from sigi.apps.casas.models import Funcionario
from sigi.apps.diagnosticos.forms import (DiagnosticoMobileForm,
        CasaLegislativaMobileForm, FuncionariosMobileForm)
from sigi.apps.contatos.models import Telefone
from sigi.shortcuts import render_to_pdf


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
def lista(request):
    """Consulta os diagnosticos do servidor logado,
    que contenham o status de não publicado.
    """
    servidor = request.user.servidor
    diagnosticos = servidor.diagnosticos
    context = RequestContext(request, {'diagnosticos': diagnosticos})
    return render_to_response('diagnosticos/diagnosticos_list.html', context)


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
@validate_diagnostico
def categorias(request, id_diagnostico):
    """Consulta as categorias do diagnostico selecionado
    a partir da sua identificação
    """
    categorias = Categoria.objects.all()
    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)

    # Estilizando a lista de categorias para que ajude a identificar
    # qual categoria foi a ultima a ser usada, como também as outras
    # que ainda não foram acessadas
    ultima_categoria = request.session.get('ultima_categoria', 0)

    context = RequestContext(request, {'categorias': categorias,
        'diagnostico': diagnostico, 'ultima_categoria': ultima_categoria})
    return render_to_response('diagnosticos/diagnosticos_categorias_list.html',
        context)


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
@validate_diagnostico
def categoria_detalhes(request, id_diagnostico, id_categoria):
    """Captura as perguntas da categoria
    selecionada. Durante o preenchimento das perguntas, o camada
    template do projeto, vai requisitar a inserção dos campos via
    AJAX a cada mudança de pergunta

    Caso alguma inserção não passe na validação do formulário em
    questão, será enviado as mensagens de erro no formato JSON,
    para que a camada de template do projeto trate-as de forma adequada.
    """

    # Grava na sessão a categoria atual, para destacar que
    # era foi a última visitada.
    request.session['ultima_categoria'] = int(id_categoria)

    try:
        categoria = Categoria.objects.get(pk=id_categoria)
    except Categoria.DoesNotExist:
        context = RequestContext(request)
        return render_to_response('mobile/404.html', context)

    diagnostico = Diagnostico.objects.filter(publicado=False).get(pk=id_diagnostico)

    if request.method == "POST":
        form = DiagnosticoMobileForm(request.POST,
            instance=diagnostico, category=id_categoria)
        if form.is_valid():
            form.save()
            resposta = {
                'mensagem': 'sucesso'
            }
        else:
            # Montando a estrutura das mensagens de erro no formato JSON
            resposta = {
                'mensagem': 'erro',
                'erros': form.errors
            }
        json = simplejson.dumps(resposta)
        return HttpResponse(json, mimetype="application/json")
    else:
        form = DiagnosticoMobileForm(instance=diagnostico,
            category=id_categoria)

    context = RequestContext(request, {'form': form, 'categoria': categoria,
        'diagnostico': diagnostico})
    return render_to_response('diagnosticos/diagnosticos_categorias_form.html',
        context)


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
@validate_diagnostico
def categoria_casa_legislativa(request, id_diagnostico):

    # Grava na sessão a categoria atual, para destacar que
    # era foi a última visitada.
    request.session['ultima_categoria'] = 1

    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
    casa_legislativa = diagnostico.casa_legislativa

    if request.method == "POST":
        form = CasaLegislativaMobileForm(request.POST,
            instance=casa_legislativa)
        if form.is_valid():
            form.save()
            resposta = {
                'mensagem': 'sucesso'
            }
        else:
            # Montando a estrutura das mensagens de erro no formato JSON
            resposta = {
                'mensagem': 'erro',
                'erros': form.errors
            }
        json = simplejson.dumps(resposta)
        return HttpResponse(json, mimetype="application/json")
    else:
        form = CasaLegislativaMobileForm(instance=casa_legislativa)

    context = RequestContext(request, {'form': form,
        'diagnostico': diagnostico, 'casa_legislativa': casa_legislativa})
    return render_to_response(
        'diagnosticos/diagnosticos_categoria_casa_legislativa_form.html',
        context)


@never_cache
@login_required(login_url=LOGIN_REDIRECT_URL)
@validate_diagnostico
def categoria_contatos(request, id_diagnostico):

    # Grava na sessão a categoria atual, para destacar que
    # era foi a última visitada.
    request.session['ultima_categoria'] = 2

    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
    casa_legislativa = diagnostico.casa_legislativa
    
    funcionarios = []
    
    for n, l in Funcionario.SETOR_CHOICES:
        if casa_legislativa.funcionario_set.filter(setor=n).count() <= 1:
            funcionarios.append(casa_legislativa.funcionario_set.get_or_create(setor=n))
        else:
            for f in casa_legislativa.funcionario_set.filter(setor=n):
                funcionarios.append((f, False))
            
    if request.method == "POST":
        forms = []
        for f, c in funcionarios:
            try:
                forms.append(FuncionariosMobileForm(request.POST, prefix=f.setor, instance=f))
            except:
                pass

        resposta = {
            'mensagem': 'sucesso',
            'erros' : {},
            'fones' : {},
            'clean' : (),
        }

        # valida e salva um formulario por vez
        for form in forms:
            if form.is_valid():
                form.save()
                s = ''
                for form_telefones in form.telefones.forms:
                    tel = form_telefones.instance
                    if tel._state.adding and tel.numero != '':
                        s += '<p>Novo telefone %s: %s</p>' % (form_telefones.instance.get_tipo_display(), form_telefones.instance.numero)
                        resposta['clean'] += ('id_' + form_telefones.prefix + '-numero',)
                if s != '':
                    resposta['fones'][form.prefix] = s
            else:
                # Montando a estrutura das mensagens de erro no formato JSON
                resposta['mensagem'] = 'erro'
                for key, value in form.errors.iteritems():
                    resposta['erros'][form.prefix + '-' + key + '-errors'] = value

                for form_telefones in form.telefones.forms:
                    if not form_telefones.is_valid():
                        if (form_telefones.fields['id'].initial is not None
                          and form_telefones.fields['tipo'].initial == 'I'
                          and form_telefones.fields['numero'].initial is None):
                            if Telefone.objects.filter(pk=form_telefones.fields['id'].initial).exists():
                                Telefone.objects.get(pk=form_telefones.fields['id'].initial).delete()
                                if not resposta['fones'].has_key(form.prefix):
                                    resposta['fones'][form.prefix] = ''
                                resposta['fones'][form.prefix] += u'<p>O telefone %s %s foi excluído da base de dados</p>' % (
                                    form_telefones.instance.get_tipo_display(), form_telefones.instance.numero)
                        else:  
                            for key, value in form_telefones.errors.iteritems():
                                key = form_telefones.prefix + "-id-errors"
                                resposta['erros'][key] = value

        json = simplejson.dumps(resposta)
        return HttpResponse(json, mimetype="application/json")
    else:
        forms = [FuncionariosMobileForm(prefix=f.setor, instance=f)
            for f, c in funcionarios]

    context = RequestContext(request, {'forms': forms,
        'diagnostico': diagnostico, 'casa_legislativa': casa_legislativa})
    return render_to_response('diagnosticos/diagnosticos_categoria_contatos_form.html',
        context)

def diagnostico_pdf(request, id_diagnostico):
    diagnostico = Diagnostico.objects.get(pk=id_diagnostico)
    categorias = Categoria.objects.all()

    casa_legislativa = diagnostico.casa_legislativa
    funcionarios = []
    for n, l in Funcionario.SETOR_CHOICES:
        if casa_legislativa.funcionario_set.filter(setor=n).count() <= 1:
            funcionarios.append(casa_legislativa.funcionario_set.get_or_create(setor=n))
        else:
            for f in casa_legislativa.funcionario_set.filter(setor=n):
                funcionarios.append(f)

    schemas_by_categoria = []
    for categoria in categorias:
        schemas = []
        for schema in diagnostico.get_schemata(categoria.id):
            datatype = schema.datatype
            data = getattr(diagnostico, schema.name)
            if datatype == schema.TYPE_MANY:
                schema.value = [x.pk for x in data]
            elif datatype == schema.TYPE_ONE:
                schema.value = data.pk if data else None,
            else:
                schema.value = data
            schemas.append(schema)

        schemas_by_categoria.append((categoria,schemas))

    context = RequestContext(request, {
          'pagesize':'A4',
          'casa_legislativa': casa_legislativa,
          'funcionarios': funcionarios,
          'diagnostico': diagnostico,
          'schemas_by_categoria': schemas_by_categoria,
        })

    return render_to_pdf('diagnosticos/diagnostico_pdf.html', context)
    #return render_to_response('diagnosticos/diagnostico_pdf.html', context)

def graficos(request):
    categorias = Categoria.objects.all()

    sel_categoria = int(request.REQUEST.get("categoria","3"))
    perguntas = Pergunta.objects.filter(categoria=sel_categoria).all()

    context = RequestContext(request, {
        'categorias': categorias,
        'sel_categoria': sel_categoria,
        'perguntas': perguntas,
        })
    return render_to_response('diagnosticos/graficos.html',
        context)

def percentage(fraction, population):
    try:
        return "%.0f%%" % ((float(fraction) / float(population)) * 100)
    except ValueError:
        return ''

def grafico_api(request):
    graph_url = "http://chart.apis.google.com/chart"
    #graph_params = QueryDict("chxt=y&chbh=a&chco=A2C180,3D7930")
    graph_params = QueryDict("")
    graph_params = graph_params.copy() # to make it mutable

    width = request.REQUEST.get('width', '800')
    height = request.REQUEST.get('height', '300')
    graph_params.update({'chs': width + 'x' + height})

    pergunta_slug = request.REQUEST.get('id', None)
    pergunta = get_object_or_404(Pergunta, name=pergunta_slug)

    if pergunta.datatype == 'one':
      total = sum([r[1] for r in pergunta.group_choices()])
      choices = [str(r[1]) for r in pergunta.group_choices()]
      legend = [percentage(r[1],total) + " " + str(r[0]) for r in pergunta.group_choices()]
      graph_params.update({
        'cht': 'p',
        'chd': 't:' + ",".join(choices),
        'chdl': '' + "|".join(legend),
        })
    elif pergunta.datatype == 'many':
      total = sum([r[1] for r in pergunta.group_choices()])
      percent = [str(float(r[1])*100/total) for r in pergunta.group_choices()]
      choices = [str(r[1]) for r in pergunta.group_choices()]
      legend = [str(r[0]) for r in pergunta.group_choices()]
#      colors =  [reduce(lambda x,y: x + hex(y).replace('0x',''), map(lambda x: x*(100-(p*10))/100,[0xff, 0xcc,0x33]),'') 
#                 for p in range(0,len(pergunta.group_choices()))]
      colors = ["%0.6x" % (0x48d1 + (0xda74 * c))
                for c in range(0,len(pergunta.group_choices()))]
      graph_params.update({
        'cht': 'bvg',
        'chxt': 'y',
        'chd': 't:' + ",".join(percent),
        'chdl': '' + "|".join(legend),
        'chl': '' + "|".join(choices),
        'chco': '' + "|".join(colors)
        })

    response = {
        "type": "photo",
        "width": width,
        "height": height,
        "title": pergunta.title,
        "url": graph_url + "?" + graph_params.urlencode(),
        "provider_name": "SIGI",
        "provider_url": "https://intranet.interlegis.gov.br/sigi/"
    }

    json = simplejson.dumps(response)
    return HttpResponse(json, mimetype="application/json")

def municipios_diagnosticados(self):
    municipios = []
    
    for d in Diagnostico.objects.all():
        m = d.casa_legislativa.municipio
        municipio = {'nome': d.casa_legislativa.nome + ', ' + m.uf.sigla, 'lat': str(m.latitude), 'lng': str(m.longitude), 'inicio': d.data_visita_inicio.strftime('%d/%m/%Y'),
                     'fim': d.data_visita_fim.strftime('%d/%m/%Y'), 'equipe': "<ul><li>" + "</li><li>".join([m.user.get_full_name() for m in d.membros]) + "</li></ul>",}
        municipios.append(municipio)
        
    return HttpResponse(simplejson.dumps(municipios), mimetype="application/json")