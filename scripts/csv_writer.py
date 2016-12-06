import codecs
import cStringIO
import csv


class CsvWriter:

    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    from https://docs.python.org/2/library/csv.html
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8"):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def clean(self, cell):
        return unicode(cell) if cell else '-'

    def writerow(self, row):
        self.writer.writerow([self.clean(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
