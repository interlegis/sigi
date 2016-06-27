import string
from cStringIO import StringIO
from itertools import product

import pyPdf
from django_dynamic_fixture.fixture_algorithms.sequential_fixture import \
    SequentialDataFixture


def pdf_text(res):
    content_as_file = StringIO(res.content)
    pdf = pyPdf.PdfFileReader(content_as_file)
    pdf_text = '\n'.join([page.extractText() for page in pdf.pages])
    return pdf_text


class SigiDataFixture(SequentialDataFixture):

    alphabet = string.ascii_uppercase

    def __init__(self):
        self.word_generators = {}  # length => word generator
        super(SigiDataFixture, self).__init__()

    def get_word_generator(self, length):
        gen = self.word_generators.get(length)
        if not gen:
            gen = (''.join(i) for i in product(self.alphabet, repeat=length))
            self.word_generators[length] = gen
        return gen

    def charfield_config(self, field, key):
        length = field.max_length or 100        # XXX leave this 100 hardcoded?
        gen = self.get_word_generator(length)
        return gen.next()
