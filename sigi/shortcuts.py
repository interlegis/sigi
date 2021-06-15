# -*- coding: utf-8 -*-
from cgi import escape
import os

from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _

import cStringIO as StringIO
import ho.pisa as pisa


def fetch_resources(uri, rel):
    if uri.find(settings.STATIC_URL) != -1:
        # Imagem está em STATIC_ROOT
        path = os.path.join(settings.STATIC_ROOT,
                            uri.replace(settings.STATIC_URL, ""))
    else:
        # Imagem está em MEDIA_ROOT
        path = os.path.join(settings.MEDIA_ROOT,
                            uri.replace(settings.MEDIA_URL, ""))
    return path


def render_to_pdf(template_src, context_dict):
    filename = template_src.replace('.html', '').replace('_pdf', '.pdf')
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('utf-8')), result, link_callback=fetch_resources)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response
    return HttpResponse(_(u'We had some errors<pre>%s</pre>') % escape(html))
