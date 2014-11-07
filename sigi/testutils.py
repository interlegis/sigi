from cStringIO import StringIO

import pyPdf


def pdf_text(res):
    content_as_file = StringIO(res.content)
    pdf = pyPdf.PdfFileReader(content_as_file)
    pdf_text = '\n'.join([page.extractText() for page in pdf.pages])
    return pdf_text
