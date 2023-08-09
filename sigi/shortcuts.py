# -*- coding: utf-8 -*-
from cgi import escape
from datetime import datetime
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
        path = os.path.join(
            settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, "")
        )
    else:
        # Imagem está em MEDIA_ROOT
        path = os.path.join(
            settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, "")
        )
    return path


def pdf_renderer(template, context, filename="report.pdf"):
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=" + filename

    pdf = pisa.CreatePDF(html, dest=response, link_callback=fetch_resources)

    if pdf.err:
        return HttpResponse(
            _("We had some errors<pre>%s</pre>") % escape(html)
        )
    return response


def render_to_pdf(template_src, context_dict):
    filename = template_src.replace(".html", "").replace("_pdf", ".pdf")
    template = get_template(template_src)
    context = Context(context_dict)

    return pdf_renderer(template, context, filename)
