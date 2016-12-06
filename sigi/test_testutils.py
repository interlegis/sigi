from collections import namedtuple

from sigi.testutils import SigiDataFixture

FieldStub = namedtuple('FieldStub', ['max_length'])


def test_sigidatafixture():
    data_fixture = SigiDataFixture()

    field1 = FieldStub(max_length=1)
    assert ['A', 'B', 'C'] == [data_fixture.charfield_config(field1, "") for i in range(3)]

    field2 = FieldStub(max_length=2)
    pairs = ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ', 'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ', 'CA', 'CB']
    assert pairs == [data_fixture.charfield_config(field2, "") for i in range(len(pairs))]
